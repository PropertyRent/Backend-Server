import os
from dotenv import load_dotenv
from tortoise.contrib.fastapi import register_tortoise

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def init_db(app):
    """
    Initialize Tortoise ORM for FastAPI app.
    """
    register_tortoise(
        app,
        db_url=DATABASE_URL,
        modules={"models": ["schemas.userModel"]},  
        generate_schemas=True, 
        add_exception_handlers=True,
    )
    print("Database connected and Tortoise initialized")
