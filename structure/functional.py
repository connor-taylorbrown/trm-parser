from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from structure.construction import Construction
from structure.formal import Logger, Utterance, SyntaxBuilder
from structure.morphology import MorphologyGraph


logger = logging.getLogger()


class FunctionalLogger(Logger):
    def __init__(self, **context):
        self.context = context
    
    def info(self, message, *args):
        logger.info(message, *args, extra=self.context)


class InterpretationNode(ABC):
    @abstractmethod
    def extend(self, text: str, *glosses: str):
        pass

    @abstractmethod
    def score(self):
        pass

    @abstractmethod
    def prune(self):
        pass

    @abstractmethod
    def structure(self):
        pass


@dataclass
class Organiser(InterpretationNode):
    id: int
    left: InterpretationNode
    right: InterpretationNode
    logger: Logger

    def __len__(self):
        return min(len(self.left), len(self.right))

    def extend(self, text, *glosses):
        self.left = self.left.extend(text, *glosses)
        self.right = self.right.extend(text, *glosses)
        return self
    
    def score(self):
        return min(self.left.score(), self.right.score()) + len(self)
    
    def prune(self):
        self.left = self.left.prune()
        self.right = self.right.prune()

        left, right = self.left.score(), self.right.score()
        self.logger.info('Pruning nodes: %s-%s score', left, right)
        if left < right:
            return self.left
        if right < left:
            return self.right
        
        return self
    
    def structure(self):
        self.left = self.left.structure()
        self.right = self.right.structure()
        return self


class Interpreter(InterpretationNode):
    def __init__(self, id: int, utterance: Utterance, context):
        self.id = id
        self.utterance = utterance
        self.context = context
        self.logger = FunctionalLogger(id=self.id, **self.context)

    def __len__(self):
        return len(self.utterance.nodes)

    def extend(self, text, *glosses):
        gloss, *alternatives = glosses
        if alternatives:
            self.logger.info('Branching interpretations on ambiguous token %s', text)
            return Organiser(
                id=self.id,
                left=self.branch(2 * self.id).extend(text, gloss),
                right=self.branch(2 * self.id + 1).extend(text, *alternatives),
                logger=self.logger
            )
        
        self.utterance.extend(gloss, text)
        return self
    
    def score(self):
        return sum(node.score() for node in self.utterance.nodes)
    
    def prune(self):
        return self
    
    def structure(self):
        construction = Construction(self.utterance.nodes, self.logger)
        while construction.peek():
            component = construction.component()
            construction.append(component)
        
        return Interpreter(id=self.id, utterance=construction, context=self.context)
    
    def branch(self, id):
        logger = FunctionalLogger(id=id, **self.context)
        return Interpreter(id, utterance=self.utterance.clone(logger), context=self.context)
    
    @staticmethod
    def create(builder: SyntaxBuilder, **context):
        logger = FunctionalLogger(id=0, **context)
        return Interpreter(id=0, utterance=builder.build(logger), context=context)


class Reviewer:
    def __init__(self, morphology: MorphologyGraph, syntax: SyntaxBuilder, structure: bool):
        self.morphology = morphology
        self.syntax = syntax
        self.structure = structure

    def read(self, text: str, **context):
        interpreter = Interpreter.create(self.syntax, **context)
        for word in text.split():
            glosses = self.morphology.gloss_affixes(word.lower().strip(',.?!"'))
            if not glosses:
                interpreter = interpreter.extend(word, '*')
            else:
                interpreter = interpreter.extend(word, *glosses)
        
        interpreter = interpreter.extend('', '#')
        if self.structure:
            interpreter = interpreter.structure()
        
        return interpreter.prune()
    

def count(morphology: MorphologyGraph, line: str):
    product = 1
    doc, line, *words = line.split()
    for word in words:
        glosses = morphology.gloss_affixes(word.lower().strip('.,?!"'))
        if not len(glosses):
            continue

        product *= len(glosses)
    
    return doc, line, product, ' '.join(words)
