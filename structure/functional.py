

import argparse
import logging
import sys
from structure.formal import Node, NonTerminal, Sentence, SyntaxBuilder, Terminal
from structure.morphology import MorphologyBuilder, MorphologyGraph


logger = logging.getLogger()


class Reviewer:
    def __init__(self, sentence: Sentence):
        self.sentence = sentence
        self.branches: list[Reviewer] = []

    def read(self, text, glosses):
        if not glosses:
            return self.sentence.read('*', text)
        
        gloss, *alternatives = glosses
        if not alternatives:
            return self.sentence.read(gloss, text)
        
        for alternative in alternatives:
            branch = Reviewer(sentence=self.sentence.clone())
            branch.read(alternative, text)
            self.branches.append(branch)

    def broadcast(self, text, glosses):
        self.read(text, glosses)
        for branch in self.branches:
            branch.read(text, glosses)


class TreeWriter:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.lines = []

    def next_id(self):
        count = self.count
        self.count += 1
        return count
    
    def traverse(self, node: Node):
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
    
    def write(self, nodes: list[Node]):
        yield f'digraph {self.name} ' + '{'
        
        root = self.next_id()
        yield f' {root} [label="S"];'
        for node in nodes:
            yield f' {root} -> {self.traverse(node)};'
        
        for line in self.lines:
            yield line

        yield '}'


trees = []
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument("input", help="Input file path")
    parser.add_argument('-t', '--test', action='store_true')
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
    
    reviewer = Reviewer(syntax_builder.build())
    print(reviewer.sentence.ranking.ranks)
    print(reviewer.sentence.mapper.sums)

    for i, line in enumerate(sys.stdin):
        words = line.split()
        for word in words:
            glosses = morphology.gloss_affixes(word.lower())
            reviewer.broadcast(word, glosses)
        
        reviewer.broadcast('', {'#'})
        phrases = reviewer.sentence.flush()
        count = len(words)
        for node in phrases:
            count -= node.count()
        
        if count:
            raise Exception(f'Expected {len(words)}, got {len(words)-count}')
        
        trees += TreeWriter(f'S{i}').write(phrases)
        
    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line + '\n' for line in trees)
