"""
Model Schema Extractor - Parse DTO/Model classes for request/response body schemas

Extracts:
- Field names and types
- Validation annotations (@NotNull, @Size, @Email, etc.)
- Required vs optional fields
- Nested object structures
- Generic types (List<Item>, Map<String, Object>)

This enables LLM to generate proper request payloads and response assertions.
"""

import javalang
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import json


@dataclass
class FieldSchema:
    """Schema for a single field"""
    name: str
    type: str
    required: bool = False
    validations: List[str] = field(default_factory=list)
    default_value: Optional[str] = None
    description: Optional[str] = None
    nested_schema: Optional[Dict] = None  # For complex types
    is_collection: bool = False
    collection_type: Optional[str] = None  # List, Set, Map


@dataclass 
class ModelSchema:
    """Complete schema for a DTO/Model class"""
    class_name: str
    package_name: str
    fields: List[FieldSchema] = field(default_factory=list)
    file_path: Optional[str] = None


class ModelSchemaExtractor:
    """
    Extracts schema information from Java DTO/Model classes.
    
    Used to understand:
    - @RequestBody payload structure
    - @ResponseBody return structure
    - Validation requirements
    """
    
    # Validation annotations that imply required
    REQUIRED_ANNOTATIONS = {
        'NotNull', 'NotEmpty', 'NotBlank', 'NonNull'
    }
    
    # All validation annotations to capture
    VALIDATION_ANNOTATIONS = {
        'NotNull', 'NotEmpty', 'NotBlank', 'NonNull',
        'Size', 'Min', 'Max', 'Range',
        'Email', 'Pattern', 'URL',
        'Positive', 'PositiveOrZero', 'Negative', 'NegativeOrZero',
        'Past', 'PastOrPresent', 'Future', 'FutureOrPresent',
        'Digits', 'DecimalMin', 'DecimalMax',
        'Valid'  # Triggers nested validation
    }
    
    # Common collection types
    COLLECTION_TYPES = {'List', 'Set', 'Collection', 'ArrayList', 'HashSet', 'LinkedList'}
    MAP_TYPES = {'Map', 'HashMap', 'LinkedHashMap', 'TreeMap'}
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.schemas: Dict[str, ModelSchema] = {}  # class_name -> schema
        self._java_files_cache: Dict[str, Path] = {}  # class_name -> file_path
        self._build_file_index()
    
    def _build_file_index(self):
        """Build index of class names to file paths for quick lookup"""
        for java_file in self.repo_path.rglob("*.java"):
            # Simple heuristic: filename often matches class name
            class_name = java_file.stem
            self._java_files_cache[class_name] = java_file
    
    def extract_schema(self, class_name: str) -> Optional[ModelSchema]:
        """
        Extract schema for a given class name.
        
        Args:
            class_name: Simple class name (e.g., "CustomerRequest") or 
                       fully qualified (e.g., "com.bank.dto.CustomerRequest")
            
        Returns:
            ModelSchema with field information, or None if not found
        """
        # Check cache first
        simple_name = class_name.split('.')[-1]
        if simple_name in self.schemas:
            return self.schemas[simple_name]
        
        # Find and parse the class file
        file_path = self._find_class_file(simple_name)
        if not file_path:
            return None
        
        schema = self._parse_class_file(file_path, simple_name)
        if schema:
            self.schemas[simple_name] = schema
        
        return schema
    
    def _find_class_file(self, class_name: str) -> Optional[Path]:
        """Find Java file containing the class definition"""
        # Direct match
        if class_name in self._java_files_cache:
            return self._java_files_cache[class_name]
        
        # Search in all files (for inner classes or different naming)
        for java_file in self.repo_path.rglob("*.java"):
            try:
                content = java_file.read_text(encoding='utf-8')
                if f"class {class_name}" in content or f"record {class_name}" in content:
                    return java_file
            except:
                continue
        
        return None
    
    def _parse_class_file(self, file_path: Path, target_class: str) -> Optional[ModelSchema]:
        """Parse a Java file to extract class schema"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = javalang.parse.parse(content)
            
            package_name = tree.package.name if tree.package else ""
            
            # Find the target class (could be main class or inner class)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                if node.name == target_class:
                    return self._extract_class_schema(node, package_name, file_path)
            
            # Also check record declarations (Java 14+)
            for path, node in tree.filter(javalang.tree.RecordDeclaration):
                if node.name == target_class:
                    return self._extract_record_schema(node, package_name, file_path)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Could not parse {file_path.name} for schema: {e}")
            return None
    
    def _extract_class_schema(self, class_node, package_name: str, file_path: Path) -> ModelSchema:
        """Extract schema from a class declaration"""
        schema = ModelSchema(
            class_name=class_node.name,
            package_name=package_name,
            file_path=str(file_path)
        )
        
        # Extract fields
        for field_decl in class_node.fields:
            field_schemas = self._extract_field_schema(field_decl)
            schema.fields.extend(field_schemas)
        
        # If no fields found, try to infer from constructor or getters
        if not schema.fields:
            schema.fields = self._infer_fields_from_methods(class_node)
        
        return schema
    
    def _extract_record_schema(self, record_node, package_name: str, file_path: Path) -> ModelSchema:
        """Extract schema from a record declaration (Java 14+)"""
        schema = ModelSchema(
            class_name=record_node.name,
            package_name=package_name,
            file_path=str(file_path)
        )
        
        # Record components are essentially the fields
        if hasattr(record_node, 'parameters') and record_node.parameters:
            for param in record_node.parameters:
                field_schema = FieldSchema(
                    name=param.name,
                    type=self._get_type_string(param.type),
                    required=True  # Record components are implicitly required
                )
                
                # Check for annotations on record components
                if param.annotations:
                    for ann in param.annotations:
                        if ann.name in self.REQUIRED_ANNOTATIONS:
                            field_schema.required = True
                        if ann.name in self.VALIDATION_ANNOTATIONS:
                            field_schema.validations.append(self._format_annotation(ann))
                
                schema.fields.append(field_schema)
        
        return schema
    
    def _extract_field_schema(self, field_decl) -> List[FieldSchema]:
        """Extract schema from a field declaration"""
        schemas = []
        
        # A field declaration can have multiple declarators (e.g., int a, b, c;)
        for declarator in field_decl.declarators:
            field_type = self._get_type_string(field_decl.type)
            
            field_schema = FieldSchema(
                name=declarator.name,
                type=field_type
            )
            
            # Check if it's a collection type
            if hasattr(field_decl.type, 'name'):
                if field_decl.type.name in self.COLLECTION_TYPES:
                    field_schema.is_collection = True
                    field_schema.collection_type = field_decl.type.name
                    # Get generic type if available
                    if hasattr(field_decl.type, 'arguments') and field_decl.type.arguments:
                        inner_type = field_decl.type.arguments[0]
                        if hasattr(inner_type, 'type') and hasattr(inner_type.type, 'name'):
                            field_schema.type = f"{field_decl.type.name}<{inner_type.type.name}>"
            
            # Check annotations
            if field_decl.annotations:
                for ann in field_decl.annotations:
                    if ann.name in self.REQUIRED_ANNOTATIONS:
                        field_schema.required = True
                    if ann.name in self.VALIDATION_ANNOTATIONS:
                        field_schema.validations.append(self._format_annotation(ann))
            
            schemas.append(field_schema)
        
        return schemas
    
    def _infer_fields_from_methods(self, class_node) -> List[FieldSchema]:
        """Infer fields from getter methods (useful for classes without explicit fields)"""
        fields = []
        seen_names = set()
        
        for method in class_node.methods:
            # Look for getters
            if method.name.startswith('get') and len(method.name) > 3:
                field_name = method.name[3:]
                field_name = field_name[0].lower() + field_name[1:]
                
                if field_name not in seen_names:
                    seen_names.add(field_name)
                    return_type = self._get_type_string(method.return_type) if method.return_type else "Object"
                    fields.append(FieldSchema(
                        name=field_name,
                        type=return_type
                    ))
            
            # Also check for is* methods (boolean getters)
            elif method.name.startswith('is') and len(method.name) > 2:
                field_name = method.name[2:]
                field_name = field_name[0].lower() + field_name[1:]
                
                if field_name not in seen_names:
                    seen_names.add(field_name)
                    fields.append(FieldSchema(
                        name=field_name,
                        type="boolean"
                    ))
        
        return fields
    
    def _get_type_string(self, type_node) -> str:
        """Convert a type node to a string representation"""
        if type_node is None:
            return "void"
        
        if isinstance(type_node, str):
            return type_node
        
        if hasattr(type_node, 'name'):
            base_type = type_node.name
            
            # Handle qualified types (e.g., java.math.BigDecimal)
            # javalang may provide sub_type for qualified names
            if hasattr(type_node, 'sub_type') and type_node.sub_type:
                # Recursively get the full qualified name
                base_type = self._get_qualified_type(type_node)
            
            # Handle generic types
            if hasattr(type_node, 'arguments') and type_node.arguments:
                generic_args = []
                for arg in type_node.arguments:
                    if hasattr(arg, 'type') and hasattr(arg.type, 'name'):
                        generic_args.append(self._get_type_string(arg.type))
                    elif hasattr(arg, 'name'):
                        generic_args.append(arg.name)
                
                if generic_args:
                    return f"{base_type}<{', '.join(generic_args)}>"
            
            return base_type
        
        # Handle BasicType (primitives)
        if hasattr(type_node, 'dimensions') and hasattr(type_node, 'name'):
            base = type_node.name
            if type_node.dimensions:
                base += "[]" * len(type_node.dimensions)
            return base
        
        return "Unknown"
    
    def _get_qualified_type(self, type_node) -> str:
        """Get fully qualified type name from nested sub_type"""
        parts = [type_node.name]
        
        current = type_node.sub_type
        while current:
            if hasattr(current, 'name'):
                parts.append(current.name)
            if hasattr(current, 'sub_type'):
                current = current.sub_type
            else:
                break
        
        # Return just the last part (simple name) for cleaner output
        # e.g., java.math.BigDecimal -> BigDecimal
        return parts[-1] if parts else "Unknown"
    
    def _format_annotation(self, annotation) -> str:
        """Format an annotation for display"""
        ann_str = f"@{annotation.name}"
        
        if annotation.element:
            # Simple value
            if isinstance(annotation.element, javalang.tree.Literal):
                ann_str += f"({annotation.element.value})"
            # Named parameters
            elif isinstance(annotation.element, list):
                params = []
                for pair in annotation.element:
                    if hasattr(pair, 'name') and hasattr(pair, 'value'):
                        if isinstance(pair.value, javalang.tree.Literal):
                            params.append(f"{pair.name}={pair.value.value}")
                if params:
                    ann_str += f"({', '.join(params)})"
        
        return ann_str
    
    def to_dict(self, schema: ModelSchema) -> Dict[str, Any]:
        """Convert ModelSchema to dictionary for JSON serialization"""
        return {
            "class_name": schema.class_name,
            "package_name": schema.package_name,
            "file_path": schema.file_path,
            "fields": [
                {
                    "name": f.name,
                    "type": f.type,
                    "required": f.required,
                    "validations": f.validations,
                    "default_value": f.default_value,
                    "is_collection": f.is_collection,
                    "collection_type": f.collection_type
                }
                for f in schema.fields
            ]
        }
    
    def extract_schemas_for_endpoints(self, entry_points: List[Dict]) -> Dict[str, Dict]:
        """
        Extract schemas for all request/response body types used in endpoints.
        
        Args:
            entry_points: List of entry points with parameter info
            
        Returns:
            Dict mapping type names to their schemas
        """
        schemas = {}
        types_to_extract = set()
        
        # Collect all @RequestBody types
        for ep in entry_points:
            params = ep.get('details', {}).get('parameters', [])
            for param in params:
                if 'RequestBody' in param.get('annotations', []):
                    types_to_extract.add(param.get('type', ''))
        
        # Extract schemas for each type
        for type_name in types_to_extract:
            if type_name and type_name not in ('Object', 'String', 'Map'):
                schema = self.extract_schema(type_name)
                if schema:
                    schemas[type_name] = self.to_dict(schema)
        
        return schemas


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python model_schema_extractor.py <repo_path> <class_name>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    class_name = sys.argv[2]
    
    extractor = ModelSchemaExtractor(repo_path)
    schema = extractor.extract_schema(class_name)
    
    if schema:
        print(json.dumps(extractor.to_dict(schema), indent=2))
    else:
        print(f"Could not find schema for: {class_name}")
