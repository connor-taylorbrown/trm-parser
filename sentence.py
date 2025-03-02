import re


class Sentence:
    def __init__(self, terminator, text):
        self.terminator = terminator
        self.text = text

    def __repr__(self):
        return f'({self.terminator}, {self.text})'
    

def read_sentence(text):
    pass


def read_sentences(text):
    sentence, suffix = read_sentence(text)
    if not suffix:
        return [sentence]
    
    return [sentence] + read_sentences(suffix)
