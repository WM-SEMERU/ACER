package CallGraph.test.java.shared_files.parent_child.child;

import CallGraph.test.java.shared_files.parent_child.parent.Parent;

public class Child extends Parent  {
	// Though inheriting Parent, cannot use default access classes nor fields
	private Parent.NestedPublicClass field1; // Okay because public 
	private CallGraph.test.java.shared_files.parent_child.parent.Parent.NestedPublicClass field2; // Or, can always use full path
	// private Parent.NestedDefaultClass field2; // Would err
	class ChildNestedDefault {}
	private void childMethod(ChildNestedDefault a, ChildNestedPublic b){
		// Make Identifier TypeResolver tests resolve the types of expressions in the prints
		System.out.println(a);
		System.out.println(b);

		System.out.println(field1);
		System.out.println(field2);
		System.out.println(field5);

		Child c = new Child();
		System.out.println(c);

		NestedPublicClass pc = new NestedPublicClass(); // resolve due to importing, not inheritance
		System.out.println(pc);
		
		Parent.NestedPublicClass pc2 = new Parent.NestedPublicClass(); // resolve due to inheritance, not importing		
		System.out.println(pc2);
		
		ChildNestedPublic cnp = new ChildNestedPublic();
		System.out.println(cnp);
		
		NestedPublicClass.NestedNestedPublicClass nn;
		nn.nestednestedpublicmethod();

	}
	public class ChildNestedPublic {}

}
