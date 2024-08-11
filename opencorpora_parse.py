import xml.sax
from word_util import word_filter


class StreamHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self._words = set()

    def startElement(self, name, attrs):
        if name == 'l':
            word = attrs['t']
            if word_filter(word):
                self._words.add(word)

    @property
    def words(self):
        return self._words


def get_opencorpora_words():
    parser = xml.sax.make_parser()
    handler = StreamHandler()
    parser.setContentHandler(handler)
    # feed the parser with small chunks to simulate
    with open('dict.opcorpora.xml') as f:
        parser.parse(f)
    return handler.words
