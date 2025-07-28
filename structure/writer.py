from structure.formal import NonTerminal, SyntaxNode, Terminal
from structure.functional import InterpretationNode, Interpreter, Organiser


class IdGenerator:
    def __init__(self, prefix=''):
        self.prefix = prefix
        self.count = 0

    def next_id(self):
        count = self.count
        self.count += 1
        return self.prefix + str(count)


class InterpretationWriter:
    def __init__(self, name: str):
        self.name = name
        self.syntax_writer = SyntaxWriter(IdGenerator('n'))
        self.lines = []
    
    def traverse(self, node: InterpretationNode, level: int):
        if isinstance(node, Interpreter):
            id = f's{node.id}'
            for phrase in node.utterance.nodes:
                self.lines.append(f' {id} -> {self.syntax_writer.traverse(phrase)}')

            return id
        elif not isinstance(node, Organiser):
            raise TypeError
        
        id = node.id + 2 ** level - 1
        self.lines.append(f' {id} -> {self.traverse(node.left, level + 1)}')
        self.lines.append(f' {id} -> {self.traverse(node.right, level + 1)}')

        return id
    
    def write(self, node: InterpretationNode):
        yield f'digraph {self.name} ' + '{'
        
        self.traverse(node, level=0)
        for line in self.lines:
            yield line

        for line in self.syntax_writer.lines:
            yield line

        yield '}'


class SyntaxWriter:
    def __init__(self, ids: IdGenerator):
        self.ids = ids
        self.lines = []

    def next_id(self):
        return self.ids.next_id()
    
    def traverse(self, node: SyntaxNode):
        id = self.next_id()
        if isinstance(node, Terminal):
            self.lines.append(f' {id} [label=<<u>{node.text}/{node.gloss}</u>>];')
            return id
        elif not isinstance(node, NonTerminal):
            raise TypeError
        
        self.lines.append(f' {id} [label="{node.gloss}"];')
        if node.left:
            self.lines.append(f' {id} -> {self.traverse(node.left)};')
        
        if node.right:
            self.lines.append(f' {id} -> {self.traverse(node.right)};')
        
        return id
