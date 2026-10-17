from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.orm_models.permission_mongo import RolePermission
from backend.app.orm_models.user_mongo import User


class MongoSettings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "agricore_dev_2478"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


mongo_settings = MongoSettings()

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database

    client = AsyncIOMotorClient(mongo_settings.mongodb_url)
    database = client[mongo_settings.mongodb_database]
    await init_beanie(
        database=database,
        document_models=[User, RolePermission],
    )
    await database.command("ping")


async def close_mongo_connection() -> None:
    global client, database

    if client is not None:
        client.close()
        client = None
        database = None


async def ping_mongo() -> None:
    if database is None:
        raise RuntimeError("MongoDB has not been initialized.")

    await database.command("ping")
