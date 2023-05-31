import core.config as conf

from http import HTTPStatus

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi_pagination import Page, paginate

from api.v1 import _details, _list, _get_cache_key, _films_for_person, _films_to_dict
from models.model import Model
from services.service import IdRequestService, ListService
from services.person import get_person_service, get_person_list_service
from services.film import get_film_list_service
from api.v1.films import FilmList
router = APIRouter()
INDEX = 'persons'


# Модель ответа API
class Person(Model):
    uuid: str
    full_name: str | None = None
    films: list[dict] | None = None


@router.get('/search',
            response_model=Page[Person],
            summary="Поиск персон",
            description="Полнотекстовый поиск по персонам",
            response_description="id, имя, id фильма и роли персоны в этом "
                                 "фильме",
            tags=['Полнотекстовый поиск']
            )
async def person_search(person_service: ListService = Depends(get_person_list_service),
                        film_service: ListService = Depends(get_film_list_service),
                        query: str = Query(None,
                                           description=conf.SEARCH_DESC),
                        page: int = Query(None,
                                          description=conf.PAGE_DESC),
                        size: int = Query(None,
                                          description=conf.SIZE_DESC),
                        ) -> Page[Person]:

    if query:
        search = {
            "bool": {
                "must":
                    {"match": {"full_name": query}}
            }
        }
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'Empty `query` attribute')

    key = await _get_cache_key({'query': query,
                                'page': page,
                                'size': size},
                               INDEX)

    persons = await _list(person_service,
                          index=INDEX,
                          search=search,
                          key=key)

    res = [Person(uuid=person.id,
                  full_name=person.full_name,
                  films=_films_to_dict(person.id, await _films_for_person(film_service, person.id)))
           for person in persons]

    return paginate(res)


@router.get('/{person_id}',
            response_model=Person,
            summary="Информация о персоне",
            description="Доступная информация по одной персоне",
            response_description="id, имя, id фильма и роли персоны в этом "
                                 "фильме",
            )
async def person_details(person_service: IdRequestService = Depends(get_person_service),
                         film_service: ListService = Depends(get_film_list_service),
                         person_id: str = None) -> Person:

    person = await _details(person_service, person_id, INDEX)

    films_res = _films_to_dict(person_id, await _films_for_person(film_service, person_id))
    return Person(uuid=person.id,
                  full_name=person.full_name,
                  films=films_res)


@router.get('/{person_id}/film',
            response_model=Page[FilmList],
            summary="Фильмы по персоне.",
            description="Список Фильмов по персоне.",
            response_description="Список фильмов с id, название, рейтинг",
            )
async def films_by_person(film_service: ListService = Depends(get_film_list_service),
                          person_id: str = None) -> Page[FilmList]:

    films = await _films_for_person(film_service, person_id)

    res = [FilmList(uuid=film.id,
                    title=film.title,
                    imdb_rating=film.imdb_rating) for film in films]
    return paginate(res)