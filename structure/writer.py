from abc import ABC, abstractmethod
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


class SyntaxWriter(ABC):
    @abstractmethod
    def write_terminal(self, id: str, terminal: Terminal):
        pass

    @abstractmethod
    def write_non_terminal(self, id: str, non_terminal: NonTerminal):
        pass

    @abstractmethod
    def write_edge(self, source: str, target: str):
        pass

    @abstractmethod
    def start(self, name: str):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def end(self):
        pass


class InterpretationWriter:
    def __init__(self, name: str, writer: SyntaxWriter):
        self.name = name
        self.syntax_writer = SyntaxVisitor(IdGenerator('n'), writer)
        self.writer = writer
    
    def traverse(self, node: InterpretationNode, level: int):
        if isinstance(node, Interpreter):
            id = f's{node.id}'
            for phrase in node.utterance.nodes:
                self.writer.write_edge(id, self.syntax_writer.traverse(phrase))

            return id
        elif not isinstance(node, Organiser):
            raise TypeError
        
        id = node.id + 2 ** level - 1
        self.writer.write_edge(id, self.traverse(node.left, level + 1))
        self.writer.write_edge(id, self.traverse(node.right, level + 1))

        return id
    
    def write(self, node: InterpretationNode):
        start = self.writer.start(self.name)
        if start:
            yield start
        
        self.traverse(node, level=0)
        for line in self.writer.read():
            yield line

        end = self.writer.end()
        if end:
            yield end


class SyntaxVisitor:
    def __init__(self, ids: IdGenerator, writer: SyntaxWriter):
        self.ids = ids
        self.writer = writer

    def next_id(self):
        return self.ids.next_id()
    
    def traverse(self, node: SyntaxNode):
        id = self.next_id()
        if isinstance(node, Terminal):
            self.writer.write_terminal(id, node)
            return id
        elif not isinstance(node, NonTerminal):
            raise TypeError
        
        self.writer.write_non_terminal(id, node)
        if node.left:
            self.writer.write_edge(id, self.traverse(node.left))
        
        if node.right:
            self.writer.write_edge(id, self.traverse(node.right))
        
        return id
    
    def read(self):
        return self.writer.read()
    

class DotWriter(SyntaxWriter):
    def __init__(self):
        self.lines = []

    def write_terminal(self, id, terminal):
        self.lines.append(f' {id} [label=<<u>{terminal.text}/{terminal.gloss}</u>>];')

    def write_non_terminal(self, id, non_terminal):
        self.lines.append(f' {id} [label="{non_terminal.gloss}"];')

    def write_edge(self, source, target):
        self.lines.append(f' {source} -> {target};')
    
    def start(self, name):
        return f'digraph "{name}" ' + '{' + '\n'
    
    def read(self):
        return [line + '\n' for line in self.lines]
    
    def end(self):
        return '}' + '\n'
    

class GlossWriter(SyntaxWriter):
    def __init__(self, document, speaker, id, line):
        self.document = document
        self.speaker = speaker
        self.id = id
        self.line = line
        self.items = []

    def write_terminal(self, id, terminal):
        self.items.append(terminal.gloss + '/')

    def write_non_terminal(self, id, non_terminal):
        if non_terminal.gloss == '$':
            self.items.append(non_terminal.gloss)

    def write_edge(self, source, target):
        return

    def start(self, name):
        return

    def read(self):
        return [','.join([
            self.document,
            self.speaker,
            self.id,
            ''.join(self.items).strip('/'),
            self.line
        ])]

    def end(self):
        return
    

class WriterFactory(ABC):
    @abstractmethod
    def start(self) -> str:
        pass

    @abstractmethod
    def create(self, utterance: str, *metadata: str) -> SyntaxWriter:
        pass


class DotWriterFactory(WriterFactory):
    def start(self):
        return []

    def create(self, *metadata):
        return DotWriter()
    

class GlossWriterFactory(WriterFactory):
    def start(self):
        return ["Document,Speaker,ID,Gloss,Utterance\n"]

    def create(self, *metadata):
        document, speaker, id, utterance = metadata
        return GlossWriter(document, speaker, id, utterance)
