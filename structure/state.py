from abc import abstractmethod
from structure.annotator import Annotator, AnnotatorFactory
from structure.formal import Logger, NonTerminal, SyntaxNode, Terminal


class Gloss:
    def __init__(self, gloss):
        self.gloss = [item for item in Gloss.parse_gloss(gloss)]

    def __str__(self):
        return '-'.join('.'.join(item) for item in self.gloss)

    @staticmethod
    def parse_gloss(gloss: str):
        for item in gloss.split('-'):
            yield set(item.split('.'))


class StateAnnotator(Annotator):
    @abstractmethod
    def preposed(self):
        pass

    @abstractmethod
    def is_demonstrative(self):
        pass

    @abstractmethod
    def base(self, marker: str):
        pass

    @abstractmethod
    def annotate(self):
        pass
    

class StateAnnotatorFactory(AnnotatorFactory):
    def create(self, node: SyntaxNode, logger: Logger):
        if not node:
            return None
        
        if isinstance(node, NonTerminal):
            return NonTerminalAnnotator(node.gloss, self.create(node.left), self.create(node.right), logger)
        elif isinstance(node, Terminal):
            return TerminalAnnotator(node, logger)
        
        raise TypeError


class NonTerminalAnnotator(StateAnnotator):
    def __init__(self, gloss: str, left: StateAnnotator, right: StateAnnotator, logger: Logger):
        self.gloss = gloss
        self.left = left
        self.right = right
        self.logger = logger

    def preposed(self):
        return None
    
    def is_demonstrative(self):
        return self.gloss == 'dem'

    def base(self, marker: str):
        if self.left.is_demonstrative():
            # We may not preserve both marker and base ordering, so we choose arbitrarily
            return [(marker, self.right.base(marker))] + self.left.annotate()
        elif self.left.preposed():
            # Preposed particles do not qualify as bases
            return self.right.base(marker)
        
        return self.left.base(marker)

    def annotate(self):
        if not self.left:
            # Marker is not yet identified
            return self.right.annotate()
        
        preposed = self.left.preposed()
        if preposed:
            # We have a non-zero-marked base
            return self.right.base(preposed)
        
        # We have a zero-marked base
        return self.base(None)


class TerminalAnnotator(StateAnnotator):
    def __init__(self, node: Terminal):
        self.gloss = [item for item in Gloss.parse_gloss(node.gloss)]
        self.text = node.text.lower().strip(',.!?"')

    def preposed(self):
        if len(self.gloss) > 1:
            # Particles are unanalysable
            return None
        
        gloss, = self.gloss
        if any(gloss.intersection({'part', 'anc', 'def'})):
            # Text corresponds to preposed particle labels
            return self.text
        
        return None
    
    def complex(self):
        if not len(self.gloss) > 1:
            return None
        
        final = self.gloss[-1]
        if not 'pron' in final:
            return None
        
        if '1s' in final:
            clitic = 'ku'
        elif '2s' in final:
            clitic = 'u'
        elif '3s' in final:
            clitic = 'na'
        else:
            raise KeyError(f'Clitic pronoun identified without expected classification: {self.gloss}')
        
        if not self.text.endswith(clitic):
            raise KeyError(f'Text {self.text} does not correspond to gloss {self.gloss}')
        
        return (self.text[:-len(clitic)], clitic)
    
    def is_demonstrative(self):
        return any('dem' in item for item in self.gloss)

    def base(self, marker: str):
        return [(marker, self.text)]

    def annotate(self):
        complex = self.complex()
        if complex:
            return [complex]
        
        return [None, self.text]
