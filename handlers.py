import asyncpg
import random

from aiogram import Bot, F, Router
from anagram_util import Anagrams
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
    InlineQuery,
    ChosenInlineResult
)
from aiogram.types.input_text_message_content import InputTextMessageContent
from aiogram.methods.answer_inline_query import InlineQueryResultArticle

my_router = Router()


@my_router.message(CommandStart())
async def command_start(message: Message, bot: Bot, base_url: str):
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(text="Open Menu", web_app=WebAppInfo(url=f"{base_url}/app")),
    )
    await message.answer("""Hi!\nSend me any type of message to start.\nOr just send /webview""")


@my_router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    return await inline_query.answer([InlineQueryResultArticle(
        title="Сыграть в анаграммы",
        id="play",
        description="Отправить приглашение",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Загрузка...",
                        callback_data="LOADING"
                    )
                ]
            ]
        ),
        input_message_content=InputTextMessageContent(
            message_text="Загрузка..."
        )
    )], cache_time=0)


@my_router.chosen_inline_result()
async def chosen_inline_result_handler(
        chosen_inline_result: ChosenInlineResult,
        pool: asyncpg.Pool,
        anagrams: Anagrams
):
    async with pool.acquire() as connection:
        connection: asyncpg.Connection
        public_id = (await connection.fetchrow(
            'INSERT INTO games(anagram_num, sender_id) '
            'VALUES ($1, $2) RETURNING public_id',
            random.randrange(len(anagrams)), chosen_inline_result.from_user.id
        ))['public_id'].hex
        await chosen_inline_result.bot.edit_message_text(
            text=f"Пользователь @{chosen_inline_result.from_user.username} "
                 "предлагает сыграть в анаграммы",
            inline_message_id=chosen_inline_result.inline_message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(
                    text="Играть",
                    url="https://t.me/play_anagram_bot/anagram?"
                        f"startapp={public_id}")]]
            ),
        )


@my_router.message(Command("webview"))
async def command_webview(message: Message, base_url: str):
    await message.answer(
        "Good. Now you can try to send it via Webview",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open Webview", web_app=WebAppInfo(url=f"{base_url}/app")
                    )
                ]
            ]
        ),
    )


@my_router.message(~F.message.via_bot)  # Echo to all messages except messages via bot
async def echo_all(message: Message, base_url: str):
    await message.answer(
        "Test webview",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Open", web_app=WebAppInfo(url=f"{base_url}/app"))]
            ]
        ),
    )
