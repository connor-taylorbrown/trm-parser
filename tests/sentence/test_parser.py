import numpy as np
from content import Word, read_content
from sentence.parser import Phrase, Sentence

import logging

logger = logging.getLogger(__name__)


alienable = Word.features.possessive + Word.features.alienable

past = Word.features.preposition + Word.features.past
goal = Word.features.preposition + Word.features.goal
possessive = Word.features.preposition + alienable
causative = Word.features.preposition + Word.features.causative

determiner = Word.features.determiner
personal = Word.features.determiner + Word.features.personal

speaker = Word.features.personal + Word.features.speaker
listener = Word.features.personal + Word.features.listener

stop = Word.features.pause + Word.features.stop

lexicon = [
    ('ngā', True, Word.features.none, determiner + Word.features.plural, Word.features.none),
    ('n', True, Word.features.possessive, causative + past, Word.features.determiner + Word.features.plural),
    ('me', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('m', True, Word.features.possessive, causative, Word.features.determiner + Word.features.plural),
    ('ā', True, Word.features.none, alienable + Word.features.determiner + Word.features.plural, Word.features.none),
    ('ō', True, Word.features.none, Word.features.possessive + Word.features.determiner + Word.features.plural, Word.features.none),
    ('i', True, Word.features.none, past, Word.features.none),
    ('te', True, Word.features.none, determiner, Word.features.none),
    ('t', True, Word.features.determiner, Word.features.none, Word.features.plural),
    ('ē', True, Word.features.none, Word.features.demonstrative + Word.features.determiner + Word.features.plural, Word.features.none),
    ('kia', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('ki', True, Word.features.none, goal, Word.features.none),
    ('ka', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('ana', True, Word.features.none, Word.features.none, Word.features.none),
    ('au', True, Word.features.none, Word.features.speaker, Word.features.none),
    ('a', True, Word.features.none, possessive + personal, Word.features.none),
    ('ko', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('he', True, Word.features.none, Word.features.determiner, Word.features.none),
    ('e', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('o', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('kei', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('hei', True, Word.features.none, Word.features.preposition, Word.features.none),

    ('tahi', False, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('rā', False, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('nei', False, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('nā', False, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('ku', False, Word.features.possessive, speaker, Word.features.none),
    ('u', False, Word.features.possessive, listener, Word.features.none),
    ('na', False, Word.features.possessive, Word.features.personal, Word.features.none),
]
    

def phrase(features, *words):
    phrase = Phrase()
    for word in words:
        phrase.append(Word(word, word, Word.features.none), features)
    
    return phrase


def match_phrases(actual: list[Phrase], expected: list[Phrase]):
    if len(actual) != len(expected):
        yield False

    for p1, p2 in zip(actual, expected):
        if np.all(p1.features == p2.features) and p1.words == p2.words:
            yield True
        else:
            yield False


def test_read():
    def words(end_features, *text):
        if not text:
            return []
        
        word = text[0]
        if not len(text) - 1:
            return [Word(word, word, end_features)]
        
        return [Word(word, word, Word.features.none)] + words(end_features, *text[1:])

    cases = [
        (
            'single word',
            words(Word.features.none, 'nā'),
            [phrase(causative + past + alienable, 'nā')]
        ),
        (
            'preposition-determiner',
            words(Word.features.none, 'nā', 'te'),
            [phrase(causative + past + alienable + determiner, 'nā', 'te')]
        ),
        (
            'preposition-content',
            words(Word.features.none, 'nā', 'Hone'),
            [phrase(causative + past + alienable, 'nā', 'Hone')]
        ),
        (
            'content-preposition',
            words(Word.features.none, 'nā', 'Hone', 'i'),
            [phrase(causative + past + alienable, 'nā', 'Hone'), phrase(past, 'i')]
        ),
        (
            'content-determiner',
            words(Word.features.none, 'nā', 'Hone', 'te'),
            [phrase(causative + past + alienable, 'nā', 'Hone'), phrase(determiner, 'te')]
        ),
        (
            'embedded preposition-determiner',
            words(Word.features.none, 'nāku', 'te'),
            [phrase(causative + past + alienable + speaker, 'nāku'), phrase(determiner, 'te')]
        ),
        (
            'embedded preposition-content',
            words(Word.features.none, 'nāku', 'noa'),
            [phrase(causative + past + alienable + speaker, 'nāku', 'noa')]
        ),
        (
            'embedded preposition-preposition',
            words(Word.features.none, 'nāku', 'i'),
            [phrase(causative + past + alienable + speaker, 'nāku'), phrase(past, 'i')]
        ),
        (
            'false start',
            words(Word.features.none, 'nā', 'i'),
            [phrase(causative + past + alienable, 'nā'), phrase(past, 'i')]
        ),
        (
            'splicing',
            words(Word.features.none, 'te', 'whare', 'nā', 'i'),
            [phrase(determiner, 'te', 'whare', 'nā'), phrase(past, 'i')]
        ),
        (
            'prosodic splicing prohibition',
            words(Word.features.pause, 'te', 'whare') + words(Word.features.none, 'nā', 'i'),
            [phrase(determiner + Word.features.pause, 'te', 'whare'), phrase(causative + past + alienable, 'nā'), phrase(past, 'i')]
        ),
        (
            'semantic splicing prohibition',
            words(Word.features.none, 'te', 'tāne', 'nāna', 'i'),
            [phrase(determiner, 'te', 'tāne'), phrase(causative + past + alienable + Word.features.personal, 'nāna'), phrase(past, 'i')]
        ),
        (
            'ambiguous preposition-determiner',
            words(Word.features.none, 'a', 'te', 'iwi', 'Māori'),
            [phrase(possessive + personal, 'a', 'te', 'iwi', 'Māori')]
        ),
        (
            'preposition-ambiguous determiner',
            words(Word.features.none, 'ki', 'a', 'au'),
            [phrase(goal + possessive + determiner + speaker, 'ki', 'a', 'au')]
        ),
        (
            'unusual',
            words(Word.features.none, 'e', 'tēnā', 'iwi', 'rānei', 'ki', 'mua'),
            [phrase(Word.features.preposition + Word.features.determiner + Word.features.demonstrative, 'e', 'tēnā', 'iwi', 'rānei'), phrase(goal, 'ki', 'mua')]
        ),
        (
            'sentence terminator',
            words(stop, 'Nā', 'rātou', 'i', 'kī', 'mai', 'ki', 'a', 'au') + words(stop, 'Āe'),
            [phrase(causative + past + alienable, 'Nā', 'rātou'), phrase(past, 'i', 'kī', 'mai'), phrase(goal + possessive + determiner + speaker + stop, 'ki', 'a', 'au')]
        )
    ]

    for message, given, expected in cases:
        sut = Sentence(lexicon)

        sut.read(given)

        assert all(match_phrases(sut.phrases, expected)), message


def test_selected_cases():
    cases = {
        1: 'Ko ngā kaute mutunga, e rua ki te kore.',
        2: 'Mehemea ka whakatakotoria mai e tēnā iwi, e tēnā iwi rānei ki mua i te aroaro, ā, anā, o te hui whakakotahi nei, engari, ki ngā mōhio, kei te haere ā waenga iwi ināianei mā tēnā iwi, mā tēnā iwi anō e whakatakoto i ōna nei whakaaro.',
        3: 'Kāore anō au kia rongo i te hā kakara mai o te atua e kōrerotia nei.',
        4: 'Mā te pepa hei kawea te whakaaro rangatira i roto i ngā, i roto i ngā kōrero.',
        5: 'E hia kē ngā tamariki e ngahoro mai ana.',
        6: 'Otirā, ā, hei parāoa, hei pata mā te whānau.',
        7: 'I konei ko te tupuna a Tini Arapata Hōrau Tirikatene, i te urupā o Te Kai-ā-te-Atua ko te whānau o tēnei tupuna.',
        8: 'He kōrero mō [Bosnia].',
        9: 'Mā te huruhuru ka rere te manu.',
        10: 'E rua ngā kōhanga reo kei runga o te marae nei ināianei.',
        11: 'Ka whāngai atu ki ngā kōhungahunga.',
        12: 'I te rā tuawhā atu ki te rā tuaono o Whiringa-ā-nuku, ka tū tētahi hui hauora ki Harataunga Marae, Harataunga.',
        13: 'Tū whakahīhī ana te, te, te tangata, erangi ka ū, titiro whakamuri, ā, i neke pēwhea, pēwhea mai tātou i roto i ngā mamaetanga, ā, haere mai ana te, te konohi aroha me te roimata.',
        14: 'Ko ētahi o rātou ka, kāore i te tino mārama.',
        15: 'Ā, mēnā ka whakaae mai a [Marie Clay] i wā mātou mahi, āe.',
        16: 'Koira noa iho aku mahi.',
        17: 'E korekore hoki, ā, tērā ka kōrero koutou i te kaupapa nei, ka tangi ake ngā reo o ngā koroua, o ngā kuia, ā, ko tētahi mea e ngaro ana i roto i te reo i tēnei wā, ahakoa tātou kōrero mō tō tātou reo Māori nei, te pai o tērā tangata mō te kōrero, te ātaahua o ana kōrero, engari, mehemea kāhore te wairua i roto i ana kōrero kei a ia, kāhore e rongohia ake ana te reka o ana kōrero.',
        18: 'Koinei te whakaaro a ētahi o tāua i te hui o ngā takawaenga mātauranga o te motu i Māngere inakuanei.',
        19: 'Ā, i muri i tērā, ka hoki mai ai ia.',
        20: 'Nō konei rā mātou rā ko Te Whiti te karaipiture, whakarunga ki roto i te, i te reo Māori.'
    }

    for case in cases:
        sut = Sentence(lexicon)

        content = read_content(cases[case])
        sut.read(content)

        for phrase in sut.phrases:
            logger.info('%d: %s', case, phrase)
