import asyncpg


async def create_tables(conn: asyncpg.Connection):
    await conn.execute('''
    DROP TABLE IF EXISTS games;
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
