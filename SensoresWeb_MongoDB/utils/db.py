import logging

from pymongo import MongoClient

from config import Config

client = MongoClient(
    Config.MONGO_URI
)

db = client[
    Config.DATABASE_NAME
]

usuarios_collection = db["usuarios"]

lecturas_collection = db["lecturas"]

configuraciones_collection = db["configuraciones"]

alertas_collection = db["alertas"]

logging.getLogger(__name__).info("MongoDB Atlas conectado correctamente")