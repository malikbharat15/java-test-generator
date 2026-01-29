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
        
        # Extract relevant data based on test type
        if test_type == 'REST_API':
            return self._format_rest_api_data(phase1, phase2, meta)
        elif test_type == 'KAFKA':
            return self._format_kafka_data(phase1, phase2, meta)
        else:
            return self._format_generic_data(phase1, phase2, meta)
    
    def _format_rest_api_data(self, phase1: Dict, phase2: Dict, meta: Dict) -> str:
        """Format REST API specific data"""
        
        rest_endpoints = phase1.get('entry_points_by_type', {}).get('REST', [])
        app_config = phase2.get('application_config', {})
        deploy_config = phase2.get('deployment_config', {})
        build_config = phase2.get('build_config', {})
        
        # Get DEV route
        dev_route = self._get_dev_route(deploy_config)
        
        data = f"""
Application: {meta.get('application', 'Unknown')}
Base URL (DEV): {dev_route}

REST Endpoints ({len(rest_endpoints)} total):
"""
        
        for ep in rest_endpoints[:20]:  # Limit to first 20 to avoid token overflow
            # Handle both flat and nested structures
            details = ep.get('details', ep)
            http_method = details.get('http_method', 'GET')
            path = details.get('path', 'N/A')
            params = details.get('parameters', [])
            
            data += f"\n  {http_method} {path}"
            if params:
                param_names = [p.get('name', '') if isinstance(p, dict) else str(p) for p in params[:3]]
                data += f" - Params: {', '.join(param_names)}"
        
        data += f"""

Application Configuration:
  Server Port: {app_config.get('server', {}).get('port', app_config.get('server_port', 8080))}
  Context Path: {app_config.get('server', {}).get('context_path', app_config.get('context_path', '/'))}

Build Configuration:
  Java Version: {build_config.get('java_version', '11')}
  Spring Boot: {build_config.get('spring_boot_version', 'N/A')}
  Test Frameworks: {', '.join([str(tf) if not isinstance(tf, dict) else tf.get('name', tf.get('artifactId', '')) for tf in build_config.get('test_frameworks', [])])}
  Dependencies: {', '.join([d.get('artifactId', str(d)) if isinstance(d, dict) else str(d) for d in build_config.get('dependencies', [])[:10]])}

Deployment:
  Platform: {deploy_config.get('platform', 'unknown')}
  Environments: {', '.join([str(e) for e in deploy_config.get('environments', [])])}
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
        # TODO: Detect WebFlux
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
