import argparse
from datetime import datetime
from corpus import Conversation, Corpus
from files import FileReader
from query import DocumentQuery, FeatureQuery, StringQuery, TextQuery
from summary import ConversationFormatter, Summary


reader = FileReader(name='MBC-raw/mbc{:03d}-not-stripped.txt', encoding='cp1252')
corpus = Corpus()

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--document', type=int)
parser.add_argument('-g', '--goto', type=int)
parser.add_argument('-r', '--range', type=int, default=0)

parser.add_argument('-s', '--summary', action=argparse.BooleanOptionalAction)
parser.add_argument('-a', '--all', action=argparse.BooleanOptionalAction)
parser.add_argument('-c', '--count')

parser.add_argument('-D', '--date', type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
parser.add_argument('-t', '--type', type=int)
parser.add_argument('-S', '--speaker')


def show_lines(formatter: ConversationFormatter, conversations: list[Conversation]):
    for conversation in conversations:
        for turn in conversation.turns:
            for line in turn.text:
                n, text = line
                print(conversation.document, n, formatter.format_date(conversation), turn.speaker, formatter.print_text(text))


def run(args, query: TextQuery, formatter: ConversationFormatter):
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

    summary = Summary(
        formatter=formatter,
        conversations=conversations,
        all=args.all,
        count=args.count
    )
    if args.summary:
        summary.show()
    else:
        show_lines(formatter, conversations)


if __name__ == '__main__':
    parser.add_argument('-F', '--format', type=int, default=0)
    parser.add_argument('-q', '--query', action='append')
    parser.add_argument('-f', '--features', action='append')
    parser.add_argument('-b', '--buffer')
    parser.add_argument('-w', '--word', action=argparse.BooleanOptionalAction)
    parser.add_argument('-x', '--exclude', action=argparse.BooleanOptionalAction)
    parser.add_argument('-e', '--end', type=int, default=0)
    
    args = parser.parse_args()
    if args.features:
        word_query = [FeatureQuery(f) for f in args.features]
    elif args.query:
        word_query = [StringQuery(q, args.word) for q in args.query]
    else:
        word_query = []
    
    query = TextQuery(
        query=word_query,
        trim=args.exclude,
        end=args.end,
        buffer=args.buffer
    )
    
    formatter = ConversationFormatter(format=args.format)
    run(args, query, formatter)
