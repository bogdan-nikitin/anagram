from pathlib import Path

import asyncpg
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Form, Request, APIRouter
from typing import Annotated

from anagram_util import Anagrams

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.web_app import (check_webapp_signature,
                                   safe_parse_webapp_init_data)

from middlewares.auth import Auth

router = APIRouter()


@router.get("/app")  # TODO make static page
async def app_handler():
    return FileResponse(Path(__file__).parent.resolve() / "app.html")


@router.post('/app/prepareGame')
async def prepare_game_handler(web_app_init_data: Auth,
                               request: Request):
    async with request.app.state.pool.acquire() as connection:
        connection: asyncpg.Connection
        game = await connection.fetchrow(
            '''SELECT 
            sender_id, sender_move_mask, invitee_id, invitee_move_mask 
            FROM games WHERE public_id = $1''',
            web_app_init_data.start_param
        )
        user_id = web_app_init_data.user.id
        # TODO
    return {"ok": True}


@router.post('/app/startGame')
async def start_game_handler(web_app_init_data: Auth,
                             request: Request):
    async with request.app.state.pool.acquire() as connection:
        connection: asyncpg.Connection
        async with connection.transaction():
            public_id = web_app_init_data.start_param
            game = await connection.fetchrow(
                '''
                SELECT 
                sender_id, sender_move_mask, invitee_id, invitee_move_mask,
                anagram_num FROM games WHERE public_id = $1 FOR UPDATE''',
                public_id
            )
            user_id = web_app_init_data.user.id
            if user_id == game['sender_id']:
                mask_column = 'sender_move_mask'
            elif game['invitee_id'] is None:
                await connection.execute('''
                UPDATE games
                SET invitee_id = $2 WHERE public_id = $1
                ''', public_id, user_id)
                mask_column = 'invitee_move_mask'
            else:
                return JSONResponse(content={"ok": False, "err": "Not invitee"})
            if game[mask_column] is not None:
                return JSONResponse(
                    content={"ok": False, "err": "Move is made"}
                )
            await connection.execute(f'''
            UPDATE games
            SET {mask_column} = $2 WHERE public_id = $1
            ''', public_id, asyncpg.BitString.from_int(1, 1))
    # return anagram and words
    anagrams: Anagrams = request.app.state.anagrams
    anagram = anagrams.ordered[game['anagram_num']]
    return {"ok": True, "anagram": anagram, "answers": anagrams[anagram]}

# @router.post("/demo/checkData")
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
                            request.url.replace(scheme='https', path='app')
                        )),
                    )
                ]
            ]
        )
    # await bot.answer_web_app_query(
    #     web_app_query_id=web_app_init_data.query_id,
    #     result=InlineQueryResultArticle(
    #         id=web_app_init_data.query_id,
    #         title="Demo",
    #         input_message_content=InputTextMessageContent(
    #             message_text="Hello, World!",
    #             parse_mode=None,
    #         ),
    #         reply_markup=reply_markup,
    #     ),
    # )
    return {"ok": True}
