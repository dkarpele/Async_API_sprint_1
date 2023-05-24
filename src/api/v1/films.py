from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.v1 import _details
from services.service import ListService
from services.film import get_film_service
from models.model import Model
# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах


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


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/films/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса
# (film_id: str)
# И указываем тип возвращаемого объекта — Film
# Внедряем ListService с помощью Depends(get_film_service)
@router.get('/{film_id}',
            response_model=Film,
            summary="Детали фильма",
            description="Доступная информация по одному фильму",
            )
async def film_details(film_id: str,
                       film_service: ListService = Depends(get_film_service))\
        -> Film:
    film = await _details(film_id, film_service, 'movies')
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


# TODO: placeholder for search method
# @router.get("/search",
#          response_model=list[Film],
#          summary="Поиск кинопроизведений",
#          description="Полнотекстовый поиск по кинопроизведениям",
#          response_description="Название и рейтинг фильма",
#          tags=['Полнотекстовый поиск']
#          )
# async def film_search():
#     ...