from dataclasses import dataclass
import logging
import re
import sys
import argparse

from structure.morphology import MorphologyBuilder, MorphologyGraph


logger = logging.getLogger(__name__)


@dataclass
class Node:
    gloss: str


@dataclass
class Terminal(Node):
    text: str


@dataclass
class NonTerminal(Node):
    left: Node
    right: Node


def _split(token):
    return set(re.split(r'[.-]', token))


class Ranking:
    def __init__(self, ranks: dict[str, set]):
        self.ranks = ranks
    
    def outranks(self, antecedent, token):
        outranks = {j for i in _split(antecedent) for j in self.ranks.get(i, {})}
        return any(outranks.intersection(_split(token)))

class Mapper:
    def __init__(self, sums: list[tuple[set, str]]):
        self.sums = sums

    def add(self, antecedent, token):
        bag = _split(antecedent).union(_split(token))
        for sum, result in self.sums:
            if not sum - bag:
                return result
    

class Sentence:
    def __init__(self, ranking: Ranking, mapper: Mapper):
        self.nodes: list[Node] = []
        self.ranking = ranking
        self.mapper = mapper

    def push(self, node):
        if node.gloss != '#':
            self.nodes.append(node)
        
        return self

    def peek(self):
        return self.nodes[-1] if len(self.nodes) else None
    
    def pop(self):
        return self.nodes.pop()
    
    def merge(self, antecedent, next):
        if not self.peek():
            logger.info('Unable to merge %s before %s: stack empty', antecedent.gloss, next.gloss)
            return None

        head = self.peek()
        result = self.mapper.add(head.gloss, antecedent.gloss)
        if not result:
            logger.info('Unable to merge: no rule for %s + %s', head.gloss, antecedent.gloss)
            return None
        
        logger.info('Given %s + %s before %s, got %s', head.gloss, antecedent.gloss, next.gloss, result)
        return self.push(NonTerminal(result, self.pop(), antecedent))
        
    def promote(self, antecedent):
        if antecedent.gloss == '$':
            raise KeyError('Unable to promote')
        
        logger.info('Promoted %s', antecedent.gloss)
        return self.push(NonTerminal('$', antecedent, None))
    
    def resolve(self, next: Node):
        antecedent = self.pop()
        if not self.merge(antecedent, next):
            self.promote(antecedent)

        if self.ranking.outranks(self.peek().gloss, next.gloss):
            return self.push(next)
        
        return self.resolve(next)
    
    def read(self, gloss, text):
        terminal = Terminal(gloss, text)
        if not len(self.nodes):
            return self.push(terminal)
        
        if self.ranking.outranks(self.peek().gloss, terminal.gloss):
            return self.push(terminal)
    
        return self.resolve(terminal)
    

class SyntaxBuilder:
    def __init__(self):
        self.ranks = {}
        self.sums = []
    
    def parse(self, line: str):
        line = line.strip()
        if not line:
            return
        
        command = line.split()
        if command[0] == 'r':
            _, key, *outranked = command
            self.ranks[key] = set(outranked)
        elif command[0] == 's':
            _, gloss, *constituents = command
            self.sums.append((set(constituents), gloss))
        else:
            return line
    
    def build(self):
        return Sentence(
            ranking=Ranking(self.ranks),
            mapper=Mapper(self.sums))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument("input", help="Input file path")
    args = parser.parse_args()

    morphology = MorphologyGraph()
    syntax_builder = SyntaxBuilder()
    morphology_builder = MorphologyBuilder(morphology)
    with open(args.input, 'r') as f:
        for line in f.readlines():
            line = syntax_builder.parse(line)
            if not line:
                continue

            morphology_builder.parse(line)            
    
    syntax = syntax_builder.build()
    for line in sys.stdin:
        for word in line.split():
            gloss = morphology.gloss_affixes(word)
            if not gloss:
                gloss = '*'
            if len(gloss) > 1:
                print(f'Multiple glosses for {word}: not supported')
                continue
            
            gloss, = gloss
            syntax.read(gloss, word)
            print(syntax.nodes)

    print(syntax.nodes)
