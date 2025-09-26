import asyncio
from dbConnection.dbConfig import engine, Base
from model import userModel  
from model import associationModel 


async def init_db():
    try:
        async with engine.begin() as conn:

            await conn.run_sync(Base.metadata.create_all)
        print(" Connected to Supabase PostgreSQL & synced all models")
    except Exception as e:
        print(" Error connecting to the database:", e)
        raise e
