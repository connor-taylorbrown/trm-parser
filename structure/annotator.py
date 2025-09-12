from abc import ABC, abstractmethod

from structure.formal import Logger, SyntaxNode


class Annotator(ABC):
    @abstractmethod
    def annotate(self):
        pass


class AnnotatorFactory(ABC):
    @abstractmethod
    def create(self, node: SyntaxNode, logger: Logger) -> Annotator:
        pass


class NullAnnotator(Annotator):
    def annotate(self):
        return


class NullAnnotatorFactory(AnnotatorFactory):
    def create(self, node, logger):
        return NullAnnotator()
