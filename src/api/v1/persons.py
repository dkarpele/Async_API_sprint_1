from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.v1 import _details
from models.model import Model
from services.service import IdRequestService
from services.person import get_person_service

router = APIRouter()
INDEX = 'persons'


# Модель ответа API
class Person(Model):
    uuid: str
    full_name: str | None = None
    films: list[dict] | None = None


@router.get('/{person_id}',
            response_model=Person,
            summary="Информация о персоне")
async def person_details(person_service: IdRequestService = Depends(get_person_service),
                         person_id: str = None)\
        -> Person:
    person = await _details(person_service, person_id, 'persons')

    return Person(uuid=person.id,
                  full_name=person.full_name,
                  films=person.films)
