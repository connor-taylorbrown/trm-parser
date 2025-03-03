import argparse
from datetime import datetime
from corpus import Conversation, Corpus, TokenType
from files import FileReader
from query import DocumentQuery, TextQuery


reader = FileReader(name='MBC-raw/mbc{:03d}-not-stripped.txt', encoding='cp1252')
corpus = Corpus()


def format_date(conversation: Conversation, format):
    if format:
        return conversation.parse_date()
    else:
        return conversation.date


def summarise_conversations(conversations: list[Conversation], format):
    for conversation in conversations:
        summary = conversation.summarise()

        yield conversation.document, format_date(conversation, format), len(conversation.turns), len(summary), summary


def summarise_all(conversations: list[Conversation]):
    all = {}
    for conversation in conversations:
        summary = conversation.summarise()
        for speaker in summary:
            running = all.get(speaker)
            if not running:
                all[speaker] = 0
            
            all[speaker] += summary[speaker]
    
    for k in all:
        yield all[k], k


def show_summary(conversations, all, format):
    if all:
        lines = summarise_all(conversations)
    else:
        lines = summarise_conversations(conversations, format)
    
    for line in lines:
        print(*line)


def print_text(text):
    t, v = text
    if t == TokenType.content:
        return (t, ' '.join(word.text for word in v))
    
    return text


def show_lines(conversations: list[Conversation], format):
    for conversation in conversations:
        for turn in conversation.turns:
            for line in turn.text:
                n, text = line
                print(conversation.document, n, format_date(conversation, format), turn.speaker, print_text(text))


parser = argparse.ArgumentParser()
parser.add_argument('-F', '--format', action=argparse.BooleanOptionalAction)
parser.add_argument('-d', '--document', type=int)
parser.add_argument('-g', '--goto', type=int)
parser.add_argument('-r', '--range', type=int, default=0)

parser.add_argument('-s', '--summary', action=argparse.BooleanOptionalAction)
parser.add_argument('-a', '--all', action=argparse.BooleanOptionalAction)

parser.add_argument('-D', '--date', type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
parser.add_argument('-t', '--type', type=int)
parser.add_argument('-S', '--speaker')

parser.add_argument('-q', '--query')
parser.add_argument('-w', '--word', action=argparse.BooleanOptionalAction)
parser.add_argument('-x', '--exclude', action=argparse.BooleanOptionalAction)
parser.add_argument('-e', '--end', type=int, default=0)

args = parser.parse_args()

query = TextQuery(
    query=args.query,
    word=args.word,
    trim=args.exclude,
    end=args.end
)

documents = DocumentQuery(
    reader=reader,
    corpus=corpus,
    query=query,
    type=args.type,
    speaker=args.speaker,
    date=args.date
)
if not args.document:
    conversations = documents.query_all()
elif args.goto:
    conversations = documents.goto_line(args.document, args.goto, args.range)
else:
    conversations = documents.filter_conversations(args.document)

if args.summary:
    show_summary(conversations, args.all, args.format)
else:
    show_lines(conversations, args.format)
