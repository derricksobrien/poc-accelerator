"""
Test Suite for Skillable Simulator
Validates all components of the lab instructions generator.
"""

import sys
import json
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from skillable_simulator.generator import LabInstructionGenerator, XMLParser
from skillable_simulator.simulator import SkillableSimulator
from models.schemas import ContextBlock, CatalogItem


class TestResult:
    """Simple test result tracking."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        self.details.append(f"[PASS] {test_name}" + (f" - {message}" if message else ""))
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.details.append(f"[FAIL] {test_name} - {error}")
    
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        for detail in self.details:
            print(detail)
        print("-"*70)
        total = self.passed + self.failed
        print(f"Total: {total} | Passed: {self.passed} | Failed: {self.failed}")
        print("="*70 + "\n")


def test_xml_parser():
    """Test 1: XMLParser component."""
    result = TestResult()
    
    try:
        parser = XMLParser()
        
        # Test extraction
        xml = "<prerequisites><item>Python 3.11</item><item>Azure CLI</item></prerequisites>"
        items = parser.extract_items(xml, "prerequisites")
        
        if len(items) == 2 and "Python 3.11" in items:
            result.add_pass("XMLParser.extract_items", "Correctly extracted 2 items")
        else:
            result.add_fail("XMLParser.extract_items", f"Expected 2 items, got {len(items)}")
        
        # Test empty case
        items_empty = parser.extract_items("<products></products>", "products")
        if items_empty == []:
            result.add_pass("XMLParser.empty_extraction", "Correctly handled empty XML")
        else:
            result.add_fail("XMLParser.empty_extraction", "Failed on empty XML")
    
    except Exception as e:
        result.add_fail("XMLParser", str(e))
    
    return result


def test_lab_instruction_generator():
    """Test 2: LabInstructionGenerator component."""
    result = TestResult()
    
    try:
        generator = LabInstructionGenerator()
        
        # Create sample context block
        context = ContextBlock(
            catalog_item_id="test-001",
            solution_name="Test Solution",
            solution_area="AI",
            complexity_level="L300",
            architecture_summary="A test solution for demonstration purposes",
            prerequisites_xml="<prerequisites><item>Azure Subscription</item></prerequisites>",
            products_xml="<products><item>Azure OpenAI</item><item>Azure Storage</item></products>",
            rai_disclaimer="Test RAI disclaimer for AI solution",
            repository_url="https://github.com/test/repo"
        )
        
        # Test guide generation
        guide = generator.generate_lab_guide(context)
        
        if guide and "lab_metadata" in guide:
            result.add_pass("LabInstructionGenerator.generate_lab_guide", 
                          "Generated complete guide structure")
        else:
            result.add_fail("LabInstructionGenerator.generate_lab_guide", 
                          "Missing lab_metadata in guide")
        
        # Verify guide structure
        required_keys = ["lab_metadata", "overview", "prerequisites", 
                        "technologies", "lab_steps", "validation"]
        if all(key in guide for key in required_keys):
            result.add_pass("LabInstructionGenerator.guide_structure", 
                          f"Contains all {len(required_keys)} required sections")
        else:
            result.add_fail("LabInstructionGenerator.guide_structure", 
                          "Missing required guide sections")
        
        # Test deployment script generation
        script = generator.generate_deployment_script(context)
        if script and "#!/bin/bash" in script:
            result.add_pass("LabInstructionGenerator.deployment_script", 
                          f"Generated bash script ({len(script)} chars)")
        else:
            result.add_fail("LabInstructionGenerator.deployment_script", 
                          "Invalid deployment script")
        
        # Test lab report generation
        report = generator.generate_lab_report(context, guide)
        if report and "Test Solution" in report:
            result.add_pass("LabInstructionGenerator.lab_report", 
                          f"Generated formatted report ({len(report)} chars)")
        else:
            result.add_fail("LabInstructionGenerator.lab_report", 
                          "Report missing expected content")
        
        # Test RAI disclaimer inclusion
        if "RESPONSIBLE AI" in report and context.rai_disclaimer:
            result.add_pass("LabInstructionGenerator.rai_inclusion", 
                          "RAI disclaimer properly included in report")
        else:
            result.add_fail("LabInstructionGenerator.rai_inclusion", 
                          "RAI disclaimer not found in report")
    
    except Exception as e:
        result.add_fail("LabInstructionGenerator", str(e))
    
    return result


def test_skillable_simulator():
    """Test 3: SkillableSimulator integration."""
    result = TestResult()
    
    try:
        # Initialize simulator
        simulator = SkillableSimulator()
        result.add_pass("SkillableSimulator.init", "Successfully initialized")
        
        # Test catalog loading
        if simulator.catalog_data and len(simulator.catalog_data.solution_accelerators) > 0:
            result.add_pass("SkillableSimulator.catalog_load", 
                          f"Loaded {len(simulator.catalog_data.solution_accelerators)} accelerators")
        else:
            result.add_fail("SkillableSimulator.catalog_load", 
                          "No accelerators loaded")
        
        # Test context block fetching
        context = simulator.fetch_context_block("Deploy automation agents")
        if context and context.solution_name:
            result.add_pass("SkillableSimulator.fetch_context_block", 
                          f"Retrieved: {context.solution_name}")
        else:
            result.add_fail("SkillableSimulator.fetch_context_block", 
                          "Failed to fetch context block")
        
        # Test lab generation
        lab_result = simulator.generate_complete_lab("Test scenario")
        if lab_result and "guide" in lab_result:
            result.add_pass("SkillableSimulator.generate_complete_lab", 
                          "Generated complete lab package")
        else:
            result.add_fail("SkillableSimulator.generate_complete_lab", 
                          "Failed to generate lab")
        
        # Test metadata summary
        summary = simulator.get_lab_metadata_summary()
        if summary["total_labs"] > 0:
            result.add_pass("SkillableSimulator.metadata_summary", 
                          f"Retrieved {summary['total_labs']} lab summaries")
        else:
            result.add_fail("SkillableSimulator.metadata_summary", 
                          "No labs in metadata summary")
    
    except Exception as e:
        result.add_fail("SkillableSimulator", str(e))
    
    return result


def test_end_to_end_workflow():
    """Test 4: Complete end-to-end workflow."""
    result = TestResult()
    
    try:
        simulator = SkillableSimulator()
        
        # Test realistic user scenarios
        scenarios = [
            ("Deploy AI automation", "AI", "L400"),
            ("Build data platform", "Data", "L400"),
            ("Create documents AI", None, None)
        ]
        
        for title, area, complexity in scenarios:
            try:
                lab_result = simulator.generate_complete_lab(
                    title,
                    solution_area=area,
                    complexity_level=complexity
                )
                
                if lab_result:
                    result.add_pass(f"E2E workflow: '{title}'", 
                                  "Successfully generated lab")
                else:
                    result.add_fail(f"E2E workflow: '{title}'", 
                                  "No result returned")
            except Exception as e:
                result.add_fail(f"E2E workflow: '{title}'", str(e))
    
    except Exception as e:
        result.add_fail("E2E Workflow Setup", str(e))
    
    return result


def test_output_structure():
    """Test 5: Output structure validation."""
    result = TestResult()
    
    try:
        simulator = SkillableSimulator()
        lab_result = simulator.generate_complete_lab("Test for structure")
        
        if not lab_result:
            result.add_fail("Output Structure", "No lab result")
            return result
        
        # Validate context_block
        if "context_block" in lab_result:
            ctx = lab_result["context_block"]
            required_ctx_fields = ["catalog_item_id", "solution_name", 
                                   "complexity_level", "repository_url"]
            if all(hasattr(ctx, field) for field in required_ctx_fields):
                result.add_pass("ContextBlock.structure", 
                              f"Contains all {len(required_ctx_fields)} required fields")
            else:
                result.add_fail("ContextBlock.structure", 
                              "Missing required fields")
        
        # Validate guide
        if "guide" in lab_result:
            guide = lab_result["guide"]
            if "lab_steps" in guide and len(guide["lab_steps"]) > 0:
                total_steps = sum(len(s["steps"]) for s in guide["lab_steps"])
                result.add_pass("Guide.structure", 
                              f"Contains {len(guide['lab_steps'])} sections, {total_steps} total steps")
            else:
                result.add_fail("Guide.structure", 
                              "No lab steps found")
        
        # Validate deployment script
        if "deployment_script" in lab_result:
            script = lab_result["deployment_script"]
            if len(script) > 100 and "#!/bin/bash" in script:
                result.add_pass("DeploymentScript.structure", 
                              "Valid bash script generated")
            else:
                result.add_fail("DeploymentScript.structure", 
                              "Invalid script structure")
        
        # Validate report
        if "lab_report" in lab_result:
            report = lab_result["lab_report"]
            if len(report) > 500:
                result.add_pass("LabReport.structure", 
                              f"Generated comprehensive report ({len(report)} chars)")
            else:
                result.add_fail("LabReport.structure", 
                              "Report too short")
    
    except Exception as e:
        result.add_fail("Output Structure", str(e))
    
    return result


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  SKILLABLE SIMULATOR TEST SUITE")
    print("="*70)
    
    all_results = []
    
    # Run all tests
    print("\n[1/5] Testing XMLParser...")
    all_results.append(test_xml_parser())
    
    print("[2/5] Testing LabInstructionGenerator...")
    all_results.append(test_lab_instruction_generator())
    
    print("[3/5] Testing SkillableSimulator...")
    all_results.append(test_skillable_simulator())
    
    print("[4/5] Testing End-to-End Workflow...")
    all_results.append(test_end_to_end_workflow())
    
    print("[5/5] Testing Output Structure...")
    all_results.append(test_output_structure())
    
    # Print summary
    print("\n" + "="*70)
    print("COMPLETE TEST SUMMARY")
    print("="*70)
    
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = total_passed + total_failed
    
    for i, result in enumerate(all_results, 1):
        print(f"\n[Test {i}] Passed: {result.passed} | Failed: {result.failed}")
        for detail in result.details:
            print(f"  {detail}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {total_tests} tests | Passed: {total_passed} | Failed: {total_failed}")
    if total_failed == 0:
        print("[PASS] ALL TESTS PASSED")
    else:
        print(f"[FAIL] {total_failed} tests failed")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
