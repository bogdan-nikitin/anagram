import itertools
from collections import defaultdict

from iterator_util import consume

CYRILLIC_LOWER_LETTERS = sorted('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
LENGTH = 6
MIN_COUNT = 20


def get_key(word):
    return ''.join(sorted(word))


def prefixes(s):
    return [s[:i] for i in range(len(s) + 1)]


def sub_keys(key):
    it = itertools.product(*(
        prefixes(''.join(g)) for _, g in itertools.groupby(key)
    ))
    consume(it, 1)
    return map(''.join, it)


def get_anagrams(words):
    exact_anagrams = defaultdict(lambda: [])
    for word in words:
        exact_anagrams[get_key(word)] += [word]
    anagrams = {}
    for seq in itertools.combinations_with_replacement(
            CYRILLIC_LOWER_LETTERS, LENGTH):
        key = get_key(seq)
        anagrams[key] = tuple(itertools.chain.from_iterable(
            exact_anagrams[k] for k in sub_keys(key)
        ))
    return anagrams


def get_used(anagrams):
    used = set()
    for _, value in anagrams:
        used |= set(value)
    return used


def calculate_histogram(anagrams):
    hist: dict = {}
    for k, v in anagrams:
        hist[len(v)] = hist.get(len(v), 0) + 1
    return hist


def filter_anagrams(anagrams):
    return {k: v for k, v in anagrams.items() if len(v) >= MIN_COUNT}

