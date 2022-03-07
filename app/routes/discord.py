import os
from flask import request, session, url_for, redirect, Blueprint
from authlib.integrations.flask_client import OAuth

from ..env import DISCORD_API_URL

oauth = OAuth()

discord = oauth.register(
    name="discord",
    client_id=os.environ["DISCORD_CLIENT_ID"],
    client_secret=os.environ["DISCORD_CLIENT_SECRET"],
    access_token_url=f"{DISCORD_API_URL}/oauth2/token",
    authorize_url=f"{DISCORD_API_URL}/oauth2/authorize",
    api_base_url=DISCORD_API_URL,
    client_kwargs={"scope": "identify"}
)
discord_blueprint = Blueprint("discord", __name__)


@discord_blueprint.route("/discord/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return discord.authorize_redirect(redirect_uri=redirect_uri)


@discord_blueprint.route("/discord/logout")
def logout():
    session.pop("discord", None)
    return redirect("/")


@discord_blueprint.route("/discord/authorize")
def authorize():
    if "error" not in request.args:
        token = discord.authorize_access_token()
        user = discord.get("/api/users/@me", token=token).json()
        session["discord"] = user
    return redirect("/")
