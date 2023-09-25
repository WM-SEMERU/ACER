from __future__ import annotations
import logging
from tree_sitter import Language
from ComponentsFactory.Base import ComponentsFactory
from pathlib import Path

from TypeResolver.Java.utils import JavaTypeResolverTypes
from CallNodeResolver.Base import CallNodeTypes

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from Preprocessor.Java import JavaPreprocessor
    from EdgeBuilder.Java import JavaEdgeBuilder
    from TypeResolver.Java.Base import JavaTypeResolver
    from CallNodeResolver.Java.Base import JavaCallNodeResolver

class JavaComponentsFactory(ComponentsFactory):
    def create_preprocessor(self) -> JavaPreprocessor:
          from Preprocessor.Java import JavaPreprocessor
          return JavaPreprocessor()

    def create_edge_builder(self) -> JavaEdgeBuilder:
        from EdgeBuilder.Java import JavaEdgeBuilder
        return JavaEdgeBuilder()

    def create_type_resolver(self, typeResolverType: JavaTypeResolverTypes) -> JavaTypeResolver:
        from TypeResolver.Java.ObjectCreationExpression import JavaObjectCreationExpressionTypeResolver
        from TypeResolver.Java.Identifier import JavaIdentifierTypeResolver
        from TypeResolver.Java.LocalVariableDeclaration import JavaLocalVariableDeclarationTypeResolver
        from TypeResolver.Java.MethodInvocation import JavaMethodInvocationTypeResolver
        from TypeResolver.Java.NullLiteral import JavaNullLiteralTypeResolver
        from TypeResolver.Java.FieldAccess import JavaFieldAccessTypeResolver
        from TypeResolver.Java.CastExpression import JavaCastExpressionTypeResolver
        from TypeResolver.Java.ParenthesizedExpression import JavaParenthesizedExpressionTypeResolver
        resolve_type_cls_map: dict[JavaTypeResolverTypes, Type[JavaTypeResolver]] = {
            JavaTypeResolverTypes.OBJECT_CREATION_EXPRESSION: JavaObjectCreationExpressionTypeResolver, 
            JavaTypeResolverTypes.IDENTIFIER: JavaIdentifierTypeResolver, 
            JavaTypeResolverTypes.LOCAL_VARIABLE_DECLARATION: JavaLocalVariableDeclarationTypeResolver,
            JavaTypeResolverTypes.METHOD_INVOCATION: JavaMethodInvocationTypeResolver, 
            JavaTypeResolverTypes.NULL_LITERAL: JavaNullLiteralTypeResolver, 
            JavaTypeResolverTypes.FIELD_ACCESS: JavaFieldAccessTypeResolver,
            JavaTypeResolverTypes.CAST_EXPRESSION: JavaCastExpressionTypeResolver,
            JavaTypeResolverTypes.PARENTHESIZED_EXPRESSION: JavaParenthesizedExpressionTypeResolver,
        }

        if typeResolverType not in resolve_type_cls_map:
            logging.warn(f"No type resolver created for type {typeResolverType} yet, exiting.")
        
        return resolve_type_cls_map[typeResolverType]()

    def create_language(self) -> Language:
        return Language(str(Path(__file__).parent.parent.parent.joinpath("build", "my-languages.so")), 'java')

    def create_call_node_resolver(self, callNodeType: CallNodeTypes) -> JavaCallNodeResolver:
        from CallNodeResolver.Java.Base import JavaCallNodeResolver
        # JavaCallNodeResolver has more subclasses, and we need to make the correct, specific one
        return JavaCallNodeResolver.makeSpecificCallNodeResolver(callNodeType)

    def create_extension(self) -> str:
        return '.java'