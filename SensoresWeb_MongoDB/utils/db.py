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

print("MongoDB Atlas conectado correctamente")