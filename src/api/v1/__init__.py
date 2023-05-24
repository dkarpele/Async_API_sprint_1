from http import HTTPStatus

from fastapi import HTTPException


async def _details(_id, _service, index):
    res = await _service.get_by_id(_id, index)
    if not res:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=f'{index} not found')
    return res
