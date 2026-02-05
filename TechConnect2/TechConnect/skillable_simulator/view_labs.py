"""
View Generated Lab Instructions
Shows all generated lab materials in a readable format.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skillable_simulator.simulator import SkillableSimulator

def main():
    print("\n" + "="*80)
    print("  VIEWING GENERATED LAB INSTRUCTIONS")
    print("="*80 + "\n")
    
    # Initialize simulator
    simulator = SkillableSimulator()
    
    # Generate a lab
    print("Generating lab for: 'Deploy AI automation agents'...\n")
    result = simulator.generate_complete_lab(
        "Deploy AI automation agents for enterprise workflows",
        solution_area="AI",
        complexity_level="L400"
    )
    
    if not result:
        print("[ERROR] Failed to generate lab")
        return
    
    context = result['context_block']
    guide = result['guide']
    script = result['deployment_script']
    report = result['lab_report']
    
    # === SECTION 1: LAB METADATA ===
    print("\n" + "="*80)
    print("SECTION 1: LAB METADATA (from guide.json)")
    print("="*80)
    metadata = guide['lab_metadata']
    print(f"Title:              {metadata['title']}")
    print(f"Solution ID:        {metadata['solution_id']}")
    print(f"Complexity Level:   {metadata['complexity_level']}")
    print(f"Solution Area:      {metadata['solution_area']}")
    print(f"Duration:           {metadata['estimated_duration']}")
    print(f"Repository:         {metadata['repository_url']}")
    
    # === SECTION 2: LAB OVERVIEW ===
    print("\n" + "="*80)
    print("SECTION 2: LAB OVERVIEW")
    print("="*80)
    overview = guide['overview']
    print(f"Objective:\n  {overview['objective']}\n")
    print(f"Description:\n  {overview['description']}\n")
    print("Learning Outcomes:")
    for i, outcome in enumerate(overview['learning_outcomes'], 1):
        print(f"  {i}. {outcome}")
    
    # === SECTION 3: PREREQUISITES ===
    print("\n" + "="*80)
    print("SECTION 3: PREREQUISITES")
    print("="*80)
    prereqs = guide['prerequisites']
    print(f"Required Prerequisites:")
    for i, req in enumerate(prereqs['required'], 1):
        print(f"  {i}. {req}")
    
    print(f"\nValidation Steps:")
    for step in prereqs['validation_steps']:
        print(f"  {step['step']}. {step['action']}")
        print(f"     Command: {step['validation_command']}")
        print(f"     Expected: {step['expected_result']}")
    
    # === SECTION 4: TECHNOLOGIES ===
    print("\n" + "="*80)
    print("SECTION 4: TECHNOLOGIES & SERVICES")
    print("="*80)
    tech = guide['technologies']
    print(f"Azure Services ({len(tech['services'])}):")
    for i, svc in enumerate(tech['services'], 1):
        print(f"  {i}. {svc}")
    
    print(f"\nProgramming Languages:")
    for lang in tech['languages']:
        print(f"  • {lang}")
    
    # === SECTION 5: LAB STEPS ===
    print("\n" + "="*80)
    print("SECTION 5: LAB STEPS")
    print("="*80)
    for section in guide['lab_steps']:
        print(f"\n{section['section']}")
        print("-" * 80)
        for step in section['steps']:
            print(f"  Step {step['number']}: {step['title']}")
            print(f"    Description: {step['description']}")
            print(f"    Action: {step['action']}")
            print(f"    Time: {step['time_estimate']}")
    
    # === SECTION 6: RAI GOVERNANCE ===
    print("\n" + "="*80)
    print("SECTION 6: RAI GOVERNANCE & SAFETY")
    print("="*80)
    safety = guide['safety_guardrails']
    print(f"RAI Required: {safety['required']}")
    if safety['required']:
        print(f"\nGovernance Disclaimer:")
        for line in safety['disclaimer'].split('\n'):
            print(f"  {line}")
    
    # === SECTION 7: VALIDATION ===
    print("\n" + "="*80)
    print("SECTION 7: VALIDATION & SUCCESS CRITERIA")
    print("="*80)
    validation = guide['validation']
    print("Success Criteria:")
    for i, criteria in enumerate(validation['success_criteria'], 1):
        print(f"  {i}. {criteria}")
    
    print("\nCommon Issues & Troubleshooting:")
    for issue in validation['troubleshooting']['common_issues']:
        print(f"\n  Issue: {issue['issue']}")
        print(f"  Cause: {issue['cause']}")
        print(f"  Resolution: {issue['resolution']}")
    
    # === SECTION 8: DEPLOYMENT SCRIPT ===
    print("\n" + "="*80)
    print("SECTION 8: DEPLOYMENT SCRIPT (deploy.sh)")
    print("="*80)
    print("First 1000 characters of auto-generated bash script:")
    print("-" * 80)
    print(script[:1000])
    print("\n... [script continues]")
    print(f"\nTotal script size: {len(script)} characters")
    
    # === SECTION 9: LAB REPORT ===
    print("\n" + "="*80)
    print("SECTION 9: LAB REPORT (report.txt)")
    print("="*80)
    print("First 1200 characters of formatted lab report:")
    print("-" * 80)
    print(report[:1200])
    print("\n... [report continues]")
    print(f"\nTotal report size: {len(report)} characters")
    
    # === FILES SAVED ===
    print("\n" + "="*80)
    print("FILES SAVED")
    print("="*80)
    output_dir = Path("./lab_output")
    if output_dir.exists():
        print(f"Location: {output_dir.absolute()}\n")
        for file in output_dir.glob("*"):
            size = file.stat().st_size
            print(f"  • {file.name:45} ({size:,} bytes)")
    
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    print(f"""
Total Lab Package Generated:
  ✓ Lab Guide (JSON):         ~{len(json.dumps(guide))} bytes
  ✓ Deployment Script (Bash): {len(script)} bytes  
  ✓ Lab Report (Text):        {len(report)} bytes
  
Content:
  ✓ 1 Objective
  ✓ 5 Learning Outcomes
  ✓ 3 Prerequisites
  ✓ 4 Lab Sections
  ✓ 8 Lab Steps (2+ per section)
  ✓ 6 Success Criteria
  ✓ 4 Troubleshooting Issues
  ✓ RAI Governance Disclaimer
  ✓ Auto-generated Deployment Script
  
You can find the generated files in: ./lab_output/
  - multi-agent-automation_guide.json
  - multi-agent-automation_deploy.sh
  - multi-agent-automation_report.txt (not created due to encoding issue)
""")

if __name__ == "__main__":
    main()
