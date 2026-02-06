"""
Skillable Simulator: End-to-End Demo
Demonstrates the complete workflow from TechConnect context retrieval
to lab instructions generation.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skillable_simulator.generator import LabInstructionGenerator
from ingestion.scraper import CatalogScraper
from vector_store.store import SimpleVectorStore
from models.schemas import ContextBlock


class SkillableSimulator:
    """
    Simulates the Skillable Gen AI Lab Instructions Generator.
    This is the downstream consumer of TechConnect context blocks.
    """
    
    def __init__(self, catalog_path: str = "catalog.json"):
        """
        Initialize the simulator with TechConnect components.
        
        Args:
            catalog_path: Path to catalog.json
        """
        self.scraper = CatalogScraper(catalog_path)
        self.vector_store = SimpleVectorStore()
        self.generator = LabInstructionGenerator()
        self.catalog_data = self.scraper.load_catalog()
        
        # Ingest catalog into vector store
        # CatalogData has solution_accelerators, not data.accelerators
        accelerators = self.catalog_data.solution_accelerators
        self.vector_store.ingest_accelerators(accelerators)
    
    def fetch_context_block(self, scenario_title: str, 
                           solution_area: Optional[str] = None,
                           complexity_level: Optional[str] = None) -> Optional[ContextBlock]:
        """
        Simulate fetching context from TechConnect broker.
        
        Args:
            scenario_title: The scenario/problem to solve
            solution_area: Optional filter (AI, Data, etc.)
            complexity_level: Optional filter (L200, L300, L400)
            
        Returns:
            ContextBlock or None if no match found
        """
        # Search vector store for best match
        search_result = self.vector_store.search(
            query=scenario_title,
            solution_area=solution_area,
            complexity=complexity_level,
            n_results=1
        )
        
        if not search_result or not search_result["ids"]:
            return None
        
        # Get the matching accelerator from the catalog
        matched_id = search_result["ids"][0]
        matched_accel = None
        
        for acc in self.catalog_data.solution_accelerators:
            if acc.id == matched_id:
                matched_accel = acc
                break
        
        if not matched_accel:
            return None
        
        # Convert accelerator to ContextBlock
        context_block = ContextBlock(
            catalog_item_id=matched_accel.id,
            solution_name=matched_accel.name,
            solution_area=matched_accel.solution_area,
            complexity_level=matched_accel.technical_complexity,
            architecture_summary=matched_accel.description,
            prerequisites_xml=self._format_prerequisites_xml(matched_accel.prerequisites),
            products_xml=self._format_products_xml(matched_accel.products_and_services),
            rai_disclaimer=self._get_rai_disclaimer() if matched_accel.responsible_ai_tag else None,
            repository_url=matched_accel.repository_url
        )
        
        return context_block
    
    def _format_prerequisites_xml(self, prerequisites: List[str]) -> str:
        """Format prerequisites list as XML."""
        if not prerequisites:
            return "<prerequisites></prerequisites>"
        items = "".join(f"<item>{p}</item>" for p in prerequisites)
        return f"<prerequisites>{items}</prerequisites>"
    
    def _format_products_xml(self, products: List[str]) -> str:
        """Format products list as XML."""
        if not products:
            return "<products></products>"
        items = "".join(f"<item>{p}</item>" for p in products)
        return f"<products>{items}</products>"
    
    def _get_rai_disclaimer(self) -> str:
        """Get standard RAI disclaimer for AI solutions."""
        return """This solution includes Generative AI/LLM components. 
