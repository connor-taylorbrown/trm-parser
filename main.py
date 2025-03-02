import argparse
from datetime import datetime
from corpus import Conversation, Corpus
from files import FileReader
from query import DocumentQuery


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


def show_lines(conversations: list[Conversation], format):
    for conversation in conversations:
        for turn in conversation.turns:
            for line in turn.text:
                n, text = line
                print(conversation.document, n, format_date(conversation, format), turn.speaker, text)


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--document', type=int)
parser.add_argument('-g', '--goto', type=int)
parser.add_argument('-t', '--type', type=int)
parser.add_argument('-r', '--range', type=int, default=0)
parser.add_argument('-s', '--summary', action=argparse.BooleanOptionalAction)
parser.add_argument('-a', '--all', action=argparse.BooleanOptionalAction)
parser.add_argument('-F', '--format', action=argparse.BooleanOptionalAction)
parser.add_argument('-D', '--date', type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
parser.add_argument('-S', '--speaker')
parser.add_argument('-q', '--query')

args = parser.parse_args()

query = DocumentQuery(
    reader=reader,
    corpus=corpus,
    type=args.type,
    speaker=args.speaker,
    date=args.date,
    query=args.query
)
if not args.document:
    conversations = query.query_all()
elif args.goto:
    conversations = query.goto_line(args.document, args.goto, args.range)
else:
    conversations = query.filter_conversations(args.document)

if args.summary:
    show_summary(conversations, args.all, args.format)
else:
    show_lines(conversations, args.format)
