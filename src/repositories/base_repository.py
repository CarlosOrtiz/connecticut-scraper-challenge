from aws_python_helper import Repository

from scripts.common.config import get_settings

settings = get_settings()


class BaseMongoRepository(Repository):
    @property
    def database_key(self) -> str:
        return settings.MONGO_DB_NAME
