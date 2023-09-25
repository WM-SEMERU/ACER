from abc import ABC, abstractmethod

class A(ABC):
    @staticmethod
    def methodA():
        print("A Method A")
        b = B()
        b.methodD()
        

    @classmethod
    def methodB(cls):
        b = B()
        b.methodE()

    @abstractmethod
    def methodC(self):
        b = B()
        b.methodE()
        self.methodA()

class B(A):
    
    def methodD(self):
        aclass = A()
        A.methodA()
        aclass.methodA()
        print("B Method A")

    def methodE(self):
        aclass = A()
        aclass.methodC()
        self.methodD()
    
        