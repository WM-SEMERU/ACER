# test 1 covers basic import logic
from basic_math_module import add, subtract
import basic_import

#import a method that imports from an additional folder
def import_subtract(a,b):
    return basic_import.import_subtract(a,b)

def add(a,b):
    return a + b

if __name__ == '__main__':
    # run a function directly from math module
    four = basic_math_module.add(2,2)
    print(four)

    one = import_subtract(four, 3)
    print(one)
