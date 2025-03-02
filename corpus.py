from dataclasses import dataclass
from datetime import datetime
import re

from sentence import Sentence, read_sentences


@dataclass
class Token:
    pattern: re.Pattern
    type: int


class TokenType:
    text = 1
    meta = 2
    header = 3
    speaker = 4
    date = 5
    sentence = 6


class Turn:
    def __init__(self, speaker):
        self.speaker = speaker
        self.text = []
    
    def add_text(self, n, text):
        self.text.append((n, text))


class Conversation:
    def __init__(self, document, date):
        self.document = document
        self.date = date
        self.turns: list[Turn] = []

    def parse_date(self):
        if not self.date:
            return self.date
        
        date = self.date.split(' ')[0]
        day, month, *year = date.split('/')
        year = ''.join(year).strip(':')
        date = '-'.join([year, month, day])

        try:
            return datetime.strptime(date, '%y-%m-%d').date()
        except:
            return datetime.strptime(date, '%Y-%m-%d').date()

    def summarise(self):
        summary = {}
        for turn in self.turns:
            count = summary.get(turn.speaker)
            if not count:
                summary[turn.speaker] = 0
            
            summary[turn.speaker] += 1

        return summary
    
    def add_turn(self, turn):
        self.turns.append(turn)


class Corpus:
    meta = Token(pattern=re.compile(r'\{(.*?)}'), type=TokenType.meta)
    header = Token(pattern=re.compile(r'<<\s*([a-z0-9]*?)>>'), type=TokenType.header)
    speaker = Token(pattern=re.compile(r'<(.*?)[>\]]'), type=TokenType.speaker)
    date = Token(pattern=re.compile(r'([0-9]{1,2}//?){2}[0-9]{2,4}'), type=TokenType.date)

    def read_pattern(self, rule: Token, line: str):
        if not line:
            return None, line
        
        line = line.lstrip()
        m = rule.pattern.match(line)
        if not m:
            return None, line
            
        return (rule.type, m.group(1).strip()), line[m.end():]
        
    def read(self, line):
        if not line or line.isspace():
            return []
        
        header, line = self.read_pattern(Corpus.header, line)
        if header:
            return [header] + self.read(line)
        
        meta, line = self.read_pattern(Corpus.meta, line)
        if meta:
            return [self.read_meta(meta)] + self.read(line)
        
        speaker, line = self.read_pattern(Corpus.speaker, line)
        if speaker:
            return [speaker] + self.read(line)

        return [(TokenType.text, line.rstrip())]
    
    def read_meta(self, meta):
        t, v = meta
        m = Corpus.date.pattern.match(v)
        if m:
            return Corpus.date.type, v
        
        return t, v
    
    def start_turn(self, speaker):
        return Turn(speaker)
    
    def end_turn(self, conversation: Conversation, turn: Turn):
        if len(turn.text):
            conversation.add_turn(turn)

    def start_conversation(self, document, date):
        return Conversation(document, date), Turn(None)

    def end_conversation(self, conversation: Conversation, turn: Turn):
        self.end_turn(conversation, turn)
        if len(conversation.turns):
            return conversation
        
    def add_document(self, lines):
        header = None
        turn = Turn(None)
        for n, line in enumerate(lines, 1):
            for token in self.read(line):
                t, v = token
                if t == Corpus.header.type:
                    header = v
                    conversation = Conversation(header, None)
                
                elif t == Corpus.date.type:
                    finished = self.end_conversation(conversation, turn)
                    if finished:
                        yield finished

                    conversation, turn = self.start_conversation(header, v)
                
                elif t == Corpus.speaker.type:
                    self.end_turn(conversation, turn)
                    turn = self.start_turn(v)
                
                elif t == Corpus.meta.type:
                    turn.add_text(n, token)
                
                else:
                    turn.add_text(n, token)

        if not header:
            conversation = Conversation(None, None)

        finished = self.end_conversation(conversation, turn)
        if finished:
            yield finished
