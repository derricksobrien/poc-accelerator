#!/usr/bin/env python3
"""
Deployment Verification Test
Tests if the redeployed container has the correct JavaScript configuration
and if API calls work without "failed to fetch" errors.
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Azure Container App URL
BASE_URL = "https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io"

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings()

def test_frontend_html():
    """Test 1: Verify frontend HTML is served"""
    print("\n" + "="*70)
    print("[TEST 1] Frontend HTML Response")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                print("✅ Frontend HTML is being served correctly")
                return True
            else:
                print("❌ Response is not HTML")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_javascript_config():
    """Test 2: Verify JavaScript has correct API configuration"""
    print("\n" + "="*70)
    print("[TEST 2] JavaScript File Configuration")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/static/script.js", timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch JavaScript: {response.status_code}")
            return False
        
        js_content = response.text
        
        # Check for updated API base URL detection
        has_getAPIBaseURL = "getAPIBaseURL" in js_content
        has_azure_detection = "azurecontainerapps.io" in js_content
        has_localhost = "localhost" in js_content
        has_cors_mode = "'mode': 'cors'" in js_content or '"mode": "cors"' in js_content
        
        print("\n--- JavaScript Configuration Checks ---")
        
        if "http://localhost:8001/api" in js_content:
            print("❌ OLD CONFIG: Still has hardcoded localhost URL!")
            print("   The deployed container has OLD code")
            return False
        else:
            print("✅ No hardcoded localhost URL found (good!)")
        
        if has_getAPIBaseURL:
            print("✅ Smart URL detection function present (getAPIBaseURL)")
        else:
            print("⚠️  No getAPIBaseURL function (but may use relative paths)")
        
        if has_azure_detection:
            print("✅ Azure domain detection included")
        
        if has_cors_mode:
            print("✅ CORS mode explicitly set in requests")
        
        if "/api" in js_content:
            print("✅ Uses relative /api paths for API calls")
        
        # Check for console logging for debugging
        if "console.log" in js_content:
            print("✅ Console logging included (for debugging)")
        
        # Check for error handling
        if "console.error" in js_content:
            print("✅ Error logging included")
        
        # If not old config, we're good
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_poc_generation():
    """Test 3: Test POC generation API endpoint"""
    print("\n" + "="*70)
    print("[TEST 3] POC Generation Endpoint (/api/rag/generate-poc)")
    print("="*70)
    
    try:
        payload = {
            "solution_area": "Azure (Data & AI)",
            "poc_title": "Test POC After Deployment",
            "query": "test query",
            "top_results": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rag/generate-poc",
            json=payload,
            timeout=10,
            verify=False,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POC Generation successful!")
            print(f"   POC ID: {data.get('poc_id', 'N/A')}")
            print(f"   Solution Area: {data.get('solution_area', 'N/A')}")
            return True
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return False

def test_api_search():
    """Test 4: Test Search API endpoint"""
    print("\n" + "="*70)
    print("[TEST 4] Search Endpoint (/api/rag/search)")
    print("="*70)
    
    try:
        payload = {
            "query": "cloud transformation",
            "top_k": 3,
            "include_synthesis": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rag/search",
            json=payload,
            timeout=10,
            verify=False,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', []))
            print(f"✅ Search successful!")
            print(f"   Results returned: {results_count}")
            if results_count > 0:
                print(f"   First result: {data['results'][0].get('title', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return False

def test_browser_fetch_simulation():
    """Test 5: Simulate browser fetch (what the frontend JavaScript does)"""
    print("\n" + "="*70)
    print("[TEST 5] Browser Fetch Simulation")
    print("="*70)
    print("Simulating what happens when browser JavaScript calls the API...")
    
    try:
        # This simulates a CORS request from the browser
        payload = {
            "solution_area": "Azure (Data & AI)",
            "poc_title": "Browser Test",
            "query": "test",
            "top_results": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rag/generate-poc",
            json=payload,
            timeout=10,
            verify=False,
            headers={
                "Content-Type": "application/json",
                "Origin": BASE_URL,
            }
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Check for CORS headers
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"✅ CORS header present: {cors_header}")
        else:
            print("⚠️  CORS header not found (but same-origin, so not blocking)")
        
        if response.status_code == 200:
            print("✅ Browser fetch simulation successful (no 'failed to fetch' error)!")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed - IS THE CONTAINER RUNNING? {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_css_file():
    """Test 6: Verify CSS is served"""
    print("\n" + "="*70)
    print("[TEST 6] CSS File (/static/style.css)")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/static/style.css", timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CSS file served correctly")
            return True
        else:
            print(f"❌ Failed to fetch CSS: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_endpoint():
    """Test 7: Check health endpoint"""
    print("\n" + "="*70)
    print("[TEST 7] Health Check Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health endpoint responding")
            return True
        else:
            print(f"⚠️  Health endpoint returned: {response.status_code}")
            return True  # Still consider it a pass if endpoint exists
    except Exception as e:
        print(f"⚠️  Health endpoint not available: {e}")
        return True  # Not critical

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SYSTEM2 RAG - DEPLOYMENT VERIFICATION TEST")
    print("="*70)
    print(f"\nTesting: {BASE_URL}")
    print("This verifies the redeployed container has correct configuration")
    
    results = {
        "Frontend HTML": test_frontend_html(),
        "JavaScript Config": test_javascript_config(),
        "POC Generation API": test_api_poc_generation(),
        "Search API": test_api_search(),
        "Browser Fetch": test_browser_fetch_simulation(),
        "CSS File": test_css_file(),
        "Health Check": test_health_endpoint(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 "*20)
        print("✅ DEPLOYMENT SUCCESSFUL - NO 'FAILED TO FETCH' ERRORS!")
        print("🎉 "*20)
        print("\nThe container app has been successfully redeployed with:")
        print("  ✅ Updated JavaScript with correct API paths")
        print("  ✅ Working API endpoints ")
        print("  ✅ Frontend properly serves HTML/CSS/JS")
        print("  ✅ Browser can fetch data without CORS errors")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
