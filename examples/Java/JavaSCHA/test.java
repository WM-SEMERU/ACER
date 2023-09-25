class A {
	void a() {
		D d = new D();
		d.a();
	}
}

class B extends A {
}

class C extends B {

}

interface AInterface {
	void a();
}

class D implements AInterface {
	void a() {
		A a = new A(); 
		a.a();

		D d = new D(); 
		d.a();
	}
}
class E extends D {}

public class Test {
	public static void main(String args[]) {
		A a = new A(); 
		a.a(); // Goes into A.a, B.a, C.a 

		E e = new E(); 
		e.a(); // Goes into E.a, E.b, E.c
	}
}