from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": DB_NAME,
                "host": DB_HOST,
                "password": DB_PASS,
                "port": int(DB_PORT),
                "user": DB_USER,
                "minsize": 1,
                "maxsize": 10,
                "statement_cache_size": 0, 
                "ssl": "disable"
            }
        }
    },
    "apps": {
        "models": {
            "models": ["model.userModel", "model.propertyModel", "model.propertyMediaModel", "model.teamModel", "model.contactModel", "model.screeningQuestionModel", "model.scheduleMeetingModel", "model.noticeModel", "model.propertyRecommendationModel", "model.chatbotModel", "model.applicationModel", "model.tidyCalModel"],
            "default_connection": "default",
        }
    }
}
print(" DATABASE_URL =", DATABASE_URL)  

def init_db(app):
    """
    Initialize Tortoise ORM for FastAPI app.
    """
    try:
        print(" Initializing database with generate_schemas=True...")
        register_tortoise(
            app,
            config=TORTOISE_ORM,
            generate_schemas=True,
            add_exception_handlers=True,
        )
        print(" Database connected and Tortoise initialized")
        print(" Tables should be automatically created if they don't exist")
    except Exception as e:
        print(" Database init failed:", e)
