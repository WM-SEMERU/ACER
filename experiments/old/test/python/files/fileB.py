from fileA import DemoClassX, DemoClassY

class DemoClassZ():
    def functionO(self):
        x = DemoClassX()
        x.functionN()

    def functionP(self):
        y = DemoClassY()
        y.functionN() 

    def functionQ(self):
        x = DemoClassX()
        x.functionM(10)

    def functionR(self):
        y = DemoClassY()
        y.functionM()