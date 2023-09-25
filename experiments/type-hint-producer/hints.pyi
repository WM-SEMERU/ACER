 
from typing import Any, List, Optional
from tree_sitter import TreeCursor

class MyNode:
    '''
    `MyNode` is tree-sitter's `Node` but without the `children` array.
    Instead, `MyNode` can directly access children nodes using either their field name (e.g., declarator) or type (e.g., break_statement).

    Further, I also removed the `children` helper methods and properties from MyNode that our CallGraph application never uses.
    For example, we never use `start_byte` and `has_error`. 

    Only purpose of removing these is to make for cleaner auto-suggestions.
    '''
    # @property
    # def start_byte(self) -> int: ...
    # @property
    # def start_point(self) -> tuple[int, int]: ...
    # @property
    # def end_byte(self) -> int: ...
    # @property
    # def end_point(self) -> tuple[int, int]: ...
    # @property
    # def has_changes(self) -> bool: ...
    # @property
    # def has_error(self) -> bool: ...
    # @property
    # def id(self) -> int: ...
    # @property
    # def is_missing(self) -> bool: ...
    # @property
    # def is_named(self) -> bool: ...
    @property
    def child_count(self) -> int: ...
    @property
    def named_child_count(self) -> bool: ...
    @property
    # def children(self) -> list[MyNode]: ...  
    # @property
    # def named_children(self) -> list[MyNode]: ...
    # @property
    def next_named_sibling(self) -> MyNode | None: ...
    @property
    def next_sibling(self) -> MyNode | None: ...
    @property
    def parent(self) -> MyNode | None: ...
    @property
    def prev_named_sibling(self) -> MyNode | None: ...
    @property
    def prev_sibling(self) -> MyNode | None: ...
    @property
    def text(self) -> bytes | Any: ...  # can be None, but annoying to check
    @property
    def type(self) -> str: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def sexp(self) -> str: ...
    def walk(self) -> TreeCursor: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

type LiteralNode = BinaryIntegerLiteralNode | CharacterLiteralNode | DecimalFloatingPointLiteralNode | DecimalIntegerLiteralNode | FalseNode | HexFloatingPointLiteralNode | HexIntegerLiteralNode | NullLiteralNode | OctalIntegerLiteralNode | StringLiteralNode | TrueNode
type SimpleTypeNode = BooleanTypeNode | FloatingPointTypeNode | GenericTypeNode | IntegralTypeNode | ScopedTypeIdentifierNode | TypeIdentifierNode | VoidTypeNode
type TypeNode = UnannotatedTypeNode | AnnotatedTypeNode
type UnannotatedTypeNode = SimpleTypeNode | ArrayTypeNode
type CommentNode = BlockCommentNode | LineCommentNode
type DeclarationNode = AnnotationTypeDeclarationNode | ClassDeclarationNode | EnumDeclarationNode | ImportDeclarationNode | InterfaceDeclarationNode | ModuleDeclarationNode | PackageDeclarationNode | RecordDeclarationNode
type ExpressionNode = AssignmentExpressionNode | BinaryExpressionNode | CastExpressionNode | InstanceofExpressionNode | LambdaExpressionNode | PrimaryExpressionNode | SwitchExpressionNode | TernaryExpressionNode | UnaryExpressionNode | UpdateExpressionNode
type ModuleDirectiveNode = ExportsModuleDirectiveNode | OpensModuleDirectiveNode | ProvidesModuleDirectiveNode | RequiresModuleDirectiveNode | UsesModuleDirectiveNode
type PrimaryExpressionNode = LiteralNode | ArrayAccessNode | ArrayCreationExpressionNode | ClassLiteralNode | FieldAccessNode | IdentifierNode | MethodInvocationNode | MethodReferenceNode | ObjectCreationExpressionNode | ParenthesizedExpressionNode | ThisNode
type StatementNode = AssertStatementNode | BlockNode | BreakStatementNode | ContinueStatementNode | DeclarationNode | DoStatementNode | EnhancedForStatementNode | ExpressionStatementNode | ForStatementNode | IfStatementNode | LabeledStatementNode | LocalVariableDeclarationNode | ReturnStatementNode | SwitchExpressionNode | SynchronizedStatementNode | ThrowStatementNode | TryStatementNode | TryWithResourcesStatementNode | WhileStatementNode | YieldStatementNode
class AnnotatedTypeNode(MyNode):
    _unannotated_type_list: List[UnannotatedTypeNode]
    annotation_list: List[AnnotationNode]
    marker_annotation_list: List[MarkerAnnotationNode]

