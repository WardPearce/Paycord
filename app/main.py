import stripe
import requests
import os
import secrets
import calendar

from flask import (
    Flask, render_template, abort, redirect, request, url_for, session
)
from functools import wraps
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth
from uuid import uuid4
from currency_symbols import CurrencySymbols
from datetime import datetime


DISCORD_API_URL = os.getenv("DISCORD_API_URL", "https://discord.com/api")
CURRENCY = os.getenv("CURRENCY", "USD")
CURRENCY_SYMBOL = CurrencySymbols.get_symbol(CURRENCY)
PAGE_NAME = os.getenv("PAGE_NAME", "Paycord")
LOGO_URL = os.getenv("LOGO_URL", "https://i.imgur.com/d5SBQ6v.png")
ROOT_DISCORD_IDS = os.environ["ROOT_DISCORD_IDS"].split(",")
SUBSCRIPTION_RECURRENCE = os.getenv("SUBSCRIPTION_RECURRENCE", "month")
SUBSCRIPTION_INTERVAL = int(os.getenv("SUBSCRIPTION_INTERVAL", 1))
MONTHLY_GOAL = float(os.getenv("MONTHLY_GOAL", 0.0))
MESSAGE_ON_COMPLETE = os.getenv(
    "MESSAGE_ON_COMPLETE",
    "Thank you {username} for subscribing to {name} for {currency_symbol}{price}"  # noqa: E501
)
DISCORD_HEADER = {
    "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"
}


app = Flask(__name__)
oauth = OAuth(app)
mongo = MongoClient(
    os.getenv("MONGO_IP", "localhost"),
    os.getenv("MONGO_PORT", 27017)
)[os.getenv("MONGO_DB", "paycord")]

app.secret_key = secrets.token_urlsafe(54)
stripe.api_key = os.environ["STRIPE_API_KEY"]

discord = oauth.register(
    name="discord",
    client_id=os.environ["DISCORD_CLIENT_ID"],
    client_secret=os.environ["DISCORD_CLIENT_SECRET"],
    access_token_url=f"{DISCORD_API_URL}/oauth2/token",
    authorize_url=f"{DISCORD_API_URL}/oauth2/authorize",
    api_base_url=DISCORD_API_URL,
    client_kwargs={"scope": "identify"}
)


def root_required(func_):
    @wraps(func_)
    def decorated_function(*args, **kwargs):
        if ("discord" not in session or
                session["discord"]["id"] not in ROOT_DISCORD_IDS):
            abort(403)

        return func_(*args, **kwargs)

    return decorated_function


