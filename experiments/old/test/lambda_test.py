

class test_lambda():

    def double(self, x):
        return x * 2


    # Program to show the use of lambda functions
    def lambda_double(self, x):
        double = lambda x: x * 2
        return double

    def lambda_map(self, li):
        new_list = list(map(lambda x: x * 2 , li)) # doubles the values in the list
        return new_list
    

def main():
    test = test_lambda()
    val = test.lambda_double(5)
    my_list = [1, 5, 4, 6, 8, 11, 3, 12]
    print(test.lambda_map(my_list))
    print(val)

main()
