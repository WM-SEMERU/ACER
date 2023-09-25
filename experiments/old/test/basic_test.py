

def hello_world_caller():
    print_hello_world()

def print_hello_world():
    print("Hello World.")

value = 0

def increment_value(value):
    value += 1
    print(value)
    return value

def main():
    print_hello_world()
    increment_value(value)


    # test overload methods
    