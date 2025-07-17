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
            'preposition',
            'equative',
            'partitive',
            'causative',
            'ergative',
            'accusative',
            'alienable',
            'possessive',
            'personal',
            'pronoun',
            'speaker',
            'listener',
            'other',
            'determiner',
            'demonstrative',
            'proximal',
            'medial',
            'tense',
            'past',
            'future',
            'goal',
            'base',
            'plural',
            'dual',
            'conditional',
            'locative',
            'number'
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

    def __init__(self, word, text, features):
        self.word = word
        self.text = text
        self.features = features

    def __repr__(self):
        return f'({self.word},{self.features})'
    
    @staticmethod
    def annotate(word: str):
        features = np.copy(Word.features.none)
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
        return Word(text, text, prefix_features + bracket_features + Word.features.pause + Word.features.stop), ''
    
    suffix_features, word = read_suffix(stem[:m.end()])
    features = prefix_features + bracket_features + suffix_features + Word.annotate(word)
    
    tail = stem[m.end():]
    head = text if not len(tail) else text[:-len(tail)]
    return Word(word, head.strip(), features), tail


def read_content(text):
    while len(text):
        word, text = read_word(text)
        yield word
