from flask import Blueprint
from flask.wrappers import Response
from bson.json_util import dumps

from ..mongo import MONGO


api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/api/products", methods=["GET"])
def api_products():
    return Response(
        dumps(list(MONGO.product.find())),
        status=200,
        mimetype="application/json"
    )


@api_blueprint.route("/api/active/<discord_id>", methods=["GET"])
def api_active_discord(discord_id: str):
    return {"active": MONGO.subscription.count_documents({
        "discord_id": discord_id
    }) > 0}
