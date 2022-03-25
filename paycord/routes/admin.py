from flask import Blueprint, request, redirect
from uuid import uuid4

from ..mongo import MONGO
from ..decorators import root_required


admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin/add", methods=["POST"])
@root_required
def admin_add():
    payload = request.form
    MONGO.product.insert_one({
        "product_id": str(uuid4()),
        "name": payload["name"],
        "price": payload["price"],
        "description": payload.get("description", ""),
        "role_id": payload["role_id"]
    })
    return redirect("/")


@admin_blueprint.route("/admin/delete/<product_id>", methods=["POST"])
@root_required
def admin_delete(product_id: str):
    MONGO.product.delete_one({"product_id": product_id})
    return redirect("/")
