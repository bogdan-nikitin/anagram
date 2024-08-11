from asyncpg import BitString


def encode_move(encoded_words: list[int], answers_length: int) -> BitString:
    encoded = 0
    for word_num in encoded_words:
        if word_num >= answers_length:
            return BitString.from_int(0, 1)
        encoded |= 1 << (word_num + 1)
    return BitString.from_int(encoded, answers_length)


def decode_answers(move_mask: BitString) -> list[int]:
    move = move_mask.to_int()
    if move & 1:
        raise ValueError("Invalid move. First bit must be zero")
    move = move >> 1
    current = 0
    words = []
    while move > 0:
        if move & 1:
            words.append(current)
        current += 1
        move = move >> 1
    return words


def is_move_finished(move_mask: BitString):
    return move_mask != GAME_STARTED and move_mask is not None



def retrieve_words(answers: list[str], encoded_words: list[int]):
    return [answers[index] for index in encoded_words]


GAME_STARTED = BitString.from_int(1, 1)
