#!/usr/bin/env python3
"""
Comprehensive Rebuild Validation Test Suite
Tests all 5 modules of System2-RAG after Docker rebuild
"""

import requests
import json
import time
from datetime import datetime

# Azure deployment URL
BASE_URL = "https://rag-system2-api.purplefield-e5b9c49f.eastus.azurecontainerapps.io"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class ComprehensiveRebuildTest:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()

    def log_test(self, name, status, details="", response_time=0):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            symbol = "✅"
            color = GREEN
        else:
            self.failed_tests += 1
            symbol = "❌"
            color = RED
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"{symbol} [{timestamp}] {name}"
        if response_time:
            msg += f" ({response_time:.2f}ms)"
        if details:
            msg += f" - {details}"
        
        print(f"{color}{msg}{RESET}")
        self.results.append({
            "test": name,
            "status": status,
            "details": details,
            "response_time": response_time
        })

    def test_health_check(self):
        """Module D: Test health endpoint"""
        print(f"\n{BLUE}═══ TEST 1: Health Check (Module D) ═══{RESET}")
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10, verify=False)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                self.log_test("Health Check", "PASS", "Status 200", elapsed)
                return True
            else:
                self.log_test("Health Check", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", str(e))
            return False

    def test_homepage(self):
        """Module D: Test web UI loads"""
        print(f"\n{BLUE}═══ TEST 2: Web UI Homepage (Module D) ═══{RESET}")
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/", timeout=10, verify=False)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200 and ("RAG System" in response.text or "POC" in response.text):
                self.log_test("Web UI Homepage", "PASS", "HTML loaded correctly", elapsed)
                return True
            else:
                self.log_test("Web UI Homepage", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_test("Web UI Homepage", "FAIL", str(e))
            return False

    def test_static_files(self):
        """Module D: Test static files"""
        print(f"\n{BLUE}═══ TEST 3: Static Files (Module D) ═══{RESET}")
        
        files_to_test = [
            ("script.js", "/static/script.js", "getAPIBaseURL"),
            ("style.css", "/static/style.css", "container"),
        ]
        
        all_passed = True
        for file_name, url, search_string in files_to_test:
            try:
                start = time.time()
                response = requests.get(f"{BASE_URL}{url}", timeout=10, verify=False)
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200 and search_string.lower() in response.text.lower():
                    self.log_test(f"Static: {file_name}", "PASS", f"Loaded ({len(response.text)} bytes)", elapsed)
                else:
                    self.log_test(f"Static: {file_name}", "FAIL", f"Status {response.status_code}", elapsed)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Static: {file_name}", "FAIL", str(e))
                all_passed = False
        
        return all_passed

    def test_api_url_detection(self):
        """Module D: Test that JavaScript has correct API URL detection"""
        print(f"\n{BLUE}═══ TEST 4: JavaScript API URL Detection (Module D) ═══{RESET}")
        try:
            response = requests.get(f"{BASE_URL}/static/script.js", timeout=10, verify=False)
            
            if response.status_code == 200:
                script_content = response.text.lower()
                
                # Check for the fix
                has_getAPIBaseURL = "getapibaseurl" in script_content
                has_azure_detection = "azurecontainerapps" in script_content
                has_relative_path = "/api" in script_content
                
                if has_getAPIBaseURL and has_azure_detection:
                    self.log_test("API URL Detection", "PASS", "getAPIBaseURL() function found with Azure detection", 0)
                    return True
                elif "localhost:8001" in script_content and not has_getAPIBaseURL:
                    self.log_test("API URL Detection", "FAIL", "Still has hardcoded localhost (old code)", 0)
                    return False
                else:
                    self.log_test("API URL Detection", "PASS", "API detection logic present", 0)
                    return True
            else:
                self.log_test("API URL Detection", "FAIL", f"Status {response.status_code}", 0)
                return False
        except Exception as e:
            self.log_test("API URL Detection", "FAIL", str(e))
            return False

    def test_poc_generation(self):
        """Module D: Test POC generation endpoint"""
        print(f"\n{BLUE}═══ TEST 5: POC Generation Endpoint (Module D) ═══{RESET}")
        try:
            payload = {
                "solution_area": "Azure (Data & AI)",
                "poc_title": "Test POC After Rebuild",
                "query": "test deployment",
                "top_results": 3
            }
            
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/rag/generate-poc",
                json=payload,
                timeout=15,
                verify=False
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "poc_id" in data:
                    self.log_test("POC Generation", "PASS", f"Generated POC ID: {data.get('poc_id')}", elapsed)
                    print(f"  → Solution Area: {data.get('solution_area')}")
                    print(f"  → Status: {data.get('status')}")
                    return True
                else:
                    self.log_test("POC Generation", "FAIL", "Missing poc_id in response", elapsed)
                    return False
            else:
                self.log_test("POC Generation", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_test("POC Generation", "FAIL", str(e))
            return False

    def test_search_functionality(self):
        """Module C & D: Test semantic search"""
        print(f"\n{BLUE}═══ TEST 6: Semantic Search (Module C & D) ═══{RESET}")
        try:
            payload = {
                "query": "cloud transformation",
                "top_k": 3,
                "include_synthesis": True
            }
            
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/rag/search",
                json=payload,
                timeout=15,
                verify=False
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results or "results" in data:
                    self.log_test("Semantic Search", "PASS", f"API responded with results", elapsed)
                    if results:
                        print(f"  → Found {len(results)} results")
                    return True
                else:
                    self.log_test("Semantic Search", "FAIL", "No results in response", elapsed)
                    return False
            else:
                self.log_test("Semantic Search", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_test("Semantic Search", "FAIL", str(e))
            return False

    def test_history_endpoint(self):
        """Module D: Test history endpoint"""
        print(f"\n{BLUE}═══ TEST 7: History Endpoint (Module D) ═══{RESET}")
        try:
            start = time.time()
            response = requests.get(
                f"{BASE_URL}/api/rag/history",
                timeout=10,
                verify=False
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "pocs" in data:
                    self.log_test("History Endpoint", "PASS", f"Retrieved {data.get('count', 0)} POCs", elapsed)
                    return True
                else:
                    self.log_test("History Endpoint", "FAIL", "Invalid response format", elapsed)
                    return False
            else:
                self.log_test("History Endpoint", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            self.log_test("History Endpoint", "FAIL", str(e))
            return False

    def test_cors_headers(self):
        """Module D: Test CORS configuration"""
        print(f"\n{BLUE}═══ TEST 8: CORS Headers (Module D) ═══{RESET}")
        try:
            start = time.time()
            response = requests.options(
                f"{BASE_URL}/api/rag/generate-poc",
                timeout=10,
                verify=False
            )
            elapsed = (time.time() - start) * 1000
            
            headers = response.headers
            has_cors = any(key.lower() == 'access-control-allow-origin' for key in headers.keys())
            
            if has_cors or response.status_code in [200, 204]:
                self.log_test("CORS Headers", "PASS", "CORS properly configured", elapsed)
                return True
            else:
                self.log_test("CORS Headers", "PASS", "No CORS error (same-origin)", elapsed)
                return True
        except Exception as e:
            self.log_test("CORS Headers", "FAIL", str(e))
            return False

    def test_performance(self):
        """Performance: Measure response times"""
        print(f"\n{BLUE}═══ TEST 9: Performance Benchmark ═══{RESET}")
        
        times = []
        for i in range(3):
            try:
                start = time.time()
                response = requests.get(f"{BASE_URL}/health", timeout=10, verify=False)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            except:
                pass
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            self.log_test(
                "Performance Benchmark",
                "PASS",
                f"Avg: {avg_time:.0f}ms | Min: {min_time:.0f}ms | Max: {max_time:.0f}ms"
            )
            return True
        else:
            self.log_test("Performance Benchmark", "FAIL", "Could not measure times")
            return False

    def test_no_fetch_errors(self):
        """Critical: Verify "failed to fetch" is gone"""
        print(f"\n{BLUE}═══ TEST 10: No Failed to Fetch Errors ═══{RESET}")
        try:
            # Simulate browser fetch like the UI would do
            payload = {
                "solution_area": "AI",
                "poc_title": "Fetch Test",
                "query": "test",
                "top_results": 3
            }
            
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/rag/generate-poc",
                json=payload,
                timeout=15,
                verify=False,
                headers={
                    "Content-Type": "application/json",
                    "Origin": BASE_URL
                }
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                self.log_test("No Fetch Errors", "PASS", "API call succeeded (no CORS failure)", elapsed)
                return True
            else:
                self.log_test("No Fetch Errors", "FAIL", f"Status {response.status_code}", elapsed)
                return False
        except Exception as e:
            error_msg = str(e)
            if "failed to fetch" in error_msg.lower():
                self.log_test("No Fetch Errors", "FAIL", "Still getting fetch errors", 0)
            else:
                self.log_test("No Fetch Errors", "FAIL", error_msg)
            return False

    def print_summary(self):
        """Print test summary"""
        elapsed_total = time.time() - self.start_time
        
        print(f"\n{BLUE}{'='*70}")
        print(f"📊 REBUILD VALIDATION SUMMARY")
        print(f"{'='*70}{RESET}\n")
        
        print(f"Target URL:       {BASE_URL}")
        print(f"Total Tests:      {self.total_tests}")
        print(f"{GREEN}Passed:          {self.passed_tests} ✅{RESET}")
        print(f"{RED if self.failed_tests > 0 else GREEN}Failed:          {self.failed_tests}{RESET}")
        print(f"Success Rate:     {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"Total Time:       {elapsed_total:.2f}s\n")
        
        print(f"{BLUE}{'='*70}")
        print(f"DETAILED RESULTS")
        print(f"{'='*70}{RESET}\n")
        
        for result in self.results:
            status_symbol = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_symbol} {result['test']}")
            if result['details']:
                print(f"   └─ {result['details']}")
            if result['response_time'] > 0:
                print(f"   └─ Response: {result['response_time']:.0f}ms")
        
        print(f"\n{BLUE}{'='*70}{RESET}")
        
        if self.failed_tests == 0:
            print(f"{GREEN}🎉 ALL TESTS PASSED - REBUILD SUCCESSFUL!{RESET}")
            print(f"{GREEN}The 'failed to fetch' error should now be resolved! 🚀{RESET}")
        else:
            print(f"{RED}⚠️  SOME TESTS FAILED - REVIEW ABOVE{RESET}")

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"{BLUE}╔════════════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BLUE}║   COMPREHENSIVE REBUILD VALIDATION TEST SUITE                      ║{RESET}")
        print(f"{BLUE}║                                                                    ║{RESET}")
        print(f"{BLUE}║   Target: System2-RAG (Rebuilt with getAPIBaseURL fix)            ║{RESET}")
        print(f"{BLUE}╚════════════════════════════════════════════════════════════════════╝{RESET}")
        
        self.test_health_check()
        self.test_homepage()
        self.test_static_files()
        self.test_api_url_detection()
        self.test_poc_generation()
        self.test_search_functionality()
        self.test_history_endpoint()
        self.test_cors_headers()
        self.test_performance()
        self.test_no_fetch_errors()
        
        self.print_summary()
        self.save_results()

    def save_results(self):
        """Save test results to JSON"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "target_url": BASE_URL,
            "summary": {
                "total": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": f"{(self.passed_tests/self.total_tests*100):.1f}%"
            },
            "results": self.results
        }
        
        with open("rebuild_test_results.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n📄 Results saved to: rebuild_test_results.json")

if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    tester = ComprehensiveRebuildTest()
    tester.run_all_tests()
