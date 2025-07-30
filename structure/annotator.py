from abc import ABC, abstractmethod
from structure.formal import Logger, SyntaxNode, NonTerminal, Terminal


class Annotator(ABC):
    @abstractmethod
    def match(self, text: str):
        pass

    @abstractmethod
    def classify(self, *modifier: str):
        pass

    @abstractmethod
    def annotate(self):
        pass

    @staticmethod
    def create(node: SyntaxNode, logger: Logger):
        if not node:
            return None
        
        if isinstance(node, NonTerminal):
            return NonTerminalAnnotator(node, logger)
        elif isinstance(node, Terminal):
            return TerminalAnnotator(node, logger)
        
        raise TypeError


class TerminalAnnotator(Annotator):
    def __init__(self, node: Terminal, logger: Logger):
        self.node = node
        self.logger = logger

    @property
    def gloss(self):
        return self.node.gloss
    
    @gloss.setter
    def gloss(self, value):
        self.node.gloss = value

    @property
    def text(self):
        return self.node.text

    def match(self, text: str):
        if text == self.text:
            return text

    def classify(self, *modifier):
        if self.text.lower() in {'e', 'me'} and 'te' in modifier:
            self.logger.info('Nominal usage selected by "te" for %s', self.text)
            return None, 'N'
        
        if self.text.lower() in {'kei'} and 'te' in modifier:
            self.logger.info('Verbal usage selected by "te" for %s', self.text)
            return None, 'V'
        
        if self.text.lower() in {'a', 'o', 'ko', 'he'} or self.node.includes({'r', 'irr'}):
            self.logger.info('Nominal interpretation selected by particle %s', self.text)
            return None, 'N'
        
        if self.text.lower() in {'i', 'ki', 'kei', 'hei'}:
            return None, None
        
        if self.node.includes({'part'}):
            self.logger.info('Verbal interpretation selected by default, given particle %s', self.text)
            return None, 'V'
        
        if self.text[0].isupper():
            self.logger.info('Nominal interpretation favoured by capitalisation of "%s"', self.text)
            return None, 'N'
        
        return None, None
    
    def apply(self, label):
        """Apply and update label to ensure appropriate annotation of modifiers"""
        if not '*' in self.gloss:
            return label
        
        self.gloss = self.gloss.replace('*', label)
        if label == 'N':
            return 'Adj'
        
        if label == 'V':
            return 'Adv'
        
        return label

    def annotate(self):
        return None


class NonTerminalAnnotator(Annotator):
    def __init__(self, node: NonTerminal, logger: Logger):
        self.node = node
        self.left = Annotator.create(node.left, logger)
        self.right = Annotator.create(node.right, logger)
        self.logger = logger

    @property
    def gloss(self):
        return self.node.gloss
    
    def match(self, text):
        return None

    def classify(self, *modifier):
        if self.gloss in {'ref', 'dem'}:
            return self.left.match('te'), 'N'
        
        if not self.right:
            return None, None
        
        maybe, annotation = self.right.classify()
        if annotation and not maybe:
            self.logger.info('Phrase classifiable as %s due to rhs=%s', annotation, self.right.gloss)
            return None, annotation
        
        if not self.left:
            self.logger.info('Phrase classifiable as %s due to missing particle', annotation)
            return None, annotation
        
        maybe, annotation = self.left.classify(maybe)
        if annotation and not maybe:
            self.logger.info('Phrase classifiable as %s due to lhs=%s', annotation, self.left.gloss)
            return None, annotation
        
        text = str(self.node).lower().split()
        if text[0] in {'e'} and text[-1] in {'ana', 'ai', 'nei', 'nā', 'rā'}:
            annotation = 'V'
            self.logger.info('Phrase classifiable as %s due to final modifiers', annotation)
            return None, 'V'
        
        return None, None
        
    def apply(self, label):        
        if self.left:
            if 'dem' in self.left.gloss:
                # Do not propagate changes to label beyond scope of demonstrative
                self.left.apply(label)
            else:
                label = self.left.apply(label)
        
        if self.right:
            return self.right.apply(label)

    def annotate(self):
        maybe, annotation = self.classify()
        if annotation and not maybe:
            self.apply(annotation)
