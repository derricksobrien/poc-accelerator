"""
Test Composite Lab Generation

Tests the cross-repo lab composition feature with realistic multi-repo scenarios.
Generates integrated labs combining 2-3 accelerators each.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from vector_store.store import VectorStore
from skillable_simulator.batch_processor import BatchProcessor


def main():
    """Run composite lab generation tests."""
    
    print("="*80)
    print("COMPOSITE LAB GENERATION TEST")
    print("="*80)
    print()
    
    # Initialize vector store (will load from existing catalog)
    print("[INIT] Loading vector store...")
    vector_store = VectorStore(persist_dir=Path(".chroma"))
    
    # Load catalog and ingest into vector store
    import json
    with open("catalog.json", "r") as f:
        catalog = json.load(f)
    
    # Import CatalogItem to convert catalog items
    from models.schemas import CatalogItem
    
    print("[INIT] Loading catalog accelerators...")
    accelerators = []
    for item in catalog.get("solution_accelerators", []):
        try:
            acc = CatalogItem(
                id=item.get("id"),
                name=item.get("name"),
                description=item.get("description", ""),
                solution_area=item.get("solution_area"),
                technical_complexity=item.get("technical_complexity"),
                products_and_services=item.get("products_and_services", []),
                languages=item.get("languages", []),
                prerequisites=item.get("prerequisites", []),
                repository_url=item.get("repository_url", ""),
                deployment_type=item.get("deployment_type", ""),
                responsible_ai_tag=item.get("responsible_ai_tag", False)
            )
            accelerators.append(acc)
        except Exception as e:
            print(f"[WARN] Failed to load {item.get('id')}: {e}")
    
    print(f"[INIT] Ingesting {len(accelerators)} accelerators...")
    vector_store.ingest_accelerators(accelerators)
    
    # List indexed accelerators
    all_items = vector_store.list_all()
    print(f"[OK] Vector store loaded with {len(all_items)} accelerators\n")
    
    for accel in all_items:
        accel_id = accel.get("id") if isinstance(accel, dict) else accel.id
        area = accel.get("solution_area") if isinstance(accel, dict) else accel.solution_area
        complexity = accel.get("technical_complexity") if isinstance(accel, dict) else accel.technical_complexity
        print(f"  - {accel_id} ({area}, {complexity})")
    print()
    
    # Define composite test scenarios
    composite_scenarios = [
        {
            "title": "AI Agent with Document Processing & Governance",
            "description": "Build an intelligent agent that processes contracts with automated governance controls",
            "solution_area": "AI",
            "secondary_areas": [],
            "is_composite": True,
            "num_repos": 1
        },
        {
            "title": "Secure Data Foundation with AI Insights",
            "description": "Create enterprise data platform with AI-powered analytics and compliance guardrails",
            "solution_area": "Azure (Data & AI)",
            "secondary_areas": ["AI"],
            "is_composite": True,
            "num_repos": 2
        },
        {
            "title": "Real-Time AI Analytics with Data Quality",
            "description": "Build real-time analytics pipeline with AI recommendations and quality monitoring",
            "solution_area": "Azure (Data & AI)",
            "secondary_areas": ["AI"],
            "is_composite": True,
            "num_repos": 2
        },
        {
            "title": "Content Processing with RAG Agents",
            "description": "Extract insights from documents and build AI agents for retrieval-augmented generation",
            "solution_area": "AI",
            "secondary_areas": ["Azure (Data & AI)"],
            "is_composite": True,
            "num_repos": 2
        },
        {
            "title": "Governed AI Platform with Unified Data",
            "description": "Enterprise AI platform combining agents, data fabric, and compliance controls",
            "solution_area": "AI",
            "secondary_areas": ["Azure (Data & AI)"],
            "is_composite": True,
            "num_repos": 2
        }
    ]
    
    # Initialize batch processor with vector store for composite support
    print("[INIT] Initializing batch processor...\n")
    processor = BatchProcessor(
        base_output_dir="lab_runs/composite_test",
        vector_store=vector_store
    )
    
    # Process scenarios
    print("="*80)
    print(f"Processing {len(composite_scenarios)} composite scenarios...")
    print("="*80)
    print()
    
    summary = processor.process_scenarios(composite_scenarios)
    
    # Print summary
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total scenarios:     {summary['total_scenarios']}")
    print(f"Successful:          {summary['successful']}")
    print(f"Failed:              {summary['failed']}")
    print(f"Composite generated: {summary['composite_scenarios']}")
    print(f"Success rate:        {(summary['successful']/summary['total_scenarios']*100):.1f}%")
    print()
    print(f"Output directory: {processor.base_output_dir}")
    print("="*80)
    
    # Print per-scenario results (use ASCII symbols for terminal compatibility)
    print("\nScenario Results:\n")
    for scenario_result in summary['scenarios']:
        status = "OK" if scenario_result['status'] == 'success' else "FAIL"
        print(f"[{status}] {scenario_result.get('title', 'Unknown')}")
        if scenario_result['status'] == 'success':
            lab_type = scenario_result.get('type', 'single')
            if lab_type == 'composite':
                repos = scenario_result.get('repos_combined', 1)
                sources = ", ".join(scenario_result.get('sources', []))
                print(f"   Type: Composite ({repos} repos)")
                print(f"   Sources: {sources}")
            print(f"   Output: {scenario_result['output_dir']}")
        else:
            print(f"   Error: {scenario_result.get('error', 'Unknown error')}")
        print()
    
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
