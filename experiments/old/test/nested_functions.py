def outer_func():
     def inner_func():
         hello_world()
     inner_func()

def hello_world():
    print('hello, world!')

outer_func()
