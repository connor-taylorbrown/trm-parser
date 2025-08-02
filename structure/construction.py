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
    
    def counterfactual(self):
        token = self.peek()
        if not token:
            return
        
        if token.gloss != 'part.me':
            return
        
        part = self.dequeue()
        token = self.peek()
        if not isinstance(token, NonTerminal):
            return
        
        subordinate = self.dequeue()
        return NonTerminal(
            '$',
            part,
            NonTerminal(
                'pred',
                subordinate.left,
                subordinate.right
            )
        )


    def locative(self):
        token = self.peek()
        if not token:
            return
        
        if token.gloss != 'part.loc':
            return
        
        part = self.dequeue()
        token = self.peek()
        if not isinstance(token, NonTerminal):
            return
        
        if not token.left:
            return
        
        if token.left.gloss != 'part.poss':
            return
        
        subordinate = self.dequeue()
        return NonTerminal(
            '$',
            part,
            NonTerminal(
                'poss',
                subordinate.left,
                subordinate.right
            )
        )

    def component(self):
        counterfactual = self.counterfactual()
        if counterfactual:
            return counterfactual
        
        locative = self.locative()
        if locative:
            return locative
        
        return self.dequeue()
