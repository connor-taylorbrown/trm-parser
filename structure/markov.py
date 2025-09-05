from structure.formal import Logger
from structure.observable import ObservableWriter, ObservableWriterFactory
from structure.writer import InterpretationWriter, WriterFactory, write_line


class MarkovWriter(InterpretationWriter):
    def __init__(self, observable: ObservableWriter, line: str, particles: int, bases: int, *context: str):
        self.observable = observable
        self.line = line
        self.context = context
        self.particles = self.context[particles].split('-')
        self.bases = self.context[bases].split('-')
        
    def write(self, node):
        resolved, annotations = self.observable.traverse(node)
        logger: Logger = node.logger
        if not resolved:
            logger.error('Replay error: Cannot resolve single interpretation')
            return
        
        states = []
        aligned = []
        for phrase in annotations:
            states.append('$')

            markers, bases = phrase
            if self.particles:
                states.append(self.particles.pop(0) + '/')
                aligned.append('.'.join(markers) if markers else '*')
            elif markers:
                logger.error('Replay error: No annotation available for marker')
                return

            if not bases:
                continue

            if isinstance(bases, str):
                bases = [bases]

            for base in bases:
                if not self.bases:
                    logger.error('Replay error: No annotation available for base')
                    return
                
                states.append(self.bases.pop(0) + '/')
                aligned.append(base)

        yield write_line(
            self.context,
            ''.join(states).strip('/'),
            ' '.join(aligned),
            self.line
        )


class MarkovWriterFactory(WriterFactory):
    def __init__(self, observable: ObservableWriterFactory):
        self.observable = observable

    def start(self, *context):
        self.particles = context.index('Particles')
        self.bases = context.index('Bases')
        return [','.join([
            *context[:-1],
            'States',
            'Aligned',
            'Fragment'
        ]) + '\n']

    def create(self, *metadata):
        _, line, *context = metadata
        return MarkovWriter(self.observable.create(*metadata), line, self.particles, self.bases, *context)
