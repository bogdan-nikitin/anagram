import requests
from collections import defaultdict
import bitstring
import huffman
from anargram import CYRILLIC_LOWER_LETTERS, LENGTH, get_anagrams
import pickle


ANAGRAM_FILE = 'anagrams.pickle'
RUSSIAN_WORDS_URL = 'https://raw.githubusercontent.com/caffidev/russianwords/main/utf-8/words.txt'


def get_words():
    response = requests.get(RUSSIAN_WORDS_URL)
    text = response.content.decode('utf-8')

    words = set(filter(
        lambda word: len(word) <= LENGTH and
                     all(c in CYRILLIC_LOWER_LETTERS for c in word),
        text.split('\n')))
    return words


def _encode_fixed(s):
    alphabet = ''.join(CYRILLIC_LOWER_LETTERS) + ' '
    arr = bitstring.BitArray()
    power = len(alphabet).bit_length()
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


def write_anagrams():
    with open(ANAGRAM_FILE, mode='wb') as file:
        pickle.dump(get_anagrams(get_words()), file)


def read_anagrams():
    with open(ANAGRAM_FILE, mode='rb') as file:
        return pickle.load(file)


if __name__ == '__main__':
    anagrams = read_anagrams()
    # b = get_grouped()
    # print(len(b))
    # print(len(zlib.compress(b, level=9)))

    # print(zlib.compress(123))
    # print(sorted(CYRILLIC_LOWER_LETTERS))
    # print(list(sub_keys('aaabbccc')))
