import argparse
import sys

from structure.formal import SyntaxBuilder
from structure.functional import Reviewer, count
from structure.morphology import MorphologyBuilder, MorphologyGraph
from structure.writer import DotWriterFactory, GlossWriterFactory, InterpretationWriter


def read_header(header: str):
    if header:
        return header.split(',')

    return sys.stdin.readline().strip().split(',')


def read_line(header: list[str]):
    offset = header.index('Fragment')
    for line in sys.stdin:
        data = line.split(',')
        context, utterance = data[:offset], data[offset:]
        yield ','.join(utterance), *context


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument('-g', '--grammar', help="Path to grammar")
    parser.add_argument('-H', '--header', help='Define header and treat first row as data')
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('-a', '--annotate', action='store_true')
    parser.add_argument('-G', '--gloss', action='store_true')
    parser.add_argument('-L', '--lower', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    morphology = MorphologyGraph()
    syntax_builder = SyntaxBuilder()
    morphology_builder = MorphologyBuilder(morphology, test=args.test)
    with open(args.grammar, 'r') as f:
        for line in f.readlines():
            line = syntax_builder.parse(line)
            if not line:
                continue

            morphology_builder.parse(line)
    
    out = []
    reviewer = Reviewer(morphology, syntax_builder, args.annotate)
    if args.gloss:
        writer = GlossWriterFactory()
    else:
        writer = DotWriterFactory()
    
    header = read_header(args.header)
    if args.verbose:
        print(f'Using header: {header}')
    
    out += writer.start(*header)
    for line, *context in read_line(header):
        if args.verbose:
            print(*context, line, sep=',')

        id = context[header.index('ID')]
        if args.lower:
            line = line.replace(line[0], line[0].lower(), 1)

        if args.count:
            product = count(morphology, line)
            print(*context, product, line, sep=',')
            continue
        
        interpretation = reviewer.read(line, line=id)
        out += InterpretationWriter(id, writer.create(line, *context)).write(interpretation)

    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line for line in out)