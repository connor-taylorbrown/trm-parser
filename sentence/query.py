import numpy as np
from content import Word
from corpus import TokenType
from query import TextQuery
from sentence.parser import Sentence


class SentenceQuery(TextQuery):
    def __init__(self, lexicon):
        self.lexicon = lexicon

    def apply(self, type, words: list[Word]):
        if not type == TokenType.content:
            return []
        
        while len(words):
            sentence = Sentence(self.lexicon)
            i = sentence.read(words)
            
            yield sentence.phrases
            words = words[i:]
