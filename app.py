import stripe

from flask import (
    Flask, render_template, abort, redirect, request, url_for, session
)
from tinydb import TinyDB, where
from authlib.integrations.flask_client import OAuth
from dotenv import dotenv_values


env = dotenv_values(".env")

app = Flask(__name__)
app.secret_key = env["SESSION_SECRET"]

oauth = OAuth(app)
stripe.api_key = env["STRIPE_API_KEY"]
db = TinyDB("paycord_db.json")

discord = oauth.register(
    name="discord",
    client_id=env["DISCORD_CLIENT_ID"],
    client_secret=env["DISCORD_CLIENT_SECRET"],
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    api_base_url="https://discord.com/api",
    client_kwargs={"scope": "identify"}
)


@app.route("/discord/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return discord.authorize_redirect(redirect_uri=redirect_uri)


@app.route("/discord/logout")
def logout():
    session.pop("discord")
    return redirect("/")


@app.route("/discord/authorize")
def authorize():
    token = discord.authorize_access_token()
    user = discord.get('/api/users/@me', token=token).json()
    session["discord_id"] = user["id"]
    return redirect("/")


@app.route("/subscription/<product_id>/<int:given_amount>", methods=["POST"])
def order(product_id: str, given_amount: int):
    if "discord_id" not in session:
        abort(403)

    config = db.table("config").all()
    if stripe.api_key is None or config is None:
        abort(500)

    product = db.table("products").search(where("product_id") == product_id)
    if not product:
        abort(404)

    if product[0]["min_price"] > given_amount:
        abort(400)

    session = stripe.checkout.Session.create(
        line_item=[{
            "price_data": {
                "product_data": {"name": product[0]["name"]},
                "unit_amount": given_amount,
                "currency": config[0]["currency"],
                "recurring": {"interval": "month", "interval_count": 1}
            },
            "quantity": 1,
            "adjustable_quantity": {"enabled": False}
        }],
        payment_method_types=["card"],
        mode="subscription",
        subscription_data={},
        success_url=request.host_url + "order/success",
        cancel_url=request.host_url + "order/cancel",
        metadata={"discord_id": session["discord_id"]}
    )

    return redirect(session.url)


@app.route("/order/success")
def success():
    return render_template("success.html")


@app.route("/order/cancel")
def cancel():
    return render_template("cancel.html")


@app.route("/event", methods=["POST"])
def event():
    config = db.table("config").all()
    if stripe.api_key is None or config is None:
        abort(500)

    payload = request.data
    signature = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, env["STRIPE_WEBHOOK_SECRET"]
        )
    except Exception:
        abort(400)

    if event["type"] == "checkout.session.completed":
        stripe.checkout.Session.retrieve(
            event["data"]["object"].id, expand=["line_items"]
        )

    return {"success": True}


if __name__ == "__main__":
    app.run()
