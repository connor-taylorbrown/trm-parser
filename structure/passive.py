import argparse


class PassiveReader:
    def __init__(self, lemmatise: dict[str, tuple[str]]):
        self.lemmatise = lemmatise

    def __repr__(self):
        return str(self.lemmatise)
    
    def match(self, w: str):
        return self.lemmatise.get(w)
    
    def orthographic(self):
        def convert(w: str):
            return w.replace('f', 'wh')\
                .replace('N', 'ng')\
                .replace('A', 'ā')\
                .replace('E', 'ē')\
                .replace('I', 'ī')\
                .replace('O', 'ō')\
                .replace('U', 'ū')
        
        return PassiveReader({
            convert(k): tuple(convert(w) for w in self.lemmatise[k])
            for k in self.lemmatise
        })

    @staticmethod
    def read(filename: list[str]):
        lemmatise = {}
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue

                _, _, wordform, lemma, suffix, *_ = line.split(',')
                if wordform in lemmatise:
                    continue

                lemmatise[wordform] = lemma, *suffix.split('/')
        
        return PassiveReader(lemmatise)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read a file line by line.")
    parser.add_argument("input", help="Input filename")
    parser.add_argument('--word', '-w', type=str, help="Word to look up")
    args = parser.parse_args()

    reader = PassiveReader.read(args.input).orthographic()
    if args.word:
        print(reader.match(args.word))
    else:
        print(reader)
