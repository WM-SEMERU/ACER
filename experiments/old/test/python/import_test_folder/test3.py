# This test uses methods of the same name in different scopes
import basic_math_module

class Shape():

    def __init__(self):
        self.shape = 'shape'

    def __str__(self):
        return "I am a {}.".format(self.shape)

    def declare_name(self):
        return "I am a {}.".format(self.shape)
        
class Polygon(Shape):

    def __init__(self):
        self.shape = 'polygon'
        self.side_lengths = None

    def compute_perimeter(self):
        return sum(self.side_lengths)

    def get_number_of_edges(self):
        return len(self.side_lengths)

    def add(self,a,b):
        return a + b

class Triangle(Polygon):

    def __init__(self):
        self.shape = 'triangle'
        self.side_lengths = [2, 2, 2]

def compute_perimeter(a,b,c):
    return add(add(a, b), c)

def declare_name():
    return "I am a shape"

def add(a,b):
    return a + b

if __name__ == '__main__':
    Tri = Triangle()
    outer_scope_name = declare_name()
    inner_scope_name = Tri.declare_name

    # same name, different parameters
    x = compute_perimeter(2,2,2)
    y = Tri.compute_perimeter()

    # three scopes for addition here
    six = add(Tri.add(1,2), basic_math_module.add(1,2))
