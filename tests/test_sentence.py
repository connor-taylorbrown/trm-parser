import numpy as np
from content import Word
from sentence import Phrase, Sentence


past = Word.features.preposition + Word.features.past
causative_past = Word.features.preposition + Word.features.causative + Word.features.past
alienable = Word.features.possessive + Word.features.alienable
speaker = Word.features.personal + Word.features.speaker
determiner = Word.features.determiner
lexicon = [
    ('n', Word.features.possessive, Word.features.preposition + Word.features.causative + Word.features.past, Word.features.plural),
    ('ā', Word.features.none, Word.features.possessive + Word.features.alienable + Word.features.plural, Word.features.none),
    ('i', Word.features.none, Word.features.preposition + Word.features.past, Word.features.none),
    ('te', Word.features.none, Word.features.determiner, Word.features.none),
    ('ku', Word.features.possessive, Word.features.personal + Word.features.speaker, Word.features.none),
    ('na', Word.features.possessive, Word.features.personal, Word.features.none)
]


def test_read():
    def words(end_features, *text):
        if not text:
            return []
        
        word = text[0]
        if not len(text) - 1:
            return [Word(word, word, end_features)]
        
        return [Word(word, word, Word.features.none)] + words(end_features, *text[1:])
    
    def phrase(features, *words):
        phrase = Phrase()
        for word in words:
            phrase.append(word, features)
        
        return phrase

    def match_phrases(actual: list[Phrase], expected: list[Phrase]):
        if len(actual) != len(expected):
            yield False

        for p1, p2 in zip(actual, expected):
            if np.all(p1.features == p2.features) and p1.words == p2.words:
                yield True
            else:
                yield False

    cases = [
        (
            'single word',
            words(Word.features.none, 'nā'),
            [phrase(causative_past + alienable, 'nā')]
        ),
        (
            'preposition-determiner',
            words(Word.features.none, 'nā', 'te'),
            [phrase(causative_past + alienable + determiner, 'nā', 'te')]
        ),
        (
            'preposition-content',
            words(Word.features.none, 'nā', 'Hone'),
            [phrase(causative_past + alienable, 'nā', 'Hone')]
        ),
        (
            'content-preposition',
            words(Word.features.none, 'nā', 'Hone', 'i'),
            [phrase(causative_past + alienable, 'nā', 'Hone'), phrase(past, 'i')]
        ),
        (
            'content-determiner',
            words(Word.features.none, 'nā', 'Hone', 'te'),
            [phrase(causative_past + alienable, 'nā', 'Hone'), phrase(determiner, 'te')]
        ),
        (
            'embedded preposition-determiner',
            words(Word.features.none, 'nāku', 'te'),
            [phrase(causative_past + alienable + speaker, 'nāku'), phrase(determiner, 'te')]
        ),
        (
            'embedded preposition-content',
            words(Word.features.none, 'nāku', 'noa'),
            [phrase(causative_past + alienable + speaker, 'nāku', 'noa')]
        ),
        (
            'embedded preposition-preposition',
            words(Word.features.none, 'nāku', 'i'),
            [phrase(causative_past + alienable + speaker, 'nāku'), phrase(past, 'i')]
        ),
        (
            'false start',
            words(Word.features.none, 'nā', 'i'),
            [phrase(causative_past + alienable, 'nā'), phrase(past, 'i')]
        ),
        (
            'splicing',
            words(Word.features.none, 'te', 'whare', 'nā', 'i'),
            [phrase(determiner, 'te', 'whare', 'nā'), phrase(past, 'i')]
        ),
        (
            'prosodic splicing prohibition',
            words(Word.features.pause, 'te', 'whare') + words(Word.features.none, 'nā', 'i'),
            [phrase(determiner + Word.features.pause, 'te', 'whare'), phrase(causative_past + alienable, 'nā'), phrase(past, 'i')]
        ),
        (
            'semantic splicing prohibition',
            words(Word.features.none, 'te', 'tāne', 'nāna', 'i'),
            [phrase(determiner, 'te', 'tāne'), phrase(causative_past + alienable + Word.features.personal, 'nāna'), phrase(past, 'i')]
        )
    ]

    for message, given, expected in cases:
        sut = Sentence(lexicon)

        sut.read(given)

        assert all(match_phrases(sut.phrases, expected)), message
