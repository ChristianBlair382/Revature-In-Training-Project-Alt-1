from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.orm_models.equipment_mongo import Equipment
from app.orm_models.farm_mongo import Farm
from app.orm_models.field_job_mongo import Field_Job
from app.orm_models.hand_mongo import Hand
from app.orm_models.permission_mongo import RolePermission
from app.orm_models.refresh_token_mongo import Refresh_Token
from app.orm_models.service_report_mongo import Service_Report
from app.orm_models.supervisor_mongo import Supervisor
from app.orm_models.user_mongo import User

class MongoSettings(BaseSettings):
    mongodb_url: str = "mongodb+srv://christianblair38_db_user:EflhFRSBmMJUaG5u@agricore-dev-mongodb.zf89m5o.mongodb.net/"
    mongodb_database: str = "agricore_dev_2478"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

mongo_settings = MongoSettings()

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None

DOCUMENT_MODELS = [
    User,
    RolePermission,
    Farm,
    Equipment,
    Field_Job,
    Hand,
    Service_Report,
    Supervisor,
    Refresh_Token,
]

def rebuild_mongo_models() -> None:
    types_namespace = {
        model.__name__: model
        for model in DOCUMENT_MODELS
    }
    for model in DOCUMENT_MODELS:
        model.model_rebuild(_types_namespace=types_namespace)

async def connect_to_mongo() -> None:
    global client, database

    rebuild_mongo_models()
    client = AsyncIOMotorClient(
        mongo_settings.mongodb_url,
        uuidRepresentation="standard",
        tz_aware=True,
    )
    database = client[mongo_settings.mongodb_database]
    await init_beanie(
        database=database,
        document_models=DOCUMENT_MODELS,
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
