import os
from pymongo import MongoClient

MONGO = MongoClient(
    os.getenv("MONGO_IP", "localhost"),
    int(os.getenv("MONGO_PORT", 27017))
)

try:
    MONGO.server_info()
except Exception as error:
    raise error

MONGO = MONGO[os.getenv("MONGO_DB", "paycord")]
