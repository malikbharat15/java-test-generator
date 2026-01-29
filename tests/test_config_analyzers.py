"""
Test Configuration Analyzers

Validates all 4 configuration analyzers on enterprise banking applications:
1. ApplicationConfigParser - application.yml
2. BuildConfigParser - pom.xml/build.gradle
3. DeploymentConfigParser - ocp/k8s configs
4. ExistingTestDetector - existing test files
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_analyzer.application_config_parser import ApplicationConfigParser
from config_analyzer.build_config_parser import BuildConfigParser
from config_analyzer.deployment_config_parser import DeploymentConfigParser
from config_analyzer.existing_test_detector import ExistingTestDetector


def test_config_analyzers(app_path: str, app_name: str):
    """Test all 4 config analyzers on a single application"""
    print(f"\n{'='*80}")
    print(f"🏦 Testing Configuration Analyzers: {app_name}")
    print(f"{'='*80}")
    
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
    
    # Combine all config analysis
    complete_config = {
        'application': app_name,
        'application_config': app_config_parser.to_dict(),
        'build_config': build_config_parser.to_dict(),
        'deployment_config': deploy_config_parser.to_dict(),
        'existing_tests': test_detector.to_dict()
    }
    
    # Export combined config
    output_file = f"config_analysis_{app_name}.json"
    Path(output_file).write_text(json.dumps(complete_config, indent=2))
    print(f"\n💾 Exported complete config analysis to: {output_file}")
    
    return complete_config


def main():
    """Test all enterprise banking applications"""
    
    examples_dir = Path(__file__).parent.parent / "examples-enterprise"
    
    applications = [
        ("core-banking-api", "Spring Boot REST API"),
        ("payment-gateway", "JAX-RS Service"),
        ("transaction-processor", "Spring Batch + Scheduled"),
        ("fraud-detection", "Kafka Consumer"),
        ("admin-cli", "CLI Tool")
    ]
    
    all_configs = {}
    
    for app_dir, app_type in applications:
        app_path = examples_dir / app_dir
        
        if app_path.exists():
            config = test_config_analyzers(str(app_path), app_dir)
            all_configs[app_dir] = config
        else:
            print(f"⚠️  {app_dir} not found at {app_path}")
    
    # Export combined report
    combined_output = {
        'total_applications': len(all_configs),
        'applications': all_configs,
        'summary': {
            'with_application_config': sum(1 for c in all_configs.values() if c['application_config']['server']['port'] != 8080),
            'with_build_files': sum(1 for c in all_configs.values() if c['build_config']['build_tool'] != 'unknown'),
            'with_deployment_config': sum(1 for c in all_configs.values() if c['deployment_config']['platform'] != 'none'),
            'with_existing_tests': sum(1 for c in all_configs.values() if c['existing_tests']['has_tests'])
        }
    }
    
    output_file = "all_config_analysis.json"
    Path(output_file).write_text(json.dumps(combined_output, indent=2))
    print(f"\n{'='*80}")
    print(f"✅ COMPLETE CONFIG ANALYSIS")
    print(f"{'='*80}")
    print(f"💾 Exported complete analysis to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Applications Analyzed: {combined_output['total_applications']}")
    print(f"   With Application Config: {combined_output['summary']['with_application_config']}")
    print(f"   With Build Files: {combined_output['summary']['with_build_files']}")
    print(f"   With Deployment Config: {combined_output['summary']['with_deployment_config']}")
    print(f"   With Existing Tests: {combined_output['summary']['with_existing_tests']}")


if __name__ == "__main__":
    main()
