"""
Test script to simulate API requests to the TechConnect Context Broker
"""

import json
import time
import subprocess
import requests
import sys
from pathlib import Path

# Change to project directory
import os
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

# Start server in subprocess
print("=" * 70)
print("Starting FastAPI Server...")
print("=" * 70)

server_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(2)

try:
    # Test 1: Health Check
    print("\n[TEST 1] Health Check Endpoint")
    print("-" * 70)
    response = requests.get("http://localhost:8000/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: List All Accelerators
    print("\n[TEST 2] List All Accelerators")
    print("-" * 70)
    response = requests.get("http://localhost:8000/accelerators")
    data = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Found {len(data)} accelerators:")
    for acc in data:
        print(f"  - {acc['metadata'].get('name', 'Unknown')}")
    
    # Test 3: Get Context - AI Automation
    print("\n[TEST 3] Get Context Block - AI Automation Scenario")
    print("-" * 70)
    request_body = {
        "scenario_title": "Build an AI agent for automating business workflows",
        "solution_area": "AI",
        "num_results": 2
    }
    print(f"Request: {json.dumps(request_body, indent=2)}")
    
    response = requests.post("http://localhost:8000/context", json=request_body)
    data = response.json()
    print(f"\nStatus Code: {response.status_code}")
    print(f"Results Found: {data['count']}")
    
    for i, block in enumerate(data['blocks'], 1):
        print(f"\n  [{i}] {block['solution_name']}")
        print(f"      Area: {block['solution_area']}")
        print(f"      Complexity: {block['complexity_level']}")
        print(f"      Summary: {block['architecture_summary'][:100]}...")
        if block['rai_disclaimer']:
            print(f"      ⚠️  RAI Disclaimer: YES (Safety guardrails required)")
    
    # Test 4: Get Context - Data & Analytics
    print("\n[TEST 4] Get Context Block - Data Platform Scenario")
    print("-" * 70)
    request_body = {
        "scenario_title": "Unified data foundation with analytics and governance",
        "solution_area": "Azure (Data & AI)",
        "num_results": 1
    }
    print(f"Request: {json.dumps(request_body, indent=2)}")
    
    response = requests.post("http://localhost:8000/context", json=request_body)
    data = response.json()
    print(f"\nStatus Code: {response.status_code}")
    print(f"Results Found: {data['count']}")
    
    for i, block in enumerate(data['blocks'], 1):
        print(f"\n  [{i}] {block['solution_name']}")
        print(f"      Area: {block['solution_area']}")
        print(f"      Complexity: {block['complexity_level']}")
        print(f"      Products: {block['products_xml'][:80]}...")
        print(f"      RAI Required: {'Yes' if block['rai_disclaimer'] else 'No'}")
    
    # Test 5: Get Specific Accelerator
    print("\n[TEST 5] Get Specific Accelerator by ID")
    print("-" * 70)
    accelerator_id = "multi-agent-automation"
    print(f"Request: GET /accelerators/{accelerator_id}")
    
    response = requests.get(f"http://localhost:8000/accelerators/{accelerator_id}")
    block = response.json()
    print(f"\nStatus Code: {response.status_code}")
    print(f"Solution: {block['solution_name']}")
    print(f"Repository: {block['repository_url']}")
    print(f"\nPrerequisites:")
    print(f"{block['prerequisites_xml']}")
    print(f"\nProducts & Services:")
    print(f"{block['products_xml'][:200]}...")
    
    # Test 6: Generic Search (no filters)
    print("\n[TEST 6] Generic Search - No Filters")
    print("-" * 70)
    request_body = {
        "scenario_title": "Process documents and extract information from content",
        "num_results": 3
    }
    print(f"Request: {json.dumps(request_body, indent=2)}")
    
    response = requests.post("http://localhost:8000/context", json=request_body)
    data = response.json()
    print(f"\nStatus Code: {response.status_code}")
    print(f"Results Found: {data['count']}")
    
    for i, block in enumerate(data['blocks'], 1):
        print(f"  {i}. {block['solution_name']} ({block['complexity_level']})")
    
    print("\n" + "=" * 70)
    print("✓ All API Tests Completed Successfully!")
    print("=" * 70)
    
finally:
    # Stop server
    print("\nStopping server...")
    server_proc.terminate()
    server_proc.wait(timeout=5)
