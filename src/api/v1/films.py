import core.config as conf

from http import HTTPStatus
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate
from typing import Optional
from api.v1 import _details, _list
from services.service import IdRequestService, ListService
from services.film import get_film_service, get_film_list_service
from models.model import Model
# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах

INDEX = 'movies'


# Модель ответа API
class Film(Model):
    uuid: str
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    # TODO: genre should have type list[dict]
    genre: list[str] | None = None
    actors: list[dict] | None = None
    writers: list[dict] | None = None
    # TODO: directors should have type list[dict]
    directors: list[str] | None = None


class FilmList(Model):
    uuid: str
    title: str
    imdb_rating: float | None = None


@router.get('/search',
            response_model=Page[FilmList],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма",
            tags=['Полнотекстовый поиск']
            )
async def film_search(film_service: ListService = Depends(get_film_list_service),
                      query: str = Query(None,
                                         description=conf.SEARCH_DESC),
                      sort: str = Query(None,
                                        description=conf.SORT_DESC)
                      ) -> Page[FilmList]:
    if query:
        search = {
            "bool": {
                "must":
                    {"match": {"title": query}}
            }
        }
        key = f'{INDEX}:title:{query}:sort:{sort}'
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Empty `query` attribute')

    films = await _list(film_service,
                        index=INDEX,
                        search=search,
                        sort=sort,
                        key=key)

    res = [FilmList(uuid=film.id,
                    title=film.title,
                    imdb_rating=film.imdb_rating) for film in films]
    return paginate(res)


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/films/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса
# (film_id: str)
# И указываем тип возвращаемого объекта — Film
# Внедряем IdRequestService с помощью Depends(get_film_service)
@router.get('/{film_id}',
            response_model=Film,
            summary="Детали фильма",
            description="Доступная информация по одному фильму",
            response_description="id, название, рейтинг, описание, жанр, "
                                 "список актеров, режиссеров и сценаристов",
            )
async def film_details(film_service: IdRequestService = Depends(get_film_service),
                       film_id: str = None) -> Film:
    film = await _details(film_service, film_id, INDEX)
    # Перекладываем данные из models.Film в Film.
    # Обратите внимание, что у модели бизнес-логики есть поле description,
    # которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования
    # ответов API вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    return Film(uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
                description=film.description,
                genre=film.genre,
                actors=film.actors,
                writers=film.writers,
                directors=film.directors)


@router.get('/',
            response_model=Page[FilmList],
            summary="Список фильмов",
            description="Список фильмов с информацией о id, названии, рейтинге",
            response_description="id, название, рейтинг",
            )
async def film_list(film_service: ListService = Depends(get_film_list_service),
                    sort: str = Query(None,
                                      description=conf.SORT_DESC),
                    genre: str = Query(None,
                                       description=conf.GENRE_DESC),
                    page: int = Query(None,
                                      description=conf.PAGE_DESC),
                    size: int = Query(None,
                                      description=conf.SIZE_DESC),
                    ) -> Page[FilmList]:
    if genre:
        # TODO: stub for testing ?genre=Comedy
        search = {
            "bool": {
                "must":
                    {"match": {"genre": genre}}
            }
        }
        # TODO: change search to genre.id after movies index update
        # search = {
        #     "nested": {
        #         "path": "genre",
        #         "query": {
        #             "bool": {
        #                 "must":
        #                     {"match": {"genre.id": genre}}
        #             }
        #         }
        #     }
        # }
        key = f'{INDEX}:genre:{genre}:sort:{sort}'
    else:
        search = None
        key = None

    films = await _list(film_service,
                        index=INDEX,
                        sort=sort,
                        search=search,
                        key=key)

    res = [FilmList(uuid=film.id,
                    title=film.title,
                    imdb_rating=film.imdb_rating) for film in films]
    return paginate(res)
