from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from structure.annotator import AnnotatorFactory
from structure.state import StateAnnotatorFactory
from structure.pos import PartOfSpeechAnnotatorFactory
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

    @abstractmethod
    def annotate(self, factory: AnnotatorFactory):
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
    
    def annotate(self, factory):
        self.left = self.left.annotate(factory)
        self.right = self.right.annotate(factory)
        return self


class Interpreter(InterpretationNode):
    def __init__(self, id: int, utterance: Utterance, context):
        self.id = id
        self.utterance = utterance
        self.context = context
        self.logger = FunctionalLogger(id=self.id, **self.context)
        self.annotation = []

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
        score = 0
        for node in self.utterance.nodes:
            score += node.score()
            if 'part' in node.gloss:
                score += 1
        
        return score
    
    def prune(self):
        return self
    
    def structure(self):
        construction = Construction(self.utterance.nodes, self.logger)
        while construction.peek():
            component = construction.component()
            construction.append(component)
        
        return Interpreter(id=self.id, utterance=construction, context=self.context)
    
    def annotate(self, factory):
        for node in self.utterance.nodes:
            annotator = factory.create(node, self.logger)
            self.annotation.append(annotator.annotate())
        
        return self
    
    def branch(self, id):
        logger = FunctionalLogger(id=id, **self.context)
        return Interpreter(id, utterance=self.utterance.clone(logger), context=self.context)
    
    @staticmethod
    def create(builder: SyntaxBuilder, **context):
        logger = FunctionalLogger(id=0, **context)
        return Interpreter(id=0, utterance=builder.build(logger), context=context)
    

@dataclass
class ReviewerConfig:
    annotate: bool
    observations: bool


class Reviewer:
    def __init__(self, morphology: MorphologyGraph, syntax: SyntaxBuilder, config: ReviewerConfig):
        self.morphology = morphology
        self.syntax = syntax
        self.annotate = config.annotate
        self.observations = config.observations

    def read(self, text: str, **context):
        interpreter = Interpreter.create(self.syntax, **context)
        for word in text.split():
            glosses = self.morphology.gloss_affixes(word.lower().strip(',.?!"'))
            if not glosses:
                interpreter = interpreter.extend(word, '*')
            else:
                interpreter = interpreter.extend(word, *glosses)
        
        interpreter = interpreter.extend('', '#').structure().prune()
        if self.annotate:
            interpreter = interpreter.annotate(PartOfSpeechAnnotatorFactory())
        elif self.observations:
            interpreter = interpreter.annotate(StateAnnotatorFactory())

        return interpreter
    

def count(morphology: MorphologyGraph, utterance: str):
    product = 1
    words = utterance.split()
    for word in words:
        glosses = morphology.gloss_affixes(word.lower().strip('.,?!"'))
        if not len(glosses):
            continue

        product *= len(glosses)
    
    return product
