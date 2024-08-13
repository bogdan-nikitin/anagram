import asyncpg


async def create_tables(conn: asyncpg.Connection):
    # DROP TABLE IF EXISTS games;
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS games(
        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        public_id uuid DEFAULT gen_random_uuid(),
        anagram_num smallint NOT NULL,
        sender_id bigint NOT NULL,
        invitee_id bigint,
        sender_move_mask BIT VARYING,
        invitee_move_mask BIT VARYING
    );
    ''')
