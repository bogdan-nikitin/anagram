from asyncpg import BitString


def encode_move(encoded_words: list[int], answers_length: int) -> BitString:
    encoded = 0
    for word_num in encoded_words:
        if word_num >= answers_length:
            return BitString.from_int(0, 1)
        encoded |= 1 << (word_num + 1)
    return BitString.from_int(encoded, answers_length)