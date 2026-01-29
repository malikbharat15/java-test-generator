"""
Prompt Builder - Dynamically Composes Prompts

Analyzes application AST + config to select appropriate prompt template
and inject actual application data.
"""

import json
from typing import Dict, List, Any
from .prompts import *


class PromptBuilder:
    """
    Builds production-grade prompts by:
    1. Detecting application type from entry points
    2. Selecting specialized prompt template
    3. Injecting actual application data
    4. Composing complete prompt for LLM
    """
    
    def __init__(self):
        self.prompt_registry = {
            'REST_API': (REST_API_PROMPT, self._has_rest_endpoints),
            'GRAPHQL': (GRAPHQL_PROMPT, self._has_graphql),
            'GRPC': (GRPC_PROMPT, self._has_grpc),
            'KAFKA': (KAFKA_TEST_PROMPT, self._has_kafka),
            'JMS': (JMS_PROMPT, self._has_jms),
            'SCHEDULED': (SCHEDULED_JOBS_PROMPT, self._has_scheduled),
            'REACTIVE': (REACTIVE_PROMPT, self._has_reactive),
            'UI': (UI_TEST_PROMPT, self._has_ui),
            'WEBSOCKET': (WEBSOCKET_PROMPT, self._has_websocket),
            'SOAP': (SOAP_PROMPT, self._has_soap),
            'BATCH': (BATCH_TEST_PROMPT, self._has_batch),
            'CLI': (CLI_TEST_PROMPT, self._has_cli),
            'ESB': (ESB_PROMPT, self._has_esb)
        }
    
    def build_prompt(self, analysis_json: Dict[str, Any]) -> str:
        """
        Main entry point: Build complete prompt from analysis JSON
        
        Args:
            analysis_json: Complete analysis from Phase 1 + Phase 2
            
        Returns:
            Complete prompt string ready for LLM
        """
        # 1. Detect application type(s)
        detected_types = self._detect_application_types(analysis_json)
        
        # 2. Select primary test strategy (prefer REST API if multiple)
        primary_type = self._select_primary_type(detected_types)
        
        # 3. Get specialized prompt
        specialized_prompt = self._get_specialized_prompt(primary_type)
        
        # 4. Inject application data
        complete_prompt = self._compose_prompt(
            specialized_prompt,
            analysis_json,
            primary_type
        )
        
        return complete_prompt
    
    def _detect_application_types(self, analysis_json: Dict) -> List[str]:
        """Detect all applicable test types from entry points"""
        detected = []
        
        for test_type, (_, detector_func) in self.prompt_registry.items():
            if detector_func(analysis_json):
                detected.append(test_type)
        
        return detected
    
    def _select_primary_type(self, detected_types: List[str]) -> str:
        """Select primary test strategy (priority order)"""
        priority_order = [
            'REST_API', 'GRAPHQL', 'GRPC', 'KAFKA', 'REACTIVE',
            'JMS', 'SCHEDULED', 'WEBSOCKET', 'SOAP', 'BATCH', 'UI', 'CLI', 'ESB'
        ]
        
        for ptype in priority_order:
            if ptype in detected_types:
                return ptype
        
        return 'CLI'  # Fallback
    
    def _get_specialized_prompt(self, test_type: str) -> str:
        """Get specialized prompt for test type"""
        prompt_template, _ = self.prompt_registry.get(test_type, (CLI_TEST_PROMPT, None))
        return BASE_SYSTEM_PROMPT + "\n\n" + prompt_template
    
    def _compose_prompt(self, base_prompt: str, analysis_json: Dict, test_type: str) -> str:
        """Inject actual application data into prompt"""
        
        app_data = self._format_application_data(analysis_json, test_type)
        
        complete_prompt = f"""{base_prompt}

APPLICATION ANALYSIS DATA:
=========================

{app_data}

NOW GENERATE:
============
Based on the application analysis above, generate production-grade smoke tests.
Return ONLY the JSON output as specified in the OUTPUT FORMAT section.
"""
        return complete_prompt
    
    def _format_application_data(self, analysis_json: Dict, test_type: str) -> str:
        """Format application data for LLM consumption"""
        
        meta = analysis_json.get('metadata', {})
        phase1 = analysis_json.get('phase_1_ast_analysis', {})
        phase2 = analysis_json.get('phase_2_configuration', {})
        
        # Detect all types present in the application
        detected_types = self._detect_application_types(analysis_json)
        
        # Extract relevant data based on test type
        if test_type == 'REST_API':
            data = self._format_rest_api_data(phase1, phase2, meta)
            
            # If app also has scheduled tasks, append that section
            if 'SCHEDULED' in detected_types:
                data += self._format_scheduled_data(phase1, phase2, meta)
            
            # If app also has Kafka consumers, append that section  
            if 'KAFKA' in detected_types:
                data += self._format_kafka_section(phase1, phase2, meta)
                
            return data
        elif test_type == 'KAFKA':
            return self._format_kafka_data(phase1, phase2, meta)
        else:
            return self._format_generic_data(phase1, phase2, meta)
    
    def _format_rest_api_data(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Format REST API specific data with comprehensive details for LLM"""
        
        rest_endpoints = phase1.get('entry_points_by_type', {}).get('REST', [])
        app_config = phase2.get('application_config', {})
        deploy_config = phase2.get('deployment_config', {})
        build_config = phase2.get('build_config', {})
        existing_tests = phase2.get('existing_tests', {})
        request_body_schemas = phase1.get('request_body_schemas', {})
        
        # Get DEV route and health endpoint
        dev_route = self._get_dev_route(deploy_config)
        health_endpoint = self._get_health_endpoint(deploy_config)
        context_path = app_config.get('server', {}).get('context_path', app_config.get('context_path', ''))
        
        data = f"""
================================================================================
APPLICATION OVERVIEW
================================================================================
Application Name: {meta.get('application', 'Unknown')}
Base URL (DEV): {dev_route}
Context Path: {context_path}
Health Check Endpoint: {health_endpoint}

================================================================================
EXISTING TEST COVERAGE
================================================================================
Has Existing Tests: {existing_tests.get('has_tests', False)}
Has Smoke Tests: {existing_tests.get('has_smoke_tests', False)}
Test Frameworks Used: {', '.join(existing_tests.get('test_frameworks', [])) or 'None detected'}
Test Libraries: {', '.join(existing_tests.get('test_libraries', [])) or 'None detected'}

================================================================================
BUILD CONFIGURATION  
================================================================================
Build Tool: {build_config.get('build_tool', 'unknown')}
Java Version: {build_config.get('java_version', '11')}
Spring Boot Version: {build_config.get('spring_boot_version', 'N/A')}
Available Test Frameworks: {', '.join(build_config.get('test_frameworks', [])) or 'None in dependencies'}
Available Test Libraries: {', '.join([str(lib) for lib in build_config.get('testing_libraries', [])]) or 'None'}

================================================================================
DEPLOYMENT CONFIGURATION
================================================================================
Platform: {deploy_config.get('platform', 'unknown')}
Environments: {', '.join([str(e) for e in deploy_config.get('environments', [])])}
Routes by Environment:
"""
        # Add routes per environment
        routes = deploy_config.get('routes', {})
        for env, route in routes.items():
            data += f"  - {env}: {route}\n"
        
        if not routes:
            data += "  (No deployment routes configured - will use localhost)\n"
        
        data += f"""
================================================================================
REST ENDPOINTS ({len(rest_endpoints)} total)
================================================================================

IMPORTANT: Generate smoke tests for ALL endpoints listed below.
For each endpoint, I'm providing: HTTP method, full path, parameters with types,
security requirements, and request body schema (if POST/PUT).

"""
        
        # Format each endpoint with full details
        for idx, ep in enumerate(rest_endpoints, 1):
            details = ep.get('details', ep)
            http_method = details.get('http_method', 'GET')
            path = details.get('path', '/')
            params = details.get('parameters', [])
            security = details.get('security', {})
            return_type = details.get('return_type', 'Unknown')
            
            data += f"""
--- Endpoint {idx}: {http_method} {path} ---
Method Name: {ep.get('method_name', 'unknown')}
Controller: {ep.get('class_name', 'unknown')}
Return Type: {return_type}
"""
            
            # Security info
            if security:
                data += f"Security: PROTECTED\n"
                data += f"  - Auth Type: {security.get('type', 'Unknown')}\n"
                if security.get('roles'):
                    data += f"  - Required Roles: {', '.join(security.get('roles', []))}\n"
                if security.get('expression'):
                    data += f"  - Expression: {security.get('expression')}\n"
            else:
                data += "Security: PUBLIC (no authentication required)\n"
            
            # Parameters
            if params:
                data += "Parameters:\n"
                for p in params:
                    param_type = p.get('param_type', 'unknown')
                    param_name = p.get('name', 'unknown')
                    param_java_type = p.get('type', 'String')
                    required = p.get('required', False)
                    default_val = p.get('default_value', None)
                    
                    req_str = "REQUIRED" if required else "optional"
                    default_str = f", default={default_val}" if default_val else ""
                    
                    data += f"  - [{param_type}] {param_name}: {param_java_type} ({req_str}{default_str})\n"
                    
                    # If it's a request body, include schema
                    if param_type == 'body' and param_java_type in request_body_schemas:
                        schema = request_body_schemas[param_java_type]
                        data += f"    Request Body Schema ({param_java_type}):\n"
                        for field in schema.get('fields', []):
                            field_req = "REQUIRED" if field.get('required') else "optional"
                            validations = ', '.join(field.get('validations', []))
                            val_str = f" [{validations}]" if validations else ""
                            data += f"      - {field['name']}: {field['type']} ({field_req}){val_str}\n"
            else:
                data += "Parameters: None\n"
        
        # Add request body schemas section
        if request_body_schemas:
            data += f"""
================================================================================
REQUEST BODY SCHEMAS (for POST/PUT endpoints)
================================================================================
"""
            for schema_name, schema in request_body_schemas.items():
                data += f"""
{schema_name}:
  Package: {schema.get('package_name', 'unknown')}
  Fields:
"""
                for field in schema.get('fields', []):
                    field_req = "REQUIRED" if field.get('required') else "optional"
                    validations = ', '.join(field.get('validations', []))
                    val_str = f" - Validations: {validations}" if validations else ""
                    default_str = f" - Default: {field.get('default_value')}" if field.get('default_value') else ""
                    data += f"    - {field['name']}: {field['type']} ({field_req}){val_str}{default_str}\n"
        
        data += f"""
================================================================================
SMOKE TEST REQUIREMENTS
================================================================================
1. HEALTH CHECK FIRST: Start with {health_endpoint or '/actuator/health'}
2. Cover ALL {len(rest_endpoints)} REST endpoints listed above
3. For PROTECTED endpoints: Include auth header placeholder (Bearer token)
4. For POST/PUT: Use the schemas above to generate valid request bodies
5. For path parameters like {{id}}: Use test values (e.g., "12345", "test-id")
6. Accept status codes: 200, 201, 204, 401, 403 (NOT 500)
7. Test response time < 5000ms for each endpoint
"""
        
        return data
    
    def _format_scheduled_data(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Format scheduled task data as additional section for mixed apps"""
        scheduled_tasks = phase1.get('entry_points_by_type', {}).get('SCHEDULED_TASK', [])
        
        if not scheduled_tasks:
            return ""
        
        data = f"""

================================================================================
SCHEDULED TASKS ({len(scheduled_tasks)} total)
================================================================================

NOTE: These are background scheduled jobs. For smoke testing, verify that:
- The scheduler is enabled and running
- Job management endpoints (if any) are accessible
- Actuator endpoints show scheduled task metrics

"""
        for idx, task in enumerate(scheduled_tasks, 1):
            details = task.get('details', {})
            data += f"""
--- Scheduled Task {idx}: {task.get('method_name', 'unknown')} ---
Class: {task.get('class_name', 'unknown')}
Schedule: {details.get('schedule', 'unknown')}
Description: {details.get('description', 'N/A')}
"""
        
        data += """
SCHEDULED TASK SMOKE TEST GUIDANCE:
- Use /actuator/scheduledtasks endpoint (if available) to verify tasks are registered
- Do NOT trigger scheduled tasks directly in smoke tests
- Verify related REST endpoints for job status/management
"""
        return data
    
    def _format_kafka_section(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Format Kafka consumer data as additional section for mixed apps"""
        kafka_consumers = phase1.get('entry_points_by_type', {}).get('MESSAGE_CONSUMER', [])
        app_config = phase2.get('application_config', {})
        
        if not kafka_consumers:
            return ""
        
        data = f"""

================================================================================
KAFKA CONSUMERS ({len(kafka_consumers)} total)
================================================================================

Bootstrap Servers: {app_config.get('kafka_bootstrap_servers', 'configured in environment')}

NOTE: For smoke testing Kafka consumers, verify:
- Consumer health via actuator endpoints
- Related REST endpoints that interact with consumed messages

"""
        for idx, consumer in enumerate(kafka_consumers, 1):
            details = consumer.get('details', {})
            data += f"""
--- Consumer {idx}: {consumer.get('method_name', 'unknown')} ---
Topic: {details.get('topic', 'unknown')}
Group ID: {details.get('group_id', 'N/A')}
Class: {consumer.get('class_name', 'unknown')}
"""
        
        return data
    
    def _format_kafka_data(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Format Kafka consumer data"""
        kafka_consumers = phase1.get('entry_points_by_type', {}).get('MESSAGE_CONSUMER', [])
        app_config = phase2.get('application_config', {})
        
        data = f"""
Application: {meta.get('application', 'Unknown')}
Kafka Bootstrap Servers: {app_config.get('kafka_bootstrap_servers', 'localhost:9092')}

Kafka Consumers ({len(kafka_consumers)} total):
"""
        for consumer in kafka_consumers:
            data += f"\n  Topic: {consumer.get('topic', 'unknown')} - Method: {consumer.get('method_name', 'N/A')}"
        
        return data
    
    def _format_generic_data(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Generic data format"""
        return json.dumps({
            'metadata': meta,
            'entry_points_summary': phase1.get('summary', {}),
            'configuration': {
                'application': phase2.get('application_config', {}),
                'build': phase2.get('build_config', {}),
                'deployment': phase2.get('deployment_config', {})
            }
        }, indent=2)
    
    def _get_dev_route(self, deploy_config: Dict) -> str:
        """Extract DEV environment route"""
        routes = deploy_config.get('routes', {})
        
        # Try dev-a, dev, development
        for dev_env in ['dev-a', 'dev', 'development']:
            if dev_env in routes:
                return routes[dev_env]
        
        # Fallback to first route or localhost
        if routes:
            return list(routes.values())[0]
        
        return 'http://localhost:8080'
    
    def _get_health_endpoint(self, deploy_config: Dict) -> str:
        """Extract health check endpoint for DEV environment"""
        health_endpoints = deploy_config.get('health_endpoints', {})
        
        # Try dev-a, dev, development
        for dev_env in ['dev-a', 'dev', 'development']:
            if dev_env in health_endpoints:
                return health_endpoints[dev_env]
        
        # Fallback to first health endpoint or default actuator
        if health_endpoints:
            return list(health_endpoints.values())[0]
        
        return '/actuator/health'
    
    # Detection methods
    def _has_rest_endpoints(self, analysis: Dict) -> bool:
        rest = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('REST', [])
        return len(rest) > 0
    
    def _has_graphql(self, analysis: Dict) -> bool:
        # TODO: Add GraphQL detection in Phase 1
        return False
    
    def _has_grpc(self, analysis: Dict) -> bool:
        # TODO: Add gRPC detection in Phase 1
        return False
    
    def _has_kafka(self, analysis: Dict) -> bool:
        kafka = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('MESSAGE_CONSUMER', [])
        return len(kafka) > 0
    
    def _has_jms(self, analysis: Dict) -> bool:
        # TODO: Add JMS detection
        return False
    
    def _has_scheduled(self, analysis: Dict) -> bool:
        scheduled = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('SCHEDULED_TASK', [])
        return len(scheduled) > 0
    
    def _has_reactive(self, analysis: Dict) -> bool:
        """Detect WebFlux reactive endpoints by checking return types and dependencies"""
        # Check if any REST endpoints return Mono<> or Flux<>
        rest_endpoints = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('REST', [])
        for ep in rest_endpoints:
            return_type = ep.get('details', {}).get('return_type', '')
            if 'Mono<' in return_type or 'Flux<' in return_type:
                return True
        
        # Check for spring-webflux in dependencies
        build_config = analysis.get('phase_2_configuration', {}).get('build_config', {})
        dependencies = build_config.get('dependencies', [])
        for dep in dependencies:
            if isinstance(dep, dict):
                artifact = dep.get('artifactId', '')
            else:
                artifact = str(dep)
            if 'webflux' in artifact.lower() or 'reactor' in artifact.lower():
                return True
        
        return False
    
    def _has_ui(self, analysis: Dict) -> bool:
        # TODO: Detect JavaFX/Swing
        return False
    
    def _has_websocket(self, analysis: Dict) -> bool:
        # TODO: Detect WebSocket
        return False
    
    def _has_soap(self, analysis: Dict) -> bool:
        # TODO: Detect SOAP
        return False
    
    def _has_batch(self, analysis: Dict) -> bool:
        batch = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('BATCH_JOB', [])
        return len(batch) > 0
    
    def _has_cli(self, analysis: Dict) -> bool:
        cli = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('CLI', [])
        main_app = analysis.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('MAIN_APPLICATION', [])
        return len(cli) > 0 or len(main_app) > 0
    
    def _has_esb(self, analysis: Dict) -> bool:
        # TODO: Detect Camel/Mule
        return False
