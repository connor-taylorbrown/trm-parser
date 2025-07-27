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

    def fetch(self, include, exclude):
        node = self.peek()
        if not node:
            return None
        
        if node.includes(exclude) or not node.includes(include):
            return None
        
        return self.dequeue()
    
    def subgroup(self):
        """Fetch phrase if valid subgroup reference"""
        phrase = self.peek()
        if not isinstance(phrase, NonTerminal):
            return None
        
        if not phrase.left.gloss == 'part.me':
            return None

        complement = phrase.right
        if complement.includes({'ref', 'dem', 'pron'}):
            return self.dequeue()
        
        if str(complement)[0].isupper():
            return self.dequeue()
    
    def join(self, head, complement):
        if not head:
            return complement
        
        return NonTerminal(head.gloss, head, complement)
    
    def reference(self, head):
        """Match topic, anchor, or subgroup references by phrasal form"""
        topic = self.fetch(include={'ref', 'dem', 'pron'}, exclude={'part', 'poss'})
        if topic:
            self.logger.info('Read topic "%s" at "%s"', topic.left, head)
            return self.join(
                head,
                self.reference(NonTerminal('top', None, topic.left))
            )
        
        anchor = self.fetch(include={'poss'}, exclude={'part'})
        if anchor:
            self.logger.info('Read anchor "%s" at "%s"', anchor.left, head)
            return self.join(
                head,
                self.reference(anchor.left)
            )
        
        subgroup = self.subgroup()
        if subgroup:
            self.logger.info('Read subgroup "%s" at "%s"', subgroup, head)
            return self.join(
                head,
                self.reference(NonTerminal('com', subgroup.left, subgroup.right))
            )
        
        return head
        
    def counterfactual(self, head):
        complement = self.component()
        if not complement:
            return head
        
        self.logger.info("Read complement of counterfactual %s", complement)
        return NonTerminal(
            complement.gloss,
            head,
            complement
        )
    
    def subordinate(self, part: SyntaxNode):
        phrase = self.peek()
        if not isinstance(phrase, NonTerminal):
            return None
        
        if part.includes({'r'}) and phrase.left.text != 'i':
            return None
        
        if phrase.left.text not in {'hei', 'e'}:
            return None
        
        return self.reference(self.dequeue())
    
    def causative(self, head: SyntaxNode):
        if not isinstance(head, NonTerminal):
            return None
        
        part = head.left
        if not part.includes({'r', 'irr'}) or part.includes({'o'}):
            return None
        
        actor = self.reference(head)
        subordinate = self.subordinate(part)
        if subordinate:
            return NonTerminal(
                'ae',
                actor,
                subordinate
            )
        
        return actor
    
    def locative(self, head: SyntaxNode):
        if not isinstance(head, NonTerminal):
            return None
        
        if not head.includes({'loc'}):
            return None
        
        location = self.reference(head)
        anchor = self.peek()
        if not isinstance(anchor, NonTerminal):
            return location
        
        if not anchor.left.text == 'i':
            return location
        
        return NonTerminal(
            'loc',
            location,
            self.reference(self.dequeue())
        )
    
    def component(self):
        """Match counterfactual expression, reference expression, or argument expression"""
        if not self.peek():
            return None
        
        phrase = self.dequeue()
        if phrase.gloss == 'part.me':
            return self.counterfactual(phrase)
        
        causative = self.causative(phrase)
        if causative:
            self.logger.info("Read causative %s", causative)
            return causative
        
        locative = self.locative(phrase)
        if locative:
            self.logger.info("Read locative %s", locative)
            return locative
        
        reference = self.reference(phrase)
        if reference:
            self.logger.info("Read reference %s", reference)
            return reference
        
        return phrase
