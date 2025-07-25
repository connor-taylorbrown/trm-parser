from abc import ABC, abstractmethod
import re
from content import Word
from corpus import Conversation, Corpus, TokenType, Turn
from files import FileReader


class WordQuery(ABC):
    @abstractmethod
    def match_word(self, word):
        pass


class StringQuery(WordQuery):
    def __init__(self, query, word):
        self.query = query
        self.word = word

    def match_word(self, word):
        if not self.query:
            return True
        
        if self.word:
            return word.text == self.query
        
        return self.query in word.text


class FeatureQuery(WordQuery):
    term = re.compile(r'[+-][A-Za-z_]+')
    
    def __init__(self, features):
        self.features = FeatureQuery.parse(features)

    def match_word(self, word: Word):
        on, off = self.features
        return all(word.features & on == on) and all(word.features & ~off == word.features)
    
    @staticmethod
    def parse(query):
        on = Word.features.none
        off = Word.features.none
        while len(query):
            term = FeatureQuery.term.match(query).group()
            op, feature = term[0], term[1:]
            if op == '+':
                on += Word.features[feature]
            elif op == '-':
                off += Word.features[feature]

            query = query[len(term):]
        
        return on, off


class TextQuery:
    def __init__(self, query: list[WordQuery], buffer, trim, end):
        self.query = query
        self.trim = trim
        self.buffer = FeatureQuery(buffer) if buffer else None
        self.end = end

    def match_segment(self, segment):
        queries = [term for term in self.query]
        for word in segment:
            if not queries:
                return True
            
            if queries[0].match_word(word):
                queries.pop(0)
        
        return False

    def match_line(self, words):
        term = self.query[0]
        if not any(term.match_word(word) for word in words):
            return []
        
        if self.match_segment(words):
            return [words]
        
        return []
        
    def match_from(self, words):
        term = self.query[0]
        for i, word in enumerate(words):
            if not term.match_word(word):
                continue
            
            if not self.end:
                return [words[i:]]
            
            segment = words[i:i+self.end]
            if not self.match_segment(segment):
                continue

            return [segment] + self.match_from(words[i+1:])
        
        return []
    
    def match_buffer(self, words: list[Word]):
        buffer = []
        matched = True
        for i, word in enumerate(words):
            buffer.append(word)
            if not matched:
                matched = self.query.match_word(word)

            if not self.buffer.match_word(word):
                continue

            if matched and self.match_segment(buffer):
                return [buffer] + self.match_buffer(words[i+1:])
            
            buffer = []

        return []

    def apply(self, type, words: list[Word]):
        if not self.query and not self.buffer:
            return [words]
        
        if not type == TokenType.content:
            return []
        
        if self.buffer:
            return self.match_buffer(words)
        
        if not self.trim:
            return self.match_line(words)
        
        return self.match_from(words)


class DocumentQuery:
    def __init__(self, reader: FileReader, corpus: Corpus, query: TextQuery, type, speaker, date):
        self.reader = reader
        self.corpus = corpus
        self.query = query
        self.type = type
        self.speaker = speaker
        self.date = date
        
    def filter_turns(self, turns: list[Turn]):
        for turn in turns:
            included = Turn(turn.speaker)
            for line in turn.text:
                n, (t, v) = line
                if self.type and t != self.type:
                    continue

                if self.speaker and turn.speaker != self.speaker:
                    continue

                results = self.query.apply(t, v)
                for result in results:
                    included.add_text(n, (t, result))
            
            if len(included.text):
                yield included

    def read_conversations(self, label):
        lines = self.reader.read_file(label)
        return self.corpus.add_document(lines)

    def filter_conversations(self, label):
        for conversation in self.read_conversations(label):
            if self.date and self.date != conversation.parse_date():
                continue

            result = Conversation(conversation.document, conversation.date)
            for turn in self.filter_turns(conversation.turns):
                result.add_turn(turn)
            
            if len(result.turns):
                yield result

    def query_all(self):
        label = 1
        while True:
            try:
                for line in self.filter_conversations(label):
                    yield line

                label += 1
            except FileNotFoundError:
                break

    def goto_line(self, document, goto, range):
        def get_turns():
            for turn in conversation.turns:
                included = Turn(turn.speaker)
                for line in turn.text:
                    n, (t, v) = line
                    if n < goto - range:
                        continue
                    elif n > goto + range:
                        break

                    results = self.query.apply(t, v)
                    for result in results:
                        included.add_text(n, (t, result))
                
                if len(included.text):
                    yield included

        for conversation in self.read_conversations(document):
            result = Conversation(conversation.document, conversation.date)
            for turn in get_turns():
                result.add_turn(turn)
            
            if len(result.turns):
                yield result
