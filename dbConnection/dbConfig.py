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
                        "models": ["model.userModel", "model.propertyModel", "model.propertyMediaModel", "model.teamModel", "model.contactModel", "model.screeningQuestionModel", "model.scheduleMeetingModel", "model.noticeModel", "model.propertyRecommendationModel", "model.chatbotModel", "model.applicationModel", "model.maintenanceRequestModel"],
            "default_connection": "default",
        }
    }
}
print(" DATABASE_URL =", DATABASE_URL)  

def init_db(app):
    """
    Initialize Tortoise ORM for FastAPI app with PgBouncer compatibility.
    """
    try:
        print(" Initializing database with PgBouncer compatibility...")
        
        # Enhanced configuration for PgBouncer
        enhanced_config = {
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
                        "statement_cache_size": 0,  # Critical for PgBouncer
                        "ssl": "disable",
                        # Additional asyncpg connection parameters for PgBouncer
                        "server_settings": {
                            "application_name": "fastapi_property_app",
                            "jit": "off"  # Disable JIT for better PgBouncer compatibility
                        }
                    }
                }
            },
            "apps": {
                "models": {
                    "models": [
                        "model.userModel", 
                        "model.propertyModel", 
                        "model.propertyMediaModel", 
                        "model.teamModel", 
                        "model.contactModel", 
                        "model.screeningQuestionModel", 
                        "model.scheduleMeetingModel", 
                        "model.noticeModel", 
                        "model.propertyRecommendationModel", 
                        "model.chatbotModel", 
                        "model.applicationModel", 
                        "model.maintenanceRequestModel"
                    ],
                    "default_connection": "default",
                }
            }
        }
        
        register_tortoise(
            app,
            config=enhanced_config,
            generate_schemas=True,
            add_exception_handlers=True,
        )
        print(" Database connected with PgBouncer compatibility")
        print(" Tables should be automatically created if they don't exist")
    except Exception as e:
        print(f"❌ Database init failed: {e}")
        # Fallback: try with direct URL connection
        try:
            print(" Trying fallback connection method...")
            register_tortoise(
                app,
                db_url=DATABASE_URL,
                modules={"models": ["model.userModel", "model.propertyModel", "model.propertyMediaModel", "model.teamModel", "model.contactModel", "model.screeningQuestionModel", "model.scheduleMeetingModel", "model.noticeModel", "model.propertyRecommendationModel", "model.chatbotModel", "model.applicationModel", "model.maintenanceRequestModel"]},
                generate_schemas=True,
                add_exception_handlers=True,
            )
            print(" Fallback database connection successful")
        except Exception as fallback_error:
            print(f" Fallback database init also failed: {fallback_error}")
