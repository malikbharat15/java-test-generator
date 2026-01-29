"""
Comprehensive End-to-End Test: Phase 1 + Phase 2

Tests complete pipeline on realistic enterprise Java applications:
1. Phase 1: AST Entry Point Discovery + Schema Extraction
2. Phase 2: Configuration Analysis (all 4 analyzers)
3. Combined output validation
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ast_parser.java_ast_parser import JavaASTParser
from ast_parser.model_schema_extractor import ModelSchemaExtractor
from config_analyzer.application_config_parser import ApplicationConfigParser
from config_analyzer.build_config_parser import BuildConfigParser
from config_analyzer.deployment_config_parser import DeploymentConfigParser
from config_analyzer.existing_test_detector import ExistingTestDetector


def run_complete_analysis(app_path: str, app_name: str):
    """Run Phase 1 + Phase 2 on a single application"""
    print(f"\n{'='*100}")
    print(f"🏗️  COMPLETE ANALYSIS: {app_name}")
    print(f"{'='*100}")
    
    start_time = datetime.now()
    
    # ===== PHASE 1: AST Entry Point Discovery =====
    print(f"\n{'─'*100}")
    print("📍 PHASE 1: AST ENTRY POINT DISCOVERY")
    print(f"{'─'*100}")
    
    ast_parser = JavaASTParser(app_path)
    entry_points = ast_parser.parse_repository()
    
    # Extract schemas for request body types
    print(f"\n📋 Extracting request body schemas...")
    schema_extractor = ModelSchemaExtractor(Path(app_path))
    entry_points_dicts = [vars(ep) for ep in entry_points]
    request_body_schemas = schema_extractor.extract_schemas_for_endpoints(entry_points_dicts)
    print(f"   Found {len(request_body_schemas)} request body schemas")
    
    print(f"\n✅ Phase 1 Complete:")
    print(f"   Total Entry Points: {len(entry_points)}")
    print(f"   REST Endpoints: {len([ep for ep in entry_points if ep.type == 'REST'])}")
    print(f"   Kafka Consumers: {len([ep for ep in entry_points if ep.type == 'MESSAGE_CONSUMER'])}")
    print(f"   Scheduled Tasks: {len([ep for ep in entry_points if ep.type == 'SCHEDULED_TASK'])}")
    print(f"   Batch Jobs: {len([ep for ep in entry_points if ep.type == 'BATCH_JOB'])}")
    print(f"   CLI Commands: {len([ep for ep in entry_points if ep.type == 'CLI'])}")
    print(f"   Request Body Schemas: {len(request_body_schemas)}")
    
    # ===== PHASE 2: Configuration Analysis =====
    print(f"\n{'─'*100}")
    print("⚙️  PHASE 2: CONFIGURATION ANALYSIS")
    print(f"{'─'*100}")
    
    # 1. Application Config
    app_config_parser = ApplicationConfigParser()
    app_config = app_config_parser.parse(app_path)
    
    # 2. Build Config
    build_config_parser = BuildConfigParser()
    build_config = build_config_parser.parse(app_path)
    
    # 3. Deployment Config
    deploy_config_parser = DeploymentConfigParser()
    deploy_config = deploy_config_parser.parse(app_path)
    
    # 4. Existing Tests
    test_detector = ExistingTestDetector()
    existing_tests = test_detector.analyze(app_path)
    
    # ===== COMBINED OUTPUT =====
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    combined_analysis = {
        'metadata': {
            'application': app_name,
            'analysis_timestamp': start_time.isoformat(),
            'duration_seconds': duration
        },
        'phase_1_ast_analysis': {
            'total_entry_points': len(entry_points),
            'entry_points_by_type': {
                'REST': [vars(ep) for ep in entry_points if ep.type == 'REST'],
                'MESSAGE_CONSUMER': [vars(ep) for ep in entry_points if ep.type == 'MESSAGE_CONSUMER'],
                'SCHEDULED_TASK': [vars(ep) for ep in entry_points if ep.type == 'SCHEDULED_TASK'],
                'BATCH_JOB': [vars(ep) for ep in entry_points if ep.type == 'BATCH_JOB'],
                'CLI': [vars(ep) for ep in entry_points if ep.type == 'CLI'],
                'MAIN_APPLICATION': [vars(ep) for ep in entry_points if ep.type == 'MAIN_APPLICATION']
            },
            'request_body_schemas': request_body_schemas,
            'summary': {
                'rest_count': len([ep for ep in entry_points if ep.type == 'REST']),
                'message_consumer_count': len([ep for ep in entry_points if ep.type == 'MESSAGE_CONSUMER']),
                'scheduled_task_count': len([ep for ep in entry_points if ep.type == 'SCHEDULED_TASK']),
                'batch_job_count': len([ep for ep in entry_points if ep.type == 'BATCH_JOB']),
                'cli_count': len([ep for ep in entry_points if ep.type == 'CLI']),
                'main_app_count': len([ep for ep in entry_points if ep.type == 'MAIN_APPLICATION']),
                'request_body_schema_count': len(request_body_schemas)
            }
        },
        'phase_2_configuration': {
            'application_config': app_config_parser.to_dict(),
            'build_config': build_config_parser.to_dict(),
            'deployment_config': deploy_config_parser.to_dict(),
            'existing_tests': test_detector.to_dict()
        }
    }
    
    # Export to JSON in output/ folder
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"complete_analysis_{app_name}.json"
    output_file.write_text(json.dumps(combined_analysis, indent=2))
    
    print(f"\n{'─'*100}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'─'*100}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"💾 Output: {output_file}")
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"   Entry Points: {combined_analysis['phase_1_ast_analysis']['total_entry_points']}")
    print(f"   - REST: {combined_analysis['phase_1_ast_analysis']['summary']['rest_count']}")
    print(f"   - Kafka: {combined_analysis['phase_1_ast_analysis']['summary']['message_consumer_count']}")
    print(f"   - Scheduled: {combined_analysis['phase_1_ast_analysis']['summary']['scheduled_task_count']}")
    print(f"   - Batch: {combined_analysis['phase_1_ast_analysis']['summary']['batch_job_count']}")
    print(f"   - Main: {combined_analysis['phase_1_ast_analysis']['summary']['main_app_count']}")
    
    print(f"\n   Configuration:")
    print(f"   - Server Port: {app_config.server_port}")
    print(f"   - Context Path: {app_config.context_path}")
    print(f"   - Build Tool: {build_config.build_tool}")
    print(f"   - Java Version: {build_config.java_version}")
    print(f"   - Spring Boot: {build_config.spring_boot_version}")
    print(f"   - Deployment Platform: {deploy_config.deployment_platform}")
    print(f"   - Environments: {len(deploy_config.environments)}")
    if deploy_config.routes:
        print(f"   - Routes: {list(deploy_config.routes.keys())}")
    
    return combined_analysis


def main():
    """Test on specific or all enterprise applications"""
    
    examples_dir = Path(__file__).parent.parent / "examples-enterprise"
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Check if specific app(s) provided as command-line arguments
    import sys
    apps_to_test = sys.argv[1:] if len(sys.argv) > 1 else None
    
    print(f"\n{'#'*100}")
    print(f"# COMPREHENSIVE END-TO-END TEST: PHASE 1 + PHASE 2")
    print(f"# Testing realistic enterprise Java applications")
    print(f"{'#'*100}")
    
    # All available applications
    all_applications = [
        ("core-banking-api", "Core Banking API - Spring Boot REST + JPA"),
        ("ecommerce-order-service", "E-Commerce Order Service - REST + Kafka + Scheduled"),
        ("payment-gateway-secured", "Payment Gateway - Spring Security + JWT + Role-based Access"),
        ("inventory-reactive-service", "Inventory Service - Spring WebFlux Reactive"),
        ("data-pipeline-batch", "Data Pipeline - Spring Batch + Scheduled Jobs")
    ]
    
    # Filter applications if specific ones requested
    if apps_to_test:
        applications = [(name, desc) for name, desc in all_applications if name in apps_to_test]
        if not applications:
            print(f"\n❌ ERROR: No matching applications found!")
            print(f"   Requested: {apps_to_test}")
            print(f"   Available: {[name for name, _ in all_applications]}")
            return
        print(f"\n🎯 Testing specific applications: {apps_to_test}")
    else:
        applications = all_applications
        print(f"\n🎯 Testing all applications")
    
    all_results = {}
    
    for app_dir, app_description in applications:
        app_path = examples_dir / app_dir
        
        if app_path.exists():
            print(f"\n\n🎯 Testing: {app_description}")
            result = run_complete_analysis(str(app_path), app_dir)
            all_results[app_dir] = result
        else:
            print(f"\n⚠️  {app_dir} not found at {app_path}")
    
    # Generate combined report
    combined_report = {
        'test_timestamp': datetime.now().isoformat(),
        'total_applications_tested': len(all_results),
        'applications': all_results,
        'aggregate_stats': {
            'total_entry_points': sum(r['phase_1_ast_analysis']['total_entry_points'] for r in all_results.values()),
            'total_rest_endpoints': sum(r['phase_1_ast_analysis']['summary']['rest_count'] for r in all_results.values()),
            'total_kafka_consumers': sum(r['phase_1_ast_analysis']['summary']['message_consumer_count'] for r in all_results.values()),
            'total_scheduled_tasks': sum(r['phase_1_ast_analysis']['summary']['scheduled_task_count'] for r in all_results.values()),
            'apps_with_ocp_deployment': sum(1 for r in all_results.values() if r['phase_2_configuration']['deployment_config']['platform'] != 'none')
        }
    }
    
    output_file = output_dir / "end_to_end_test_results.json"
    output_file.write_text(json.dumps(combined_report, indent=2))
    
    print(f"\n\n{'#'*100}")
    print(f"# FINAL RESULTS")
    print(f"{'#'*100}")
    print(f"\n📊 Aggregate Statistics:")
    print(f"   Applications Tested: {combined_report['total_applications_tested']}")
    print(f"   Total Entry Points: {combined_report['aggregate_stats']['total_entry_points']}")
    print(f"   Total REST Endpoints: {combined_report['aggregate_stats']['total_rest_endpoints']}")
    print(f"   Total Kafka Consumers: {combined_report['aggregate_stats']['total_kafka_consumers']}")
    print(f"   Total Scheduled Tasks: {combined_report['aggregate_stats']['total_scheduled_tasks']}")
    print(f"   Apps with OCP Deployment: {combined_report['aggregate_stats']['apps_with_ocp_deployment']}")
    
    print(f"\n💾 Complete Report: {output_file}")
    print(f"\n{'#'*100}")
    print(f"# ✅ END-TO-END TEST COMPLETE")
    print(f"{'#'*100}\n")


if __name__ == "__main__":
    main()
