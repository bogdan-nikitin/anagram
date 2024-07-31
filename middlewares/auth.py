from typing import Annotated

from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import HTTPException, Depends
from starlette.requests import Request
from pydantic import BaseModel


class Auth(BaseModel):
    init_data: str


async def auth_dependency(auth: Auth,
                          request: Request) -> WebAppInitData:
    try:
        return safe_parse_webapp_init_data(
            token=request.app.state.bot.token, init_data=auth.init_data
        )
    except ValueError:
        raise HTTPException(content={"ok": False, "err": "Unauthorized"},
                            status_code=401)


AuthDependency = Annotated[WebAppInitData, Depends(auth_dependency)]
