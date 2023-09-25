from abc import ABC

class DemoClassX(ABC):
    def functionN(self):
        pass

    def functionM(self, value):
        pass

class DemoClassY(DemoClassX):
    def functionM(self):
        pass
