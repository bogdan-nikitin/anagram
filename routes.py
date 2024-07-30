from pathlib import Path

from asyncpg import Connection, BitString
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Form, Request, APIRouter

from anagram_util import Anagrams

from game import encode_move
from pydantic import BaseModel

from middlewares.auth import Auth



router = APIRouter()


GAME_STARTED = BitString.from_int(1, 1)


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
        connection: Connection
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
            ''', public_id, GAME_STARTED)
    anagrams: Anagrams = request.app.state.anagrams
    anagram = anagrams.ordered[game['anagram_num']]
    return {"ok": True, "anagram": anagram, "answers": anagrams[anagram]}


@router.post('/app/makeMove')
async def make_move_handler(web_app_init_data: Auth,
                            request: Request):
    async with request.app.state.pool.acquire() as connection:
        connection: Connection
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
            elif user_id == game['invitee_id']:
                await connection.execute('''
                UPDATE games
                SET invitee_id = $2 WHERE public_id = $1
                ''', public_id, user_id)
                mask_column = 'invitee_move_mask'
            else:
                return JSONResponse(content={"ok": False,
                                             "err": "Unknown player"})
            if game[mask_column] != GAME_STARTED:
                return JSONResponse(
                    content={"ok": False, "err": "Not started or finished"}
                )
            # TODO
            anagrams: Anagrams = request.app.state.anagrams
            anagram = anagrams.ordered[game['anagram_num']]
            answers = anagrams[anagram]
            await connection.execute(f'''
            UPDATE games
            SET {mask_column} = $2 WHERE public_id = $1
            ''', public_id, None)  # TODO
    return {"ok": True}

