from abc import ABC, abstractmethod
import argparse
from dataclasses import dataclass
import logging
import sys
from structure.formal import SyntaxNode, NonTerminal, Utterance, SyntaxBuilder, Terminal
from structure.morphology import MorphologyBuilder, MorphologyGraph


logger = logging.getLogger()


class InterpretationNode(ABC):
    @abstractmethod
    def extend(self, text: str, *glosses: str):
        pass


@dataclass
class Organiser(InterpretationNode):
    id: int
    left: InterpretationNode
    right: InterpretationNode

    def extend(self, text, *glosses):
        self.left = self.left.extend(text, *glosses)
        self.right = self.right.extend(text, *glosses)
        return self


class Interpreter(InterpretationNode):
    def __init__(self, id: int, utterance: Utterance, context):
        self.id = id
        self.utterance = utterance
        self.context = context

    def extend(self, text, *glosses):
        gloss, *alternatives = glosses
        if alternatives:
            return Organiser(
                id=self.id,
                left=Interpreter(id=2 * self.id, utterance=self.utterance.clone(), context=self.context).extend(text, gloss),
                right=Interpreter(id=2 * self.id + 1, utterance=self.utterance.clone(), context=self.context).extend(text, *alternatives),
            )
        
        self.utterance.extend(gloss, text, id=self.id, **self.context)
        return self


class Reviewer:
    def __init__(self, morphology: MorphologyGraph, syntax: SyntaxBuilder):
        self.morphology = morphology
        self.syntax = syntax

    def read(self, text: str, **context):
        interpreter = Interpreter(id=0, utterance=self.syntax.build(), context=context)
        for word in text.split():
            glosses = morphology.gloss_affixes(word.lower())
            if not glosses:
                interpreter = interpreter.extend(word, '*')
            else:
                interpreter = interpreter.extend(word, *glosses)
        
        return interpreter.extend('', '#')
    

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


def count(morphology: MorphologyGraph, line: str):
    product = 1
    doc, line, *words = line.split()
    for word in words:
        glosses = morphology.gloss_affixes(word.lower().strip('.,?!"'))
        if not len(glosses):
            continue

        product *= len(glosses)
    
    return doc, line, product, ' '.join(words)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument("input", help="Input file path")
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    morphology = MorphologyGraph()
    syntax_builder = SyntaxBuilder()
    morphology_builder = MorphologyBuilder(morphology, test=args.test)
    with open(args.input, 'r') as f:
        for line in f.readlines():
            line = syntax_builder.parse(line)
            if not line:
                continue

            morphology_builder.parse(line)
    
    trees = []
    reviewer = Reviewer(morphology, syntax_builder)
    for i, line in enumerate(sys.stdin):
        if args.count:
            print(' '.join(str(i) for i in count(morphology, line)))
        else:
            interpretation = reviewer.read(line, line=i+1)
            trees += InterpretationWriter(f'S{i}').write(interpretation)

    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line + '\n' for line in trees)
