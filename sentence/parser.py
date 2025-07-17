import numpy as np

from content import Feature, Word
from sentence.header import Header


alienable = Word.features.possessive + Word.features.alienable

goal = Word.features.preposition + Word.features.goal
possessive = Word.features.preposition + alienable
causative = Word.features.preposition + Word.features.causative

determiner = Word.features.determiner
personal = Word.features.determiner + Word.features.personal

stop = Word.features.pause + Word.features.stop

lexicon = [
    ('ku', False, Word.features.possessive, Word.features.personal + Word.features.speaker, Word.features.none),
    ('u', False, Word.features.possessive, Word.features.personal + Word.features.listener, Word.features.none),
    ('na', False, Word.features.possessive, Word.features.personal, Word.features.none),
    ('tahi', False, Word.features.demonstrative, Word.features.number, Word.features.none),
    ('tehi', False, Word.features.demonstrative, Word.features.number, Word.features.none),

    ('au', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.speaker, Word.features.none),
    ('koe', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.listener, Word.features.none),
    ('ia', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.other, Word.features.none),

    ('tāua', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.speaker + Word.features.listener + Word.features.dual, Word.features.none),
    ('māua', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.speaker + Word.features.dual, Word.features.none),
    ('korua', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.listener + Word.features.dual, Word.features.none),
    ('rāua', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.other + Word.features.dual, Word.features.none),

    ('tātou', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.speaker + Word.features.listener + Word.features.plural, Word.features.none),
    ('mātou', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.speaker + Word.features.plural, Word.features.none),
    ('koutou', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.listener + Word.features.plural, Word.features.none),
    ('rātou', True, Word.features.none, Word.features.pronoun + Word.features.personal + Word.features.other + Word.features.plural, Word.features.none),

    ('tahi', True, Word.features.none, Word.features.number, Word.features.none),
    ('rua', True, Word.features.none, Word.features.number, Word.features.none),
    ('toru', True, Word.features.none, Word.features.number, Word.features.none),
    ('whā', True, Word.features.none, Word.features.number, Word.features.none),
    ('rima', True, Word.features.none, Word.features.number, Word.features.none),
    ('ono', True, Word.features.none, Word.features.number, Word.features.none),
    ('whitu', True, Word.features.none, Word.features.number, Word.features.none),
    ('waru', True, Word.features.none, Word.features.number, Word.features.none),
    ('iwa', True, Word.features.none, Word.features.number, Word.features.none),
    ('ngā', True, Word.features.none, determiner + Word.features.plural, Word.features.none),
    ('n', True, Word.features.possessive, causative + Word.features.past + Word.features.preposition, Word.features.determiner + Word.features.plural),
    ('me', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('m', True, Word.features.possessive, causative, Word.features.determiner + Word.features.plural),
    ('ā', True, Word.features.none, alienable + Word.features.determiner + Word.features.plural, Word.features.none),
    ('ō', True, Word.features.none, Word.features.possessive + Word.features.determiner + Word.features.plural, Word.features.none),
    ('i', True, Word.features.none, Word.features.past + Word.features.preposition + Word.features.tense, Word.features.none),
    ('te', True, Word.features.none, determiner, Word.features.none),
    ('t', True, Word.features.determiner, Word.features.none, Word.features.plural),
    ('ē', True, Word.features.none, Word.features.demonstrative + Word.features.determiner + Word.features.plural, Word.features.none),
    ('wē', True, Word.features.none, Word.features.demonstrative + Word.features.determiner + Word.features.plural, Word.features.none),
    ('aua', True, Word.features.none, Word.features.demonstrative + Word.features.determiner + Word.features.plural, Word.features.none),
    ('kia', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('kua', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('ki', True, Word.features.none, goal, Word.features.none),
    ('ka', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('ana', True, Word.features.none, Word.features.determiner + Word.features.plural, Word.features.none),
    ('ai', True, Word.features.none, Word.features.conditional, Word.features.none),
    ('a', True, Word.features.none, possessive + personal, Word.features.none),
    ('ko', True, Word.features.none, Word.features.preposition, Word.features.none),
    ('e', True, Word.features.none, Word.features.preposition + Word.features.tense, Word.features.none),
    ('o', True, Word.features.none, Word.features.preposition + Word.features.possessive, Word.features.none),
    ('kei', True, Word.features.none, Word.features.preposition + Word.features.tense, Word.features.none),
    ('hei', True, Word.features.none, Word.features.preposition + Word.features.tense, Word.features.none),
    ('he', True, Word.features.none, Word.features.determiner, Word.features.none),
    ('reira', True, Word.features.none, Word.features.locative, Word.features.none),
    ('roto', True, Word.features.none, Word.features.locative, Word.features.none),
    ('runga', True, Word.features.none, Word.features.locative, Word.features.none),
    ('raro', True, Word.features.none, Word.features.locative, Word.features.none),
    ('waho', True, Word.features.none, Word.features.locative, Word.features.none),
    ('muri', True, Word.features.none, Word.features.locative, Word.features.none),
    ('mua', True, Word.features.none, Word.features.locative, Word.features.none),
    ('waenganui', True, Word.features.none, Word.features.locative, Word.features.none),
    ('rā', True, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('nei', True, Word.features.demonstrative, Word.features.none, Word.features.none),
    ('nā', True, Word.features.demonstrative, Word.features.none, Word.features.none),
]


class Phrase:
    def __init__(self):
        self.words = []
        self.features = np.copy(Word.features.none)
        self.base = None

    def __repr__(self):
        features = []
        for feature in Feature.features:
            i = Feature.features[feature]
            if self.features[i-1]:
                features.append('+' + feature)

        return f'Phrase(base={self.base}, words="{" ".join(self.words)}", {"".join(features)})'

    def append(self, word: Word, features, payload):
        self.words.append(word.text)
        self.features |= features

        # Set core lexical content of phrase
        if payload and not self.base:
            self.base = word.word

    '''
    Enable two phrases to be joined if optimistic matching fails.
    This erases the features of the failed phrase.
    '''
    def splice(self, phrase: 'Phrase'):
        self.words += phrase.words


class Sentence:
    def __init__(self, lexicon):
        self.phrases: list[Phrase] = []
        self.header = Header(lexicon)

    def terminate(self, phrase: Phrase):
        if phrase.words:
            self.phrases.append(phrase)
        
        return Phrase()
    
    def splice(self, phrase: Phrase, last, current):
        # Commit existing interpretation
        if not np.any(last & (Word.features.preposition | Word.features.determiner)):
            return self.terminate(phrase)
        
        # Interpretation as determiner is valid, continue
        if np.any(last & Word.features.preposition) and np.any(current & Word.features.determiner):
            return phrase
        
        # End of first phrase
        if not self.phrases:
            return self.terminate(phrase)
        
        # Do not splice across pause
        target = self.phrases[-1]
        if np.any(target.features & Word.features.pause):
            return self.terminate(phrase)
        
        # Amend interpretation given two sequential prepositions
        target.splice(phrase)
        return Phrase()

    
    def read(self, words: list[Word]):
        buffer = Phrase()
        last = Word.features.none
        for i, text in enumerate(words):
            # Fetch prefix semantics and apply punctuation
            signifier = text.word
            stem, prefix_features = self.header.enter(signifier)

            word_features = self.header.match(prefix_features, stem)

            # Incorporate determiner via pronoun unless previously specified
            if np.any(word_features & Word.features.pronoun) and not np.any(last & Word.features.determiner):
                word_features |= Word.features.determiner

            # Start new buffer when reading preposition
            is_preposition = np.any(word_features & Word.features.preposition)
            if is_preposition:
                buffer = self.splice(buffer, last, word_features)

            # Start new buffer when reading determiner, unless local to a preposition
            is_determiner = np.any(word_features & Word.features.determiner)
            if is_determiner and not np.any(last & Word.features.preposition):
                buffer = self.splice(buffer, last, word_features)
            
            # Append with punctuation features and identify as lexical payload
            is_anaphora = np.any(word_features & (Word.features.demonstrative | Word.features.pronoun))
            is_clitic = np.any(word_features & ~prefix_features)
            word_features |= text.features
            buffer.append(text, word_features, is_anaphora or is_clitic or not is_preposition and not is_determiner)

            # Suppress requirement for complement if possible
            if is_anaphora:
                word_features = word_features & ~Word.features.determiner

            # Splice on sentence terminator
            if np.any(word_features & Word.features.stop):
                buffer = self.splice(buffer, word_features, Word.features.none)
                return i
            
            # Otherwise terminate on pause
            if np.any(word_features & Word.features.pause):
                buffer = self.terminate(buffer)

            # If stem matches prefix, suppress local matching of prepositions
            if is_clitic:
                last = Word.features.none
            else:
                last = word_features

        self.terminate(buffer)
        return len(words)
    