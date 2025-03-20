import numpy as np
from content import Word, read_content
from sentence.parser import Phrase, Sentence, lexicon, causative, alienable, determiner, possessive, personal, goal, stop

import logging

logger = logging.getLogger(__name__)


def phrase(base, features, *words):
    phrase = Phrase()
    for word in words:
        phrase.append(Word(word, word, Word.features.none), features, False)
    
    phrase.base = base
    return phrase


def match_phrases(actual: list[Phrase], expected: list[Phrase]):
    if len(actual) != len(expected):
        yield False

    for p1, p2 in zip(actual, expected):
        if np.all(p1.features == p2.features) and p1.words == p2.words and p1.base == p2.base:
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

    speaker = Word.features.personal + Word.features.speaker
    other = Word.features.personal + Word.features.other
    past = Word.features.preposition + Word.features.past
    cases = [
        (
            'single word',
            words(Word.features.none, 'nā'),
            [phrase(None, causative + past + alienable, 'nā')]
        ),
        (
            'preposition-determiner',
            words(Word.features.none, 'nā', 'te'),
            [phrase(None, causative + past + alienable + determiner, 'nā', 'te')]
        ),
        (
            'preposition-content',
            words(Word.features.none, 'nā', 'Hone'),
            [phrase('Hone', causative + past + alienable, 'nā', 'Hone')]
        ),
        (
            'content-preposition',
            words(Word.features.none, 'nā', 'Hone', 'i'),
            [phrase('Hone', causative + past + alienable, 'nā', 'Hone'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'content-determiner',
            words(Word.features.none, 'nā', 'Hone', 'te'),
            [phrase('Hone', causative + past + alienable, 'nā', 'Hone'), phrase(None, determiner, 'te')]
        ),
        (
            'embedded preposition-determiner',
            words(Word.features.none, 'nāku', 'te'),
            [phrase('nāku', causative + past + alienable + speaker, 'nāku'), phrase(None, determiner, 'te')]
        ),
        (
            'embedded preposition-content',
            words(Word.features.none, 'nāku', 'noa'),
            [phrase('nāku', causative + past + alienable + speaker, 'nāku', 'noa')]
        ),
        (
            'embedded preposition-preposition',
            words(Word.features.none, 'nāku', 'i'),
            [phrase('nāku', causative + past + alienable + speaker, 'nāku'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'false start',
            words(Word.features.none, 'nā', 'i'),
            [phrase(None, causative + past + alienable, 'nā'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'splicing preposition on preposition',
            words(Word.features.none, 'te', 'whare', 'nā', 'i'),
            [phrase('whare', determiner, 'te', 'whare', 'nā'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'splicing determiner on preposition',
            words(Word.features.none, 'e', 'ngaro', 'ana', 'i'),
            [phrase('ngaro', Word.features.preposition + Word.features.tense, 'e', 'ngaro', 'ana'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'splicing determiner on determiner',
            words(Word.features.none, 'e', 'rongohia', 'ake', 'ana', 'te'),
            [phrase('rongohia', Word.features.preposition + Word.features.tense, 'e', 'rongohia', 'ake', 'ana'), phrase(None, determiner, 'te')]
        ),
        (
            'prosodic splicing prohibition',
            words(Word.features.pause, 'te', 'whare') + words(Word.features.none, 'nā', 'i'),
            [phrase('whare', determiner + Word.features.pause, 'te', 'whare'), phrase(None, causative + past + alienable, 'nā'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'semantic splicing prohibition',
            words(Word.features.none, 'te', 'tāne', 'nāna', 'i'),
            [phrase('tāne', determiner, 'te', 'tāne'), phrase('nāna', causative + past + alienable + Word.features.personal, 'nāna'), phrase(None, past + Word.features.tense, 'i')]
        ),
        (
            'ambiguous preposition-determiner',
            words(Word.features.none, 'a', 'te', 'iwi', 'Māori'),
            [phrase('iwi', possessive + personal, 'a', 'te', 'iwi', 'Māori')]
        ),
        (
            'preposition-ambiguous determiner',
            words(Word.features.none, 'ki', 'a', 'au'),
            [phrase('au', Word.features.pronoun + goal + possessive + determiner + speaker, 'ki', 'a', 'au')]
        ),
        (
            'unusual',
            words(Word.features.none, 'e', 'tēnā', 'iwi', 'rānei', 'ki', 'mua'),
            [phrase('tēnā', Word.features.preposition + Word.features.determiner + Word.features.demonstrative + Word.features.tense, 'e', 'tēnā', 'iwi', 'rānei'), phrase('mua', goal, 'ki', 'mua')]
        ),
        (
            'unusual #2',
            words(Word.features.none, 'mā', 'te', 'marae', 'rā', 'pea', 'hei', 'whakaata', 'mai'),
            [phrase('marae', causative + alienable + determiner, 'mā', 'te', 'marae', 'rā', 'pea'), phrase('whakaata', Word.features.preposition + Word.features.tense, 'hei', 'whakaata', 'mai')]
        ),
        (
            'sentence terminator',
            words(stop, 'Nā', 'rātou', 'i', 'kī', 'mai', 'ki', 'a', 'au') + words(stop, 'Āe'),
            [phrase('rātou', Word.features.determiner + Word.features.pronoun + causative + past + alienable + other + Word.features.plural, 'Nā', 'rātou'), phrase('kī', past + Word.features.tense, 'i', 'kī', 'mai'), phrase('au', Word.features.pronoun + goal + possessive + determiner + speaker + stop, 'ki', 'a', 'au')]
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
        16: 'Ka kōrero mai a Rehua ki a Pou, "Me āta mau rawa i tā tāua pōtiki.',
        17: 'E korekore hoki, ā, tērā ka kōrero koutou i te kaupapa nei, ka tangi ake ngā reo o ngā koroua, o ngā kuia, ā, ko tētahi mea e ngaro ana i roto i te reo i tēnei wā, ahakoa tātou kōrero mō tō tātou reo Māori nei, te pai o tērā tangata mō te kōrero, te ātaahua o ana kōrero, engari, mehemea kāhore te wairua i roto i ana kōrero kei a ia, kāhore e rongohia ake ana te reka o ana kōrero.',
        18: 'Koinei te whakaaro a ētahi o tāua i te hui o ngā takawaenga mātauranga o te motu i Māngere inakuanei.',
        19: 'Kia whai hua, kia whai wāhi mātou {unclear} Kia āhei ahau e Ihowa ki te tāpae i ōku hē katoa ki mua i a koe, māu e Ihowa, e te matua, {unclear} i ēnei hē katoa, ōku hāereeretanga i roto i ngā {unclear} (o te whenua pōuri), ōku nekeneketanga, kia tahuri ai koutou i roto hoki i tā koutou',
        20: 'Nō konei rā mātou rā ko Te Whiti te karaipiture, whakarunga ki roto i te, i te reo Māori.'
    }

    for case in cases:
        sut = Sentence(lexicon)

        content = read_content(cases[case])
        sut.read(content)

        for phrase in sut.phrases:
            logger.info('%d: %s', case, phrase)
