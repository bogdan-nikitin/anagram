from asyncpg import BitString
from typing import Optional


def encode_move(encoded_words: list[int], answers_length: int) -> BitString:
    encoded = 0
    for word_num in encoded_words:
        if word_num >= answers_length:
            return BitString.from_int(0, 1)
        encoded |= 1 << (word_num + 1)
    return BitString.from_int(encoded, answers_length + 1)


def decode_move(move_mask: BitString) -> Optional[list[int]]:
    if move_mask is None or move_mask == GAME_STARTED:
        return
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



def retrieve_words(answers: tuple[str],
                   encoded_words: list[int]) -> Optional[list[str]]:
    if encoded_words is None:
        return None
    return [answers[index] for index in encoded_words]


def retrieve_words_from_move(answers: tuple[str],
                             move_mask: BitString) -> list[str]:
    return retrieve_words(answers, decode_move(move_mask))


GAME_STARTED = BitString.from_int(1, 1)
POINTS = [100, 400, 1200, 2000]
