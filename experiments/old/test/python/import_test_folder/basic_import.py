from basic_math_module import add, subtract

# import a method with the same name from another folder
def add(a, b):
    return a + b

# call a method with a different name from another folder
def import_subtract(a,b):
    return subtract(a,b)

if __name__ == "__main__":
    five = add(2,3)
    print(five)
    three = import_subtract(five, 2)
    print(three)
