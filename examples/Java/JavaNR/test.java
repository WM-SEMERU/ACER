public class Test {
	void d() {
		a();
	}
	public static void main(String args[]) {
		a();
	}
	void a() {
		b();
	}
	void b() {		
		a();
		c();
	}
	void c() {
		b();
		main();
		c();
		a();
	}
}