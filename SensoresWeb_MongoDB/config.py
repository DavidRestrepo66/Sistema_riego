import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "sensores_mongo")
    ARDUINO_PORT = os.getenv("ARDUINO_PORT", "COM3")
    try:
        BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
    except ValueError:
        BAUD_RATE = 9600
    SQL_SERVER = os.getenv("SQL_SERVER", r"localhost\SQLEXPRESS")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "sensores")
