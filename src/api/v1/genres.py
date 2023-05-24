from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.v1 import _details
from models.model import Model
from services.service import ListService
from services.genre import get_genre_service
router = APIRouter()


# Модель ответа API
class Genre(Model):
    uuid: str
    name: str | None = None


@router.get('/{genre_id}',
            response_model=Genre,
            summary="Детали жанра",
            )
async def genre_details(genre_id: str,
                        genre_service: ListService = Depends(get_genre_service))\
        -> Genre:
    genre = await _details(genre_id, genre_service, 'genres')

    return Genre(uuid=genre.id,
                 name=genre.name)
