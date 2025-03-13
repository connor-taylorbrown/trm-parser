import numpy as np
from content import Word


class Header:
    def __init__(self, lexicon):
        self.lexicon = lexicon

    def enter(self, word: str):
        for signifier, expectation, effect, override in self.lexicon:
            # Identify a valid signifier
            prefix = word[:len(signifier)]
            if prefix.lower() != signifier:
                continue

            # Build full prefix, taking account of expected stem semantics
            effect = np.copy(effect)
            stem = word[len(signifier):]
            if np.any(expectation):
                stem, result = self.enter(stem)
                effect |= result
            
            # Ensure expectations are satisfied
            if not np.any(expectation & ~effect):
                return stem, effect & ~override
        
        return word, np.copy(Word.features.none)

    def match(self, conditions, stem: str):
        if not stem:
            return conditions
        
        for signifier, expectation, effect, override in self.lexicon:
            # Identify a valid signifier
            if stem.lower() != signifier:
                continue

            # Reject signifier if it does not match conditions
            if np.any(expectation & ~conditions):
                return np.copy(Word.features.none)
            
            # Build full word
            effect = np.copy(effect)
            effect |= conditions
            return effect & ~override
        
        return np.copy(Word.features.none)
