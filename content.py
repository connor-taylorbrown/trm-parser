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

    def __init__(self, text, features):
        self.text = text
        self.features = features

    def __repr__(self):
        return f'({self.text},{self.features})'
    

def read_prefix(text: str):
    for prefix in Word.prefixes:
        if not text.startswith(prefix):
            continue

        features, stem = read_prefix(text[len(prefix):]) 
        features += Word.prefixes[prefix]
        return features, stem
    
    return Word.features.none, text


def read_suffix(stem: str):
    for suffix in Word.suffixes:
        if not stem.endswith(suffix):
            continue

        features = read_suffix(stem[:-len(suffix)])
        features += Word.suffixes[suffix]
        return features
    
    return Word.features.none


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
        return Word(text, prefix_features + bracket_features), ''
    
    word = stem[:m.end()]
    suffix_features = read_suffix(word)
    
    tail = stem[m.end():]
    head = text if not len(tail) else text[:-len(tail)]
    return Word(head.strip(), prefix_features + bracket_features + suffix_features), tail


def read_content(text):
    while len(text):
        word, text = read_word(text)
        yield word
