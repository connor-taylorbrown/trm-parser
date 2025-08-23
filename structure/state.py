from abc import abstractmethod
from structure.annotator import Annotator, AnnotatorFactory
from structure.formal import Logger, NonTerminal, SyntaxNode, Terminal
from structure.functional import Interpreter, Organiser
from structure.writer import InterpretationWriter, WriterFactory, write_line


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
    def complex(self):
        pass

    @abstractmethod
    def is_demonstrative(self):
        pass

    @abstractmethod
    def base(self, marker: list[str]):
        pass

    @abstractmethod
    def annotate(self):
        pass
    

class StateAnnotatorFactory(AnnotatorFactory):
    def create(self, node: SyntaxNode, logger: Logger):
        if not node:
            return None
        
        if isinstance(node, NonTerminal):
            return NonTerminalAnnotator(node.gloss, self.create(node.left, logger), self.create(node.right, logger), logger)
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

    def complex(self):
        return None
    
    def is_demonstrative(self):
        return self.gloss == 'dem'

    def base(self, marker: list[str]):
        if self.left.is_demonstrative():
            demonstrative, anchor = self.left.annotate()
            if isinstance(anchor, tuple):
                self.logger.info('Flattening demonstrative anchor %s', anchor)
                anchor, _ = anchor

            paradigm, referent = self.right.base(marker)
            return paradigm + demonstrative, (anchor, referent)
        
        preposed = self.left.preposed()
        if preposed:
            marker += [preposed]
            if not self.right:
                return marker, None
            
            # Preposed particles do not qualify as bases
            return self.right.base(marker)
        
        return self.left.base(marker)

    def annotate(self):
        if not self.left:
            # Marker is not yet identified
            return self.right.annotate()
        
        complex = self.left.complex()
        if complex:
            # Marker and base are single-item
            return complex
        
        preposed = self.left.preposed()
        if preposed:
            # We have a non-zero-marked base
            return self.right.base([preposed])
        
        # We have a zero-marked base
        return self.base([])


class TerminalAnnotator(StateAnnotator):
    def __init__(self, node: Terminal, logger: Logger):
        self.gloss = [item for item in Gloss.parse_gloss(node.gloss)]
        self.text = node.text.lower().strip(',.!?"')
        self.logger = logger

    def preposed(self):        
        gloss, *_ = self.gloss
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
        
        return ([self.text[:-len(clitic)]], clitic)
    
    def is_demonstrative(self):
        return any('dem' in item for item in self.gloss)

    def base(self, marker: list[str]):
        return (marker, self.text)

    def annotate(self):
        complex = self.complex()
        if complex:
            return complex
        
        preposed = self.preposed()
        if preposed:
            return ([preposed], None)
        
        return self.base([])
    
class StateWriter(InterpretationWriter):
    def __init__(self, line, marker: int, *context):
        self.line = line
        self.context = context
        self.marker = marker

    def traverse(self, node):
        def particles(phrases):
            for phrase in phrases:
                marker, _ = phrase
                for particle in marker:
                    yield particle

        if isinstance(node, Interpreter):
            return True, node.annotations
        
        elif not isinstance(node, Organiser):
            raise TypeError
        
        left_resolved, left = self.traverse(node.left)
        right_resolved, right = self.traverse(node.right)

        logger = node.logger
        if not left_resolved and not right_resolved:
            return False, None
        elif not left_resolved:
            return True, right
        elif not right_resolved:
            return True, left

        if len(left) == len(right) and all(a == b for a, b in zip(particles(left), particles(right))):
            logger.info('Identical interpretations, choosing arbitrarily')
            return True, left

        if len(left) != len(right):
            logger.info('Ambiguous interpretations: Minimising phrase count')
            return True, min(left, right, key=len)
        
        logger.info('Unable to resolve ambiguity: %s cannot be preferred to %s', left, right)
        return False, None
    
    def particles(self, annotations):
        for phrase in annotations:
            marker, _ = phrase
            yield '.'.join(marker[:self.marker])

    def bases(self, annotations):
        for phrase in annotations:
            _, bases = phrase
            if not bases:
                continue

            if isinstance(bases, str):
                yield bases
                continue
            
            for base in bases:
                yield base

    def write(self, node):
        def delimit(v, delimiter: str):
            return delimiter.join(i for i in v)
        
        resolved, annotations = self.traverse(node)
        if not resolved:
            return
        
        if self.marker:
            yield write_line(self.context, delimit(self.particles(annotations), '/'), delimit(self.bases(annotations), '/'), self.line)
        else:
            yield write_line(self.context, ''.join(str(annotation) for annotation in annotations), self.line)
    

class StateWriterFactory(WriterFactory):
    def __init__(self, marker: int):
        self.marker = marker

    def start(self, *context):
        if self.marker:
            return [','.join([
                *context[:-1],
                'Particles',
                'Bases',
                'Fragment'
            ]) + '\n']
        
        return [','.join([
            *context[:-1],
            'States',
            'Fragment'
        ]) + '\n']
    
    def create(self, *metadata) -> InterpretationWriter:
        _, line, *context = metadata
        return StateWriter(line, self.marker, *context)
