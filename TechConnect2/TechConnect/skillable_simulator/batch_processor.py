"""
Batch Processing Module for Skillable Simulator

Processes multiple scenarios, generating lab instructions for each.
Supports both single-repo and cross-repo composite labs.
Stores output in separate folders with markdown format and input scenario metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from skillable_simulator.simulator import SkillableSimulator
from skillable_simulator.generator import LabInstructionGenerator
from skillable_simulator.composite_generator import CompositeLabGenerator
from models.schemas import ContextBlock
from vector_store.store import VectorStore


class BatchProcessor:
    """Process multiple scenarios in batch mode (single-repo and composite)"""
    
    def __init__(self, base_output_dir: str = "lab_runs", vector_store: Optional[VectorStore] = None):
        """
        Initialize batch processor
        
        Args:
            base_output_dir: Root directory for all batch outputs
            vector_store: VectorStore instance for composite lab generation
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.results = []
        self.vector_store = vector_store
        self.composite_generator = None
        if vector_store:
            self.composite_generator = CompositeLabGenerator(vector_store)
        
    def process_scenarios(self, scenarios: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process a list of scenarios (single-repo or composite)
        
        Args:
            scenarios: List of scenario dicts with 'title', 'solution_area', 'complexity'
                      Composite scenarios also have 'secondary_areas' and 'is_composite': True
            
        Returns:
            Summary of processing results
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(scenarios),
            "successful": 0,
            "failed": 0,
            "composite_scenarios": 0,
            "scenarios": []
        }
        
        for idx, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*80}")
            print(f"Processing Scenario {idx}/{len(scenarios)}: {scenario['title']}")
            is_composite = scenario.get('is_composite', False)
            if is_composite:
                print(f"[COMPOSITE] Combining {len(scenario.get('secondary_areas', [])) + 1} repos")
            print(f"{'='*80}")
            
            try:
                result = self._process_single_scenario(scenario, idx)
                summary["scenarios"].append(result)
                summary["successful"] += 1
                if is_composite:
                    summary["composite_scenarios"] += 1
                print(f"[SUCCESS] Scenario {idx} completed successfully")
            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Scenario {idx} failed: {error_msg}")
                summary["scenarios"].append({
                    "scenario_number": idx,
                    "title": scenario['title'],
                    "status": "failed",
                    "error": error_msg,
                    "output_dir": None
                })
                summary["failed"] += 1
                
        return summary
    
    def _process_single_scenario(self, scenario: Dict[str, str], scenario_num: int) -> Dict[str, Any]:
        """
        Process a single scenario (single-repo or composite)
        
        Args:
            scenario: Scenario dict (may include is_composite, secondary_areas, num_repos)
            scenario_num: Scenario number for directory naming
            
        Returns:
            Result dict with processing details
        """
        # Create output directory for this scenario
        scenario_slug = self._create_slug(scenario['title'])
        output_dir = self.base_output_dir / f"{scenario_num:02d}-{scenario_slug}"
        output_dir.mkdir(exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        
        # Save input scenario as metadata
        scenario_file = output_dir / "input_scenario.json"
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Input scenario: {scenario_file}")
        
        # Determine if this is a composite scenario
        is_composite = scenario.get('is_composite', False)
        
        if is_composite and self.composite_generator:
            return self._process_composite_scenario(scenario, output_dir)
        else:
            return self._process_single_repo_scenario(scenario, output_dir)
    
    def _process_single_repo_scenario(
        self,
        scenario: Dict[str, str],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Process traditional single-repo lab scenario."""
        
        # Initialize simulator and generate lab
        simulator = SkillableSimulator()
        
        # Fetch context block
        print(f"[FETCH] Fetching context block for: {scenario['title']}")
        context_block = simulator.fetch_context_block(
            scenario_title=scenario['title'],
            solution_area=scenario.get('solution_area'),
            complexity_level=scenario.get('complexity')
        )
        
        if not context_block:
            raise Exception(f"No context block found for scenario: {scenario['title']}")
        
        # Generate lab instructions
        print(f"[GENERATE] Creating lab instructions...")
        generator = LabInstructionGenerator()
        
        # Generate guide (JSON)
        guide = generator.generate_lab_guide(context_block)
        guide_file = output_dir / "lab_guide.md"
        self._save_guide_as_markdown(guide, guide_file)
        print(f"[SAVE] Lab guide: {guide_file}")
        
        # Generate deployment script as markdown
        script = generator.generate_deployment_script(context_block)
        script_file = output_dir / "deployment_script.md"
        self._save_script_as_markdown(script, script_file)
        print(f"[SAVE] Deployment script: {script_file}")
        
        # Generate lab report as markdown (pass guide as second argument)
        report = generator.generate_lab_report(context_block, guide)
        report_file = output_dir / "lab_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[SAVE] Lab report: {report_file}")
        
        # Save context block metadata
        context_file = output_dir / "context_block.json"
        context_dict = {
            "title": context_block.title if hasattr(context_block, 'title') else "Unknown",
            "solution_area": context_block.solution_area if hasattr(context_block, 'solution_area') else "Unknown",
            "complexity": context_block.complexity if hasattr(context_block, 'complexity') else 0,
            "prerequisites": context_block.prerequisites if hasattr(context_block, 'prerequisites') else [],
            "technologies": context_block.technologies if hasattr(context_block, 'technologies') else [],
        }
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context_dict, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Context block: {context_file}")
        
        # Create processing summary
        summary_file = output_dir / "PROCESSING_SUMMARY.md"
        self._save_processing_summary(summary_file, scenario, scenario_num, output_dir)
        print(f"[SAVE] Processing summary: {summary_file}")
        
        return {
            "scenario_number": scenario_num,
            "title": scenario['title'],
            "status": "success",
            "output_dir": str(output_dir),
            "files": {
                "input_scenario": str(scenario_file),
                "lab_guide": str(guide_file),
                "deployment_script": str(script_file),
                "lab_report": str(report_file),
                "context_block": str(context_file),
                "processing_summary": str(summary_file)
            }
        }
    
    def _process_composite_scenario(
        self,
        scenario: Dict[str, str],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Process composite multi-repo lab scenario."""
        
        print(f"[COMPOSITE] Generating integrated lab from multiple repos...")
        
        # Generate composite lab
        composite_lab = self.composite_generator.generate_composite_lab(
            scenario_title=scenario['title'],
            primary_solution_area=scenario['solution_area'],
            secondary_areas=scenario.get('secondary_areas'),
            num_repos=scenario.get('num_repos', 2)
        )
        
        # Save full composite lab structure as JSON
        composite_file = output_dir / "composite_lab.json"
        with open(composite_file, 'w', encoding='utf-8') as f:
            json.dump(composite_lab, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Composite lab structure: {composite_file}")
        
        # Save synthesized instructions as markdown
        instructions_file = output_dir / "lab_guide.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(composite_lab['synthesized_instructions'])
        print(f"[SAVE] Synthesized instructions: {instructions_file}")
        
        # Save architecture diagram
        architecture_file = output_dir / "architecture.md"
        with open(architecture_file, 'w', encoding='utf-8') as f:
            arch = composite_lab['integrated_architecture']
            f.write("# Integrated Architecture\n\n")
            f.write(f"**Pattern:** {arch['integration_pattern']}\n\n")
            f.write("## Components\n\n")
            for comp in arch['components']:
                f.write(f"### Layer {comp['index']}: {comp['repo_id']}\n")
                f.write(f"- **Role:** {comp['role']}\n")
                f.write(f"- **Solution Area:** {comp['solution_area']}\n")
                f.write(f"- **Services:** {', '.join(comp['key_services'])}\n\n")
            f.write("\n## Data Flows\n\n")
            for flow in arch['data_flows']:
                f.write(f"- **{flow['from']}** → {flow['data_type']} → **{flow['to']}**\n")
            f.write("\n## ASCII Diagram\n\n```\n")
            f.write(arch['diagram_ascii'])
            f.write("\n```\n")
        print(f"[SAVE] Architecture diagram: {architecture_file}")
        
        # Save deployment steps
        deployment_file = output_dir / "deployment_script.md"
        with open(deployment_file, 'w', encoding='utf-8') as f:
            f.write("# Deployment Steps\n\n")
            f.write(f"**Estimated Duration:** {composite_lab['estimated_duration_hours']} hours\n\n")
            for step in composite_lab['deployment_steps']:
                f.write(f"## Step {step['sequence']}: {step['title']}\n\n")
                f.write(f"**Phase:** {step['phase']}\n")
                f.write(f"**Estimated Time:** {step['estimated_minutes']} minutes\n\n")
                f.write(f"{step['description']}\n\n")
                if step.get('commands'):
                    f.write("### Commands\n\n```bash\n")
                    f.write("\n".join(step['commands']))
                    f.write("\n```\n\n")
                f.write("---\n\n")
        print(f"[SAVE] Deployment steps: {deployment_file}")
        
        # Save prerequisites
        prerequisites_file = output_dir / "prerequisites.md"
        with open(prerequisites_file, 'w', encoding='utf-8') as f:
            f.write("# Prerequisites\n\n")
            for i, prereq in enumerate(composite_lab['prerequisites'], 1):
                f.write(f"{i}. {prereq}\n")
        print(f"[SAVE] Prerequisites: {prerequisites_file}")
        
        # Save RAI disclaimer if applicable
        if composite_lab['rai_disclaimer']:
            rai_file = output_dir / "RAI_DISCLAIMER.md"
            with open(rai_file, 'w', encoding='utf-8') as f:
                f.write(composite_lab['rai_disclaimer'])
            print(f"[SAVE] RAI Disclaimer: {rai_file}")
        
        # Save context block from primary repo
        context_file = output_dir / "context_block.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scenario": scenario['title'],
                "composite_sources": composite_lab['composite_sources'],
                "source_repos": composite_lab['source_repos'],
                "estimated_duration_hours": composite_lab['estimated_duration_hours'],
                "responsible_ai_tag": composite_lab['responsible_ai_tag']
            }, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Context block: {context_file}")
        
        # Save processing summary
        summary_file = output_dir / "PROCESSING_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Processing Summary\n\n")
            f.write(f"**Scenario:** {scenario['title']}\n")
            f.write(f"**Type:** Composite Multi-Repo Lab\n")
            f.write(f"**Repos Combined:** {len(composite_lab['composite_sources'])}\n")
            f.write(f"**Sources:** {', '.join(composite_lab['composite_sources'])}\n")
            f.write(f"**Duration:** {composite_lab['estimated_duration_hours']} hours\n")
            f.write(f"**RAI Disclaimer Required:** {'Yes' if composite_lab['responsible_ai_tag'] else 'No'}\n\n")
            f.write("## Generated Files\n\n")
            f.write("- `lab_guide.md` - Synthesized integrated instructions\n")
            f.write("- `architecture.md` - Component architecture and data flows\n")
            f.write("- `deployment_script.md` - Step-by-step deployment\n")
            f.write("- `prerequisites.md` - All prerequisites\n")
            f.write("- `composite_lab.json` - Full composite lab structure\n")
            if composite_lab['rai_disclaimer']:
                f.write("- `RAI_DISCLAIMER.md` - Responsible AI considerations\n")
        print(f"[SAVE] Processing summary: {summary_file}")
        
        # Return result dict
        return {
            "scenario_number": 0,  # Will be set by caller
            "title": scenario['title'],
            "status": "success",
            "type": "composite",
            "repos_combined": len(composite_lab['composite_sources']),
            "sources": composite_lab['composite_sources'],
            "output_dir": str(output_dir)
        }
    
    def _create_slug(self, title: str) -> str:
        """Convert title to directory-safe slug"""
        slug = title.lower()
        slug = "".join(c if c.isalnum() or c == ' ' else '' for c in slug)
        slug = slug.strip().replace(' ', '_')
        return slug[:50]  # Limit length
    
    def _save_guide_as_markdown(self, guide: Dict[str, Any], output_file: Path) -> None:
        """Convert JSON guide to markdown format"""
        md_lines = []
        
        # Title and Metadata
        metadata = guide.get('metadata', {})
        md_lines.append(f"# Lab: {metadata.get('title', 'Untitled')}\n")
        md_lines.append(f"**Lab ID:** {metadata.get('lab_id', 'N/A')}")
        md_lines.append(f"**Complexity Level:** {metadata.get('complexity_level', 'N/A')}")
        md_lines.append(f"**Solution Area:** {metadata.get('solution_area', 'N/A')}")
        md_lines.append(f"**Duration:** {metadata.get('estimated_duration', 'N/A')}")
        md_lines.append(f"**Repository:** {metadata.get('repository_url', 'N/A')}\n")
        
        # Overview
        if 'overview' in guide:
            md_lines.append("## Lab Overview\n")
            md_lines.append(f"{guide['overview'].get('objective', 'N/A')}\n")
            
            if 'learning_outcomes' in guide['overview']:
                md_lines.append("### Learning Outcomes\n")
                for outcome in guide['overview'].get('learning_outcomes', []):
                    md_lines.append(f"- {outcome}")
                md_lines.append("")
        
        # Prerequisites
        if 'prerequisites' in guide:
            md_lines.append("\n## Prerequisites\n")
            for prereq in guide['prerequisites']:
                if isinstance(prereq, dict):
                    md_lines.append(f"- **{prereq.get('item', 'N/A')}**")
                    if 'description' in prereq:
                        md_lines.append(f"  - {prereq['description']}")
                    if 'validation_command' in prereq:
                        md_lines.append(f"  - Validation: `{prereq['validation_command']}`")
                else:
                    md_lines.append(f"- {prereq}")
        
        # Technologies
        if 'technologies' in guide:
            md_lines.append("\n## Technologies Used\n")
            if isinstance(guide['technologies'], dict):
                if 'azure_services' in guide['technologies']:
                    md_lines.append("### Azure Services\n")
                    for service in guide['technologies']['azure_services']:
                        md_lines.append(f"- {service}")
                if 'programming_languages' in guide['technologies']:
                    md_lines.append("\n### Programming Languages\n")
                    for lang in guide['technologies']['programming_languages']:
                        md_lines.append(f"- {lang}")
        
        # Lab Steps
        if 'lab_steps' in guide:
            md_lines.append("\n## Lab Steps\n")
            for section in guide['lab_steps']:
                md_lines.append(f"\n### {section.get('section_name', 'Unknown Section')}\n")
                md_lines.append(f"**Time Estimate:** {section.get('time_estimate', 'N/A')}\n")
                for step in section.get('steps', []):
                    md_lines.append(f"\n**{step.get('step_number', 'N/A')}. {step.get('title', 'Untitled')}**\n")
                    md_lines.append(f"{step.get('description', 'N/A')}\n")
                    if step.get('code_snippet'):
                        md_lines.append("```")
                        md_lines.append(step['code_snippet'])
                        md_lines.append("```\n")
        
        # Validation & Success Criteria
        if 'validation' in guide:
            md_lines.append("\n## Validation & Success Criteria\n")
            for criteria in guide['validation'].get('success_criteria', []):
                md_lines.append(f"- [PASS] {criteria}")
        
        # RAI Governance
        if 'responsible_ai_governance' in guide:
            rai = guide['responsible_ai_governance']
            md_lines.append("\n## Responsible AI Governance\n")
            md_lines.append(f"**RAI Required:** {rai.get('required', False)}\n")
            if rai.get('required'):
                md_lines.append("### RAI Requirements\n")
                for req in rai.get('requirements', []):
                    md_lines.append(f"- {req}")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
    
    def _save_script_as_markdown(self, script: str, output_file: Path) -> None:
        """Convert bash script to markdown format"""
        md_content = f"""# Deployment Script

This script automates the deployment of the lab environment.

## Script Content

```bash
{script}
```

## How to Use

1. Save this script to a file: `deploy.sh`
2. Make it executable: `chmod +x deploy.sh`
3. Run the script: `./deploy.sh`

## Prerequisites

- Azure CLI installed
- Azure subscription with appropriate permissions
- Required Azure services available in your region

## Script Breakdown

The deployment script performs the following operations:

1. **Prerequisite Validation** - Checks that all required tools and permissions are in place
2. **Environment Setup** - Configures environment variables and resource locations
3. **Resource Deployment** - Creates Azure resources as defined in the lab configuration
4. **Configuration** - Applies configuration and settings to deployed resources
5. **Validation** - Verifies that all resources are deployed correctly

## Troubleshooting

If the script fails:

1. Check that you have the correct Azure subscription selected
2. Verify that your account has sufficient permissions
3. Ensure all prerequisites are installed and accessible
4. Review the error messages for specific issues
5. Check Azure service availability in your region

"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _save_processing_summary(self, output_file: Path, scenario: Dict[str, str], 
                                scenario_num: int, output_dir: Path) -> None:
        """Create a processing summary document"""
        summary = f"""# Processing Summary - Scenario {scenario_num}

**Generated:** {datetime.now().isoformat()}

## Input Scenario

| Field | Value |
|-------|-------|
| Title | {scenario.get('title', 'N/A')} |
| Solution Area | {scenario.get('solution_area', 'N/A')} |
| Complexity Level | {scenario.get('complexity', 'N/A')} |

## Output Files

This scenario has generated the following lab materials:

- **lab_guide.md** - Complete lab guide in markdown format
- **deployment_script.md** - Automated deployment script with documentation
- **lab_report.md** - Formatted lab report with all instructions
- **context_block.json** - Context metadata from TechConnect broker
- **input_scenario.json** - Original input scenario data

## File Locations

All files for this scenario are stored in: `{output_dir}`

## Next Steps

1. Review the lab_guide.md for complete lab instructions
2. Use deployment_script.md to automate resource setup
3. Follow lab_report.md for detailed step-by-step instructions
4. Store context_block.json for reference and metadata tracking

## Integration Notes

- All files are in UTF-8 encoding with Markdown formatting
- The deployment script includes bash code that can be extracted and executed
- The lab guide includes structured data suitable for LMS integration
- Context metadata can be stored in your knowledge base for future reference

---
*This lab was generated by the Skillable Simulator from a TechConnect context block.*
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
    
    def save_batch_summary(self, summary: Dict[str, Any]) -> Path:
        """Save overall batch processing summary"""
        summary_file = self.base_output_dir / "BATCH_PROCESSING_SUMMARY.md"
        
        md_lines = [
            "# Batch Processing Summary\n",
            f"**Generated:** {summary['timestamp']}\n",
            f"**Total Scenarios:** {summary['total_scenarios']}",
            f"**Successful:** {summary['successful']}",
            f"**Failed:** {summary['failed']}\n",
            "## Scenarios Processed\n",
        ]
        
        for scenario in summary['scenarios']:
            status = "[SUCCESS]" if scenario['status'] == 'success' else "[FAILED]"
            md_lines.append(f"### {status} Scenario {scenario['scenario_number']}: {scenario['title']}\n")
            
            if scenario['status'] == 'success':
                md_lines.append(f"**Output Directory:** `{scenario['output_dir']}`\n")
                md_lines.append("**Generated Files:**\n")
                for file_type, file_path in scenario.get('files', {}).items():
                    md_lines.append(f"- {file_type}: `{file_path}`")
            else:
                md_lines.append(f"**Error:** {scenario.get('error', 'Unknown error')}\n")
            
            md_lines.append("")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        return summary_file


# Predefined scenarios - matched to available accelerators
SAMPLE_SCENARIOS = [
    {
        "title": "Deploy Multi-Agent Custom Automation Engine",
        "solution_area": "AI",
        "complexity": "L400",
        "description": "Implement multi-agent orchestration for enterprise automation workflows"
    },
    {
        "title": "Multi-Agent Custom Automation Engine for Customer Support",
        "solution_area": "AI",
        "complexity": "L300",
        "description": "Deploy multi-agent system to automate customer support routing and resolution"
    },
    {
        "title": "Multi-Agent Custom Automation Engine",
        "solution_area": "AI",
        "complexity": "L350",
        "description": "Build multi-agent automation for complex business process orchestration"
    },
    {
        "title": "Content Processing Accelerator Implementation",
        "solution_area": "AI",
        "complexity": "L300",
        "description": "Deploy content processing system for document intelligence and extraction"
    },
    {
        "title": "Content Processing Accelerator",
        "solution_area": "AI",
        "complexity": "L250",
        "description": "Build intelligent document summarization and metadata extraction pipeline"
    },
    {
        "title": "Content Processing for Enterprise",
        "solution_area": "AI",
        "complexity": "L300",
        "description": "Implement end-to-end content processing for compliance and analysis"
    },
    {
        "title": "Unified Data Foundation with Fabric",
        "solution_area": "Data",
        "complexity": "L350",
        "description": "Deploy unified data platform using Microsoft Fabric for integrated analytics"
    },
    {
        "title": "Unified Data Foundation",
        "solution_area": "Data",
        "complexity": "L300",
        "description": "Build comprehensive data integration and warehouse solution with Fabric"
    },
    {
        "title": "Data Foundation Fabric",
        "solution_area": "Data",
        "complexity": "L400",
        "description": "Create enterprise-scale analytics and data governance platform using Fabric"
    },
    {
        "title": "Fabric Unified Data Foundation",
        "solution_area": "Data",
        "complexity": "L350",
        "description": "Implement real-time analytics and data discovery using unified Fabric foundation"
    }
]


def run_batch_processing():
    """Main entry point for batch processing"""
    print("\n" + "="*80)
    print("SKILLABLE SIMULATOR - BATCH PROCESSING")
    print("="*80 + "\n")
    
    processor = BatchProcessor(base_output_dir="lab_runs")
    
    print(f"Processing {len(SAMPLE_SCENARIOS)} scenarios...\n")
    summary = processor.process_scenarios(SAMPLE_SCENARIOS)
    
    # Save batch summary
    summary_file = processor.save_batch_summary(summary)
    
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETE")
    print("="*80)
    print(f"Summary: {summary['successful']} successful, {summary['failed']} failed")
    if summary.get('composite_scenarios', 0) > 0:
        print(f"Composite scenarios: {summary['composite_scenarios']}")
    print(f"Batch summary saved to: {summary_file}")
    print(f"All scenario outputs in: {processor.base_output_dir}")
    print("="*80 + "\n")
    
    return summary
    
    def _process_composite_scenario(
        self,
        scenario: Dict[str, str],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Process composite multi-repo lab scenario."""
        
        print(f"[COMPOSITE] Generating integrated lab from multiple repos...")
        
        # Generate composite lab
        composite_lab = self.composite_generator.generate_composite_lab(
            scenario_title=scenario['title'],
            primary_solution_area=scenario['solution_area'],
            secondary_areas=scenario.get('secondary_areas'),
            num_repos=scenario.get('num_repos', 2)
        )
        
        # Save full composite lab structure as JSON
        composite_file = output_dir / "composite_lab.json"
        with open(composite_file, 'w', encoding='utf-8') as f:
            json.dump(composite_lab, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Composite lab structure: {composite_file}")
        
        # Save synthesized instructions as markdown
        instructions_file = output_dir / "lab_guide.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(composite_lab['synthesized_instructions'])
        print(f"[SAVE] Synthesized instructions: {instructions_file}")
        
        # Save architecture diagram
        architecture_file = output_dir / "architecture.md"
        with open(architecture_file, 'w', encoding='utf-8') as f:
            arch = composite_lab['integrated_architecture']
            f.write("# Integrated Architecture\n\n")
            f.write(f"**Pattern:** {arch['integration_pattern']}\n\n")
            f.write("## Components\n\n")
            for comp in arch['components']:
                f.write(f"### Layer {comp['index']}: {comp['repo_id']}\n")
                f.write(f"- **Role:** {comp['role']}\n")
                f.write(f"- **Solution Area:** {comp['solution_area']}\n")
                f.write(f"- **Services:** {', '.join(comp['key_services'])}\n\n")
            f.write("\n## Data Flows\n\n")
            for flow in arch['data_flows']:
                f.write(f"- **{flow['from']}** → {flow['data_type']} → **{flow['to']}**\n")
            f.write("\n## ASCII Diagram\n\n```\n")
            f.write(arch['diagram_ascii'])
            f.write("\n```\n")
        print(f"[SAVE] Architecture diagram: {architecture_file}")
        
        # Save deployment steps
        deployment_file = output_dir / "deployment_script.md"
        with open(deployment_file, 'w', encoding='utf-8') as f:
            f.write("# Deployment Steps\n\n")
            f.write(f"**Estimated Duration:** {composite_lab['estimated_duration_hours']} hours\n\n")
            for step in composite_lab['deployment_steps']:
                f.write(f"## Step {step['sequence']}: {step['title']}\n\n")
                f.write(f"**Phase:** {step['phase']}\n")
                f.write(f"**Estimated Time:** {step['estimated_minutes']} minutes\n\n")
                f.write(f"{step['description']}\n\n")
                if step.get('commands'):
                    f.write("### Commands\n\n```bash\n")
                    f.write("\n".join(step['commands']))
                    f.write("\n```\n\n")
                f.write("---\n\n")
        print(f"[SAVE] Deployment steps: {deployment_file}")
        
        # Save prerequisites
        prerequisites_file = output_dir / "prerequisites.md"
        with open(prerequisites_file, 'w', encoding='utf-8') as f:
            f.write("# Prerequisites\n\n")
            for i, prereq in enumerate(composite_lab['prerequisites'], 1):
                f.write(f"{i}. {prereq}\n")
        print(f"[SAVE] Prerequisites: {prerequisites_file}")
        
        # Save RAI disclaimer if applicable
        if composite_lab['rai_disclaimer']:
            rai_file = output_dir / "RAI_DISCLAIMER.md"
            with open(rai_file, 'w', encoding='utf-8') as f:
                f.write(composite_lab['rai_disclaimer'])
            print(f"[SAVE] RAI Disclaimer: {rai_file}")
        
        # Save context block from primary repo
        context_file = output_dir / "context_block.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scenario": scenario['title'],
                "composite_sources": composite_lab['composite_sources'],
                "source_repos": composite_lab['source_repos'],
                "estimated_duration_hours": composite_lab['estimated_duration_hours'],
                "responsible_ai_tag": composite_lab['responsible_ai_tag']
            }, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Context block: {context_file}")
        
        # Save processing summary
        summary_file = output_dir / "PROCESSING_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Processing Summary\n\n")
            f.write(f"**Scenario:** {scenario['title']}\n")
            f.write(f"**Type:** Composite Multi-Repo Lab\n")
            f.write(f"**Repos Combined:** {len(composite_lab['composite_sources'])}\n")
            f.write(f"**Sources:** {', '.join(composite_lab['composite_sources'])}\n")
            f.write(f"**Duration:** {composite_lab['estimated_duration_hours']} hours\n")
            f.write(f"**RAI Disclaimer Required:** {'Yes' if composite_lab['responsible_ai_tag'] else 'No'}\n\n")
            f.write("## Generated Files\n\n")
            f.write("- `lab_guide.md` - Synthesized integrated instructions\n")
            f.write("- `architecture.md` - Component architecture and data flows\n")
            f.write("- `deployment_script.md` - Step-by-step deployment\n")
            f.write("- `prerequisites.md` - All prerequisites\n")
            f.write("- `composite_lab.json` - Full composite lab structure\n")
            if composite_lab['rai_disclaimer']:
                f.write("- `RAI_DISCLAIMER.md` - Responsible AI considerations\n")
        print(f"[SAVE] Processing summary: {summary_file}")
        
        # Return result dict
        return {
            "scenario_number": 0,  # Will be set by caller
            "title": scenario['title'],
            "status": "success",
            "type": "composite",
            "repos_combined": len(composite_lab['composite_sources']),
            "sources": composite_lab['composite_sources'],
            "output_dir": str(output_dir)
        }


if __name__ == "__main__":
    run_batch_processing()
