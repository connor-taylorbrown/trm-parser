import numpy as np
from content import Word
from sentence.header import Header


lexicon = [
    ('m', True, Word.features.possessive, Word.features.causative, Word.features.plural),
    ('n', True, Word.features.possessive, Word.features.causative + Word.features.past, Word.features.plural),
    ('ō', True, Word.features.none, Word.features.possessive + Word.features.plural, Word.features.none),
    ('ā', True, Word.features.none, Word.features.possessive + Word.features.alienable + Word.features.plural, Word.features.none),
    ('na', False, Word.features.possessive, Word.features.none, Word.features.none),
    ('ku', False, Word.features.possessive, Word.features.speaker, Word.features.none),
    ('u', False, Word.features.possessive, Word.features.listener, Word.features.none),
]


def test_enter():
    cases = [
        ('atomic', 'ā', '', Word.features.possessive + Word.features.alienable + Word.features.plural),
        ('partial (no ambiguity)', 'āku', 'ku', Word.features.possessive + Word.features.alienable + Word.features.plural),
        ('partial (global ambiguity)', 'āna', 'na', Word.features.possessive + Word.features.alienable + Word.features.plural),
        ('parameterised with override', 'nā', '', Word.features.causative + Word.features.past + Word.features.possessive + Word.features.alienable),
        ('missing', 'kē', 'kē', Word.features.none),
        ('incomplete', 'nei', 'nei', Word.features.none)
    ]

    for message, word, expected_stem, expected_effect in cases:
        sut = Header(lexicon)

        stem, effect = sut.enter(word)

        assert stem == expected_stem and np.all(effect == expected_effect), message

def test_match():
    cases = [
        ('complete', '', Word.features.causative + Word.features.possessive, Word.features.causative + Word.features.possessive),
        ('match clitic', 'ku', Word.features.causative + Word.features.possessive, Word.features.causative + Word.features.possessive + Word.features.speaker),
        ('missing clitic', 'ianei', Word.features.causative + Word.features.possessive, Word.features.none)
    ]

    for message, stem, prefix_features, expected_effect in cases:
        sut = Header(lexicon)

        effect = sut.match(prefix_features, stem)

        assert np.all(effect == expected_effect), message
