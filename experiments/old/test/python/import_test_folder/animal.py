# https://gist.github.com/rtoal/331c855a8092e82673dd

class Animal(object):
    def __init__(self, name):
        self.name = name

    def speak(self):
        print (self.name, 'says', self.sound())

class Cow(Animal):
    def __init__(self, name):
        super(Cow, self).__init__(name)

    def sound(self):
        return 'moo'

class Horse(Animal):
    def __init__(self, name):
        super(Horse, self).__init__(name)

    def sound(self):
        return 'neigh'

class Sheep(Animal):
    def __init__(self, name):
        super(Sheep, self).__init__(name)

    def sound(self):
        return 'baaaaa'

if __name__ == '__main__':
    s = Horse('CJ')
    s.speak()
    c = Cow('Bessie')
    c.speak()
    Sheep('Little Lamb').speak()
