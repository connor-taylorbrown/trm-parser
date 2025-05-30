class FileReader:
    def __init__(self, name, encoding):
        self.name = name
        self.encoding = encoding
        self.map = {
            'ä': 'ā',
            'ë': 'ē',
            'ï': 'ī',
            'ö': 'ō',
            'ü': 'ū',
            'Ä': 'Ā',
            'Ë': 'Ē',
            'Ï': 'Ī',
            'Ö': 'Ō',
            'Ü': 'Ū'
        }

    def convert(self, line):
        def map(c):
            to = self.map.get(c)
            if not to:
                return c
            
            return to
        
        return ''.join(map(c) for c in line)


    def read_file(self, label):
        name = self.name.format(label)
        with open(name, 'r', encoding=self.encoding) as f:
            for line in f.readlines():
                yield self.convert(line)


class InputReader:
    def __init__(self):
        self.terminated = False

    def read_file(self, _):
        if self.terminated:
            raise FileNotFoundError("Input reading has been terminated.")
        
        while True:
            try:
                line = input()
                yield line
            except EOFError:
                self.terminated = True
                break
