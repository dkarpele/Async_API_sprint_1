from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from api.v1 import _details, _list
from models.model import Model
from services.service import IdRequestService, ListService
from services.genre import get_genre_service, get_genre_list_service

router = APIRouter()
INDEX = 'genres'


# Модель ответа API
class Genre(Model):
    uuid: str
    name: str | None = None


@router.get('/{genre_id}',
            response_model=Genre,
            summary="Детали жанра",
            description="Доступная информация по одному жанру",
            response_description="id, название"
            )
async def genre_details(genre_service: IdRequestService = Depends(get_genre_service),
                        genre_id: str = None) -> Genre:
    genre = await _details(genre_service, genre_id, INDEX)

    return Genre(uuid=genre.id,
                 name=genre.name)


@router.get('/',
            response_model=Page[Genre],
            summary="Список жанров",
            description="Список жанров с информацией о id, названии",
            response_description="id, название"
            )
async def genre_list(genre_service: ListService = Depends(get_genre_list_service))\
        -> Page[Genre]:
    genres = await _list(genre_service, index=INDEX)

    res = [Genre(uuid=genre.id,
                 name=genre.name) for genre in genres]
    return paginate(res)
