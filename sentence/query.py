from content import Word
from corpus import TokenType
from query import FeatureQuery, TextQuery
from sentence.parser import Sentence, lexicon
from mbc import parser, run
from summary import ConversationFormatter


class PhraseFormatter(ConversationFormatter):
    def print_text(self, text):
        return text


class SentenceQuery(TextQuery):
    def __init__(self, lexicon, features, end, format):
        self.lexicon = lexicon
        self.features = [FeatureQuery(f) for f in features]
        self.end = end
        self.format = format

    def match_buffer(self, buffer):
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
                    else:
                        result.append(' '.join(' '.join(p.words) for p in buffer))
            
            words = words[n+1:]

        return result
    

if __name__ == '__main__':
    parser.add_argument('-f', '--features', action='append', default=[])
    parser.add_argument('-e', '--end', type=int, default=1)
    parser.add_argument('-F', '--format', type=int, default=0)

    args = parser.parse_args()

    query = SentenceQuery(lexicon, args.features, args.end, args.format)
    formatter = PhraseFormatter(args.format)
    
    run(args, query, formatter)
