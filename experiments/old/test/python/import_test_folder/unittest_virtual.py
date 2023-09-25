# inspired by https://github.com/bgreenlee/virtualmethod
class Base(object):
    @virtualmethod
    def my_virtual_method(self):
        return True

    @virtualmethod
    @classmethod
    def my_virtual_class_method(cls):
        return True

    @virtualmethod
    @staticmethod
    def my_virtual_static_method():
        return True

class A(Base):
    pass

class B(Base):
    def my_virtual_method(self):
        return True

    @classmethod
    def my_virtual_class_method(cls):
        return True

    @staticmethod
    def my_virtual_static_method():
        return True

class VirtualMethodTest(unittest.TestCase):
    def setUp(self):
        self.base = Base()
        self.sub_a = A()
        self.sub_b = B()

    def test_virtual_method(self):
        self.assertTrue(self.sub_a.my_virtual_method())
        self.assertTrue(self.sub_b.my_virtual_method())
        self.assertRaises(TypeError, self.base.my_virtual_method)

    def test_virtual_class_method(self):
        self.assertTrue(A.my_virtual_class_method())
        self.assertTrue(B.my_virtual_class_method())
        self.assertRaises(TypeError, Base.my_virtual_class_method)

    def test_virtual_static_method(self):
        self.assertTrue(A.my_virtual_static_method())
        self.assertTrue(B.my_virtual_static_method())
        self.assertRaises(TypeError, Base.my_virtual_static_method)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
