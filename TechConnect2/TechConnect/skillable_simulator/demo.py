"""
Skillable Simulator - Quick Start Demo
Shows the complete lab generation workflow with sample output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skillable_simulator.simulator import SkillableSimulator

def main():
    print("\n" + "="*80)
    print("  SKILLABLE GEN AI LAB INSTRUCTIONS GENERATOR - QUICK START DEMO")
    print("="*80 + "\n")
    
    # Initialize simulator
    print("[1/3] Initializing Skillable Simulator...")
    simulator = SkillableSimulator()
    print(f"  [OK] Simulator initialized with {len(simulator.catalog_data.solution_accelerators)} accelerators\n")
    
    # Show available labs
    print("[2/3] Available Labs in Catalog:")
    metadata = simulator.get_lab_metadata_summary()
    for i, lab in enumerate(metadata['labs'], 1):
        print(f"  {i}. {lab['name']}")
        print(f"     Area: {lab['area']} | Complexity: {lab['complexity']} | RAI Required: {lab['rai_required']}")
    print()
    
    # Generate a sample lab
    print("[3/3] Generating Sample Lab...")
    print("  Scenario: Deploy AI automation agents")
    result = simulator.generate_complete_lab(
        "Deploy AI automation agents for enterprise workflows",
        solution_area="AI",
        complexity_level="L400",
        output_dir="./lab_output"
    )
    
    if result:
        print("\n" + "="*80)
        print("  GENERATED LAB PACKAGE SUMMARY")
        print("="*80 + "\n")
        
        context = result['context_block']
        guide = result['guide']
        
        print(f"Solution Name:     {context.solution_name}")
        print(f"Solution ID:       {context.catalog_item_id}")
        print(f"Complexity Level:  {context.complexity_level}")
        print(f"Solution Area:     {context.solution_area}")
        print(f"Repository:        {context.repository_url}")
        print(f"Duration:          {guide['lab_metadata']['estimated_duration']}")
        print()
        
        print("Lab Sections:")
        for i, section in enumerate(guide['lab_steps'], 1):
            total_steps = len(section['steps'])
            print(f"  {i}. {section['section']} ({total_steps} steps)")
        print()
        
        print("Generated Outputs:")
        print(f"  - Lab Guide (JSON):         ~{len(str(guide))} chars")
        print(f"  - Deployment Script (Bash): {len(result['deployment_script'])} chars")
        print(f"  - Lab Report (Text):        {len(result['lab_report'])} chars")
        print()
        
        if context.rai_disclaimer:
            print("RAI Governance:")
            print(f"  [REQUIRED] This solution includes AI components")
            print(f"  - Disclaimer: Yes")
            print(f"  - Governance Required: Yes")
        print()
        
        print("Success! Lab package generated and saved to ./lab_output/")
        print("  - lab_output/accel-001_guide.json")
        print("  - lab_output/accel-001_deploy.sh")
        print("  - lab_output/accel-001_report.txt")
        
        print("\n" + "="*80)
        print("  DEMO COMPLETE")
        print("="*80 + "\n")
    else:
        print("[FAIL] Failed to generate lab")

if __name__ == "__main__":
    main()
