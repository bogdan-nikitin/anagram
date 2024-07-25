import requests
import bitstring
import huffman
from anargram import *
import pickle


ANAGRAM_FILE = 'anagrams.pickle'
MINI_ANAGRAM_FILE = 'mini_anagrams.pickle'
RUSSIAN_WORDS_URL = 'https://raw.githubusercontent.com/caffidev/russianwords/main/utf-8/words.txt'
MINI_SIZE = 10


class Anagrams:
    def __init__(self, anagrams: dict[str, tuple[str]]):
        self._anagrams = anagrams
        self._ordered = tuple(sorted(anagrams))

    def write(self, filename):
        write_anagrams(self._anagrams, filename)

    @staticmethod
    def read(filename: str) -> 'Anagrams':
        return Anagrams(read_anagrams(filename))

    @property
    def ordered(self) -> tuple[str]:
        return self._ordered

    def __getitem__(self, item) -> tuple[str]:
        return self._anagrams[item]

    def __len__(self):
        return len(self.ordered)


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


def get_filtered_anagrams():
    return filter_anagrams(get_anagrams(get_words()))


def write_anagrams(anagrams=None, filename=ANAGRAM_FILE):
    anagrams = anagrams or get_filtered_anagrams()
    with open(filename, mode='wb') as file:
        pickle.dump(anagrams, file)


def read_anagrams(filename=ANAGRAM_FILE) -> dict[str, tuple[str]]:
    with open(filename, mode='rb') as file:
        return pickle.load(file)


def get_mini_anagrams():
    return dict(itertools.islice(get_filtered_anagrams().items(), MINI_SIZE))


if __name__ == '__main__':
    # print(len(get_filtered_anagrams()))
    print(Anagrams.read(MINI_ANAGRAM_FILE).ordered)
    # Anagrams(get_mini_anagrams()).write(MINI_ANAGRAM_FILE)
    # write_anagrams(get_mini_anagrams(), MINI_ANAGRAM_FILE)
    # anagrams = get_anagrams(get_words())
    # anagrams = read_anagrams(MINI_ANAGRAM_FILE)
    # b = get_grouped()
    # print(len(b))
    # print(len(zlib.compress(b, level=9)))

    # print(zlib.compress(123))
    # print(sorted(CYRILLIC_LOWER_LETTERS))
    # print(list(sub_keys('aaabbccc')))
