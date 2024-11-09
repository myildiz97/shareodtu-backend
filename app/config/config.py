import os, certifi
from motor.motor_asyncio import AsyncIOMotorClient
from config.singleton import singleton
from pydantic_settings import BaseSettings
from beanie import init_beanie
from models import __models__

# Choose the environment file to load settings from
env_file = os.environ.get("ENV_FILE", ".env")


@singleton
class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


async def connect_to_database():
    """Initiate database connection on startup"""
    client = AsyncIOMotorClient(Settings().MONGO_URI, tlsCAFile=certifi.where())

    await init_beanie(
        database=client.get_database(Settings().MONGO_DB_NAME),
        document_models=__models__,
    )
    # Send a ping to confirm a successful connection
    try:
        client.admin.command("ping")
        print(f"Successfully connected to {Settings().MONGO_DB_NAME}")
    except Exception as e:
        print("Unable to connect to the database.")
        print(e)

    return client
