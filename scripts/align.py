from dataclasses import dataclass
import sys
import argparse


@dataclass
class Annotation:
    noun: int = 0
    verb: int = 0
    adjective: int = 0
    adverb: int = 0
    grammatical: int = 0
    unclear: int = 0

    def __str__(self):
        return f'{self.noun},{self.verb},{self.adjective},{self.adverb},{self.grammatical},{self.unclear}'


def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]


class Summary:
    def __init__(self):
        self.annotations = {}

    def add_label(self, id, text: str, label):
        text = text.lower().strip('"?,.')
        annotation = self.annotations.get(text)
        if not annotation:
            annotation = Annotation()
            self.annotations[text] = annotation
        
        if label == 'N':
            annotation.noun += 1
        elif label == 'V':
            annotation.verb += 1
        elif label == 'Adj':
            annotation.adjective += 1
        elif label == 'Adv':
            annotation.adverb += 1
        elif '*' in label:
            annotation.unclear += 1
        else:
            annotation.grammatical += 1

    def write(self):
        print('Text', 'Noun', 'Verb', 'Adjective', 'Adverb', 'Grammatical', 'Unclear', sep=',')
        for key in self.annotations:
            print(key, self.annotations[key], sep=',')


class Gloss:
    def __init__(self):
        self.lines = {}
    
    def add_label(self, id, text: str, label):
        line = self.lines.get(id)
        if not line:
            line = []
            self.lines[id] = line

        content = text.strip('"?,.')
        punctuation = text.replace(content, '')
        line.append(f'{content}/{label}{punctuation}')

    def write(self):
        print('ID', 'Glossed', sep=',')
        for key in self.lines:
            print(key, ' '.join(self.lines[key]))


parser = argparse.ArgumentParser(description="Align and summarize linguistic annotations.")
parser.add_argument('-s', '--summary', action='store_true', help='Print summary of annotations')
args = parser.parse_args()

if args.summary:
    result = Summary()
else:
    result = Gloss()

for i, line in enumerate(sys.stdin):
    if not i:
        continue

    _, _, id, gloss, *utterance = line.split(',')
    utterance = ','.join(utterance).split()
    gloss = gloss.split('/')
    for word in zip(utterance, zip(*chunk(gloss, len(utterance)))):
        text, labels = word

        unique = set(labels)
        if len(unique) > 1:
            result.add_label(id, text, '*')
            continue

        label, = unique
        result.add_label(id, text, label)

result.write()
