from http import HTTPStatus

from fastapi import HTTPException


async def _details(_service, _id, index: str = None):
    res = await _service.get_by_id(_id, index)
    if not res:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'{index} not found')
    return res


async def _list(_service, index: str = None, sort: str = None):
    res = await _service.get_list(index, sort)
    if not res:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'{index} not found')
    return res
