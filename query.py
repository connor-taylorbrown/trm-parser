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
        return sum(word.features & on) > 0 and sum(word.features & ~off) > 0
    
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
    def __init__(self, query: WordQuery, trim, end):
        self.query = query
        self.trim = trim
        self.end = end

    def match_line(self, words):
        if any(self.query.match_word(word) for word in words):
            return [words]
        
        return []
    
    def match_section(self, words):
        if not self.end:
            return [words]
        
        return [words[:self.end]] + self.queries(words[1:])
        
    def queries(self, words):
        for i, word in enumerate(words):
            if not self.query.match_word(word):
                continue
            
            return self.match_section(words[i:])
        
        return []

    def apply(self, type, words: list[Word]):
        if not self.query:
            return [words]
        
        if not type == TokenType.content:
            return []
        
        if not self.trim:
            return self.match_line(words)
        
        return self.queries(words)


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
                result = Turn(turn.speaker)
                for line in turn.text:
                    n, text = line
                    if n < goto - range:
                        continue
                    elif n > goto + range:
                        break

                    result.add_text(n, text)
                
                if len(result.text):
                    yield result

        for conversation in self.read_conversations(document):
            result = Conversation(conversation.document, conversation.date)
            for turn in get_turns():
                result.add_turn(turn)
            
            if len(result.turns):
                yield result
