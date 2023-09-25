from Context.Java import JavaContext
from utils.java import aliased_type_to_full_type

from my_enums.java import JAVA_ERR_FULL_TYPE
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver
from TypeResolver.Java.utils import JavaTypeResolverTypes
from TypeResolver.Java.Base import JavaTypeResolver
from my_types.java import JavaFullType, class_cache_field, enum_cache_field, interface_cache_field


class JavaFieldAccessTypeResolver(JavaTypeResolver):
    def resolve(self, field_access_node: Node) -> JavaFullType:
        field = field_access_node.child_by_field_name("field").text.decode("utf8")
        object = field_access_node.child_by_field_name("object")

        if object.type == JavaTypeResolverTypes.THIS: 
            # In the case of `this.b`, the type is b's type.
            return aliased_type_to_full_type(field, field_access_node)

        resolver = JavaContext.componentsFactory.create_type_resolver(
            JavaTypeResolverTypes.from_str(object.type)
        )
        
        object_full_type = resolver.resolve(object)

        if object_full_type in JavaContext.cache.models_cache: 
            cache = JavaContext.cache.models_cache[object_full_type]
            if type(cache) is class_cache_field:
                aliased_type = cache.fields[field]["type"]
                return aliased_type_to_full_type(aliased_type, field_access_node)
            elif type(cache) is interface_cache_field: 
                aliased_type = cache.constants[field]["type"]
                return aliased_type_to_full_type(aliased_type, field_access_node)
            elif type(cache) is enum_cache_field: 
                # TODO: Consider if enum constants' full type should just be their enum class. 
                # For now, assume so.
                return object_full_type


        return JAVA_ERR_FULL_TYPE
