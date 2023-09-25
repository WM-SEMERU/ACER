package CallGraph.test.java.shared_files.parent_child.parent;

class PublicField {}
class DefaultField {}
class ProtectedField {}

public class Parent {
	public PublicField field1; 
	DefaultField field2;
	ProtectedField field3;
	private NestedDefaultClass field4; 
	protected NestedPublicClass field5; 

	class NestedDefaultClass {
		public class NestedNestedPublicClass {
			private void nestednestedmethod(){}
		}
	}
	public class NestedPublicClass {
		class NestedNestedDefaultClass {}
		public class NestedNestedPublicClass {
			public void nestednestedpublicmethod(){
				NestedDefaultClass.NestedNestedPublicClass nn;
				nn.nestednestedmethod();
			}
		}
		public void nestedpublicmethod(int a, int b){}
	}
}