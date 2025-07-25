import argparse
from content import Word
from corpus import Conversation, TokenType
from query import FeatureQuery, TextQuery
from sentence.parser import Phrase, Sentence, lexicon
from mbc import display, parser, run
from summary import ConversationFormatter


class PhraseFormatter(ConversationFormatter):
    def print_text(self, text):
        return text


class SentenceQuery(TextQuery):
    def __init__(self, lexicon, features, end, base, text, format):
        self.lexicon = lexicon
        self.features = [FeatureQuery(f) for f in features]
        self.end = end
        self.base = base
        self.text = text
        self.format = format

    def match_buffer(self, buffer: list[Phrase]):
        queries = [i for i in self.features]
        for p in buffer:
            if queries and queries[0].match_word(p):
                queries.pop(0)
            
            if not queries:
                return True

    def apply(self, type, words: list[Word]):
        if not type == TokenType.content:
            return []
        
        result = []
        while len(words):
            sentence = Sentence(self.lexicon)
            n = sentence.read(words)
            
            for i, phrase in enumerate(sentence.phrases):
                if self.features and not self.features[0].match_word(phrase):
                    continue

                buffer = sentence.phrases[i:i+self.end]
                if self.match_buffer(buffer):
                    if self.format & 2:
                        result.append(buffer)
                    elif self.base:
                        result.append([self.format_text(p.base) for p in buffer])
                    elif self.text:
                        result.append([self.format_text(w) for p in buffer for w in p.words])
                    else:
                        result.append(' '.join(' '.join(p.words) for p in buffer))
            
            words = words[n+1:]

        return result
    
    def format_text(self, word):
        if not word:
            return '*'
        elif ' ' in word:
            return word.replace(' ', '-')
        else:
            return word
    

def show_base(conversations: list[Conversation]):
    for conversation in conversations:
        for turn in conversation.turns:
            for line in turn.text:
                n, (_, bases) = line
                print(conversation.document, n, *bases)
    

if __name__ == '__main__':
    parser.add_argument('-f', '--features', action='append', default=[])
    parser.add_argument('-e', '--end', type=int, default=1)
    parser.add_argument('-F', '--format', type=int, default=0)
    parser.add_argument('-b', '--base', action=argparse.BooleanOptionalAction)
    parser.add_argument('-T', '--text', action=argparse.BooleanOptionalAction)    

    args = parser.parse_args()

    query = SentenceQuery(lexicon, args.features, args.end, args.base, args.text, args.format)
    formatter = PhraseFormatter(args.format)
    
    conversations = run(args, query)
    if args.base:
        show_base(conversations)
    elif args.text:
        show_base(conversations)
    else:
        display(args, conversations, formatter)
