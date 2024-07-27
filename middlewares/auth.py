from typing import Annotated

from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import Form, HTTPException, Depends
from starlette.requests import Request


async def auth(init_data: Annotated[str, Form()],
               request: Request) -> WebAppInitData:
    try:
        return safe_parse_webapp_init_data(
            token=request.app.state.bot.token, init_data=init_data
        )
    except ValueError:
        raise HTTPException(content={"ok": False, "err": "Unauthorized"},
                            status_code=401)


Auth = Annotated[WebAppInitData, Depends(auth)]
