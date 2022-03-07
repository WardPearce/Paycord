from flask import (
    render_template, abort, redirect, request, url_for, session,
    Blueprint
)

from ..env import (
    CURRENCY, CURRENCY_SYMBOL,
    PAGE_NAME, LOGO_URL, ROOT_DISCORD_IDS, SUBSCRIPTION_RECURRENCE,
    SUBSCRIPTION_INTERVAL, MONTHLY_GOAL, MONTHLY_GOAL_PARAGRAPH
)

from ..pay import stripe
from ..mongo import MONGO

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def index():
    if "discord" in session:
        user = MONGO.user.find_one({
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
        subscriptions = MONGO.subscription.aggregate([{
            "$group": {"_id": None, "total": {"$sum": "$price"}}
        }])

        for sub in subscriptions:
            currently_at = sub["total"]

    return render_template(
        "index.html",
        session=session,
        product_ids=product_ids,
        is_root=is_root,
        products=MONGO.product.find(),
        currency=CURRENCY_SYMBOL,
        page_name=PAGE_NAME,
        logo_url=LOGO_URL,
        monthly_goal_paragraph=MONTHLY_GOAL_PARAGRAPH,
        monthly_goal=MONTHLY_GOAL,
        currently_at=currently_at,
        order_status=request.args.get("order", None)
    )


@home_blueprint.route("/portal")
def portal():
    if "discord" not in session:
        abort(403)

    user = MONGO.user.find_one({
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


@home_blueprint.route("/subscription/<product_id>", methods=["POST"])
def order(product_id: str):
    if "discord" not in session:
        abort(403)

    product = MONGO.product.find_one({
        "product_id": product_id
    })
    if not product:
        abort(404)

    metadata = {
        "discord_id": session["discord"]["id"],
        "role_id": product["role_id"],
        "product_id": product_id
    }

    user = MONGO.user.find_one({
        "discord_id": session["discord"]["id"]
    })
    if not user:
        customer = stripe.Customer.create(metadata=metadata)
        MONGO.user.insert_one({
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


@home_blueprint.route("/order/success")
def success():
    return redirect("/?order=success")


@home_blueprint.route("/order/cancel")
def cancel():
    return redirect("/?order=cancel")
