from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.results import DeleteResult

from config import MONGO_DB_NAME, MONGO_CONNECTION_URI, MONGO_CONNECTION_MS_TIMEOUT
from exceptions import DBConnectionError
from service.logger import logger
from models.models import TaskStatus, TaskResult


class RKSOKDatabaseClient:
    """Database interface."""

    async def get(self, name: str) -> TaskResult:
        """Abstract method for getting data from db."""
        raise NotImplementedError()

    async def update(self, name: str, value: str) -> TaskResult:
        """Abstract method for creating (updating) data in db."""
        raise NotImplementedError()

    async def delete(self, name: str) -> TaskResult:
        """Abstract method for deleting data from db."""
        raise NotImplementedError()


class RKSOKMongoClient(RKSOKDatabaseClient):
    """Mongo database for RKSOK protocol."""

    def __init__(self) -> None:
        self.client = None
        self.collection = None
        self._is_connected = False

    async def connect_to_db(
            self,
            connection_uri: Optional[str] = MONGO_CONNECTION_URI,
            db_name: Optional[str] = MONGO_DB_NAME,
            user_id: Optional[str] = 'user1',
            ms_timeout: Optional[int] = MONGO_CONNECTION_MS_TIMEOUT
    ) -> None:
        """Connects to mongodb unless already connected, creates new collection for new client."""
        if not self._is_connected:
            self.client = AsyncIOMotorClient(connection_uri, serverSelectionTimeoutMS=ms_timeout)
            try:
                await self.client.server_info()
            except ServerSelectionTimeoutError:
                raise DBConnectionError('Error connecting to the mongodb!')
            self._is_connected = True
            logger.debug(f'Successfully connected to MongoDb at {connection_uri}.')
        self.collection = self.client[db_name][user_id]

    async def get(self, name: str) -> TaskResult:
        """Gets phone by name from db."""
        value: dict[str, str] | None = await self.collection.find_one({'_id': name})
        status = TaskStatus.OK if value else TaskStatus.NOT_OK
        result = value['phone'] if value else None
        return TaskResult(status=status, result=result)

    async def update(self, name: str, value: str) -> TaskResult:
        """Creates or updates document with name and phone."""
        await self.collection.update_one({'_id': name}, {'$set': {'phone': value}}, upsert=True)
        return TaskResult(status=TaskStatus.OK, result=None)

    async def delete(self, name: str) -> TaskResult:
        """Deletes document by name from db."""
        delete_result: DeleteResult = await self.collection.delete_one({'_id': name})
        status = TaskStatus.OK if delete_result.deleted_count == 1 else TaskStatus.NOT_OK
        return TaskResult(status=status, result=None)
