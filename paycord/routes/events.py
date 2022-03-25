import requests
import os

from flask import (
    abort, request, Blueprint
)
from datetime import datetime
from importlib import import_module

from ..env import (
    DISCORD_API_URL,
    DISCORD_HEADER,
    THIRD_PARTY_MODULES
)
from ..pay import stripe
from ..mongo import MONGO

modules = []
for module in THIRD_PARTY_MODULES:
    modules.append(import_module(module))


events_blueprint = Blueprint("events", __name__)


@events_blueprint.route("/event", methods=["POST"])
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

        MONGO.user.update_one({
            "discord_id": metadata["discord_id"]
        }, {"$push": {"product_ids": metadata["product_id"]}})

        price_in_dollars = subscription["amount_total"] * 0.01

        MONGO.subscription.insert_one({
            "discord_id": metadata["discord_id"],
            "subscription_id": event["data"]["object"].subscription,
            "role_id": metadata["role_id"],
            "product_id": metadata["product_id"],
            "price": price_in_dollars,
            "created": datetime.now()
        })

        requests.put(
            format_role_url(metadata["discord_id"], metadata["role_id"]),
            headers=DISCORD_HEADER
        )

        product = MONGO.product.find_one({
            "product_id": metadata["product_id"]
        })
        if not product:
            product = {}

        for module in modules:
            if hasattr(module, "run_on_complete"):
                getattr(module, "run_on_complete")(
                    product, subscription
                )

    elif event["type"] == "customer.subscription.deleted":
        subscription = MONGO.subscription.find_one({
            "subscription_id": event["data"]["object"].id
        })
        if subscription:
            MONGO.subscription.delete_one({
                "subscription_id": event["data"]["object"].id
            })
            MONGO.user.update_one(
                {"discord_id": subscription["discord_id"]},
                {"$pull": {
                    "product_ids": {"$in": [subscription["product_id"]]}
                }}
            )

            requests.delete(
                format_role_url(
                    subscription["discord_id"],
                    subscription["role_id"]
                ),
                headers=DISCORD_HEADER
            )

            product = MONGO.product.find_one({
                "product_id": subscription["product_id"]
            })
            if not product:
                product = {}

            for module in modules:
                if hasattr(module, "run_on_delete"):
                    getattr(module, "run_on_delete")(
                        product, subscription
                    )

    return {"success": True}
