import argparse
import sys

from structure.formal import SyntaxBuilder
from structure.functional import Reviewer, count
from structure.morphology import MorphologyBuilder, MorphologyGraph
from structure.writer import InterpretationWriter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process linguistic input file.")
    parser.add_argument("input", help="Input file path")
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--count', action='store_true')
    parser.add_argument('-s', '--structure', action='store_true')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    morphology = MorphologyGraph()
    syntax_builder = SyntaxBuilder()
    morphology_builder = MorphologyBuilder(morphology, test=args.test)
    with open(args.input, 'r') as f:
        for line in f.readlines():
            line = syntax_builder.parse(line)
            if not line:
                continue

            morphology_builder.parse(line)
    
    trees = []
    reviewer = Reviewer(morphology, syntax_builder, args.structure)
    for i, line in enumerate(sys.stdin):
        if args.count:
            print(' '.join(str(i) for i in count(morphology, line)))
            continue
        
        interpretation = reviewer.read(line, line=i+1)
        trees += InterpretationWriter(f'S{i}').write(interpretation)

    if args.output:
        with open(args.output, 'w') as f:
            f.writelines(line + '\n' for line in trees)