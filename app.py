import stripe
import requests

from flask import (
    Flask, render_template, abort, redirect, request, url_for, session
)
from functools import wraps
from tinydb import TinyDB, where
from authlib.integrations.flask_client import OAuth
from dotenv import dotenv_values
from uuid import uuid4


env = dotenv_values(".env")

app = Flask(__name__)
app.secret_key = env["SESSION_SECRET"]

oauth = OAuth(app)
stripe.api_key = env["STRIPE_API_KEY"]
db = TinyDB("paycord_db.json")
root_discord_ids = env["ROOT_DISCORD_IDS"].split(",")  # type: ignore

discord = oauth.register(
    name="discord",
    client_id=env["DISCORD_CLIENT_ID"],
    client_secret=env["DISCORD_CLIENT_SECRET"],
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    api_base_url="https://discord.com/api",
    client_kwargs={"scope": "identify"}
)


def root_required(func_):
    @wraps(func_)
    def decorated_function(*args, **kwargs):
        if ("discord" not in session or
                session["discord"]["id"] not in root_discord_ids):
            abort(403)

        return func_(*args, **kwargs)

    return decorated_function


@app.route("/admin/add", methods=["POST"])
@root_required
def admin_add():
    payload = request.form
    db.table("products").insert({
        "product_id": str(uuid4()),
        "name": payload["name"],
        "price": payload["price"],
        "description": payload.get("description", ""),
        "role_id": payload["role_id"]
    })
    return redirect("/")


@app.route("/admin/delete/<product_id>", methods=["POST"])
@root_required
def admin_delete(product_id: str):
    db.table("products").remove(where("product_id") == product_id)
    return redirect("/")


@app.route("/")
def index():
    if "discord" in session:
        user = db.table("user").search(
            where("discord_id") == session["discord"]["id"]
        )
        active_products = [
            prod["product_id"] for prod in
            db.table("subscriptions").search(
                where("discord_id") == session["discord"]["id"]
            )
        ]
        is_root = session["discord"]["id"] in root_discord_ids
    else:
        user = None
        is_root = False
        active_products = []

    return render_template(
        "index.html",
        session=session,
        user=user,
        active_products=active_products,
        is_root=is_root,
        products=db.table("products").all(),
        currency=env["CURRENCY"],
        order_status=request.args.get("order", None)
    )


@app.route("/discord/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return discord.authorize_redirect(redirect_uri=redirect_uri)


@app.route("/discord/logout")
def logout():
    session.pop("discord", None)
    return redirect("/")


@app.route("/discord/authorize")
def authorize():
    token = discord.authorize_access_token()
    user = discord.get("/api/users/@me", token=token).json()
    session["discord"] = user
    return redirect("/")


@app.route("/portal")
def portal():
    if "discord" not in session:
        abort(403)

    user = db.table("user").search(
        where("discord_id") == session["discord"]["id"]
    )
    if user:
        billing_session = stripe.billing_portal.Session.create(
            customer=user[0]["customer_id"],
            return_url=url_for("index", _external=True)
        )
        return redirect(billing_session.url)
    else:
        abort(400)


@app.route("/subscription/<product_id>", methods=["POST"])
def order(product_id: str):
    if "discord" not in session:
        abort(403)

    product = db.table("products").search(where("product_id") == product_id)
    if not product:
        abort(404)

    metadata = {
        "discord_id": session["discord"]["id"],
        "role_id": product[0]["role_id"],
        "product_id": product_id
    }

    user = db.table("user").search(
        where("discord_id") == session["discord"]["id"]
    )
    if not user:
        customer = stripe.Customer.create(metadata=metadata)
        db.table("user").insert({
            "discord_id": session["discord"]["id"],
            "customer_id": customer.id
        })
        customer_id = customer.id
    else:
        customer_id = user[0]["customer_id"]

    checkout_session = stripe.checkout.Session.create(
        line_items=[{
            "price_data": {
                "product_data": {"name": product[0]["name"]},
                "unit_amount": int(int(product[0]["price"]) / 0.01),
                "currency": env["CURRENCY"],
                "recurring": {"interval": "month", "interval_count": 1}
            },
            "quantity": 1,
            "adjustable_quantity": {"enabled": False}
        }],
        customer=customer_id,
        payment_method_types=["card"],
        mode="subscription",
        success_url=request.host_url + "order/success",
        cancel_url=request.host_url + "order/cancel",
        metadata=metadata
    )

    return redirect(checkout_session.url)


@app.route("/order/success")
def success():
    return redirect("/?order=success")


@app.route("/order/cancel")
def cancel():
    return redirect("/?order=cancel")


@app.route("/event", methods=["POST"])
def event():
    payload = request.data
    signature = request.headers["STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, env["STRIPE_WEBHOOK_SECRET"]
        )
    except Exception:
        abort(400)

    def format_url(discord_id: str, role_id: str) -> str:
        return (f"{env['DISCORD_API_URL']}/guilds/{env['DISCORD_GUILD_ID']}"
                f"/members/{discord_id}/roles/{role_id}")

    if event["type"] == "checkout.session.completed":
        metadata = (stripe.checkout.Session.retrieve(
            event["data"]["object"].id
        )).metadata

        requests.put(
            format_url(metadata["discord_id"], metadata["role_id"]),
            headers={"Authorization": f"Bot {env['DISCORD_BOT_TOKEN']}"}
        )

        db.table("subscriptions").insert({
            **metadata,
            "subscription_id": event["data"]["object"].subscription,
        })
    elif event["type"] == "customer.subscription.deleted":
        subscription = db.table("subscriptions").search(
            where("subscription_id") == event["data"]["object"].id
        )
        if subscription:
            requests.delete(
                format_url(
                    subscription[0]["discord_id"],
                    subscription[0]["role_id"]
                ),
                headers={"Authorization": f"Bot {env['DISCORD_BOT_TOKEN']}"}
            )
            db.table("subscriptions").remove(
                where("subscription_id") == event["data"]["object"].id
            )

    return {"success": True}


if __name__ == "__main__":
    app.run()
