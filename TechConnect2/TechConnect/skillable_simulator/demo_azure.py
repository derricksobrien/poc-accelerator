"""
Run Skillable Simulator against Azure API
Fetches context from the running Azure Container Instance instead of local data.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from skillable_simulator.simulator import SkillableSimulator
from models.schemas import ContextBlock

# Azure API Configuration
AZURE_API_URL = "http://techconnect-api-prod.eastus.azurecontainer.io:8000"


def test_azure_api():
    """Test that Azure API is reachable"""
    try:
        response = requests.get(f"{AZURE_API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Azure API is healthy")
            return True
        else:
            print(f"⚠️  Azure API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Azure API at {AZURE_API_URL}")
        print("   Make sure the container is running")
        return False
    except Exception as e:
        print(f"❌ Error testing Azure API: {e}")
        return False


def fetch_context_from_azure(scenario_title: str, 
                            solution_area: Optional[str] = None,
                            num_results: int = 1) -> Optional[dict]:
    """
    Fetch context from Azure API instead of local simulator
    
    Args:
        scenario_title: The business scenario
        solution_area: Optional solution area filter
        num_results: Number of results to return
        
    Returns:
        Context block as dictionary, or None if error
    """
    try:
        payload = {
            "scenario_title": scenario_title,
            "num_results": num_results
        }
        
        if solution_area:
            payload["solution_area"] = solution_area
            
        print(f"Calling Azure API with: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{AZURE_API_URL}/context",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Got response from Azure API")
            # Parse XML or JSON response
            content = response.text
            print(f"\nContext Block (raw):\n{content[:500]}...\n")
            return {"raw": content, "status": response.status_code}
        else:
            print(f"❌ Azure API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Azure API timeout (took > 10 seconds)")
        return None
    except Exception as e:
        print(f"❌ Error calling Azure API: {e}")
        return None


def main():
    print("\n" + "="*80)
    print("  SKILLABLE SIMULATOR - AZURE API VERSION")
    print("="*80 + "\n")
    
    # Step 1: Test Azure API connectivity
    print("[1/4] Testing Azure API Connectivity...")
    print(f"  URL: {AZURE_API_URL}")
    if not test_azure_api():
        print("\n❌ Cannot continue without Azure API")
        return
    
    print()
    
    # Step 2: Fetch accelerators list
    print("[2/4] Fetching Accelerators List...")
    try:
        response = requests.get(f"{AZURE_API_URL}/accelerators", timeout=5)
        if response.status_code == 200:
            accs = response.json()
            count = accs.get('count', len(accs.get('accelerators', [])))
            print(f"✅ Found {count} accelerators in registry")
        else:
            print(f"⚠️  Got status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not fetch list: {e}")
    
    print()
    
    # Step 3: Fetch context from Azure API
    print("[3/4] Fetching Context from Azure API...")
    scenarios = [
        ("Deploy AI automation agents for enterprise workflows", "AI", 2),
        ("Build enterprise data platform with Azure Fabric", "Data", 2),
        ("Implement cloud security and compliance framework", None, 1),
    ]
    
    results = []
    for scenario, area, num in scenarios:
        print(f"\n  Scenario: {scenario}")
        if area:
            print(f"  Area: {area}")
        
        context = fetch_context_from_azure(scenario, area, num)
        if context:
            results.append({
                "scenario": scenario,
                "area": area,
                "results": num,
                "success": True,
                "response": context
            })
            print(f"  ✅ Success")
        else:
            print(f"  ❌ Failed")
    
    print()
    
    # Step 4: Generate Skillable Labs
    print("[4/4] Generating Skillable Labs from Context...")
    print(f"  Total successful contexts: {len([r for r in results if r['success']])}\n")
    
    # Initialize local simulator for lab generation
    print("  Initializing Skillable Generator...")
    try:
        simulator = SkillableSimulator()
        print(f"  ✅ Generator ready with {len(simulator.catalog_data.solution_accelerators)} local accelerators")
    except Exception as e:
        print(f"  ⚠️  Generator initialization error: {e}")
        simulator = None
    
    print()
    
    # Summary
    print("="*80)
    print("  RESULTS SUMMARY")
    print("="*80 + "\n")
    
    print(f"Azure API Status:        ✅ Connected")
    print(f"Scenarios Tested:        {len(scenarios)}")
    print(f"Successful Contexts:     {len([r for r in results if r['success']])}")
    print(f"Failed Contexts:         {len([r for r in results if not r['success']])}")
    print(f"Skillable Generator:     {'✅ Ready' if simulator else '⚠️  Not Available'}")
    
    print(f"\nAPI Endpoint:            {AZURE_API_URL}")
    print(f"Container Status:        ✅ Running")
    
    print("\n" + "="*80)
    print("  NEXT STEPS")
    print("="*80 + "\n")
    print("1. Use the context blocks to generate Skillable labs")
    print("2. Share the lab guides with Skillable platform")
    print("3. Monitor API performance and costs")
    print("4. See: HOW_TO_USE_API.md for more API examples")
    print()


if __name__ == "__main__":
    main()
