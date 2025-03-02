from corpus import Conversation, Corpus, Turn
from files import FileReader


class DocumentQuery:
    def __init__(self, reader: FileReader, corpus: Corpus, type, speaker, date, query):
        self.reader = reader
        self.corpus = corpus
        self.type = type
        self.speaker = speaker
        self.date = date
        self.query = query

    def filter_turns(self, turns: list[Turn]):
        for turn in turns:
            result = Turn(turn.speaker)
            for line in turn.text:
                _, (t, v) = line
                if self.type and t != self.type:
                    continue

                if self.speaker and turn.speaker != self.speaker:
                    continue

                if self.query and self.query not in v:
                    continue
                
                result.add_text(*line)
            
            if len(result.text):
                yield result

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
