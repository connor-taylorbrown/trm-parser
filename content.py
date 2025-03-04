import re
import numpy as np


class Feature(dict):
    features = {
        k: v 
        for v, k in enumerate([
            'none',
            'pause',
            'stop',
            'exclamation',
            'question',
            'start_quote',
            'end_quote',
            'exotic',
            'meta',
            'novel',
            'past',
            'causative',
            'alienable',
            'possessive',
            'speaker',
            'listener',
            'determiner',
            'tense',
            'past',
            'base',
            'plural',
            'dual'
        ])
    }

    def __getitem__(self, k):
        return self.__getattr__(k)

    def __getattr__(self, k):
        c = len(Feature.features)
        vec = np.zeros(c, dtype=bool)
        i = Feature.features[k]
        if i:
            vec[i-1] = True
        
        return vec
    



class Word:
    features = Feature()
    delimiter = re.compile(r'[ ]+|[,\.\?!]\"?')

    brackets = {
        '[': (']', features.exotic),
        '{': ('}', features.meta),
        '(': (')', features.novel)
    }

    prefixes = {
        '"': features.start_quote
    }

    suffixes = {
        '"': features.end_quote,
        ',': features.pause,
        '.': features.pause + features.stop,
        '?': features.pause + features.stop + features.question,
        '!': features.pause + features.stop + features.exclamation
    }

    words = {
        'nō': features.causative + features.past + features.possessive,
        'nōku': features.causative + features.past + features.possessive + features.speaker + features.determiner + features.base,
        'nōu': features.causative + features.past + features.possessive + features.listener + features.determiner + features.base,
        'nōna': features.causative + features.past + features.possessive + features.determiner + features.base,

        'mō': features.causative,
        'mōku': features.causative + features.speaker + features.determiner + features.base,
        'mōu': features.causative + features.listener + features.determiner + features.base,
        'mōna': features.causative + features.determiner + features.base,

        'nā': features.causative + features.past + features.alienable + features.possessive,
        'nāku': features.causative + features.past + features.alienable + features.possessive + features.speaker + features.determiner + features.base,
        'nāu': features.causative + features.past + features.alienable + features.possessive + features.listener + features.determiner + features.base,
        'nāna': features.causative + features.past + features.alienable + features.possessive + features.determiner + features.base,

        'mā': features.causative + features.alienable + features.possessive,
        'māku': features.causative + features.alienable + features.possessive + features.speaker + features.determiner + features.base,
        'māu': features.causative + features.alienable + features.possessive + features.listener + features.determiner + features.base,
        'māna': features.causative + features.alienable + features.possessive + features.determiner + features.base,

        'e': features.tense,
        'i': features.tense + features.past,

        'te': features.determiner,
        'ngā': features.determiner + features.plural,
        
        'au': features.base + features.determiner + features.speaker,
        'koe': features.base + features.determiner + features.listener,
        'ia': features.base + features.determiner,
        
        'māua': features.base + features.determiner + features.speaker + features.dual,
        'tāua': features.base + features.determiner + features.speaker + features.listener + features.dual,
        'korua': features.base + features.determiner + features.listener + features.dual,
        'rāua': features.base + features.determiner + features.dual,

        'mātou': features.base + features.determiner + features.speaker + features.plural,
        'tātou': features.base + features.determiner + features.speaker + features.listener + features.plural,
        'koutou': features.base + features.determiner + features.listener + features.plural,
        'rātou': features.base + features.determiner + features.plural,
    }

    def __init__(self, word, text, features):
        self.word = word
        self.text = text
        self.features = features

    def __repr__(self):
        return f'({self.word},{self.features})'
    
    @staticmethod
    def annotate(word: str):
        features = Word.words.get(word.lower())
        if features is None:
            return Word.features.none
        
        return features
    

def read_prefix(text: str):
    for prefix in Word.prefixes:
        if not text[:len(prefix)].lower() == prefix:
            continue

        features, stem = read_prefix(text[len(prefix):]) 
        features += Word.prefixes[prefix]
        return features, stem
    
    return Word.features.none, text


def read_suffix(stem: str):
    stem = stem.rstrip()
    for suffix in Word.suffixes:
        if not stem.endswith(suffix):
            continue

        features, word = read_suffix(stem[:-len(suffix)])
        features += Word.suffixes[suffix]
        return features, word
    
    return Word.features.none, stem


def read_brackets(text: str):
    if text and text[0] in Word.brackets:
        bracket, text = text[0], text[1:]
        expected, feature = Word.brackets[bracket]
        open = 1
        for i, c in enumerate(text):   
            if not open:
                return feature, text[i:]
                
            if c == bracket:
                open += 1
            elif c == expected:
                open -= 1

        return feature, ''
    
    return Word.features.none, text


def read_word(text: str):
    text = text.lstrip()
    prefix_features, stem = read_prefix(text)
    bracket_features, stem = read_brackets(stem)

    m = Word.delimiter.search(stem)
    if not m:
        return Word(text, text, prefix_features + bracket_features + Word.features.stop), ''
    
    suffix_features, word = read_suffix(stem[:m.end()])
    features = prefix_features + bracket_features + suffix_features + Word.annotate(word)
    
    tail = stem[m.end():]
    head = text if not len(tail) else text[:-len(tail)]
    return Word(word, head.strip(), features), tail


def read_content(text):
    while len(text):
        word, text = read_word(text)
        yield word
