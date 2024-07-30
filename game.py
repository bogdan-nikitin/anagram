from asyncpg import BitString


def encode_move(move: list[int], answers_length: int) -> BitString:
    encoded = 0
    for word_num in move:
        if word_num >= answers_length:
            return BitString.from_int(0, 1)
        encoded |= 1 << (word_num + 1)
    return BitString.from_int(encoded, answers_length)