from structure.formal import NonTerminal, SyntaxNode, Terminal
from structure.functional import InterpretationNode, Interpreter, Organiser
from structure.writer import InterpretationWriter, WriterFactory, write_line


class QtreeWriter(InterpretationWriter):
    def __init__(self, id, line):
        self.id = id
        self.line = line

    def traverse_syntax(self, node: SyntaxNode):
        def latex_print(gloss):
            if gloss == '$':
                return '\$'
            
            if gloss == '*':
                return '*'
            
            return f'\\textsc{{{gloss}}}'
        

        if isinstance(node, Terminal):
            return f'[.{latex_print(node.gloss)} {node.text} ]'
        
        elif not isinstance(node, NonTerminal):
            raise TypeError
        
        children = []
        if node.left:
            children.append(self.traverse_syntax(node.left))
        
        if node.right:
            children.append(self.traverse_syntax(node.right))

        children = ' '.join(children)
        return f'[.{latex_print(node.gloss)} {children} ]'

    def traverse_interpretation(self, node: InterpretationNode):
        if isinstance(node, Organiser):
            return f'[.s{node.id} {self.traverse_interpretation(node.left)} {self.traverse_interpretation(node.right)} ]'
        elif isinstance(node, Interpreter):
            utterance = ' '.join(self.traverse_syntax(p) for p in node.utterance.nodes)
            return f'[.s{node.id} {utterance} ]'
        
        raise TypeError

    def write(self, node):
        yield ' '.join([self.id, self.line, self.traverse_interpretation(node)]) + '\n'


class QtreeWriterFactory(WriterFactory):
    def start(self, *_):
        return []
    
    def create(self, *metadata) -> InterpretationWriter:
        id, line, *_ = metadata
        return QtreeWriter(id, line)
