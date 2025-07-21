from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import re


logger = logging.getLogger()


@dataclass
class Node(ABC):
    gloss: str

    @abstractmethod
    def count(self):
        pass


@dataclass
class Terminal(Node):
    text: str

    def count(self):
        return 1


@dataclass
class NonTerminal(Node):
    left: Node
    right: Node

    def count(self):
        left = self.left.count() if self.left else 0
        right = self.right.count() if self.right else 0
        return left + right


def _split(token):
    return set(re.split(r'[.-]', token))


class Ranking:
    def __init__(self, ranks: dict[str, set]):
        self.ranks = ranks
    
    def outranks(self, antecedent, token):
        if antecedent == '$':
            return True
        
        outranks = {j for i in _split(antecedent) for j in self.ranks.get(i, {})}
        return any(outranks.intersection(_split(token)))

class Mapper:
    def __init__(self, sums: list[tuple[set, str]]):
        self.sums = sums

    def add(self, antecedent, token):
        if antecedent == '$':
            return
        
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
            logger.info('Unable to merge before %s: no rule for %s + %s', next.gloss, head.gloss, antecedent.gloss)
            return None
        
        logger.info('Given %s + %s before %s, got %s', head.gloss, antecedent.gloss, next.gloss, result)
        return self.push(NonTerminal(result, self.pop(), antecedent))
        
    def promote(self, antecedent):
        if antecedent.gloss == '$':
            raise KeyError('Unable to promote', self.nodes)
        
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
        logger.info('Read %s/%s', text, gloss)
        terminal = Terminal(gloss, text)
        if not len(self.nodes):
            return self.push(terminal)
        
        if self.ranking.outranks(self.peek().gloss, terminal.gloss):
            return self.push(terminal)
    
        return self.resolve(terminal)
    
    def flush(self):
        nodes = self.nodes
        self.nodes = []
        return nodes
    
    def clone(self):
        s = Sentence(
            ranking=self.ranking,
            mapper=self.mapper
        )

        s.nodes = self.nodes.copy()
        return s
    

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
