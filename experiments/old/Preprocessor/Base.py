from abc import ABC, abstractmethod
from typing import Dict


class Preprocessor(ABC):
    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def makeMethodDict(self) -> Dict:
        pass
