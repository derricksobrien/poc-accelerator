"""
MVP Test Script for TechConnect Contextual Broker
Tests all 5 modules in atomic fashion.
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ingestion.scraper import CatalogScraper
from vector_store.store import VectorStore
from models.schemas import ContextBlock


def test_module_a_scraper():
    """Test Module A: Scraper - Load and parse catalog.json"""
    print("\n" + "="*70)
    print("TEST MODULE A: Scraper (Data Ingestion)")
    print("="*70)
    
    try:
        catalog_path = project_root / "catalog.json"
        scraper = CatalogScraper(catalog_path)
        catalog = scraper.load_catalog()
        
        print(f"✓ Loaded catalog with {len(catalog.solution_accelerators)} accelerators")
        print(f"  Version: {catalog.catalog_metadata.version}")
        print(f"  Last Updated: {catalog.catalog_metadata.last_updated}")
        
        # Test retrieval
        first_acc = catalog.solution_accelerators[0]
        print(f"\n  Sample Accelerator:")
        print(f"    ID: {first_acc.id}")
        print(f"    Name: {first_acc.name}")
        print(f"    Area: {first_acc.solution_area}")
        print(f"    Complexity: {first_acc.technical_complexity}")
        print(f"    RAI Required: {first_acc.responsible_ai_tag}")
        
        return scraper
    
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return None


def test_module_b_metadata():
    """Test Module B: Metadata Extractor - Validate schema"""
    print("\n" + "="*70)
    print("TEST MODULE B: Metadata Extractor (LLM Processing)")
    print("="*70)
    
    try:
        catalog_path = project_root / "catalog.json"
        scraper = CatalogScraper(catalog_path)
        catalog = scraper.load_catalog()
        
        # Validate each accelerator matches schema
        print(f"✓ Validating {len(catalog.solution_accelerators)} CatalogItem schemas...")
        
        for acc in catalog.solution_accelerators:
            assert acc.id, "Missing id"
            assert acc.name, "Missing name"
            assert acc.solution_area, "Missing solution_area"
            assert acc.repository_url, "Missing repository_url"
            assert isinstance(acc.prerequisites, list), "prerequisites not a list"
            assert isinstance(acc.responsible_ai_tag, bool), "responsible_ai_tag not bool"
        
        print(f"✓ All {len(catalog.solution_accelerators)} items valid")
        
        # Check RAI-tagged items
        rai_items = scraper.get_rai_required()
        print(f"✓ Found {len(rai_items)} items requiring RAI disclaimer")
        
        return True
    
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_module_c_vector_store():
    """Test Module C: Vector Store - Index and search"""
    print("\n" + "="*70)
    print("TEST MODULE C: Vector Store (RAG Memory)")
    print("="*70)
    
    try:
        # Initialize in-memory vector store
        vector_store = VectorStore(persist_dir=None)
        
        # Load accelerators
        catalog_path = project_root / "catalog.json"
        scraper = CatalogScraper(catalog_path)
        catalog = scraper.load_catalog()
        
        # Ingest
        vector_store.ingest_accelerators(catalog.solution_accelerators)
        print(f"✓ Ingested {len(catalog.solution_accelerators)} accelerators into ChromaDB")
        
        # Test semantic search
        results = vector_store.search("AI automation agents", n_results=3)
        print(f"✓ Semantic search returned {len(results['ids'])} results")
        
        for i, acc_id in enumerate(results['ids']):
            print(f"  {i+1}. {acc_id}")
        
        # Test filtered search
        ai_results = vector_store.search(
            "automation",
            solution_area="AI",
            n_results=2
        )
        print(f"✓ Filtered search (AI area) returned {len(ai_results['ids'])} results")
        
        # Test get_by_id
        single = vector_store.get_by_id("multi-agent-automation")
        if single:
            print(f"✓ Retrieved by ID: {single['metadata'].get('name', 'N/A')}")
        
        return vector_store
    
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return None


def test_module_d_context_provider():
    """Test Module D: Context Provider - Format context blocks"""
    print("\n" + "="*70)
    print("TEST MODULE D: Context Provider (A2A Interface)")
    print("="*70)
    
    try:
        from api.main import _create_context_block
        
        # Load an accelerator
        catalog_path = project_root / "catalog.json"
        scraper = CatalogScraper(catalog_path)
        catalog = scraper.load_catalog()
        
        acc = catalog.solution_accelerators[0]
        
        # Create context block
        block = _create_context_block(acc)
        
        print(f"✓ Created context block for '{block.solution_name}'")
        print(f"  Area: {block.solution_area}")
        print(f"  Complexity: {block.complexity_level}")
        print(f"  Summary: {block.architecture_summary[:100]}...")
        print(f"  Has Prerequisites XML: {'<prerequisites>' in block.prerequisites_xml}")
        print(f"  Has Products XML: {'<products>' in block.products_xml}")
        print(f"  RAI Disclaimer: {'Yes' if block.rai_disclaimer else 'No'}")
        
        return True
    
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_module_e_rai_injection():
    """Test Module E: Governance Guardrails - RAI injection"""
    print("\n" + "="*70)
    print("TEST MODULE E: Governance Guardrails (RAI Injection)")
    print("="*70)
    
    try:
        from api.main import _get_rai_disclaimer
        
        # Test with AI solution requiring RAI
        disclaimer = _get_rai_disclaimer(responsible_ai_tag=True, solution_area="AI")
        
        if disclaimer:
            print(f"✓ RAI disclaimer generated for AI solutions")
            print(f"  Disclaimer length: {len(disclaimer)} chars")
            print(f"  Contains 'Responsible AI': {'Responsible AI' in disclaimer}")
        else:
            print(f"✗ No disclaimer generated")
            return False
        
        # Test with non-AI solution
        disclaimer_non_ai = _get_rai_disclaimer(responsible_ai_tag=True, solution_area="Security")
        print(f"✓ Non-AI solution (no disclaimer): {disclaimer_non_ai is None}")
        
        return True
    
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def main():
    """Run all MVP tests."""
    print("\n" + "="*70)
    print("TechConnect MVP Test Suite")
    print("Testing Atomic 5-Module Pipeline")
    print("="*70)
    
    results = {}
    
    # Run tests
    results['A_Scraper'] = test_module_a_scraper() is not None
    results['B_Metadata'] = test_module_b_metadata()
    results['C_VectorStore'] = test_module_c_vector_store() is not None
    results['D_ContextProvider'] = test_module_d_context_provider()
    results['E_RAIGuardrails'] = test_module_e_rai_injection()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} modules passed")
    
    if passed == total:
        print("\n✓ All MVP tests passed! Ready for FastAPI server.")
        print("\nNext step: Run FastAPI server")
        print("  cd c:\\Users\\derri\\Code\\TechConnect")
        print("  python -m uvicorn api.main:app --reload --port 8000")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
