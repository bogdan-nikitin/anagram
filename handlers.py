import asyncpg

from aiogram import Bot, F, Router
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
        menu_button=MenuButtonWebApp(text="Open Menu", web_app=WebAppInfo(url=f"{base_url}/demo")),
    )
    await message.answer("""Hi!\nSend me any type of message to start.\nOr just send /webview""")


@my_router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    return await inline_query.answer([InlineQueryResultArticle(
        title="Example3",
        id="example1",
        description="Description",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Test1",
                        callback_data="dummy"
                    )
                ]
            ]
        ),
        input_message_content=InputTextMessageContent(message_text="Test")
    )], cache_time=0)


@my_router.chosen_inline_result()
async def chosen_inline_result_handler(
        chosen_inline_result: ChosenInlineResult,
        pool: asyncpg.Pool
):
    # await chosen_inline_result.bot.edit_message_text(
    #     text="Changed",
    #     inline_message_id=chosen_inline_result.inline_message_id,
    #     # reply_markup=InlineKeyboardMarkup(
    #     #     inline_keyboard=[
    #     #         [
    #     #             InlineKeyboardButton(
    #     #                 text="Test2",
    #     #                 web_app=WebAppInfo(url=f"{base_url}/demo")
    #     #             )
    #     #         ]
    #     #     ]
    #     # ),
    # )
    await chosen_inline_result.bot.edit_message_reply_markup(
        inline_message_id=chosen_inline_result.inline_message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Test2",
                        url=f"https://t.me/play_anagram_bot/anagram",
                    )
                ]
            ]
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
                        text="Open Webview", web_app=WebAppInfo(url=f"{base_url}/demo")
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
                [InlineKeyboardButton(text="Open", web_app=WebAppInfo(url=f"{base_url}/demo"))]
            ]
        ),
    )
