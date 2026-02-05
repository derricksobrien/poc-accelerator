#!/usr/bin/env python
"""
Test Skillable Simulator against expanded repo collection
Tests multiple scenarios across all solution areas
"""

from skillable_simulator.batch_processor import BatchProcessor
from datetime import datetime

# Test scenarios covering all repos and solution areas
test_scenarios = [
    # AI Acceleration (L400)
    {'title': 'Deploy Multi-Agent Automation Engine', 'solution_area': 'AI', 'complexity': 'L400'},
    {'title': 'Build Agentic Applications with Unified Data', 'solution_area': 'AI', 'complexity': 'L400'},
    
    # AI Content Processing (L300)
    {'title': 'Create Content Processing Pipeline', 'solution_area': 'AI', 'complexity': 'L300'},
    {'title': 'Build AI Chat Application with Search', 'solution_area': 'AI', 'complexity': 'L300'},
    
    # AI Intelligent Apps (L300)
    {'title': 'Implement Semantic Kernel Agents', 'solution_area': 'AI', 'complexity': 'L300'},
    
    # Prompt Engineering (L200)
    {'title': 'Optimize and Guide LLM Prompts', 'solution_area': 'AI', 'complexity': 'L200'},
    
    # Data & Analytics Foundation (L400)
    {'title': 'Setup Unified Data Foundation with Fabric', 'solution_area': 'Azure (Data & AI)', 'complexity': 'L400'},
    
    # Data & Analytics Samples (L300)
    {'title': 'Deploy Microsoft Fabric Analytics', 'solution_area': 'Azure (Data & AI)', 'complexity': 'L300'},
]

def main():
    print("\n" + "="*80)
    print("SKILLABLE SIMULATOR - BATCH TEST")
    print("Testing against expanded repo collection (8 accelerators)")
    print("="*80)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize processor
    base_dir = f"lab_runs/batch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    processor = BatchProcessor(base_dir)
    
    # Run batch processing
    print(f"Processing {len(test_scenarios)} scenarios...\n")
    summary = processor.process_scenarios(test_scenarios)
    
    # Print summary
    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    print(f"Total Scenarios:  {summary['total_scenarios']}")
    print(f"Successful:       {summary['successful']}")
    print(f"Failed:           {summary['failed']}")
    if summary['total_scenarios'] > 0:
        success_rate = (summary['successful'] / summary['total_scenarios']) * 100
        print(f"Success Rate:     {success_rate:.1f}%")
    print(f"Output Directory: {base_dir}")
    print("="*80 + "\n")
    
    # Detail results
    print("SCENARIO RESULTS:")
    print("-" * 80)
    for scenario in summary['scenarios']:
        status_icon = "✅" if scenario.get('status') == 'success' else "❌"
        print(f"{status_icon} {scenario.get('title', 'Unknown')}")
        if scenario.get('status') == 'failed':
            print(f"   Error: {scenario.get('error')}")
    
    print("\n✨ Batch processing complete!")
    return summary

if __name__ == "__main__":
    main()
