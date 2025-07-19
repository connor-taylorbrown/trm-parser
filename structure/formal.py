from dataclasses import dataclass
from structure.morphology import MorphologyGraph


@dataclass
class Node:
    item_type: str


@dataclass
class Terminal(Node):
    gloss: str
    text: str


@dataclass
class NonTerminal(Node):
    left: Node
    right: Node


class Sentence:
    def __init__(self, morphology: MorphologyGraph, positionality: dict[str, bool], default: str):
        self.morphology = morphology
        self.positionality = positionality
        self.default = default

        self.phrases: list[Node] = []
        self.branches: list['Sentence'] = []

    def gloss(self, text):
        glosses = set()
        for prefix in [True, False]:
            for gloss in self.morphology.gloss_affixes(text, prefix):
                if gloss in glosses:
                    continue

                glosses.add(gloss)
        
        return glosses
    
    def terminate(self, item_type):
        top = self.phrases[-1] if self.phrases else None
        if not top:
            # Can push first terminal
            return None
        
        if not top.item_type:
            # Can push after phrase
            return None
        
        constraints = self.preceding.get(item_type)
        if not constraints:
            # Can push in all contexts
            return None
        
        resolve, constraints = constraints
        if top.item_type in constraints:
            # Can push in this context
            return None
        
        # Resolve expression of chosen type
        return resolve
    
    def resolve(self, item_type):
        pass
    
    def read(self, text):
        glosses = self.gloss(text)
        if len(glosses) > 1:
            raise NotImplementedError('Ambiguous glosses not yet supported')
        elif not glosses:
            gloss = self.default
        else:
            gloss, = glosses

        item_type, *features = gloss.split('.')
        preposed, gloss = self.positionality[item_type], '.'.join(features)
        prior = self.terminate(item_type)
        if prior:
            self.resolve(prior)
        
        terminal = Terminal(
            item_type=item_type,
            gloss=gloss,
            text=text
        )
        if preposed:
            self.phrases.append(terminal)
        else:
            head = self.phrases.pop()
            self.phrases.append(NonTerminal(
                item_type=head.item_type,
                left=head,
                right=terminal
            ))
