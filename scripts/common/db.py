import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from common.config import settings
from common.logger import logger


async def init_db():
    logger.info("Conectando a MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_URL, tlsCAFile=certifi.where())
    from models.user import User

    await init_beanie(
        database=client[settings.MONGO_DATABASE],
        document_models=[User],
    )
    logger.info("MongoDB conectado exitosamente.")
