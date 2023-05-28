from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
ES_MAX_SIZE = 1000


class IdRequestService:
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
            doc = await self.elastic.get(index=index, id=_id)
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


class ListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, model):
        self.redis = redis
        self.elastic = elastic
        self.model = model

    async def get_list(self,
                       index: str,
                       sort: str = None,
                       search: dict = None,
                       query: str = None) -> Optional:
        if search:
            key = f'search:{query}'
        else:
            key = None
        entities = await self._get_from_cache(key)
        if not entities:
            entities = await self._get_from_elastic(index, sort, search)
            if not entities:
                return None
            await self._put_to_cache(key, entities)

        return entities

    async def _get_from_elastic(self,
                                index: str,
                                sort: str = None,
                                search: dict = None) -> Optional:
        if sort:
            try:
                order = 'desc' if sort.startswith('-') else 'asc'
                sort = sort[1:] if sort.startswith('-') else sort
                sorting = [{sort: {'order': order}}]
            except AttributeError:
                sorting = None
        else:
            sorting = None

        try:
            docs = await self.elastic.search(
                index=index,
                query=search,
                size=ES_MAX_SIZE,
                sort=sorting,
            )
        except NotFoundError:
            return None

        return [self.model(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_from_cache(self, name: str) -> Optional:
        data = await self.redis.hgetall(name)
        if not data:
            return None

        res = [self.model.parse_raw(i) for i in data.values()]
        return res

    async def _put_to_cache(self, key, entities: list):
        entities_dict: dict =\
            {f'e-{item}': entity.json() for item, entity in enumerate(entities)}
        return await self.redis.hset(name=key, mapping=entities_dict)
