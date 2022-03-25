from flask import (
    abort, session
)
from functools import wraps

from .env import ROOT_DISCORD_IDS


def root_required(func_):
    @wraps(func_)
    def decorated_function(*args, **kwargs):
        if ("discord" not in session or
                session["discord"]["id"] not in ROOT_DISCORD_IDS):
            abort(403)
        else:
            return func_(*args, **kwargs)

    return decorated_function
