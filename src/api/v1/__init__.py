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
