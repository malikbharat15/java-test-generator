"""
Test AST Parser on Enterprise Banking Applications
Analyzes each application separately and generates individual reports
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ast_parser.java_ast_parser import JavaASTParser


def test_single_application(app_name, app_path):
    """Test AST parser on a single application"""
    print(f"\n{'='*80}")
    print(f"🏦 ANALYZING: {app_name.upper()}")
    print(f"{'='*80}")
    print(f"📁 Path: {app_path}")
    
    if not app_path.exists():
        print(f"⚠️  Application not found: {app_path}")
        return None
    
    # Parse the application
    parser = JavaASTParser(app_path)
    entry_points = parser.parse_repository()
    
    # Print summary
    parser.print_summary()
    
    # Generate report
    report = parser.generate_report()
    
    # Save individual report
    output_file = Path(f"output_{app_name}_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved to: {output_file}")
    
    return report


def main():
    """Test all enterprise banking applications"""
    
    enterprise_dir = Path(__file__).parent.parent / "examples-enterprise"
    
    print("\n" + "="*80)
    print("🧪 TESTING ENTERPRISE BANKING APPLICATIONS")
    print("="*80)
    
    # Define applications to test
    applications = [
        ("core-banking-api", "Core Banking REST API"),
        ("payment-gateway", "Payment Gateway Service (JAX-RS)"),
        ("transaction-processor", "Transaction Batch Processor"),
        ("fraud-detection", "Fraud Detection Service (Kafka)"),
        ("admin-cli", "Administration CLI Tool")
    ]
    
    all_results = {}
    
    for app_dir, app_description in applications:
        app_path = enterprise_dir / app_dir
        
        print(f"\n{'─'*80}")
        print(f"📦 {app_description}")
        print(f"{'─'*80}")
        
        result = test_single_application(app_dir, app_path)
        
        if result:
            all_results[app_dir] = {
                "description": app_description,
                "analysis": result
            }
    
    # Save combined report
    combined_output = Path("enterprise_banking_analysis.json")
    with open(combined_output, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"📄 Combined report saved to: {combined_output}\n")
    
    # Print overall summary
    print_overall_summary(all_results)


def print_overall_summary(results):
    """Print overall summary across all applications"""
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY - ENTERPRISE BANKING APPLICATIONS")
    print("="*80)
    
    total_entry_points = 0
    by_type_total = {}
    by_app = {}
    
    for app_name, app_data in results.items():
        report = app_data["analysis"]
        app_total = report["total_entry_points"]
        total_entry_points += app_total
        by_app[app_name] = app_total
        
        for ep_type, count in report["by_type"].items():
            by_type_total[ep_type] = by_type_total.get(ep_type, 0) + count
    
    print(f"\n📈 Total Entry Points Discovered: {total_entry_points}")
    
    print(f"\n📋 Breakdown by Application:")
    for app_name, count in sorted(by_app.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {app_name:30s}: {count:3d} entry points")
    
    print(f"\n📋 Breakdown by Type:")
    for ep_type, count in sorted(by_type_total.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {ep_type:20s}: {count:3d}")
    
    print("\n" + "="*80 + "\n")
    
    # Print detailed breakdown
    print("🔍 DETAILED BREAKDOWN BY APPLICATION")
    print("="*80)
    
    for app_name, app_data in results.items():
        report = app_data["analysis"]
        print(f"\n📦 {app_data['description']}")
        print(f"   Total: {report['total_entry_points']} entry points")
        
        if report['by_type']:
            print(f"   Types:")
            for ep_type, count in report['by_type'].items():
                print(f"     - {ep_type}: {count}")
        
        # Show sample entry points
        if report['entry_points']:
            print(f"   Sample Entry Points:")
            for ep in report['entry_points'][:3]:  # Show first 3
                if ep['type'] == 'REST':
                    method = ep['details'].get('http_method', 'GET')
                    path = ep['details'].get('path', '/')
                    print(f"     - {method} {path}")
                elif ep['type'] == 'MESSAGE_CONSUMER':
                    consumer_type = ep['details'].get('consumer_type', 'Unknown')
                    print(f"     - {consumer_type} Consumer: {ep['method']}")
                elif ep['type'] in ['CLI', 'BATCH_JOB', 'SCHEDULED_TASK']:
                    print(f"     - {ep['type']}: {ep['method']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
