package CallGraph.test.java.preprocessor.models_cache.files;

interface BContract {}
public interface B extends BContract {
	/* final fields are allowed and static methods can have bodies in an interface! */
	public final static int field1 = 3;
	A field2 = new A();
}