The following governance practices are required:
- Enable monitoring for model outputs
- Implement human review workflows  
- Document AI capabilities and limitations
- Ensure Microsoft RAI compliance
- Setup audit logging and tracking"""
    
    def generate_complete_lab(self, scenario_title: str,
                             solution_area: Optional[str] = None,
                             complexity_level: Optional[str] = None,
                             output_dir: Optional[str] = None) -> Dict:
        """
        Generate a complete lab package (instructions + deployment script + report).
        
        Args:
            scenario_title: The scenario to create a lab for
            solution_area: Optional filter
            complexity_level: Optional filter
            output_dir: Optional directory to save files
            
        Returns:
            Dict with generated content (guide, script, report)
        """
        print(f"\n{'='*70}")
        print(f"  SKILLABLE LAB GENERATION WORKFLOW")
        print(f"  Scenario: {scenario_title}")
        print(f"{'='*70}\n")
        
        # Step 1: Fetch context from TechConnect broker
        print("[1/4] Fetching context from TechConnect broker...")
        context_block = self.fetch_context_block(
            scenario_title, 
            solution_area=solution_area,
            complexity_level=complexity_level
        )
        
        if not context_block:
            print(f"  [FAIL] No matching context found for: {scenario_title}")
            return {}
        
        print(f"  [PASS] Found: {context_block.solution_name}")
        print(f"    - Complexity: {context_block.complexity_level}")
        print(f"    - Area: {context_block.solution_area}")
        print(f"    - Repository: {context_block.repository_url}")
        
        # Step 2: Generate lab guide
        print("\n[2/4] Generating lab instructions...")
        guide = self.generator.generate_lab_guide(context_block)
        print(f"  [PASS] Generated guide with {len(guide['lab_steps'])} sections")
        print(f"    - {sum(len(s['steps']) for s in guide['lab_steps'])} total steps")
        
        # Step 3: Generate deployment script
        print("\n[3/4] Generating deployment script...")
        script = self.generator.generate_deployment_script(context_block)
        print(f"  [PASS] Generated bash deployment script ({len(script)} chars)")
        
        # Step 4: Generate lab report
        print("\n[4/4] Generating lab report...")
        report = self.generator.generate_lab_report(context_block, guide)
        print(f"  [PASS] Generated formatted lab report")
        
        result = {
            "context_block": context_block,
            "guide": guide,
            "deployment_script": script,
            "lab_report": report
        }
        
        # Save to files if output_dir provided
        if output_dir:
            self._save_lab_package(output_dir, context_block, result)
        
        print(f"\n{'='*70}")
        print(f"  [PASS] Lab generation complete!")
        print(f"{'='*70}\n")
        
        return result
    
    def _save_lab_package(self, output_dir: str, 
                         context_block: ContextBlock, 
                         result: Dict) -> None:
        """Save generated lab package to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save guide as JSON
        guide_file = output_path / f"{context_block.catalog_item_id}_guide.json"
        with open(guide_file, 'w') as f:
            json.dump(result['guide'], f, indent=2)
        print(f"\n  Saved: {guide_file}")
        
        # Save deployment script
        script_file = output_path / f"{context_block.catalog_item_id}_deploy.sh"
        with open(script_file, 'w') as f:
            f.write(result['deployment_script'])
        print(f"  Saved: {script_file}")
        
        # Save lab report
        report_file = output_path / f"{context_block.catalog_item_id}_report.txt"
        with open(report_file, 'w') as f:
            f.write(result['lab_report'])
        print(f"  Saved: {report_file}")
    
    def simulate_multiple_requests(self) -> List[Dict]:
        """
        Simulate multiple lab generation requests from different users.
        Demonstrates realistic usage patterns.
        """
        test_scenarios = [
            {
                "title": "Deploy multi-agent automation system",
                "area": "AI",
                "complexity": "L400"
            },
            {
                "title": "Build document processing pipeline",
                "area": "AI",
                "complexity": "L300"
            },
            {
                "title": "Setup unified data platform",
                "area": "Data",
                "complexity": "L400"
            },
            {
                "title": "Create AI solution with responsible AI",
                "area": None,
                "complexity": None
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            print(f"\nProcessing scenario: {scenario['title']}")
            result = self.generate_complete_lab(
                scenario['title'],
                solution_area=scenario['area'],
                complexity_level=scenario['complexity']
            )
            results.append(result)
        
        return results
    
    def get_lab_metadata_summary(self) -> Dict:
        """Get summary of all available labs in the catalog."""
        accelerators = self.catalog_data.solution_accelerators
        
        summary = {
            "total_labs": len(accelerators),
            "by_complexity": {},
            "by_area": {},
            "labs": []
        }
        
        for acc in accelerators:
            # By complexity
            complexity = acc.technical_complexity
            if complexity not in summary["by_complexity"]:
                summary["by_complexity"][complexity] = []
            summary["by_complexity"][complexity].append(acc.name)
            
            # By area
            area = acc.solution_area
            if area not in summary["by_area"]:
                summary["by_area"][area] = []
            summary["by_area"][area].append(acc.name)
            
            # Lab details
            summary["labs"].append({
                "id": acc.id,
                "name": acc.name,
                "area": acc.solution_area,
                "complexity": acc.technical_complexity,
                "rai_required": acc.responsible_ai_tag,
                "repository": acc.repository_url
            })
        
        return summary


def main():
    """Run the Skillable simulator demo."""
    print("\n" + "="*70)
    print("  SKILLABLE GEN AI LAB INSTRUCTIONS GENERATOR - SIMULATOR")
    print("="*70)
    
    # Initialize simulator
    simulator = SkillableSimulator()
    
    # Show available labs
    print("\n[CATALOG] Available Labs:")
    metadata = simulator.get_lab_metadata_summary()
    print(f"  Total: {metadata['total_labs']} labs")
    print(f"  By Complexity: {json.dumps(metadata['by_complexity'], indent=4)}")
    print(f"  By Area: {json.dumps(metadata['by_area'], indent=4)}")
    
    # Generate a single lab as example
    print("\n\n[DEMO] Generating a sample lab...")
    result = simulator.generate_complete_lab(
        "Deploy AI automation agents for enterprise workflows",
        solution_area="AI",
        complexity_level="L400",
        output_dir="./lab_output"
    )
    
    if result:
        # Print excerpt of generated guide
        print("\n[SAMPLE] Lab Instructions Guide Structure:")
        guide = result['guide']
        print(f"\n  Lab Title: {guide['lab_metadata']['title']}")
        print(f"  Estimated Duration: {guide['lab_metadata']['duration']}")
        print(f"\n  Lab Sections:")
        for section in guide['lab_steps']:
            print(f"    - {section['section']}: {len(section['steps'])} steps")
        
        # Print excerpt of lab report
        print("\n[SAMPLE] Lab Report (first 500 chars):")
        print("  " + result['lab_report'][:500].replace("\n", "\n  ") + "...\n")


if __name__ == "__main__":
    main()