@app.route("/admin/add", methods=["POST"])
@root_required
def admin_add():
    payload = request.form
    mongo.product.insert_one({
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
    mongo.product.delete_one({"product_id": product_id})
    return redirect("/")


@app.route("/")
def index():
    if "discord" in session:
        user = mongo.user.find_one({
            "discord_id": session["discord"]["id"]
        })
        if user:
            product_ids = user["product_ids"]
        else:
            product_ids = []

        is_root = session["discord"]["id"] in ROOT_DISCORD_IDS
    else:
        is_root = False
        product_ids = []

    currently_at = 0.0
    if MONTHLY_GOAL:
        now = datetime.now()
        subscriptions = mongo.subscription.aggregate([{
            "$match": {"$and": [
                {"created": {"$gte": now.replace(day=1)}},
                {"created": {
                    "$lte": now.replace(
                        day=calendar.monthrange(now.year, now.month)[1]
                    )
                }}
            ]},
        }, {
            "$group": {"_id": None, "total": {"$sum": "$price"}}
        }])

        for sub in subscriptions:
            currently_at = sub["total"]

    return render_template(
        "index.html",
        session=session,
        product_ids=product_ids,
        is_root=is_root,
        products=mongo.product.find(),
        currency=CURRENCY_SYMBOL,
        page_name=PAGE_NAME,
        logo_url=LOGO_URL,
        monthly_goal=MONTHLY_GOAL,
        currently_at=currently_at,
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
    if "error" not in request.args:
        token = discord.authorize_access_token()
        user = discord.get("/api/users/@me", token=token).json()
        session["discord"] = user
    return redirect("/")


@app.route("/portal")
def portal():
    if "discord" not in session:
        abort(403)

    user = mongo.user.find_one({
        "discord_id": session["discord"]["id"]
    })
    if user:
        billing_session = stripe.billing_portal.Session.create(
            customer=user["customer_id"],
            return_url=url_for("index", _external=True)
        )
        return redirect(billing_session.url)
    else:
        abort(400)


@app.route("/subscription/<product_id>", methods=["POST"])
def order(product_id: str):
    if "discord" not in session:
        abort(403)

    product = mongo.product.find_one({
        "product_id": product_id
    })
    if not product:
        abort(404)

    metadata = {
        "discord_id": session["discord"]["id"],
        "role_id": product["role_id"],
        "product_id": product_id
    }

    user = mongo.user.find_one({
        "discord_id": session["discord"]["id"]
    })
    if not user:
        customer = stripe.Customer.create(metadata=metadata)
        mongo.user.insert_one({
            "discord_id": session["discord"]["id"],
            "customer_id": customer.id,
            "product_ids": []
        })
        customer_id = customer.id
    else:
        customer_id = user["customer_id"]

    checkout_session = stripe.checkout.Session.create(
        line_items=[{
            "price_data": {
                "product_data": {"name": product["name"]},
                "unit_amount": int(int(product["price"]) / 0.01),
                "currency": CURRENCY,
                "recurring": {
                    "interval": SUBSCRIPTION_RECURRENCE,
                    "interval_count": SUBSCRIPTION_INTERVAL
                }
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

    if "STRIPE_SIGNATURE" not in request.headers:
        abort(400)

    signature = request.headers["STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except Exception:
        abort(400)

    def format_role_url(discord_id: str, role_id: str) -> str:
        return (f"{DISCORD_API_URL}/"
                f"guilds/{os.environ['DISCORD_GUILD_ID']}"
                f"/members/{discord_id}/roles/{role_id}")

    if event["type"] == "checkout.session.completed":
        subscription = stripe.checkout.Session.retrieve(
            event["data"]["object"].id
        )

        metadata = subscription.metadata

        mongo.user.update_one({
            "discord_id": metadata["discord_id"]
        }, {"$push": {"product_ids": metadata["product_id"]}})

        mongo.subscription.insert_one({
            "discord_id": metadata["discord_id"],
            "subscription_id": event["data"]["object"].subscription,
            "role_id": metadata["role_id"],
            "product_id": metadata["product_id"],
            "price": subscription["amount_total"] * 0.01,
            "created": datetime.now()
        })

        requests.put(
            format_role_url(metadata["discord_id"], metadata["role_id"]),
            headers=DISCORD_HEADER
        )

        if MESSAGE_ON_COMPLETE:
            channel = requests.post(
                f"{DISCORD_API_URL}/users/@me/channels",
                json={"recipient_id": metadata["discord_id"]},
                headers=DISCORD_HEADER
            )
            if channel.status_code == 200:
                product = mongo.product.find_one({
                    "product_id": metadata["product_id"]
                })
                if not product:
                    product = {}

                channel_data = channel.json()
                requests.post(
                    (f"{DISCORD_API_URL}/channels/{channel_data['id']}"
                     "/messages"),
                    json={
                        "content": MESSAGE_ON_COMPLETE.format_map(
                            {
                                **channel_data["recipients"][0],
                                **product,
                                "currency": CURRENCY,
                                "currency_symbol": CURRENCY_SYMBOL
                            }
                        )
                    },
                    headers=DISCORD_HEADER
                )

    elif event["type"] == "customer.subscription.deleted":
        subscription = mongo.subscription.find_one({
            "subscription_id": event["data"]["object"].id
        })
        if subscription:
            sub = mongo.subscription.find_one({
                "discord_id": subscription["discord_id"]
            })
            if sub:
                requests.delete(
                    format_role_url(
                        subscription["discord_id"],
                        sub["role_id"]
                    ),
                    headers=DISCORD_HEADER
                )

            mongo.subscription.delete_one({
                "subscription_id": event["data"]["object"].id
            })
            mongo.user.update_one(
                {"discord_id": subscription["discord_id"]},
                {"$pull": {
                    "product_ids": {"$in": [subscription["product_id"]]}
                }}
            )

    return {"success": True}


if __name__ == "__main__":
    app.run(debug=True)
