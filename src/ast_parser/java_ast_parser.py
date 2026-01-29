"""
AST Parser for Java Source Code
Uses javalang to parse Java files and extract entry points
"""

import javalang
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class EntryPoint:
    """Represents an application entry point"""
    type: str  # REST, CLI, BATCH, SCHEDULED, MESSAGE_CONSUMER
    class_name: str
    method_name: str
    file_path: str
    details: Dict[str, Any] = field(default_factory=dict)


class JavaASTParser:
    """Parse Java source files to extract entry points"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.entry_points: List[EntryPoint] = []
    
    def parse_repository(self) -> List[EntryPoint]:
        """Parse all Java files in the repository"""
        java_files = list(self.repo_path.rglob("*.java"))
        print(f"\n📂 Found {len(java_files)} Java files")
        
        for java_file in java_files:
            try:
                self.parse_file(java_file)
            except Exception as e:
                print(f"⚠️  Error parsing {java_file.name}: {e}")
        
        return self.entry_points
    
    def parse_file(self, file_path: Path):
        """Parse a single Java file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = javalang.parse.parse(code)
            
            # Extract package and imports for context
            package_name = tree.package.name if tree.package else ""
            
            # Analyze each class
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                self._analyze_class(node, file_path, package_name)
                
        except javalang.parser.JavaSyntaxError as e:
            print(f"⚠️  Syntax error in {file_path.name}: {e}")
        except Exception as e:
            print(f"⚠️  Error processing {file_path.name}: {e}")
    
    def _analyze_class(self, class_node: javalang.tree.ClassDeclaration, 
                       file_path: Path, package_name: str):
        """Analyze a class declaration for entry points"""
        
        # Check class-level annotations
        class_annotations = self._get_annotations(class_node)
        
        # Check for REST controllers
        if self._is_rest_controller(class_annotations):
            self._extract_rest_endpoints(class_node, file_path, package_name, class_annotations)
        
        # Check for JAX-RS resources
        elif self._is_jaxrs_resource(class_annotations):
            self._extract_jaxrs_endpoints(class_node, file_path, package_name, class_annotations)
        
        # Check for Spring Boot application
        elif self._is_spring_boot_app(class_annotations):
            self._extract_main_entry_point(class_node, file_path, package_name)
        
        # Check for message consumers
        elif self._is_message_consumer(class_annotations):
            self._extract_message_listeners(class_node, file_path, package_name)
        
        # Check for batch jobs
        elif self._is_batch_job(class_annotations):
            self._extract_batch_jobs(class_node, file_path, package_name)
        
        # Check for CLI tools (main method)
        elif self._has_main_method(class_node):
            self._extract_cli_entry_point(class_node, file_path, package_name)
        
        # Check for scheduled tasks (independent of other checks)
        # This needs to run AFTER other checks to avoid being caught by elif
        if self._has_scheduled_methods(class_node):
            self._extract_scheduled_tasks(class_node, file_path, package_name)
    
    def _get_annotations(self, node) -> List[str]:
        """Extract annotation names from a node"""
        if not hasattr(node, 'annotations') or not node.annotations:
            return []
        return [ann.name for ann in node.annotations]
    
    def _is_rest_controller(self, annotations: List[str]) -> bool:
        """Check if class is a Spring REST controller"""
        return 'RestController' in annotations or 'Controller' in annotations
    
    def _is_jaxrs_resource(self, annotations: List[str]) -> bool:
        """Check if class is a JAX-RS resource"""
        return 'Path' in annotations
    
    def _is_spring_boot_app(self, annotations: List[str]) -> bool:
        """Check if class is Spring Boot application"""
        return 'SpringBootApplication' in annotations
    
    def _is_message_consumer(self, annotations: List[str]) -> bool:
        """Check if class is a message consumer"""
        return 'Component' in annotations or 'Service' in annotations
    
    def _is_batch_job(self, annotations: List[str]) -> bool:
        """Check if class is a batch job configuration"""
        return 'Configuration' in annotations and 'EnableBatchProcessing' in annotations
    
    def _has_scheduled_methods(self, class_node) -> bool:
        """Check if class has scheduled methods"""
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            if 'Scheduled' in method_annotations:
                return True
        return False
    
    def _has_main_method(self, class_node) -> bool:
        """Check if class has a main method"""
        for method in class_node.methods:
            if (method.name == 'main' and 
                'static' in method.modifiers and 
                'public' in method.modifiers):
                return True
        return False
    
    def _extract_rest_endpoints(self, class_node, file_path: Path, 
                                package_name: str, class_annotations: List[str]):
        """Extract REST endpoints from Spring controller"""
        base_path = self._extract_request_mapping(class_node)
        
        # Check class-level security
        class_security = self._extract_security_annotations(class_node)
        
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            
            # Check for mapping annotations
            mapping_types = ['GetMapping', 'PostMapping', 'PutMapping', 
                            'DeleteMapping', 'PatchMapping', 'RequestMapping']
            
            for mapping in mapping_types:
                if mapping in method_annotations:
                    http_method = self._get_http_method(mapping, method)
                    path = self._extract_method_path(method, method_annotations)
                    full_path = f"{base_path}{path}".replace('//', '/')
                    
                    # Ensure path starts with /
                    if full_path and not full_path.startswith('/'):
                        full_path = '/' + full_path
                    
                    # Extract method-level security (overrides class-level)
                    method_security = self._extract_security_annotations(method)
                    security = method_security if method_security else class_security
                    
                    # Extract return type
                    return_type = self._extract_return_type(method)
                    
                    entry_point = EntryPoint(
                        type="REST",
                        class_name=f"{package_name}.{class_node.name}",
                        method_name=method.name,
                        file_path=str(file_path),
                        details={
                            "http_method": http_method,
                            "path": full_path,
                            "parameters": self._extract_parameters(method),
                            "return_type": return_type,
                            "security": security
                        }
                    )
                    self.entry_points.append(entry_point)
    
    def _extract_jaxrs_endpoints(self, class_node, file_path: Path, 
                                 package_name: str, class_annotations: List[str]):
        """Extract JAX-RS REST endpoints"""
        base_path = self._extract_path_annotation(class_node)
        
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            
            # Check for HTTP method annotations
            http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
            
            for http_method in http_methods:
                if http_method in method_annotations:
                    path = self._extract_path_annotation(method)
                    full_path = f"{base_path}{path}".replace('//', '/')
                    
                    entry_point = EntryPoint(
                        type="REST",
                        class_name=f"{package_name}.{class_node.name}",
                        method_name=method.name,
                        file_path=str(file_path),
                        details={
                            "http_method": http_method,
                            "path": full_path,
                            "framework": "JAX-RS",
                            "parameters": self._extract_parameters(method)
                        }
                    )
                    self.entry_points.append(entry_point)
    
    def _extract_main_entry_point(self, class_node, file_path: Path, package_name: str):
        """Extract Spring Boot main application entry point"""
        entry_point = EntryPoint(
            type="MAIN_APPLICATION",
            class_name=f"{package_name}.{class_node.name}",
            method_name="main",
            file_path=str(file_path),
            details={
                "annotation": "SpringBootApplication",
                "description": "Application startup entry point"
            }
        )
        self.entry_points.append(entry_point)
    
    def _extract_message_listeners(self, class_node, file_path: Path, package_name: str):
        """Extract message consumer entry points"""
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            
            if 'KafkaListener' in method_annotations:
                topics = self._extract_annotation_param(method, 'KafkaListener', 'topics')
                entry_point = EntryPoint(
                    type="MESSAGE_CONSUMER",
                    class_name=f"{package_name}.{class_node.name}",
                    method_name=method.name,
                    file_path=str(file_path),
                    details={
                        "consumer_type": "Kafka",
                        "topics": topics,
                        "parameters": self._extract_parameters(method)
                    }
                )
                self.entry_points.append(entry_point)
            
            elif 'JmsListener' in method_annotations:
                destination = self._extract_annotation_param(method, 'JmsListener', 'destination')
                entry_point = EntryPoint(
                    type="MESSAGE_CONSUMER",
                    class_name=f"{package_name}.{class_node.name}",
                    method_name=method.name,
                    file_path=str(file_path),
                    details={
                        "consumer_type": "JMS",
                        "destination": destination,
                        "parameters": self._extract_parameters(method)
                    }
                )
                self.entry_points.append(entry_point)
    
    def _extract_batch_jobs(self, class_node, file_path: Path, package_name: str):
        """Extract Spring Batch job entry points"""
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            
            if 'Bean' in method_annotations and method.return_type and 'Job' in str(method.return_type.name):
                entry_point = EntryPoint(
                    type="BATCH_JOB",
                    class_name=f"{package_name}.{class_node.name}",
                    method_name=method.name,
                    file_path=str(file_path),
                    details={
                        "job_type": "Spring Batch",
                        "description": f"Batch job: {method.name}"
                    }
                )
                self.entry_points.append(entry_point)
    
    def _extract_scheduled_tasks(self, class_node, file_path: Path, package_name: str):
        """Extract scheduled task entry points"""
        for method in class_node.methods:
            method_annotations = self._get_annotations(method)
            
            if 'Scheduled' in method_annotations:
                schedule_info = self._extract_schedule_info(method)
                entry_point = EntryPoint(
                    type="SCHEDULED_TASK",
                    class_name=f"{package_name}.{class_node.name}",
                    method_name=method.name,
                    file_path=str(file_path),
                    details={
                        "schedule": schedule_info,
                        "description": f"Scheduled task: {method.name}"
                    }
                )
                self.entry_points.append(entry_point)
    
    def _extract_cli_entry_point(self, class_node, file_path: Path, package_name: str):
        """Extract CLI main method entry point"""
        entry_point = EntryPoint(
            type="CLI",
            class_name=f"{package_name}.{class_node.name}",
            method_name="main",
            file_path=str(file_path),
            details={
                "description": "Command-line interface entry point"
            }
        )
        self.entry_points.append(entry_point)
    
    # Helper methods
    
    def _extract_request_mapping(self, class_node) -> str:
        """Extract RequestMapping value from class"""
        for annotation in class_node.annotations:
            if annotation.name == 'RequestMapping':
                # Handle direct literal value: @RequestMapping("/api/v1/customers")
                if annotation.element:
                    if isinstance(annotation.element, javalang.tree.Literal):
                        return annotation.element.value.strip('"')
                    
                    # Handle array literal: @RequestMapping({"/api/v1/customers"})
                    if isinstance(annotation.element, javalang.tree.ElementArrayValue):
                        if annotation.element.values:
                            first_val = annotation.element.values[0]
                            if isinstance(first_val, javalang.tree.Literal):
                                return first_val.value.strip('"')
                    
                    # Handle named parameters: @RequestMapping(value = "/api/v1/customers")
                    if isinstance(annotation.element, list):
                        for pair in annotation.element:
                            if hasattr(pair, 'name') and pair.name in ['value', 'path']:
                                if isinstance(pair.value, javalang.tree.Literal):
                                    return pair.value.value.strip('"')
                                elif isinstance(pair.value, javalang.tree.ElementArrayValue):
                                    if pair.value.values:
                                        first_val = pair.value.values[0]
                                        if isinstance(first_val, javalang.tree.Literal):
                                            return first_val.value.strip('"')
                    
                    # Handle ElementValuePair with values attribute
                    if hasattr(annotation.element, 'values'):
                        for value in annotation.element.values:
                            if hasattr(value, 'value') and isinstance(value.value, javalang.tree.Literal):
                                return value.value.value.strip('"')
        return ""
    
    def _extract_path_annotation(self, node) -> str:
        """Extract Path annotation value"""
        if not hasattr(node, 'annotations'):
            return ""
        
        for annotation in node.annotations:
            if annotation.name == 'Path':
                if annotation.element:
                    if isinstance(annotation.element, javalang.tree.Literal):
                        return annotation.element.value.strip('"')
        return ""
    
    def _get_http_method(self, mapping_annotation: str, method) -> str:
        """Determine HTTP method from annotation"""
        mapping_to_http = {
            'GetMapping': 'GET',
            'PostMapping': 'POST',
            'PutMapping': 'PUT',
            'DeleteMapping': 'DELETE',
            'PatchMapping': 'PATCH',
            'RequestMapping': 'GET'  # Default
        }
        return mapping_to_http.get(mapping_annotation, 'GET')
    
    def _extract_method_path(self, method, annotations: List[str]) -> str:
        """Extract path from method mapping annotation"""
        for annotation in method.annotations:
            if annotation.name in ['GetMapping', 'PostMapping', 'PutMapping', 
                                   'DeleteMapping', 'PatchMapping', 'RequestMapping']:
                if annotation.element:
                    if isinstance(annotation.element, javalang.tree.Literal):
                        return annotation.element.value.strip('"')
        return ""
    
    def _extract_parameters(self, method) -> List[Dict[str, Any]]:
        """Extract method parameters with full details including defaults and required flags"""
        params = []
        if method.parameters:
            for param in method.parameters:
                param_info = {
                    "name": param.name,
                    "type": str(param.type.name) if param.type else "Unknown"
                }
                
                # Check for parameter annotations
                if param.annotations:
                    param_info["annotations"] = [ann.name for ann in param.annotations]
                    
                    # Extract details from specific annotations
                    for ann in param.annotations:
                        if ann.name == 'RequestParam':
                            param_info["param_type"] = "query"
                            self._extract_request_param_details(ann, param_info)
                        elif ann.name == 'PathVariable':
                            param_info["param_type"] = "path"
                            param_info["required"] = True
                        elif ann.name == 'RequestBody':
                            param_info["param_type"] = "body"
                            param_info["required"] = True
                        elif ann.name == 'RequestHeader':
                            param_info["param_type"] = "header"
                            self._extract_request_param_details(ann, param_info)
                
                params.append(param_info)
        return params
    
    def _extract_request_param_details(self, annotation, param_info: Dict):
        """Extract defaultValue, required from @RequestParam or similar annotations"""
        if annotation.element:
            # Handle list of ElementValuePair
            if isinstance(annotation.element, list):
                for pair in annotation.element:
                    if hasattr(pair, 'name') and hasattr(pair, 'value'):
                        if pair.name == 'defaultValue':
                            if isinstance(pair.value, javalang.tree.Literal):
                                param_info["default_value"] = pair.value.value.strip('"')
                        elif pair.name == 'required':
                            if isinstance(pair.value, javalang.tree.Literal):
                                param_info["required"] = pair.value.value == 'true'
                            elif isinstance(pair.value, javalang.tree.MemberReference):
                                param_info["required"] = str(pair.value.member) == 'true'
                        elif pair.name == 'value' or pair.name == 'name':
                            if isinstance(pair.value, javalang.tree.Literal):
                                param_info["alias"] = pair.value.value.strip('"')
    
    def _extract_security_annotations(self, node) -> Optional[Dict[str, Any]]:
        """Extract security annotations from class or method"""
        if not hasattr(node, 'annotations') or not node.annotations:
            return None
        
        security_info = {}
        
        for ann in node.annotations:
            # Spring Security annotations
            if ann.name == 'PreAuthorize':
                security_info['type'] = 'PreAuthorize'
                security_info['requires_auth'] = True
                if ann.element:
                    if isinstance(ann.element, javalang.tree.Literal):
                        security_info['expression'] = ann.element.value.strip('"')
                        # Parse roles from expression like "hasRole('ADMIN')"
                        expr = security_info['expression']
                        if 'hasRole' in expr or 'hasAuthority' in expr:
                            import re
                            roles = re.findall(r"'([^']+)'", expr)
                            security_info['roles'] = roles
            
            elif ann.name == 'Secured':
                security_info['type'] = 'Secured'
                security_info['requires_auth'] = True
                if ann.element:
                    if isinstance(ann.element, javalang.tree.ElementArrayValue):
                        roles = []
                        for val in ann.element.values:
                            if isinstance(val, javalang.tree.Literal):
                                roles.append(val.value.strip('"'))
                        security_info['roles'] = roles
                    elif isinstance(ann.element, javalang.tree.Literal):
                        security_info['roles'] = [ann.element.value.strip('"')]
            
            elif ann.name == 'RolesAllowed':
                security_info['type'] = 'RolesAllowed'
                security_info['requires_auth'] = True
                if ann.element:
                    if isinstance(ann.element, javalang.tree.ElementArrayValue):
                        roles = []
                        for val in ann.element.values:
                            if isinstance(val, javalang.tree.Literal):
                                roles.append(val.value.strip('"'))
                        security_info['roles'] = roles
                    elif isinstance(ann.element, javalang.tree.Literal):
                        security_info['roles'] = [ann.element.value.strip('"')]
            
            elif ann.name == 'PermitAll':
                security_info['type'] = 'PermitAll'
                security_info['requires_auth'] = False
            
            elif ann.name == 'DenyAll':
                security_info['type'] = 'DenyAll'
                security_info['requires_auth'] = True
                security_info['denied'] = True
        
        return security_info if security_info else None
    
    def _extract_return_type(self, method) -> Optional[str]:
        """Extract return type from method"""
        if not method.return_type:
            return "void"
        
        type_name = method.return_type.name if hasattr(method.return_type, 'name') else str(method.return_type)
        
        # Handle generic types like ResponseEntity<Customer>
        if hasattr(method.return_type, 'arguments') and method.return_type.arguments:
            generic_args = []
            for arg in method.return_type.arguments:
                if hasattr(arg, 'type') and hasattr(arg.type, 'name'):
                    generic_args.append(arg.type.name)
                elif hasattr(arg, 'name'):
                    generic_args.append(arg.name)
            
            if generic_args:
                return f"{type_name}<{', '.join(generic_args)}>"
        
        return type_name
    
    def _extract_annotation_param(self, method, annotation_name: str, param_name: str) -> str:
        """Extract parameter value from annotation"""
        for annotation in method.annotations:
            if annotation.name == annotation_name:
                # Handle direct literal value (e.g., @KafkaListener("topic-name"))
                if annotation.element and isinstance(annotation.element, javalang.tree.Literal):
                    return annotation.element.value.strip('"')
                
                # Handle list of ElementValuePair (most common case)
                if annotation.element and isinstance(annotation.element, list):
                    for pair in annotation.element:
                        if hasattr(pair, 'name') and pair.name == param_name:
                            if isinstance(pair.value, javalang.tree.Literal):
                                return pair.value.value.strip('"')
                            # Handle array of literals
                            elif hasattr(pair.value, 'values'):
                                topics = []
                                for item in pair.value.values:
                                    if isinstance(item, javalang.tree.Literal):
                                        topics.append(item.value.strip('"'))
                                return ", ".join(topics)
                
                # Handle named parameters with values attribute (alternative structure)
                if annotation.element and hasattr(annotation.element, 'values'):
                    for value in annotation.element.values:
                        if hasattr(value, 'name') and value.name == param_name:
                            if isinstance(value.value, javalang.tree.Literal):
                                return value.value.value.strip('"')
                            # Handle array of literals
                            elif hasattr(value.value, 'values'):
                                topics = []
                                for item in value.value.values:
                                    if isinstance(item, javalang.tree.Literal):
                                        topics.append(item.value.strip('"'))
                                return ", ".join(topics)
                
                # Handle single parameter without name
                if annotation.element and hasattr(annotation.element, 'value'):
                    if isinstance(annotation.element.value, javalang.tree.Literal):
                        return annotation.element.value.value.strip('"')
        
        return ""
    
    def _extract_schedule_info(self, method) -> str:
        """Extract scheduling information"""
        for annotation in method.annotations:
            if annotation.name == 'Scheduled':
                # Handle list of ElementValuePair (most common)
                if annotation.element and isinstance(annotation.element, list):
                    schedule_parts = []
                    for pair in annotation.element:
                        if hasattr(pair, 'name') and hasattr(pair, 'value'):
                            value_str = str(pair.value.value) if isinstance(pair.value, javalang.tree.Literal) else str(pair.value)
                            value_str = value_str.strip('"')
                            schedule_parts.append(f"{pair.name}={value_str}")
                    if schedule_parts:
                        return ", ".join(schedule_parts)
                
                # Handle alternative structure with values attribute
                if annotation.element and hasattr(annotation.element, 'values'):
                    schedule_parts = []
                    for value in annotation.element.values:
                        if hasattr(value, 'name') and hasattr(value, 'value'):
                            schedule_parts.append(f"{value.name}={value.value}")
                    if schedule_parts:
                        return ", ".join(schedule_parts)
        
        return "Unknown schedule"
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a summary report of discovered entry points"""
        report = {
            "total_entry_points": len(self.entry_points),
            "by_type": {},
            "entry_points": []
        }
        
        # Group by type
        for ep in self.entry_points:
            if ep.type not in report["by_type"]:
                report["by_type"][ep.type] = 0
            report["by_type"][ep.type] += 1
            
            report["entry_points"].append({
                "type": ep.type,
                "class": ep.class_name,
                "method": ep.method_name,
                "file": ep.file_path,
                "details": ep.details
            })
        
        return report
    
    def print_summary(self):
        """Print a formatted summary of discovered entry points"""
        print(f"\n{'='*70}")
        print(f"🔍 AST ANALYSIS SUMMARY")
        print(f"{'='*70}")
        print(f"\n📊 Total Entry Points Found: {len(self.entry_points)}")
        
        # Group by type
        by_type = {}
        for ep in self.entry_points:
            if ep.type not in by_type:
                by_type[ep.type] = []
            by_type[ep.type].append(ep)
        
        # Print by type
        for ep_type, eps in by_type.items():
            print(f"\n{'─'*70}")
            print(f"📌 {ep_type} ({len(eps)} found)")
            print(f"{'─'*70}")
            
            for ep in eps:
                print(f"\n  Class: {ep.class_name}")
                print(f"  Method: {ep.method_name}")
                print(f"  File: {Path(ep.file_path).name}")
                
                if ep.type == "REST":
                    print(f"  → {ep.details.get('http_method', 'GET')} {ep.details.get('path', '/')}")
                    if ep.details.get('parameters'):
                        print(f"  Parameters: {len(ep.details['parameters'])}")
                
                elif ep.type == "MESSAGE_CONSUMER":
                    consumer_type = ep.details.get('consumer_type', 'Unknown')
                    topic = ep.details.get('topics') or ep.details.get('destination')
                    print(f"  → {consumer_type} Consumer")
                    print(f"  Topic/Destination: {topic}")
                
                elif ep.type == "SCHEDULED_TASK":
                    print(f"  → {ep.details.get('schedule', 'Unknown schedule')}")
                
                elif ep.type == "BATCH_JOB":
                    print(f"  → {ep.details.get('description', 'Batch job')}")
        
        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python java_ast_parser.py <path_to_java_repo>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    
    if not repo_path.exists():
        print(f"Error: Path {repo_path} does not exist")
        sys.exit(1)
    
    parser = JavaASTParser(repo_path)
    entry_points = parser.parse_repository()
    parser.print_summary()
    
    # Save report
    report = parser.generate_report()
    output_file = Path("ast_analysis_report.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {output_file}")
