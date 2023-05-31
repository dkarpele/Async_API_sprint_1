from http import HTTPStatus

from fastapi import HTTPException


async def _details(_service, _id: str, index: str = None):
    res = await _service.get_by_id(_id, index)
    if not res:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'{_id} not found in {index}')
    return res


async def _list(_service,
                index: str = None,
                sort: str = None,
                search: dict = None,
                key: str = None):
    res = await _service.get_list(index, sort, search, key)
    if not res:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'{index} not found')
    return res


async def _get_cache_key(args_dict: dict,
                         index: str = None) -> str:
    key = ''
    for k, v in args_dict.items():
        if v:
            key += f':{k}:{v}'

    return f'index:{index}{key}' if key else None


async def _films_for_person(_service, person_id: str = None) -> list[dict]:
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

    films = await _list(_service, index='movies', search=search)

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

    return films_res
