import re
import numpy as np


class Feature(dict):
    features = {
        k: v 
        for v, k in enumerate([
            'none',
            'start',
            'pause',
            'stop',
            'exclamation',
            'question',
            'start_quote',
            'end_quote',
            'exotic',
            'meta',
            'novel',
            'equative',
            'partitive',
            'causative',
            'ergative',
            'accusative',
            'alienable',
            'possessive',
            'personal',
            'speaker',
            'listener',
            'determiner',
            'demonstrative',
            'proximal',
            'medial',
            'tense',
            'past',
            'future',
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
        'nōku': features.causative + features.past + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'nōu': features.causative + features.past + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'nōna': features.causative + features.past + features.possessive + features.personal + features.determiner + features.base,

        'nā': features.causative + features.past + features.alienable + features.possessive,
        'nāku': features.causative + features.past + features.alienable + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'nāu': features.causative + features.past + features.alienable + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'nāna': features.causative + features.past + features.alienable + features.possessive + features.personal + features.determiner + features.base,

        'mō': features.causative,
        'mōku': features.causative + features.personal + features.speaker + features.determiner + features.base,
        'mōu': features.causative + features.personal + features.listener + features.determiner + features.base,
        'mōna': features.causative + features.personal + features.determiner + features.base,

        'mā': features.causative + features.alienable + features.possessive,
        'māku': features.causative + features.alienable + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'māu': features.causative + features.alienable + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'māna': features.causative + features.alienable + features.possessive + features.personal + features.determiner + features.base,

        'tō': features.possessive + features.determiner,
        'tōku': features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'tōu': features.possessive + features.personal + features.listener + features.determiner + features.base,
        'tōna': features.possessive + features.personal + features.determiner + features.base,

        'tā': features.alienable + features.possessive + features.determiner,
        'tāku': features.alienable + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'tāu': features.alienable + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'tāna': features.alienable + features.possessive + features.personal + features.determiner + features.base,

        'ō': features.plural + features.possessive + features.determiner,
        'ōku': features.plural + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'ōu': features.plural + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'ōna': features.plural + features.possessive + features.personal + features.determiner + features.base,

        'ā': features.plural + features.alienable + features.possessive + features.determiner,
        'āku': features.plural + features.alienable + features.possessive + features.personal + features.speaker + features.determiner + features.base,
        'āu': features.plural + features.alienable + features.possessive + features.personal + features.listener + features.determiner + features.base,
        'āna': features.plural + features.alienable + features.possessive + features.personal + features.determiner + features.base,

        'e': features.tense + features.ergative,
        'i': features.tense + features.past + features.accusative,
        'hei': features.tense + features.future,

        'te': features.determiner,
        'ngā': features.determiner + features.plural,
        
        'a': features.determiner + features.personal + features.possessive + features.alienable,
        'o': features.possessive,

        'tēnei': features.determiner + features.demonstrative + features.proximal,
        'ēnei': features.determiner + features.demonstrative + features.proximal + features.plural,
        'wēnei': features.determiner + features.demonstrative + features.proximal + features.plural,
        'tēnā': features.determiner + features.demonstrative + features.medial,
        'ēnā': features.determiner + features.demonstrative + features.medial + features.plural,
        'wēnā': features.determiner + features.demonstrative + features.medial + features.plural,
        'tērā': features.determiner + features.demonstrative,
        'ērā': features.determiner + features.demonstrative + features.plural,
        'wērā': features.determiner + features.demonstrative + features.plural,

        'ko': features.equative,
        'he': features.partitive,
        
        'au': features.base + features.determiner + features.personal + features.speaker,
        'koe': features.base + features.determiner + features.personal + features.listener,
        'wai': features.base + features.determiner + features.personal + features.question,
        'ia': features.base + features.determiner,
        
        'māua': features.base + features.determiner + features.personal + features.speaker + features.dual,
        'tāua': features.base + features.determiner + features.personal + features.speaker + features.listener + features.dual,
        'korua': features.base + features.determiner + features.personal + features.listener + features.dual,
        'rāua': features.base + features.determiner + features.personal + features.dual,

        'mātou': features.base + features.determiner + features.personal + features.speaker + features.plural,
        'tātou': features.base + features.determiner + features.personal + features.speaker + features.listener + features.plural,
        'koutou': features.base + features.determiner + features.personal + features.listener + features.plural,
        'rātou': features.base + features.determiner + features.personal + features.plural,
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
            features = Word.features.none

        if word and word[0].isupper():
            features += Word.features.start
        
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
