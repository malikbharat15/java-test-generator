"""
Integration Test: Prompt Generation Validation

Tests that PromptBuilder correctly:
1. Detects application type from Phase 1 + Phase 2 analysis
2. Selects appropriate prompt template
3. Injects actual application data
4. Generates complete, valid prompt ready for LLM

Run: python3 tests/test_prompt_generation.py
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from test_generator.prompt_builder import PromptBuilder
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def test_rest_api_prompt_generation():
    """
    Test: ecommerce-order-service (REST API app)
    Should generate Newman/Postman prompt
    """
    console.print("\n" + "="*100, style="bold blue")
    console.print("🧪 TEST: REST API Prompt Generation", style="bold blue")
    console.print("="*100 + "\n", style="bold blue")
    
    # Load Phase 1 + Phase 2 analysis
    analysis_file = Path(__file__).parent.parent / "output" / "complete_analysis_ecommerce-order-service.json"
    
    if not analysis_file.exists():
        console.print(f"❌ Analysis file not found: {analysis_file}", style="bold red")
        console.print("💡 Run: python3 tests/test_end_to_end.py ecommerce-order-service", style="yellow")
        return False
    
    console.print(f"📂 Loading analysis: {analysis_file.name}", style="cyan")
    with open(analysis_file, 'r') as f:
        analysis_json = json.load(f)
    
    # Initialize PromptBuilder
    console.print("🔧 Initializing PromptBuilder...", style="cyan")
    prompt_builder = PromptBuilder()
    
    # Detect application type
    console.print("\n📍 Step 1: Detecting Application Type", style="bold yellow")
    detected_types = prompt_builder._detect_application_types(analysis_json)
    console.print(f"   Detected Types: {detected_types}", style="green")
    
    # Validate detection
    assert 'REST_API' in detected_types, "❌ Failed to detect REST API endpoints!"
    console.print("   ✅ REST_API detected correctly", style="green")
    
    # Select primary type
    console.print("\n📍 Step 2: Selecting Primary Test Strategy", style="bold yellow")
    primary_type = prompt_builder._select_primary_type(detected_types)
    console.print(f"   Primary Type: {primary_type}", style="green")
    
    assert primary_type == 'REST_API', f"❌ Expected REST_API, got {primary_type}"
    console.print("   ✅ REST_API selected as primary (correct priority)", style="green")
    
    # Build complete prompt
    console.print("\n📍 Step 3: Building Complete Prompt", style="bold yellow")
    complete_prompt = prompt_builder.build_prompt(analysis_json)
    
    # Validate prompt structure
    console.print("\n🔍 Validating Prompt Structure:", style="bold yellow")
    
    # Check key sections exist
    required_sections = [
        "DEPLOYED TESTS ONLY",
        "SMOKE TEST PHILOSOPHY",
        "REST API Smoke Tests using Newman/Postman",
        "POSTMAN COLLECTION",
        "OUTPUT FORMAT",
        "APPLICATION ANALYSIS DATA"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section in complete_prompt:
            console.print(f"   ✅ Contains: '{section}'", style="green")
        else:
            console.print(f"   ❌ Missing: '{section}'", style="red")
            missing_sections.append(section)
    
    assert len(missing_sections) == 0, f"❌ Missing sections: {missing_sections}"
    
    # Check application-specific data injection
    console.print("\n🔍 Validating Data Injection:", style="bold yellow")
    
    # Should contain actual endpoint data
    assert "/orders" in complete_prompt, "❌ Missing /orders endpoint"
    console.print("   ✅ Contains actual endpoint: /orders", style="green")
    
    # Should contain OCP route
    assert "order-service-dev" in complete_prompt or "baseUrl" in complete_prompt, "❌ Missing DEV route"
    console.print("   ✅ Contains deployment route reference", style="green")
    
    # Should contain port/context path
    assert "8081" in complete_prompt, "❌ Missing port 8081"
    console.print("   ✅ Contains server port: 8081", style="green")
    
    # Should mention Spring Boot version
    assert "Spring Boot" in complete_prompt or "2.7" in complete_prompt, "❌ Missing Spring Boot version"
    console.print("   ✅ Contains Spring Boot version", style="green")
    
    # Print prompt statistics
    console.print("\n📊 Prompt Statistics:", style="bold yellow")
    console.print(f"   Total Length: {len(complete_prompt)} characters", style="cyan")
    console.print(f"   Lines: {len(complete_prompt.splitlines())}", style="cyan")
    console.print(f"   Estimated Tokens: ~{len(complete_prompt) // 4}", style="cyan")
    
    # Show prompt preview (first 2000 chars)
    console.print("\n📄 Prompt Preview (first 2000 chars):", style="bold yellow")
    preview = complete_prompt[:2000] + "\n\n[... truncated ...]"
    syntax = Syntax(preview, "markdown", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Generated Prompt", border_style="blue"))
    
    # Save full prompt for manual inspection
    output_dir = Path(__file__).parent.parent / "output"
    output_file = output_dir / "generated_prompt_rest_api.txt"
    output_file.write_text(complete_prompt)
    console.print(f"\n💾 Full prompt saved to: {output_file}", style="green")
    
    console.print("\n" + "="*100, style="bold green")
    console.print("✅ TEST PASSED: REST API Prompt Generation", style="bold green")
    console.print("="*100 + "\n", style="bold green")
    
    return True


def test_kafka_prompt_generation():
    """
    Test: ecommerce-order-service (has Kafka consumers)
    Should detect Kafka but prioritize REST API
    """
    console.print("\n" + "="*100, style="bold blue")
    console.print("🧪 TEST: Kafka Detection (Mixed App)", style="bold blue")
    console.print("="*100 + "\n", style="bold blue")
    
    analysis_file = Path(__file__).parent.parent / "output" / "complete_analysis_ecommerce-order-service.json"
    
    if not analysis_file.exists():
        console.print(f"❌ Analysis file not found", style="bold red")
        return False
    
    with open(analysis_file, 'r') as f:
        analysis_json = json.load(f)
    
    prompt_builder = PromptBuilder()
    
    # Check Kafka detection
    has_kafka = prompt_builder._has_kafka(analysis_json)
    console.print(f"   Kafka Consumers Detected: {has_kafka}", style="green" if has_kafka else "yellow")
    
    assert has_kafka, "❌ Failed to detect Kafka consumers!"
    console.print("   ✅ Kafka consumers detected correctly", style="green")
    
    # Check scheduled tasks detection
    has_scheduled = prompt_builder._has_scheduled(analysis_json)
    console.print(f"   Scheduled Tasks Detected: {has_scheduled}", style="green" if has_scheduled else "yellow")
    
    assert has_scheduled, "❌ Failed to detect scheduled tasks!"
    console.print("   ✅ Scheduled tasks detected correctly", style="green")
    
    # Verify REST API is still primary (priority)
    detected_types = prompt_builder._detect_application_types(analysis_json)
    console.print(f"\n   All Detected Types: {detected_types}", style="cyan")
    
    primary = prompt_builder._select_primary_type(detected_types)
    console.print(f"   Primary Type Selected: {primary}", style="cyan")
    
    assert primary == 'REST_API', "❌ REST_API should have priority over Kafka/Scheduled"
    console.print("   ✅ REST_API correctly prioritized (even with Kafka + Scheduled present)", style="green")
    
    console.print("\n" + "="*100, style="bold green")
    console.print("✅ TEST PASSED: Multi-Type Detection", style="bold green")
    console.print("="*100 + "\n", style="bold green")
    
    return True


def test_core_banking_api_prompt():
    """
    Test: core-banking-api (pure REST API, larger)
    Should handle multiple controllers and environments
    """
    console.print("\n" + "="*100, style="bold blue")
    console.print("🧪 TEST: Core Banking API Prompt (Multi-Controller)", style="bold blue")
    console.print("="*100 + "\n", style="bold blue")
    
    # First, generate the analysis if not exists
    analysis_file = Path(__file__).parent.parent / "output" / "complete_analysis_core-banking-api.json"
    
    if not analysis_file.exists():
        console.print(f"⚠️  Analysis file not found: {analysis_file.name}", style="yellow")
        console.print("💡 Generating analysis...", style="yellow")
        
        # Run end-to-end test to generate it
        import subprocess
        result = subprocess.run(
            ["python3", "tests/test_end_to_end.py", "core-banking-api"],
            cwd=Path(__file__).parent.parent,
            capture_output=True
        )
        
        if result.returncode != 0:
            console.print("❌ Failed to generate analysis", style="red")
            return False
        
        console.print("✅ Analysis generated", style="green")
    
    with open(analysis_file, 'r') as f:
        analysis_json = json.load(f)
    
    prompt_builder = PromptBuilder()
    
    # Check endpoint count
    rest_endpoints = analysis_json.get('phase_1_ast_analysis', {}).get('entry_points_by_type', {}).get('REST', [])
    console.print(f"   REST Endpoints Found: {len(rest_endpoints)}", style="cyan")
    
    assert len(rest_endpoints) >= 15, "❌ Expected at least 15 endpoints"
    console.print("   ✅ Multiple endpoints detected", style="green")
    
    # Build prompt
    complete_prompt = prompt_builder.build_prompt(analysis_json)
    
    # Check for multiple controllers
    assert "Account" in complete_prompt or "Customer" in complete_prompt or "Transaction" in complete_prompt
    console.print("   ✅ Multi-controller endpoints included", style="green")
    
    # Check for multiple environments
    deploy_config = analysis_json.get('phase_2_configuration', {}).get('deployment_config', {})
    environments = deploy_config.get('environments', [])
    console.print(f"   Environments Detected: {environments}", style="cyan")
    
    assert len(environments) >= 2, "❌ Expected multiple environments"
    console.print("   ✅ Multiple OCP environments detected", style="green")
    
    # Save prompt
    output_file = Path(__file__).parent.parent / "output" / "generated_prompt_core_banking.txt"
    output_file.write_text(complete_prompt)
    console.print(f"\n💾 Full prompt saved to: {output_file}", style="green")
    
    console.print("\n" + "="*100, style="bold green")
    console.print("✅ TEST PASSED: Multi-Controller Prompt", style="bold green")
    console.print("="*100 + "\n", style="bold green")
    
    return True


def main():
    """Run all prompt generation tests"""
    
    console.print("\n" + "🚀 "*50, style="bold magenta")
    console.print("PROMPT GENERATION INTEGRATION TESTS", style="bold magenta")
    console.print("🚀 "*50 + "\n", style="bold magenta")
    
    results = {}
    
    # Test 1: REST API prompt generation
    try:
        results['rest_api'] = test_rest_api_prompt_generation()
    except Exception as e:
        console.print(f"\n❌ TEST FAILED: {e}", style="bold red")
        results['rest_api'] = False
    
    # Test 2: Multi-type detection
    try:
        results['kafka_detection'] = test_kafka_prompt_generation()
    except Exception as e:
        console.print(f"\n❌ TEST FAILED: {e}", style="bold red")
        results['kafka_detection'] = False
    
    # Test 3: Core Banking API
    try:
        results['core_banking'] = test_core_banking_api_prompt()
    except Exception as e:
        console.print(f"\n❌ TEST FAILED: {e}", style="bold red")
        results['core_banking'] = False
    
    # Summary
    console.print("\n" + "="*100, style="bold magenta")
    console.print("📊 TEST SUMMARY", style="bold magenta")
    console.print("="*100, style="bold magenta")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        style = "green" if passed else "red"
        console.print(f"   {test_name}: {status}", style=style)
    
    all_passed = all(results.values())
    
    if all_passed:
        console.print("\n🎉 ALL TESTS PASSED! Prompt generation is working correctly.", style="bold green")
        console.print("✅ Ready to integrate with Anthropic Claude LLM", style="bold green")
    else:
        console.print("\n⚠️  SOME TESTS FAILED. Fix issues before LLM integration.", style="bold yellow")
    
    console.print("\n" + "="*100 + "\n", style="bold magenta")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
