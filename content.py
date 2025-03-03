import re


class Word:
    delimiter = re.compile(r'[ ]+|[,\.\?!]\"?')
    bracket = re.compile(r'\[\{\(')

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


def read_word(text: str):
    text = text.lstrip()

    m = Word.delimiter.search(text)
    if not m:
        return Word(text), ''
    
    word = text[:m.end()]
    suffix = text[m.end():]
    return Word(word.strip()), suffix


def read_content(text):
    while len(text):
        word, text = read_word(text)
        yield word
