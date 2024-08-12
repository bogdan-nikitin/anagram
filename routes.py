from pathlib import Path

from asyncpg import Connection
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, APIRouter

from anagram_util import Anagrams

from game import encode_move, GAME_STARTED, retrieve_words_from_move, POINTS
from pydantic import BaseModel

from middlewares.auth import AuthDependency


class Move(BaseModel):
    encoded_words: list[int]

app_router = APIRouter(prefix="/app")


@app_router.get("/")  # TODO make static page
async def app_handler():
    return FileResponse(Path(__file__).parent.resolve() / "app.html")


@app_router.post('/prepareGame')
async def prepare_game_handler(web_app_init_data: AuthDependency,
                               request: Request):
    async with request.app.state.pool.acquire() as connection:
        connection: Connection
        game = await connection.fetchrow(
            '''SELECT 
            sender_id, sender_move_mask, invitee_id, invitee_move_mask 
            FROM games WHERE public_id = $1''',
            web_app_init_data.start_param
        )
        if game is None:
            return JSONResponse(content={"ok": False, "err": "No such game"})
    user_id = web_app_init_data.user.id
    action_ready = {'ok': True, 'action': 'ready'}
    if user_id == game['sender_id']:
        mask_column = 'sender_move_mask'
    elif user_id == game['invitee_id']:
        mask_column = 'invitee_move_mask'
    else:
        return action_ready
    if game[mask_column] is None:
        return action_ready
    return {'ok': True, 'action': 'results'}



@app_router.post('/startGame')
async def start_game_handler(web_app_init_data: AuthDependency,
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
            if game is None:
                return JSONResponse(
                    content={"ok": False, "err": "No such game"})
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
    return {'ok': True,
            'points': POINTS,
            'anagram': anagram,
            'answers': anagrams[anagram]}


@app_router.post('/move')
async def move_handler(web_app_init_data: AuthDependency,
                       request: Request,
                       move: Move):
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
            if game is None:
                return JSONResponse(
                    content={"ok": False, "err": "No such game"})
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
            anagrams: Anagrams = request.app.state.anagrams
            anagram = anagrams.ordered[game['anagram_num']]
            answers = anagrams[anagram]
            await connection.execute(f'''
            UPDATE games
            SET {mask_column} = $2 WHERE public_id = $1
            ''', public_id, encode_move(move.encoded_words, len(answers)))
    return {"ok": True}


@app_router.post("/results")
async def results_handler(web_app_init_data: AuthDependency,
                          request: Request):
    async with request.app.state.pool.acquire() as connection:
        connection: Connection
        public_id = web_app_init_data.start_param
        game = await connection.fetchrow(
            '''
            SELECT 
            sender_id, sender_move_mask, invitee_id, invitee_move_mask,
            anagram_num FROM games WHERE public_id = $1''',
            public_id
        )
        if game is None:
            return JSONResponse(content={"ok": False, "err": "No such game"})
    user_id = web_app_init_data.user.id
    if user_id == game['sender_id']:
        player_move_mask = game['sender_move_mask']
        opponent_move_mask = game['invitee_move_mask']
    elif user_id == game['invitee_id']:
        player_move_mask = game['invitee_move_mask']
        opponent_move_mask = game['sender_move_mask']
    else:
        return JSONResponse(content={"ok": False,
                                     "err": "No results for player"})
    if player_move_mask == GAME_STARTED or player_move_mask is None:
        return JSONResponse(
            content={"ok": False, "err": "Not started or finished"}
        )
    anagrams: Anagrams = request.app.state.anagrams
    anagram = anagrams.ordered[game['anagram_num']]
    answers = anagrams[anagram]
    return {'ok': True,
            'points': POINTS,
            'player_move':
                retrieve_words_from_move(answers, player_move_mask),
            'opponent_move':
                retrieve_words_from_move(answers, opponent_move_mask)}


