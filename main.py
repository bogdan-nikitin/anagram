from contextlib import asynccontextmanager

import uvicorn

import logging
import sys
from os import getenv

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

TOKEN = getenv('BOT_TOKEN')

APP_BASE_URL = getenv("APP_BASE_URL")


async def create_tables(conn: asyncpg.Connection):
    await conn.execute('''
    DROP TABLE IF EXISTS games
    ''')
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS games(
        id serial PRIMARY KEY
    )
    ''')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(
        url=f"{APP_BASE_URL}/webhook",
        allowed_updates=dispatcher.resolve_used_update_types(),
        drop_pending_updates=True
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
        text="Open Menu", web_app=WebAppInfo(url=f"{APP_BASE_URL}/demo"))
    )
    async with asyncpg.create_pool(
            'postgresql://postgres@localhost/anagram'
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
bot = Bot(token=TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML),
          session=session)
dispatcher = Dispatcher()
dispatcher["base_url"] = APP_BASE_URL
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
