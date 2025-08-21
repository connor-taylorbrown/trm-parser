from collections import deque

from structure.formal import Logger, NonTerminal, SyntaxNode


class Construction:
    def __init__(self, queue: list[SyntaxNode], logger: Logger):
        self.queue = deque(queue)
        self.nodes = []
        self.logger = logger

    def append(self, node: SyntaxNode):
        self.nodes.append(node)

    def peek(self):
        if not self.queue:
            return None
        
        return self.queue[0]
    
    def dequeue(self):
        return self.queue.popleft()
    
    def repackage(self, label, part, subordinate):
        if subordinate.left:
            left = subordinate.left
            right = subordinate.right
        else:
            left = subordinate.right
            right = None

        return NonTerminal(
            '$',
            part,
            NonTerminal(
                label,
                left,
                right
            )
        )
    
    def counterfactual(self):
        token = self.peek()
        if not token:
            return
        
        if token.gloss != 'part.me':
            return
        
        part = self.dequeue()
        token = self.peek()
        if not isinstance(token, NonTerminal):
            return part
        
        subordinate = self.dequeue()
        return self.repackage('pred', part, subordinate)

    def locative(self):
        token = self.peek()
        if not token:
            return
        
        if token.gloss != 'part.loc':
            return
        
        part = self.dequeue()
        token = self.peek()
        if not isinstance(token, NonTerminal):
            return part
        
        if not token.left:
            return part
        
        if token.left.gloss != 'part.poss':
            return part
        
        subordinate = self.dequeue()
        return self.repackage('poss', part, subordinate)

    def component(self):
        counterfactual = self.counterfactual()
        if counterfactual:
            return counterfactual
        
        locative = self.locative()
        if locative:
            return locative
        
        return self.dequeue()
