from contextlib import asynccontextmanager

import uvicorn
from anagram_util import Anagrams
from settings import settings

import logging
import sys

import asyncpg

from fastapi import FastAPI, Request
from handlers import my_router
from routes import router

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import MenuButtonWebApp, WebAppInfo, Update
from aiogram.client.session.aiohttp import AiohttpSession

PYTHONANYWHERE = False


async def create_tables(conn: asyncpg.Connection):
    await conn.execute('''
    DROP TABLE IF EXISTS games;
    CREATE TABLE IF NOT EXISTS games(
        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        public_id uuid DEFAULT gen_random_uuid(),
        anagram_num smallint NOT NULL,
        sender_id bigint NOT NULL,
        invitee_id bigint,
        sender_move_mask bigint,
        invitee_move_mask bigint
    );
    ''')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{settings.APP_BASE_URL}/webhook",
        allowed_updates=dispatcher.resolve_used_update_types(),
        drop_pending_updates=True
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
        text="Open Menu", web_app=WebAppInfo(url=f"{settings.APP_BASE_URL}/app"))
    )
    async with asyncpg.create_pool(
            'postgresql://postgres@localhost/anagram',
            password=settings.PGPASSWORD.get_secret_value()
    ) as pool:
        app.state.pool = pool
        dispatcher['pool'] = pool
        async with pool.acquire() as connection:
            await create_tables(connection)
        yield
        await bot.delete_webhook()


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
session = AiohttpSession(
    proxy='http://proxy.server:3128'
) if PYTHONANYWHERE else None
bot = Bot(token=settings.BOT_TOKEN.get_secret_value(),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML),
          session=session)
dispatcher = Dispatcher()
dispatcher['base_url'] = settings.APP_BASE_URL
anagrams = Anagrams.read(settings.ANAGRAM_FILE)
dispatcher['anagrams'] = anagrams
dispatcher.include_router(my_router)
app = FastAPI(lifespan=lifespan)
app.state.bot = bot
app.include_router(router)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(),
                                   context={"bot": bot})
    await dispatcher.feed_update(bot, update)


uvicorn.run(app, host="0.0.0.0", port=8002)
