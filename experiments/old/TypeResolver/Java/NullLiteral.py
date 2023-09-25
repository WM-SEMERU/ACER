from TypeResolver.Java.Base import JavaTypeResolver
from utils.java import *


class JavaNullLiteralTypeResolver(JavaTypeResolver):
    """
    Return the full return type of a.method1()
    Resolving process is similar to MethodInvocationCallNodeResolver, except, after locating the unique method,
    we also get its return type (by querying method_dict). So in fact, I use MethodInvocationCallNodeResolver
    """

    def resolve(self, method_invocation_node: Node) -> JavaFullType:
        return JAVA_ERR_FULL_TYPE