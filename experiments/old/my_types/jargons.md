# Java Call Graph Jargons
Understanding the following will help understanding the code base.

`model`: A Java entity that introduces a name to the type system. For example, `class`, `interface`, `enum`. "Java type" and "model" are used synonymously.

`JavaFullType`: Uniquely represents a Java type with the tuple `(package_name, contained_by, shorthand)`. `contained_by` is only utilized when uniquely identifying a nested classes. E.g., if class `C` is nestedly declared within class `B` and `B` within `A`, then, C's `JavaFullType` is 

`(some_package, A.B, C)`  Note that only `model`s correspond to `JavaFullType` as only `model` can introduce a name to the type system.

`aliased_type`: Used to represent the types directly encountered in the source code. Usually, programmers always use the shorthand of a type, and thus, `aliased_type` is often just the `shorthand`. Of course, this `aliased_type` might just be the full type. Consider the following: 

```
package com.project;

class D() {}

method() {
	D obj = new D(); // In our parsing logic, `D` is the `aliased_type`.
	com.project.D obj2 = new com.project.D(); // In our parsing logic, `com.project.D` is the `aliased_type`.
}

```

`container`: A `container` is the model containing some node.
`outer`: A `container` of a `container`. Corresponds with "nested classes"