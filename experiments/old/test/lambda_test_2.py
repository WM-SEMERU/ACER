'''
The following test case tests nested
lambda functions
'''


def add(x,w):
    z = lambda y:x+y
    return z(w)


def main(): 
    print(add(2,3))
    my_lambda = lambda x,w,y: add(x,w)*y
    print(my_lambda(2,3,4))


main() 