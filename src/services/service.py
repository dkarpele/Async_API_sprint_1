from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class ListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, model):
        self.redis = redis
        self.elastic = elastic
        self.model = model

    async def get_by_id(self, _id: str, index: str) -> Optional:
        entity = await self._get_from_cache(_id)
        if not entity:
            entity = await self._get_from_elastic(_id, index)
            if not entity:
                return None
            await self._put_to_cache(entity)

        return entity

    async def _get_from_elastic(self, _id: str, index: str) -> Optional:
        try:
            doc = await self.elastic.get(index, _id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    async def _get_from_cache(self, _id: str) -> Optional:
        data = await self.redis.get(_id)
        if not data:
            return None

        res = self.model.parse_raw(data)
        return res

    async def _put_to_cache(self, entity):
        await self.redis.set(entity.id, entity.json(), CACHE_EXPIRE_IN_SECONDS)