class AnnotationNode(MyNode):
    arguments: AnnotationArgumentListNode
    name: IdentifierNode | ScopedIdentifierNode

class AnnotationArgumentListNode(MyNode):
    annotation_list: Optional[List[AnnotationNode]]
    element_value_array_initializer_list: Optional[List[ElementValueArrayInitializerNode]]
    element_value_pair_list: Optional[List[ElementValuePairNode]]
    expression_list: Optional[List[ExpressionNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

class AnnotationTypeBodyNode(MyNode):
    annotation_type_declaration_list: Optional[List[AnnotationTypeDeclarationNode]]
    annotation_type_element_declaration_list: Optional[List[AnnotationTypeElementDeclarationNode]]
    class_declaration_list: Optional[List[ClassDeclarationNode]]
    constant_declaration_list: Optional[List[ConstantDeclarationNode]]
    enum_declaration_list: Optional[List[EnumDeclarationNode]]
    interface_declaration_list: Optional[List[InterfaceDeclarationNode]]

class AnnotationTypeDeclarationNode(MyNode):
    body: AnnotationTypeBodyNode
    name: IdentifierNode
    modifiers: Optional[ModifiersNode]

class AnnotationTypeElementDeclarationNode(MyNode):
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    type: UnannotatedTypeNode
    value: Optional[AnnotationNode | ElementValueArrayInitializerNode | ExpressionNode | MarkerAnnotationNode]
    modifiers: Optional[ModifiersNode]

class ArgumentListNode(MyNode):
    expression_list: Optional[List[ExpressionNode]]

class ArrayAccessNode(MyNode):
    array: PrimaryExpressionNode
    index: ExpressionNode

class ArrayCreationExpressionNode(MyNode):
    dimensions: List[DimensionsNode | DimensionsExprNode]
    type: SimpleTypeNode
    value: Optional[ArrayInitializerNode]
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

class ArrayInitializerNode(MyNode):
    array_initializer_list: Optional[List[ArrayInitializerNode]]
    expression_list: Optional[List[ExpressionNode]]

class ArrayTypeNode(MyNode):
    dimensions: DimensionsNode
    element: UnannotatedTypeNode

class AssertStatementNode(MyNode):
    expression_list: List[ExpressionNode]

class AssignmentExpressionNode(MyNode):
    left: ArrayAccessNode | FieldAccessNode | IdentifierNode
    right: ExpressionNode

type AsteriskNode = MyNode
class BinaryExpressionNode(MyNode):
    left: ExpressionNode
    right: ExpressionNode

class BlockNode(MyNode):
    statement_list: Optional[List[StatementNode]]

class BreakStatementNode(MyNode):
    identifier: Optional[IdentifierNode]

class CastExpressionNode(MyNode):
    type: List[TypeNode]
    value: ExpressionNode

class CatchClauseNode(MyNode):
    body: BlockNode
    catch_formal_parameter: CatchFormalParameterNode

class CatchFormalParameterNode(MyNode):
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    catch_type_list: List[CatchTypeNode]
    modifiers_list: List[ModifiersNode]

class CatchTypeNode(MyNode):
    _unannotated_type_list: List[UnannotatedTypeNode]

class ClassBodyNode(MyNode):
    annotation_type_declaration_list: Optional[List[AnnotationTypeDeclarationNode]]
    block_list: Optional[List[BlockNode]]
    class_declaration_list: Optional[List[ClassDeclarationNode]]
    compact_constructor_declaration_list: Optional[List[CompactConstructorDeclarationNode]]
    constructor_declaration_list: Optional[List[ConstructorDeclarationNode]]
    enum_declaration_list: Optional[List[EnumDeclarationNode]]
    field_declaration_list: Optional[List[FieldDeclarationNode]]
    interface_declaration_list: Optional[List[InterfaceDeclarationNode]]
    method_declaration_list: Optional[List[MethodDeclarationNode]]
    record_declaration_list: Optional[List[RecordDeclarationNode]]
    static_initializer_list: Optional[List[StaticInitializerNode]]

class ClassDeclarationNode(MyNode):
    body: ClassBodyNode
    interfaces: Optional[SuperInterfacesNode]
    name: IdentifierNode
    permits: Optional[PermitsNode]
    superclass: Optional[SuperclassNode]
    type_parameters: Optional[TypeParametersNode]
    modifiers: Optional[ModifiersNode]

class ClassLiteralNode(MyNode):
    _unannotated_type: UnannotatedTypeNode

class CompactConstructorDeclarationNode(MyNode):
    body: BlockNode
    name: IdentifierNode
    modifiers: Optional[ModifiersNode]

class ConditionNode(MyNode):
    expression: ExpressionNode

class ConstantDeclarationNode(MyNode):
    declarator: List[VariableDeclaratorNode]
    type: UnannotatedTypeNode
    modifiers: Optional[ModifiersNode]

class ConstructorBodyNode(MyNode):
    explicit_constructor_invocation_list: Optional[List[ExplicitConstructorInvocationNode]]
    statement_list: Optional[List[StatementNode]]

class ConstructorDeclarationNode(MyNode):
    body: ConstructorBodyNode
    name: IdentifierNode
    parameters: FormalParametersNode
    type_parameters: Optional[TypeParametersNode]
    modifiers_list: Optional[List[ModifiersNode]]
    throws_list: Optional[List[ThrowsNode]]

class ContinueStatementNode(MyNode):
    identifier: Optional[IdentifierNode]

class DimensionsNode(MyNode):
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

class DimensionsExprNode(MyNode):
    annotation_list: List[AnnotationNode]
    expression_list: List[ExpressionNode]
    marker_annotation_list: List[MarkerAnnotationNode]

class DoStatementNode(MyNode):
    body: StatementNode
    condition: ParenthesizedExpressionNode

class ElementValueArrayInitializerNode(MyNode):
    annotation_list: Optional[List[AnnotationNode]]
    element_value_array_initializer_list: Optional[List[ElementValueArrayInitializerNode]]
    expression_list: Optional[List[ExpressionNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

class ElementValuePairNode(MyNode):
    key: IdentifierNode
    value: AnnotationNode | ElementValueArrayInitializerNode | ExpressionNode | MarkerAnnotationNode

class EnhancedForStatementNode(MyNode):
    body: StatementNode
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    type: UnannotatedTypeNode
    value: ExpressionNode
    modifiers: Optional[ModifiersNode]

class EnumBodyNode(MyNode):
    enum_body_declarations_list: Optional[List[EnumBodyDeclarationsNode]]
    enum_constant_list: Optional[List[EnumConstantNode]]

class EnumBodyDeclarationsNode(MyNode):
    annotation_type_declaration_list: Optional[List[AnnotationTypeDeclarationNode]]
    block_list: Optional[List[BlockNode]]
    class_declaration_list: Optional[List[ClassDeclarationNode]]
    compact_constructor_declaration_list: Optional[List[CompactConstructorDeclarationNode]]
    constructor_declaration_list: Optional[List[ConstructorDeclarationNode]]
    enum_declaration_list: Optional[List[EnumDeclarationNode]]
    field_declaration_list: Optional[List[FieldDeclarationNode]]
    interface_declaration_list: Optional[List[InterfaceDeclarationNode]]
    method_declaration_list: Optional[List[MethodDeclarationNode]]
    record_declaration_list: Optional[List[RecordDeclarationNode]]
    static_initializer_list: Optional[List[StaticInitializerNode]]

class EnumConstantNode(MyNode):
    arguments: Optional[ArgumentListNode]
    body: Optional[ClassBodyNode]
    name: IdentifierNode
    modifiers: Optional[ModifiersNode]

class EnumDeclarationNode(MyNode):
    body: EnumBodyNode
    interfaces: Optional[SuperInterfacesNode]
    name: IdentifierNode
    modifiers: Optional[ModifiersNode]

class ExplicitConstructorInvocationNode(MyNode):
    arguments: ArgumentListNode
    constructor: SuperNode | ThisNode
    object: Optional[PrimaryExpressionNode]
    type_arguments: Optional[TypeArgumentsNode]

class ExportsModuleDirectiveNode(MyNode):
    modules: Optional[List[IdentifierNode | ScopedIdentifierNode]]
    package: IdentifierNode | ScopedIdentifierNode

class ExpressionStatementNode(MyNode):
    expression: ExpressionNode

class ExtendsInterfacesNode(MyNode):
    type_list: TypeListNode

class FieldAccessNode(MyNode):
    field: IdentifierNode | ThisNode
    object: PrimaryExpressionNode | SuperNode
    super: Optional[SuperNode]

class FieldDeclarationNode(MyNode):
    declarator: List[VariableDeclaratorNode]
    type: UnannotatedTypeNode
    modifiers: Optional[ModifiersNode]

class FinallyClauseNode(MyNode):
    block: BlockNode

type FloatingPointTypeNode = MyNode
class ForStatementNode(MyNode):
    body: StatementNode
    condition: Optional[ExpressionNode]
    init: Optional[List[ExpressionNode | LocalVariableDeclarationNode]]
    update: Optional[List[ExpressionNode]]

class FormalParameterNode(MyNode):
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    type: UnannotatedTypeNode
    modifiers: Optional[ModifiersNode]

class FormalParametersNode(MyNode):
    formal_parameter_list: Optional[List[FormalParameterNode]]
    receiver_parameter_list: Optional[List[ReceiverParameterNode]]
    spread_parameter_list: Optional[List[SpreadParameterNode]]

class GenericTypeNode(MyNode):
    scoped_type_identifier_list: List[ScopedTypeIdentifierNode]
    type_arguments_list: List[TypeArgumentsNode]
    type_identifier_list: List[TypeIdentifierNode]

class IfStatementNode(MyNode):
    alternative: Optional[StatementNode]
    condition: ConditionNode
    consequence: StatementNode

class ImportDeclarationNode(MyNode):
    asterisk_list: List[AsteriskNode]
    identifier_list: List[IdentifierNode]
    scoped_identifier_list: List[ScopedIdentifierNode]

class InferredParametersNode(MyNode):
    identifier_list: List[IdentifierNode]

class InstanceofExpressionNode(MyNode):
    left: ExpressionNode
    name: Optional[IdentifierNode]
    right: TypeNode

type IntegralTypeNode = MyNode
class InterfaceBodyNode(MyNode):
    annotation_type_declaration_list: Optional[List[AnnotationTypeDeclarationNode]]
    class_declaration_list: Optional[List[ClassDeclarationNode]]
    constant_declaration_list: Optional[List[ConstantDeclarationNode]]
    enum_declaration_list: Optional[List[EnumDeclarationNode]]
    interface_declaration_list: Optional[List[InterfaceDeclarationNode]]
    method_declaration_list: Optional[List[MethodDeclarationNode]]
    record_declaration_list: Optional[List[RecordDeclarationNode]]

class InterfaceDeclarationNode(MyNode):
    body: InterfaceBodyNode
    name: IdentifierNode
    permits: Optional[PermitsNode]
    type_parameters: Optional[TypeParametersNode]
    extends_interfaces_list: Optional[List[ExtendsInterfacesNode]]
    modifiers_list: Optional[List[ModifiersNode]]

class LabeledStatementNode(MyNode):
    identifier_list: List[IdentifierNode]
    statement_list: List[StatementNode]

class LambdaExpressionNode(MyNode):
    body: BlockNode | ExpressionNode
    parameters: FormalParametersNode | IdentifierNode | InferredParametersNode

class LocalVariableDeclarationNode(MyNode):
    declarator: List[VariableDeclaratorNode]
    type: UnannotatedTypeNode
    modifiers: Optional[ModifiersNode]

class MarkerAnnotationNode(MyNode):
    name: IdentifierNode | ScopedIdentifierNode

class MethodDeclarationNode(MyNode):
    body: Optional[BlockNode]
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    parameters: FormalParametersNode
    type: UnannotatedTypeNode
    type_parameters: Optional[TypeParametersNode]
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]
    modifiers_list: Optional[List[ModifiersNode]]
    throws_list: Optional[List[ThrowsNode]]

class MethodInvocationNode(MyNode):
    arguments: ArgumentListNode
    name: IdentifierNode
    object: Optional[PrimaryExpressionNode | SuperNode]
    type_arguments: Optional[TypeArgumentsNode]
    super: Optional[SuperNode]

class MethodReferenceNode(MyNode):
    _type_list: List[TypeNode]
    primary_expression_list: List[PrimaryExpressionNode]
    super_list: List[SuperNode]
    type_arguments_list: List[TypeArgumentsNode]

class ModifiersNode(MyNode):
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

class ModuleBodyNode(MyNode):
    module_directive_list: Optional[List[ModuleDirectiveNode]]

class ModuleDeclarationNode(MyNode):
    body: ModuleBodyNode
    name: IdentifierNode | ScopedIdentifierNode
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]

type MultilineStringFragmentNode = MyNode
class ObjectCreationExpressionNode(MyNode):
    arguments: ArgumentListNode
    type: SimpleTypeNode
    type_arguments: Optional[TypeArgumentsNode]
    class_body_list: Optional[List[ClassBodyNode]]
    primary_expression_list: Optional[List[PrimaryExpressionNode]]

class OpensModuleDirectiveNode(MyNode):
    modules: Optional[List[IdentifierNode | ScopedIdentifierNode]]
    package: IdentifierNode | ScopedIdentifierNode

class PackageDeclarationNode(MyNode):
    annotation_list: List[AnnotationNode]
    identifier_list: List[IdentifierNode]
    marker_annotation_list: List[MarkerAnnotationNode]
    scoped_identifier_list: List[ScopedIdentifierNode]

class ParenthesizedExpressionNode(MyNode):
    expression: ExpressionNode

class PermitsNode(MyNode):
    type_list: TypeListNode

class ProgramNode(MyNode):
    statement_list: Optional[List[StatementNode]]

class ProvidesModuleDirectiveNode(MyNode):
    provided: IdentifierNode | ScopedIdentifierNode
    provider: Optional[List[IdentifierNode | ScopedIdentifierNode]]
    identifier: IdentifierNode
    scoped_identifier: ScopedIdentifierNode

class ReceiverParameterNode(MyNode):
    _unannotated_type_list: List[UnannotatedTypeNode]
    annotation_list: List[AnnotationNode]
    identifier_list: List[IdentifierNode]
    marker_annotation_list: List[MarkerAnnotationNode]
    this_list: List[ThisNode]

class RecordDeclarationNode(MyNode):
    body: ClassBodyNode
    interfaces: Optional[SuperInterfacesNode]
    name: IdentifierNode
    parameters: FormalParametersNode
    type_parameters: Optional[TypeParametersNode]
    modifiers: Optional[ModifiersNode]

type RequiresModifierNode = MyNode
class RequiresModuleDirectiveNode(MyNode):
    modifiers: Optional[List[RequiresModifierNode]]
    module: IdentifierNode | ScopedIdentifierNode

class ResourceNode(MyNode):
    dimensions: Optional[DimensionsNode]
    name: Optional[IdentifierNode]
    type: Optional[UnannotatedTypeNode]
    value: Optional[ExpressionNode]
    field_access: Optional[FieldAccessNode]
    identifier: Optional[IdentifierNode]
    modifiers: Optional[ModifiersNode]

class ResourceSpecificationNode(MyNode):
    resource_list: List[ResourceNode]

class ReturnStatementNode(MyNode):
    expression: Optional[ExpressionNode]

class ScopedIdentifierNode(MyNode):
    name: IdentifierNode
    scope: IdentifierNode | ScopedIdentifierNode

class ScopedTypeIdentifierNode(MyNode):
    annotation_list: List[AnnotationNode]
    generic_type_list: List[GenericTypeNode]
    marker_annotation_list: List[MarkerAnnotationNode]
    scoped_type_identifier_list: List[ScopedTypeIdentifierNode]
    type_identifier_list: List[TypeIdentifierNode]

class SpreadParameterNode(MyNode):
    _unannotated_type_list: List[UnannotatedTypeNode]
    modifiers_list: List[ModifiersNode]
    variable_declarator_list: List[VariableDeclaratorNode]

class StaticInitializerNode(MyNode):
    block: BlockNode

class StringLiteralNode(MyNode):
    escape_sequence_list: Optional[List[EscapeSequenceNode]]
    multiline_string_fragment_list: Optional[List[MultilineStringFragmentNode]]
    string_fragment_list: Optional[List[StringFragmentNode]]

class SuperInterfacesNode(MyNode):
    type_list: TypeListNode

class SuperclassNode(MyNode):
    _type: TypeNode

class SwitchBlockNode(MyNode):
    switch_block_statement_group_list: Optional[List[SwitchBlockStatementGroupNode]]
    switch_rule_list: Optional[List[SwitchRuleNode]]

class SwitchBlockStatementGroupNode(MyNode):
    statement_list: List[StatementNode]
    switch_label_list: List[SwitchLabelNode]

class SwitchExpressionNode(MyNode):
    body: SwitchBlockNode
    condition: ParenthesizedExpressionNode

class SwitchLabelNode(MyNode):
    expression_list: Optional[List[ExpressionNode]]

class SwitchRuleNode(MyNode):
    block_list: List[BlockNode]
    expression_statement_list: List[ExpressionStatementNode]
    switch_label_list: List[SwitchLabelNode]
    throw_statement_list: List[ThrowStatementNode]

class SynchronizedStatementNode(MyNode):
    body: BlockNode
    parenthesized_expression: ParenthesizedExpressionNode

class TernaryExpressionNode(MyNode):
    alternative: ExpressionNode
    condition: ExpressionNode
    consequence: ExpressionNode

class ThrowStatementNode(MyNode):
    expression: ExpressionNode

class ThrowsNode(MyNode):
    _type_list: List[TypeNode]

class TryStatementNode(MyNode):
    body: BlockNode
    catch_clause_list: List[CatchClauseNode]
    finally_clause_list: List[FinallyClauseNode]

class TryWithResourcesStatementNode(MyNode):
    body: BlockNode
    resources: ResourceSpecificationNode
    catch_clause_list: Optional[List[CatchClauseNode]]
    finally_clause_list: Optional[List[FinallyClauseNode]]

class TypeArgumentsNode(MyNode):
    _type_list: Optional[List[TypeNode]]
    wildcard_list: Optional[List[WildcardNode]]

class TypeBoundNode(MyNode):
    _type_list: List[TypeNode]

class TypeListNode(MyNode):
    _type_list: List[TypeNode]

class TypeParameterNode(MyNode):
    annotation_list: List[AnnotationNode]
    marker_annotation_list: List[MarkerAnnotationNode]
    type_bound_list: List[TypeBoundNode]
    type_identifier_list: List[TypeIdentifierNode]

class TypeParametersNode(MyNode):
    type_parameter_list: List[TypeParameterNode]

class UnaryExpressionNode(MyNode):
    operand: ExpressionNode

class UpdateExpressionNode(MyNode):
    expression: ExpressionNode

class UsesModuleDirectiveNode(MyNode):
    type: IdentifierNode | ScopedIdentifierNode

class VariableDeclaratorNode(MyNode):
    dimensions: Optional[DimensionsNode]
    name: IdentifierNode
    value: Optional[ArrayInitializerNode | ExpressionNode]

class WhileStatementNode(MyNode):
    body: StatementNode
    condition: ConditionNode

class WildcardNode(MyNode):
    _type_list: Optional[List[TypeNode]]
    annotation_list: Optional[List[AnnotationNode]]
    marker_annotation_list: Optional[List[MarkerAnnotationNode]]
    super_list: Optional[List[SuperNode]]

class YieldStatementNode(MyNode):
    expression: ExpressionNode

type BinaryIntegerLiteralNode = MyNode
type BlockCommentNode = MyNode
type BooleanTypeNode = MyNode
type CharacterLiteralNode = MyNode
type DecimalFloatingPointLiteralNode = MyNode
type DecimalIntegerLiteralNode = MyNode
type EscapeSequenceNode = MyNode
type FalseNode = MyNode
type HexFloatingPointLiteralNode = MyNode
type HexIntegerLiteralNode = MyNode
type IdentifierNode = MyNode
type LineCommentNode = MyNode
type NullLiteralNode = MyNode
type OctalIntegerLiteralNode = MyNode
type StringFragmentNode = MyNode
type SuperNode = MyNode
type ThisNode = MyNode
type TrueNode = MyNode
type TypeIdentifierNode = MyNode
type VoidTypeNode = MyNode
