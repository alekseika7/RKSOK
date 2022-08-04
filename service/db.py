import asyncio
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.results import DeleteResult, UpdateResult

from config import MONGO_DB_NAME, MONGO_CONNECTION_URI, MONGO_CONNECTION_MS_TIMEOUT
from exceptions import DBConnectionError
from models.models import TaskStatus, TaskResult


class RKSOKDatabaseClient:
    """"""
    async def get(self, name: str) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')

    async def update(self, name: str, value: str) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')

    async def delete(self, name: str) -> TaskResult:
        """"""
        raise NotImplementedError('Abstract method!')


class RKSOKMongoClient(RKSOKDatabaseClient):
    """"""
    def __init__(self) -> None:
        self.client = None
        self.collection = None

    async def connect_to_db(
        self,
        connection_uri: Optional[str] = MONGO_CONNECTION_URI,
        db_name: Optional[str] = MONGO_DB_NAME,
        user_id: Optional[str] = 'user1',
        ms_timeout: Optional[int] = MONGO_CONNECTION_MS_TIMEOUT
    ) -> None:
        """"""
        self.client = AsyncIOMotorClient(connection_uri, serverSelectionTimeoutMS=ms_timeout)
        try:
            await self.client.server_info()
        except ServerSelectionTimeoutError:
            raise DBConnectionError('Error connecting to the mongodb!')
        else:
            self.collection = self.client[db_name][user_id]

    async def get(self, name: str) -> TaskResult:
        """"""
        value: dict[str, str] | None = await self.collection.find_one({'_id': name})
        status = TaskStatus.OK if value else TaskStatus.NOT_OK
        result = value['phone'] if value else None
        return TaskResult(status=status, result=result)

    async def update(self, name: str, value: str) -> TaskResult:
        """"""
        update_result: UpdateResult = await self.collection.update_one(
            {'_id': name}, {'$set': {'phone': value}}, upsert=True)
        # status = TaskStatus.OK if update_result.raw_result['ok'] == 1 else TaskStatus.NOT_OK
        return TaskResult(status=TaskStatus.OK, result=None)

    async def delete(self, name: str) -> TaskResult:
        """"""
        delete_result: DeleteResult = await self.collection.delete_one({'_id': name})
        status = TaskStatus.OK if delete_result.deleted_count == 1 else TaskStatus.NOT_OK
        return TaskResult(status=status, result=None)


if __name__ == '__main__':
    from pprint import pprint

    async def main():
        db_client = RKSOKMongoClient()
        await db_client.connect_to_db()
        res1 = await db_client.update(name='Alex', value='7777777777')
        res2 = await db_client.get(name='Alex')
        res3 = await db_client.delete(name='Alex')
        pprint((res1, res2, res3))

    asyncio.run(main())
