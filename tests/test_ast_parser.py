"""
Test script to run AST parser on all example Java applications
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ast_parser.java_ast_parser import JavaASTParser
import json


def test_all_examples():
    """Test AST parser on all example applications"""
    examples_dir = Path(__file__).parent.parent / "examples"
    
    print("\n" + "="*80)
    print("🧪 TESTING AST PARSER ON ALL EXAMPLE JAVA APPLICATIONS")
    print("="*80)
    
    all_results = {}
    
    # Test each example type
    example_types = [
        "spring-boot-rest",
        "jaxrs-service",
        "spring-batch",
        "kafka-consumer",
        "cli-tool"
    ]
    
    for example_type in example_types:
        example_path = examples_dir / example_type
        
        if not example_path.exists():
            print(f"\n⚠️  {example_type} not found, skipping...")
            continue
        
        print(f"\n{'─'*80}")
        print(f"📁 Testing: {example_type}")
        print(f"{'─'*80}")
        
        # Parse the example
        parser = JavaASTParser(example_path)
        entry_points = parser.parse_repository()
        
        # Print summary
        parser.print_summary()
        
        # Store results
        report = parser.generate_report()
        all_results[example_type] = report
    
    # Save combined report
    output_file = Path("all_examples_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ TESTING COMPLETE")
    print(f"{'='*80}")
    print(f"📄 Full report saved to: {output_file}\n")
    
    # Print overall summary
    print_overall_summary(all_results)


def print_overall_summary(results):
    """Print overall summary across all examples"""
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY ACROSS ALL EXAMPLES")
    print("="*80)
    
    total_entry_points = 0
    by_type_total = {}
    
    for example_name, report in results.items():
        total_entry_points += report["total_entry_points"]
        for ep_type, count in report["by_type"].items():
            by_type_total[ep_type] = by_type_total.get(ep_type, 0) + count
    
    print(f"\n📈 Total Entry Points Discovered: {total_entry_points}")
    print(f"\n📋 Breakdown by Type:")
    for ep_type, count in sorted(by_type_total.items()):
        print(f"  • {ep_type:20s}: {count:3d}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_all_examples()
