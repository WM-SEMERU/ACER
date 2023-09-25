from abc import ABC, abstractmethod
from typing import Dict


class EdgeBuilder(ABC):
    """
    Builds `edge_dict`.
    """

    @abstractmethod
    def buildEdges(self) -> Dict:
        pass