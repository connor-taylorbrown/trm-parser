import numpy as np

from content import Feature, Word
from sentence.header import Header


class Phrase:
    def __init__(self):
        self.words = []
        self.features = np.copy(Word.features.none)

    def __repr__(self):
        features = []
        for feature in Feature.features:
            i = Feature.features[feature]
            if self.features[i-1]:
                features.append('+' + feature)

        return f'Phrase(words="{" ".join(self.words)}", {"".join(features)})'

    def append(self, word: Word, features):
        self.words.append(word.text)
        self.features |= features

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
        if not np.any(last & Word.features.preposition):
            return self.terminate(phrase)
        
        # Interpretation as determiner is valid, continue
        if np.any(current & Word.features.determiner):
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

            # Start new buffer when reading preposition
            word_features = self.header.match(prefix_features, stem)
            if np.any(word_features & Word.features.preposition):
                buffer = self.splice(buffer, last, word_features)

            # Start new buffer when reading determiner, unless local to a preposition
            if np.any(word_features & Word.features.determiner) and not np.any(last & Word.features.preposition):
                buffer = self.terminate(buffer)
            
            # Append with punctuation features and terminate if necessary
            word_features |= text.features
            buffer.append(text, word_features)
            if np.any(word_features & Word.features.pause):
                buffer = self.terminate(buffer)

            if np.any(word_features & Word.features.stop):
                return i

            # If stem matches prefix, suppress local matching of prepositions
            if not np.any(word_features & ~prefix_features):
                last = word_features
            else:
                last = Word.features.none

        self.terminate(buffer)
        return len(words)
    