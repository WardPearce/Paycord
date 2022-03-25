import secrets

from flask import Flask

from .routes.api import api_blueprint
from .routes.admin import admin_blueprint
from .routes.discord import oauth, discord_blueprint
from .routes.events import events_blueprint
from .routes.home import home_blueprint


app = Flask(__name__)
oauth.init_app(app)

blueprints = [api_blueprint, admin_blueprint, discord_blueprint,
              events_blueprint, home_blueprint]
for blueprint in blueprints:
    app.register_blueprint(blueprint)

app.secret_key = secrets.token_urlsafe(24)


__all__ = [
    "app"
]
