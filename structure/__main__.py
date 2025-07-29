import argparse
import sys

from structure.formal import SyntaxBuilder
from structure.functional import Reviewer, count
from structure.morphology import MorphologyBuilder, MorphologyGraph
from structure.writer import InterpretationWriter


def read_line():
    for i, line in enumerate(sys.stdin):
        document, speaker, id, *utterance = line.split(',')
        if i:
            yield document, speaker, id, ','.join(utterance)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument('-g', '--grammar', help="Path to grammar")
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('-s', '--structure', action='store_true')
    parser.add_argument('-a', '--annotate', action='store_true')
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
    
    trees = []
    reviewer = Reviewer(morphology, syntax_builder, args.structure, args.annotate)
    for document, speaker, id, line in read_line():
        if args.count:
            product = count(morphology, line)
            print(document, speaker, id, product, line, sep=',')
            continue
        
        interpretation = reviewer.read(line, line=id)
        trees += InterpretationWriter(id).write(interpretation)

    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line + '\n' for line in trees)