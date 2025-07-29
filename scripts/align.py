from dataclasses import dataclass
import sys


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


annotations = {}

for i, line in enumerate(sys.stdin):
    if not i:
        continue

    _, _, id, gloss, *utterance = line.split(',')
    utterance = ','.join(utterance).split()
    gloss = gloss.split('/')
    for word in zip(utterance, zip(*chunk(gloss, len(utterance)))):
        text, labels = word
        text = text.lower().strip('"?,.')
        unique = set(labels)
        if len(unique) > 1:
            continue

        label, = unique
        annotation = annotations.get(text)
        if not annotation:
            annotation = Annotation()
            annotations[text] = annotation

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

print('Text', 'Noun', 'Verb', 'Adjective', 'Adverb', 'Grammatical', 'Unclear', sep=',')
for key in annotations:
    print(key, annotations[key], sep=',')    
