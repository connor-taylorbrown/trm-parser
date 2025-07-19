import sys
import argparse

class MorphologyNode:
    def __init__(self, gloss: str, *overrides: str):
        self.gloss = gloss
        self.overrides = overrides
        self.items: dict[str, 'MorphologyNode'] = {}
        self.prefixes: dict[str, 'MorphologyNode'] = {}
        self.suffixes: dict[str, 'MorphologyNode'] = {}

    def __str__(self):
        lines = []
        for item in self.items:
            lines.append(f'item {item} {self.items[item]}')
        
        for prefix in self.prefixes:
            lines.append(f'prefix {prefix} {self.prefixes[prefix]}')
        
        for suffix in self.suffixes:
            lines.append(f'suffix {suffix} {self.suffixes[suffix]}')

        return '\n'.join(lines)

    def add_node(self, type, key, node):
        getattr(self, type)[key] = node
        return self

    def split_word(self, text, i):
        return text[:i], text[i:]
    
    def apply_gloss(self, gloss: str, prefix):
        for override in self.overrides:
            gloss = gloss.replace(override, '')

        if prefix:
            return self.gloss + gloss
        
        return gloss + self.gloss
    
    def get_item(self, text):
        item = self.items.get(text)
        if item:
            return self.apply_gloss(item.gloss, prefix)

    def gloss_affixes(self, text, prefix):
        homonyms = self.prefixes.get('$')
        if homonyms:
            for gloss in homonyms.gloss_affixes(text, prefix):
                yield gloss

        affixes = self.prefixes if prefix else self.suffixes
        item = self.get_item(text)
        if item:
            yield item

        for i in range(1, len(text)):
            if prefix:
                affix, stem = self.split_word(text, i)
            else:
                stem, affix = self.split_word(text, i)

            next = affixes.get(affix)
            if not next:
                continue

            for gloss in next.gloss_affixes(stem, prefix):
                yield self.apply_gloss(gloss, prefix)


class MorphologyGraph:
    def __init__(self):
        self.nodes: dict[str, MorphologyNode] = {
            '$': MorphologyNode('')
        }

    def __str__(self):
        return str(self.get_root())
    
    def get_root(self):
        return self.nodes['$']

    def add_node(self, key, gloss, *overrides):
        if key in self.nodes:
            root = self.nodes['$']
            self.nodes['$'] = MorphologyNode('').add_node('prefixes', '$', root)
        self.nodes[key] = MorphologyNode(gloss, *overrides)
    
    def add_edge(self, source, target, label):
        self.nodes[source].add_node(label, target, self.nodes[target])

    def gloss_affixes(self, text, prefix):
        return [gloss.strip("-.") for gloss in self.get_root().gloss_affixes(text, prefix)]
    

class GraphWriter:
    def __init__(self):
        self.ids = {}
        self.visited = set()
        self.nodes: dict[str, dict] = {}
        self.edges = []
        self.count = 0
    
    def next_id(self):
        count = self.count
        self.count += 1
        return f'n{count}'
    
    def update_node(self, text, gloss, **kwargs):
        key = text + gloss
        id = self.ids.get(key)
        if not id:
            id = self.next_id()
            self.ids[key] = id
            self.nodes[id] = kwargs
        else:
            attrs = self.nodes[id]
            self.nodes[id] = {**attrs, **kwargs}

        return id
    
    def add_affix(self, text, gloss):
        return self.update_node(text, gloss, label=f'"{text}/{gloss}"')
    
    def add_item(self, text, gloss):
        return self.update_node(text, gloss, label=f'<<u>{text}/{gloss}</u>>')

    def find_components(self, node: MorphologyNode):
        for prefix in node.prefixes:
            next = node.prefixes[prefix]
            if prefix == '$':
                for component in self.find_components(next):
                    yield component

                continue

            self.add_affix(prefix, next.gloss)
            yield next, prefix, True
        
        for suffix in node.suffixes:
            next = node.suffixes[suffix]
            self.add_affix(suffix, next.gloss)
            yield next, suffix, False

        for item in node.items:
            next = node.items[item]
            self.add_item(item, next.gloss)
    
    def add_edge(self, current, child, prefix):
        if prefix:
            edge = f'{current} -> {child}'
        else:
            edge = f'{child} -> {current}'

        self.edges.append(edge)
    
    def visit(self, node: MorphologyNode, text: str, prefix: bool):
        current = self.ids[text + node.gloss]
        for item in node.items:
            next = node.items[item]
            edge = (text + node.gloss, next.gloss) 
            if edge in self.visited:
                continue

            child = self.add_item(item, next.gloss)
            self.add_edge(current, child, prefix)
            self.visited.add(edge)

        for affix in node.prefixes:
            next = node.prefixes[affix]
            edge = (text + node.gloss, next.gloss)
            if edge in self.visited:
                continue

            child = self.visit(next, affix, prefix=True)
            self.add_edge(current, child, prefix)
            self.visited.add(edge)
        
        for affix in node.suffixes:
            next = node.suffixes[affix]
            edge = (text + node.gloss, next.gloss) 
            if edge in self.visited:
                continue
            
            child = self.visit(next, affix, prefix=False)
            self.add_edge(current, child, prefix)
            self.visited.add(edge)

        return current
    
    def write(self):
        yield 'digraph G {'

        for node in self.nodes:
            attrs = self.nodes[node]
            attr_text = [f'{k}={attrs[k]}' for k in attrs]
            yield f'{node} [{" ".join(attr for attr in attr_text)}];'

        for edge in self.edges:
            yield f'{edge};'
        
        yield '}'


def generate(node: MorphologyNode):
    for item in node.items:
        yield item, node.items[item].gloss
    
    for prefix in node.prefixes:
        next = node.prefixes[prefix]
        for stem, gloss in generate(next):
            yield prefix + stem, next.apply_gloss(gloss, True)
        
        yield prefix, next.gloss
    
    for suffix in node.suffixes:
        next = node.suffixes[suffix]
        for stem, gloss in generate(next):
            yield stem + suffix, next.apply_gloss(gloss, False)
        
        yield suffix, next.gloss


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Morphology Graph CLI")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate all possible strings')
    parser.add_argument('-t', '--test', action='store_true', help='Display test results')
    parser.add_argument('-o', '--output', help='Save to GraphML file')
    args = parser.parse_args()

    graph = MorphologyGraph()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        command = line.split()
        if command[0] == '#':
            pass
        elif command[0] == 'n':
            _, key, gloss, *overrides = command
            graph.add_node(key, gloss, *overrides)
        elif command[0] == 'e':
            _, source, target, *label = command
            for label in label:
                graph.add_edge(source, target, label)

            if args.verbose:
                print(graph)
        elif args.test:
            command, = command
            glosses = set()
            for prefix in [True, False]:
                for gloss in graph.gloss_affixes(command, prefix):
                    if gloss in glosses:
                        continue
                    
                    print(f'{command}: prefix={prefix},{gloss}')
                    glosses.add(gloss)

    if args.output:
        w = GraphWriter()
        for component, text, prefix in w.find_components(graph.get_root()):
            w.visit(component, text, prefix)

        with open(args.output, 'w') as f:
            f.writelines(line + '\n' for line in w.write())

    if args.generate:
        for token, gloss in generate(graph.get_root()):
            print(f'{token} {gloss}')
