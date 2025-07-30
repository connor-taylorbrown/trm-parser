import argparse
import sys

from structure.formal import SyntaxBuilder
from structure.functional import Reviewer, count
from structure.morphology import MorphologyBuilder, MorphologyGraph
from structure.writer import DotWriterFactory, GlossWriterFactory, InterpretationWriter


def read_line(header):
    for i, line in enumerate(sys.stdin):
        document, speaker, id, *utterance = line.split(',')
        if i or header:
            yield document, speaker, id, ','.join(utterance)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument('-g', '--grammar', help="Path to grammar")
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('-s', '--structure', action='store_true')
    parser.add_argument('-a', '--annotate', action='store_true')
    parser.add_argument('-G', '--gloss', action='store_true')
    parser.add_argument('-H', '--header', action='store_true')
    parser.add_argument('-L', '--lower', action='store_true')
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
    reviewer = Reviewer(morphology, syntax_builder, args.structure, args.annotate)
    if args.gloss:
        writer = GlossWriterFactory()
    else:
        writer = DotWriterFactory()
    
    out += writer.start()
    for document, speaker, id, line in read_line(args.header):
        if args.lower:
            line = line.replace(line[0], line[0].lower(), 1)

        if args.count:
            product = count(morphology, line)
            print(document, speaker, id, product, line, sep=',')
            continue
        
        interpretation = reviewer.read(line, line=id)
        out += InterpretationWriter(id, writer.create(document, speaker, id, line)).write(interpretation)

    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line for line in out)