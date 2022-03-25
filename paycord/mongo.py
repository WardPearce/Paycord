import os
from pymongo import MongoClient

MONGO = MongoClient(
    os.environ["MONGO_IP"],
    int(os.environ["MONGO_PORT"])
)

try:
    MONGO.server_info()
except Exception as error:
    raise error

MONGO = MONGO[os.environ["MONGO_DB"]]
