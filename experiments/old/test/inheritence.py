'''
The purpose of this test case is to test code that
uses inheritence. 
'''


'''
This class functions like a normal bank account. 

''' 
class BankAccount(object): 
    def __init__(self,initialBal,acctNum): 
        self.balance = initialBal
        self.number = acctNum 

    def deposit(self,amount):
        self.balance += amount 

    def withdraw(self,amount):
        self.balance -= amount 

    def getAccountNumber(self):
        return self.number 

    def returnBalance(self):
        return self.balance


'''
This class functions like a normal bank account,
but deposits 
'''
class PremiumBankAccount(BankAccount):
    def __init__(self,initialBal,acctNum):
        super().__init__(initialBal,acctNum) 

    def deposit(self,amount):
        amount *= 1.25
        self.balance = self.balance + amount 

def main(): 
    firstBankAccount = BankAccount(100,1234)
    firstBankAccount.deposit(500)
    secondBankAccount = PremiumBankAccount(100,2222)
    secondBankAccount.deposit(500)
    print(firstBankAccount.returnBalance(),secondBankAccount.returnBalance())


main() 
     
    