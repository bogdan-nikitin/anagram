from pathlib import Path

from fastapi.responses import FileResponse, JSONResponse
from fastapi import Form, Request, APIRouter
from typing import Annotated


from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
)
from aiogram.utils.web_app import (check_webapp_signature,
                                   safe_parse_webapp_init_data)


router = APIRouter()


@router.get("/app")
async def demo_handler():
    return FileResponse(Path(__file__).parent.resolve() / "demo.html")


@router.post("/demo/checkData")
async def check_data_handler(
        auth: Annotated[str, Form(alias="_auth")],
        request: Request):
    bot: Bot = request.app.state.bot

    if check_webapp_signature(bot.token, auth):
        return {"ok": True}
    return JSONResponse(content={"ok": False, "err": "Unauthorized"},
                        status_code=401)


@router.post("/demo/sendMessage")
async def send_message_handler(auth: Annotated[str, Form(alias="_auth")],
                               with_webview: Annotated[str, Form()],
                               request: Request):
    bot: Bot = request.app.state.bot
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token,
                                                        init_data=auth)
    except ValueError:
        return JSONResponse(content={"ok": False, "err": "Unauthorized"},
                            status_code=401)

    reply_markup = None
    if with_webview == "1":
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open",
                        web_app=WebAppInfo(url=str(
                            request.url.replace(scheme="https")
                        )),
                    )
                ]
            ]
        )
    await bot.answer_web_app_query(
        web_app_query_id=web_app_init_data.query_id,
        result=InlineQueryResultArticle(
            id=web_app_init_data.query_id,
            title="Demo",
            input_message_content=InputTextMessageContent(
                message_text="Hello, World!",
                parse_mode=None,
            ),
            reply_markup=reply_markup,
        ),
    )
    return {"ok": True}
