import requests
from collections import defaultdict
import itertools
import zlib
import bitstring
import huffman


# RUSSIAN_WORDS_URL = 'https://raw.githubusercontent.com/danakt/russian-words/master/russian.txt'
RUSSIAN_WORDS_URL = 'https://raw.githubusercontent.com/caffidev/russianwords/main/utf-8/words.txt'

CYRILLIC_LOWER_LETTERS = sorted('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
LENGTH = 6


def consume(iterator, n):
    """Advance the iterator n-steps ahead."""
    # Use functions that consume iterators at C speed.
    next(itertools.islice(iterator, n, n), None)


def prefixes(s):
    return [s[:i] for i in range(len(s) + 1)]


def sub_keys(key):
    it = itertools.product(*(
        prefixes(''.join(g)) for _, g in itertools.groupby(key)
    ))
    consume(it, 1)
    return map(''.join, it)


def get_words():
    response = requests.get(RUSSIAN_WORDS_URL)
    # text = response.content.decode('cp1251')
    text = response.content.decode('utf-8')

    words = set(filter(
        lambda word: len(word) <= LENGTH and
                     all(c in CYRILLIC_LOWER_LETTERS for c in word),
        text.split('\n')))
    return words


def get_score():
    words = get_words()

    count = defaultdict(lambda: 0)
    for word in words:
        count[''.join(sorted(word))] += 1

    score = {}
    for seq in itertools.combinations_with_replacement(
            CYRILLIC_LOWER_LETTERS, LENGTH):
        s = ''.join(seq)
        score[s] = sum(count[k] for k in sub_keys(s))
    sorted_keys = sorted(score.items(), key=lambda pair: pair[1], reverse=True)
    print(sorted_keys[:10])


def get_grouped():
    words = get_words()
    print(len(words))

    count = defaultdict(lambda: [])
    for word in words:
        count[''.join(sorted(word))] += [word]

    score = {}
    # cache = {}
    for seq in itertools.combinations_with_replacement(
            CYRILLIC_LOWER_LETTERS, LENGTH):
        s = ''.join(seq)
        score[s] = list(
            itertools.chain.from_iterable(count[k] for k in sub_keys(s)))
    sorted_keys = sorted(score.items(), key=lambda pair: len(pair[1]),
                         reverse=True)
    hist = {}
    for k, v in sorted_keys:
        hist[len(v)] = hist.get(len(v), 0) + 1
    print(hist)
    used = set()
    for _, value in sorted_keys:
        used |= set(value)
    print(len(used))
    # print(len(encode(used)))
    # return encode_fixed(used)
    return encode_huffman(used)
    # print(sorted_keys[:2])


def _encode_fixed(s):
    alphabet = ''.join(CYRILLIC_LOWER_LETTERS) + ' '
    arr = bitstring.BitArray()
    power = len(alphabet).bit_length()
    print(power)
    for c in s:
        arr.append(bitstring.Bits(uint=alphabet.index(c), length=power))
    return arr.tobytes()


def encode_fixed(words):
    return _encode_fixed(' '.join(words))


def encode_huffman(words):
    s = ' '.join(words)
    weights = defaultdict(lambda: 0)
    for c in s:
        weights[c] += 1
    return huffman.encode(s, weights)


if __name__ == '__main__':
    pass
    # b = get_grouped()
    # print(len(b))
    # print(len(zlib.compress(b, level=9)))

    # print(zlib.compress(123))
    # print(sorted(CYRILLIC_LOWER_LETTERS))
    # print(list(sub_keys('aaabbccc')))
