from anargram import *


def word_filter(word):
    return (len(word) <= LENGTH and
            all(c in CYRILLIC_LOWER_LETTERS for c in word))
