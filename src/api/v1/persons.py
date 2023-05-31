from http import HTTPStatus

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi_pagination import Page, paginate

from api.v1 import _details, _list, _get_cache_key
from models.model import Model
from services.service import IdRequestService, ListService
from services.person import get_person_service
from services.film import get_film_list_service
from api.v1.films import FilmList
router = APIRouter()
INDEX = 'persons'


# Модель ответа API
class Person(Model):
    uuid: str
    full_name: str | None = None
    films: list[dict] | None = None


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

    search = {
        "bool": {
            "should": [
                {"nested": {
                    "path": "actors",
                    "query": {
                        "bool": {
                            "must": {"match": {
                                "actors.id": person_id}}
                        }
                    }
                }},
                {"nested": {
                    "path": "writers",
                    "query": {
                        "bool": {
                            "must": {
                                "match": {
                                    "writers.id": person_id}}
                        }
                    }
                }},
                {"nested": {
                    "path": "directors",
                    "query": {
                        "bool": {
                            "must": {
                                "match": {
                                    "directors.id": person_id}}
                        }
                    }
                }}
            ]
        }
    }

    films = await _list(film_service, index='movies', search=search)

    def collect_roles(movie):
        film_structure = {"uuid": movie.id, "roles": []}

        def roles_list(persons_list, role):
            if person_id in [actor["id"] for actor in persons_list]:
                film_structure["roles"].append(role)

        roles_list(movie.actors, 'actor')
        roles_list(movie.writers, 'writer')
        roles_list(movie.directors, 'director')
        return film_structure

    films_res = []
    for film in films:
        films_structure = collect_roles(film)
        films_res.append(films_structure)

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

    films = ...

    res = [FilmList(uuid=film.id,
                    title=film.title,
                    imdb_rating=film.imdb_rating) for film in films]
    return paginate(res)
