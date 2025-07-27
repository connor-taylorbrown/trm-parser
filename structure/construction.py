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
    
    def gloss(self, gloss, node):
        return NonTerminal(
            gloss,
            node.left,
            node.right
        )
    
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
            'cf',
            head,
            complement
        )
    
    def causative(self, head: SyntaxNode):
        if not isinstance(head, NonTerminal):
            return None
        
        part = head.left
        if part.includes({'o'}):
            return None
        
        past = part.includes({'r'})
        fut = part.includes({'irr'})
        if not past and not fut:
            return None
        
        actor = self.reference(head)
        subordinate = self.peek()
        if not isinstance(subordinate, NonTerminal):
            return self.gloss('caus', actor)
        
        self.logger.info('Reading possible subordinate %s of causative %s', subordinate.left, part)
        if subordinate.left.text == 'i' and not past:
            return self.gloss('caus', actor)
        
        if subordinate.left.text in {'hei', 'e'} and not fut:
            return self.gloss('caus', actor)
        
        return NonTerminal(
            'caus',
            actor,
            self.reference(self.dequeue())
        )
        
    def locative(self, head: SyntaxNode):
        if not isinstance(head, NonTerminal):
            return None
        
        if not head.includes({'loc'}):
            return None
        
        location = self.reference(head)
        anchor = self.peek()
        if not isinstance(anchor, NonTerminal):
            return self.gloss('loc', location)
        
        if not anchor.left.text == 'i':
            return self.gloss('loc', location)
        
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
