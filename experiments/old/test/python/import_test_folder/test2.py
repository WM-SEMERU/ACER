from animal import Animal as Mammal, Horse
import basic_math_module as math
import basic_math_module

# test import as statement, using the same package with two aliases
def add_twice(a,b):
    return basic_math_module.add(math.add(a,b), math.add(a,b))

def add_four_times(a,b):
    return(add_twice(basic_math_module.add(a,b), math.add(a,b)))

# create a subclass with the same name as imported folder
class Cow(Mammal):
    def __init__(self, name):
        super(Cow, self).__init__(name)

    def sound(self):
        return 'moo'

# create a new subclass with alias
class Monkey(Mammal):
    def __init__(self, name):
        super(Monkey, self).__init__(name)

    def sound(self):
        return 'ooh ooh aah aah'

if __name__ == '__main__':

    # test method containing multiple imports
    twenty = add_four_times(2,3)
    print(twenty)


    # import a subclass from another file that uses virtual methods
    s = Horse('CJ')
    s.speak()

    # call new subclasses
    c = Cow('Bessie')
    c.speak()

    m = Monkey('Mo')
    m.speak()
