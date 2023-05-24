from pydantic import Field

from models.model import Model


class Film(Model):
    id: str = Field(..., alias="uuid")
    title: str
    imdb_rating: float | None = None
    # TODO: genre should have type list[dict]
    genre: list[str] | None = Field(None, alias="genres")
    description: str | None = None
    # TODO: directors should have type list[dict]
    directors: list[str] | None = Field(None, alias="director")
    actors_names: list[str] | None = None
    writers_names: list[str] | None = None
    actors: list[dict] | None = None
    writers: list[dict] | None = None
