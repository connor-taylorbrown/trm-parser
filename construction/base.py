import numpy as np

from dataclasses import dataclass


@dataclass
class SyntaxNode:
    mat: np.ndarray

    def label(self):
        argmax = np.unravel_index(np.nanargmax(self.mat), self.mat.shape)
        return argmax, round(self.mat[argmax], 2)


@dataclass
class NonTerminal(SyntaxNode):
    left: SyntaxNode
    right: SyntaxNode

    def __str__(self):
        return f'({self.left} {self.right})/{self.label()}'


@dataclass
class Terminal(SyntaxNode):
    phrase: str

    def __str__(self):
        return f'{self.phrase}/{self.label()}'


class Construction:
    def __init__(self, ranking: dict[str, np.ndarray], tol: int):
        self.ranking = ranking
        self.tol = tol
        self.nodes = []

    def peek(self):
        return self.nodes[-1]

    def push(self, node: SyntaxNode):
        return self.nodes.append(node)
    
    def pop(self):
        return self.nodes.pop()
    
    def outranks(self, antecedent: SyntaxNode, terminal: Terminal):
        if terminal.phrase == '#':
            # Stop symbol
            return False
        
        diff = terminal.mat - antecedent.mat
        diff_predicate, diff_verb = diff[0], diff[:,0]
        return np.sum(diff_predicate) < -self.tol or np.sum(diff_verb) < -self.tol
    
    def merge(self, antecedent: SyntaxNode):
        head = self.pop()
        self.push(NonTerminal(head.mat, head, antecedent))
        return head
    
    def resolve(self, terminal: Terminal):
        antecedent = self.pop()
        if not self.nodes:
            self.push(antecedent)
            if terminal.phrase == '#':
                return
            
            # Utterance begins with inversion, push new head
            return self.push(terminal)
        
        head = self.merge(antecedent)
        if self.outranks(head, terminal):
            return self.push(terminal)
        
        return self.resolve(terminal)

    def read(self, phrase: str):
        if phrase == '#':
            terminal = Terminal(None, phrase)
        else:
            terminal = Terminal(self.ranking[phrase], phrase)

        if not self.nodes:
            return self.push(terminal)
        
        antecedent = self.peek()
        if self.outranks(antecedent, terminal):
            return self.push(terminal)
        
        return self.resolve(terminal)
    
    def flush(self):
        node = self.pop()
        if self.nodes:
            raise ValueError
        
        return node
