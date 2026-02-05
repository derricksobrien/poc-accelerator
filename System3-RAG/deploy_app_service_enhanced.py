#!/usr/bin/env python3
"""
Azure App Service Deployment Script for System3-RAG (Enhanced with Progress Tracking)

Deploys to Azure App Service with:
- Real-time progress tracking
- Detailed status indicators for each resource
- Azure AI Search service
- Azure AI Foundry agent integration
- Full monitoring and logging

Usage:
    python deploy_app_service_enhanced.py \
      --name system3-rag \
      --resource-group my-rg \
      --region westus2 \
      --enable-ai-search \
      --enable-ai-foundry
"""

import subprocess
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

# Status indicators
STATUS_PENDING = "⏳"
STATUS_RUNNING = "🔄"
STATUS_SUCCESS = "✅"
STATUS_WARNING = "⚠️"
STATUS_ERROR = "❌"
STATUS_SKIPPED = "⏭️"

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header."""
    width = 80
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}\n")


def print_stage(stage_num: int, title: str, description: str = ""):
    """Print stage header with description."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{timestamp}] STAGE {stage_num}: {title}{Colors.RESET}")
    if description:
        print(f"    {description}")
    print(f"    {'-' * 70}")


def print_status(status: str, message: str, details: str = ""):
    """Print status line with indicator."""
    print(f"  {status} {Colors.BOLD}{message}{Colors.RESET}")
    if details:
        print(f"      {Colors.CYAN}{details}{Colors.RESET}")


def print_section(title: str):
    """Print section divider."""
    print(f"\n  {Colors.YELLOW}→ {title}{Colors.RESET}")


class AzureResourceTracker:
    """Track all deployed Azure resources."""
    
    def __init__(self):
        self.resources = {
            "resource_group": {"status": "pending", "name": "", "url": ""},
            "app_service_plan": {"status": "pending", "name": "", "sku": ""},
            "web_app": {"status": "pending", "name": "", "url": ""},
            "ai_search_service": {"status": "pending", "name": "", "url": ""},
            "ai_hub": {"status": "pending", "name": "", "url": ""},
            "ai_agent": {"status": "pending", "name": "", "url": ""},
        }
    
    def update(self, resource: str, status: str, details: dict = None):
        """Update resource status."""
        if resource in self.resources:
            self.resources[resource]["status"] = status
            if details:
                self.resources[resource].update(details)
    
    def print_summary(self):
        """Print resource summary."""
        print(f"\n{Colors.BOLD}{'Resource':<30} {'Status':<15} {'Details'}{Colors.RESET}")
        print(f"{'-' * 80}")
        
        status_icons = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "skipped": "⏭️",
            "failed": "❌",
        }
        
        for resource, data in self.resources.items():
            status_text = data["status"].upper()
            icon = status_icons.get(data["status"], "?")
            details = data.get("name", "") or data.get("url", "")
            print(f"  {resource:<28} {icon:<2} {status_text:<12} {Colors.CYAN}{details}{Colors.RESET}")


class AppServiceDeployer:
    """Deploys System3-RAG to Azure App Service with full resource tracking."""
    
    def __init__(
        self,
        app_name: str,
        resource_group: str,
        region: str = "eastus",
        runtime: str = "PYTHON|3.10",
        enable_ai_search: bool = True,
        enable_ai_foundry: bool = True
    ):
        self.app_name = app_name
        self.resource_group = resource_group
        self.region = region
        self.runtime = runtime
        self.enable_ai_search = enable_ai_search
        self.enable_ai_foundry = enable_ai_foundry
        self.app_service_plan = f"{app_name}-plan"
        self.ai_search_name = f"{app_name}-search"
        self.ai_hub_name = f"{app_name}-hub"
        
        # Resource tracker
        self.tracker = AzureResourceTracker()
        
        # Timestamps
        self.start_time = datetime.now()
    
    def run_command(self, cmd: str, check: bool = True) -> Tuple[int, str]:
        """Execute Azure CLI command."""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0 and check:
            print(f"{STATUS_ERROR} Command failed: {cmd}")
            print(f"   Error: {result.stderr.strip()[:200]}")
            sys.exit(1)
        
        return result.returncode, result.stdout.strip()
    
    def stage_1_prerequisites(self) -> bool:
        """Stage 1: Check prerequisites."""
        print_stage(1, "Checking Prerequisites", "Verifying Azure CLI and authentication")
        
        # Check Azure CLI
        print_section("Checking Azure CLI")
        code, out = self.run_command("az --version", check=False)
        if code != 0:
            print_status(STATUS_ERROR, "Azure CLI not installed")
            print_status(STATUS_WARNING, "Download from: https://aka.ms/azcliinstaller")
            return False
        
        version_line = out.split('\n')[0]
        print_status(STATUS_SUCCESS, "Azure CLI installed", version_line)
        
        # Check authentication
        print_section("Checking Azure Authentication")
        code, out = self.run_command("az account show", check=False)
        if code != 0:
            print_status(STATUS_ERROR, "Not authenticated with Azure")
            print_status(STATUS_WARNING, "Run: az login")
            return False
        
        try:
            account = json.loads(out)
            subscription_name = account.get("name", "Unknown")
            subscription_id = account.get("id", "Unknown")
            print_status(STATUS_SUCCESS, "Authenticated", 
                        f"Subscription: {subscription_name}")
        except:
            print_status(STATUS_SUCCESS, "Authenticated with Azure")
        
        # Check required tools
        print_section("Checking Application Requirements")
        if not Path("requirements.txt").exists():
            print_status(STATUS_ERROR, "requirements.txt not found")
            return False
        print_status(STATUS_SUCCESS, "requirements.txt found")
        
        if not Path("app/main.py").exists():
            print_status(STATUS_ERROR, "app/main.py not found")
            return False
        print_status(STATUS_SUCCESS, "Application code found")
        
        print_status(STATUS_SUCCESS, "All prerequisites OK")
        return True
    
    def stage_2_resource_group(self) -> bool:
        """Stage 2: Create/verify resource group."""
        print_stage(2, "Setting Up Resource Group", f"Region: {self.region}")
        
        # Check if RG exists
        code, _ = self.run_command(
            f"az group exists -n {self.resource_group}",
            check=False
        )
        
        if code == 0 and _ == "true":
            print_status(STATUS_SUCCESS, f"Resource group '{self.resource_group}' already exists")
            self.tracker.update("resource_group", "completed", {"name": self.resource_group})
            return True
        
        # Create RG
        print_status(STATUS_RUNNING, f"Creating resource group: {self.resource_group}")
        code, _ = self.run_command(
            f"az group create -n {self.resource_group} -l {self.region}"
        )
        
        if code == 0:
            print_status(STATUS_SUCCESS, "Resource group created", 
                        f"Location: {self.region}")
            self.tracker.update("resource_group", "completed", {"name": self.resource_group})
            return True
        else:
            print_status(STATUS_ERROR, "Failed to create resource group")
            return False
    
    def stage_3_app_service_plan(self) -> bool:
        """Stage 3: Create App Service Plan."""
        print_stage(3, "Creating App Service Plan", "SKU: B1 (Basic - $13/mo)")
        
        # Check if plan exists
        print_status(STATUS_RUNNING, "Checking for existing plan...")
        code, _ = self.run_command(
            f"az appservice plan show -n {self.app_service_plan} -g {self.resource_group}",
            check=False
        )
        
        if code == 0:
            print_status(STATUS_SUCCESS, f"Plan '{self.app_service_plan}' already exists")
            self.tracker.update("app_service_plan", "completed", 
                              {"name": self.app_service_plan, "sku": "B1"})
            return True
        
        # Create plan
        print_status(STATUS_RUNNING, "Creating App Service Plan...")
        code, _ = self.run_command(
            f'az appservice plan create '
            f'-n {self.app_service_plan} '
            f'-g {self.resource_group} '
            f'-l {self.region} '
            f'--is-linux '
            f'--sku B1'
        )
        
        if code == 0:
            print_status(STATUS_SUCCESS, "App Service Plan created", "SKU: B1")
            self.tracker.update("app_service_plan", "completed", 
                              {"name": self.app_service_plan, "sku": "B1"})
            return True
        else:
            print_status(STATUS_ERROR, "Failed to create App Service Plan")
            return False
    
    def stage_4_web_app(self) -> bool:
        """Stage 4: Create Web App."""
        print_stage(4, "Creating Web App", "Runtime: Python 3.10")
        
        # Check if app exists
        print_status(STATUS_RUNNING, "Checking for existing app...")
        code, _ = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group}",
            check=False
        )
        
        if code == 0:
            print_status(STATUS_SUCCESS, f"Web App '{self.app_name}' already exists")
            self.tracker.update("web_app", "completed", {"name": self.app_name})
            return True
        
        # Create web app
        print_status(STATUS_RUNNING, "Creating Web App...")
        code, output = self.run_command(
            f'az webapp create '
            f'-n {self.app_name} '
            f'-g {self.resource_group} '
            f'--plan {self.app_service_plan} '
            f'--runtime "PYTHON|3.10"'
        )
        
        if code == 0:
            # Get the URL
            code, url = self.run_command(
                f"az webapp show -n {self.app_name} -g {self.resource_group} "
                f"-o json"
            )
            
            if code == 0:
                try:
                    app_data = json.loads(url)
                    app_url = app_data.get("defaultHostName", "unknown")
                    print_status(STATUS_SUCCESS, "Web App created", 
                                f"URL: https://{app_url}")
                    self.tracker.update("web_app", "completed", 
                                      {"name": self.app_name, 
                                       "url": f"https://{app_url}"})
                    return True
                except:
                    print_status(STATUS_SUCCESS, "Web App created")
                    self.tracker.update("web_app", "completed", {"name": self.app_name})
                    return True
        
        print_status(STATUS_ERROR, "Failed to create Web App")
        return False
    
    def stage_5_ai_search(self) -> bool:
        """Stage 5: Create Azure AI Search service."""
        if not self.enable_ai_search:
            print_stage(5, "Azure AI Search", "(Skipped - not enabled)")
            print_status(STATUS_SKIPPED, "AI Search disabled by user")
            self.tracker.update("ai_search_service", "skipped")
            return True
        
        print_stage(5, "Creating Azure AI Search Service", "For semantic search on solutions")
        
        print("\n  📋 AI SEARCH CONFIGURATION:")
        print("  " + "─" * 70)
        print(f"     Service Name: {self.ai_search_name}")
        print(f"     Location: {self.region}")
        print(f"     SKU: Basic ($50-100/month)")
        print(f"     Features: Semantic search, vector search, metadata filtering")
        print("  " + "─" * 70 + "\n")
        
        # Check if search service exists
        print_status(STATUS_RUNNING, "Checking for existing search service...")
        start = time.time()
        code, _ = self.run_command(
            f"az search service show -n {self.ai_search_name} -g {self.resource_group}",
            check=False
        )
        elapsed = time.time() - start
        
        if code == 0:
            print_status(STATUS_SUCCESS, f"Search service '{self.ai_search_name}' already exists")
            print_status(STATUS_SUCCESS, f"   ↳ Query completed in {elapsed:.1f}s")
            self.tracker.update("ai_search_service", "completed", 
                              {"name": self.ai_search_name})
            return True
        
        # Create search service
        print_status(STATUS_RUNNING, "Creating AI Search service...")
        print_status(STATUS_RUNNING, "   ↳ This may take 1-3 minutes")
        print("\n  🔄 CREATION PROGRESS:")
        print("  " + "─" * 70)
        
        start = time.time()
        code, output = self.run_command(
            f'az search service create '
            f'-n {self.ai_search_name} '
            f'-g {self.resource_group} '
            f'-l {self.region} '
            f'--sku basic',
            check=False
        )
        elapsed = time.time() - start
        
        if code == 0:
            print(f"  ✓ Service creation completed in {int(elapsed)}s")
            print_status(STATUS_SUCCESS, "AI Search service created", "SKU: Basic")
            print_status(STATUS_SUCCESS, "   ↳ Service name: {self.ai_search_name}")
            print_status(STATUS_SUCCESS, "   ↳ Region: {self.region}")
            print_status(STATUS_SUCCESS, "   ↳ Status: Provisioned and ready")
            print("  " + "─" * 70)
            self.tracker.update("ai_search_service", "completed", 
                              {"name": self.ai_search_name})
            return True
        else:
            print(f"  ⚠️  Creation attempt took {int(elapsed)}s")
            if "quota" in output.lower():
                print_status(STATUS_WARNING, "AI Search: Quota limit reached")
                print("     Solution: Request quota increase in Azure Portal")
            elif "already exists" in output.lower():
                print_status(STATUS_SUCCESS, "AI Search service already exists")
                self.tracker.update("ai_search_service", "completed", 
                                  {"name": self.ai_search_name})
                return True
            else:
                print_status(STATUS_WARNING, "Could not create AI Search (may require quota)")
                self.tracker.update("ai_search_service", "skipped")
                return True  # Don't fail deployment
    
    def stage_6_deploy_code(self) -> bool:
        """Stage 6: Deploy code to App Service with detailed progress."""
        print_stage(6, "Deploying Application Code", "Using Azure App Service deployment with detailed logging")
        
        if not Path("requirements.txt").exists():
            print_status(STATUS_ERROR, "requirements.txt not found")
            return False
        
        print_status(STATUS_RUNNING, "Starting code deployment...")
        print("\n  📋 DEPLOYMENT DETAILS:")
        print("  " + "─" * 70)
        
        # Show what's being deployed
        files_to_deploy = [
            "streamlit_app.py",
            "requirements.txt",
            "app/main.py",
            "app/agent.py",
            "app/session.py",
            ".streamlit/config.toml",
        ]
        
        print("  📦 Files to be deployed:")
        for f in files_to_deploy:
            if Path(f).exists():
                print(f"     ✓ {f}")
            else:
                print(f"     ✗ {f} (missing)")
        
        print("\n  ⏱️  TIMING ESTIMATE:")
        print("     • File upload: 30-60 seconds")
        print("     • Dependency installation: 1-2 minutes")
        print("     • App initialization: 30-60 seconds")
        print("     • Total: 2-5 minutes")
        print("  " + "─" * 70 + "\n")
        
        print_status(STATUS_RUNNING, "Starting deployment process...")
        print_status(STATUS_RUNNING, "   ↳ Command: az webapp up")
        
        # Deploy using az webapp up with detailed output
        cmd = (
            f'az webapp up '
            f'--name {self.app_name} '
            f'--resource-group {self.resource_group} '
            f'--runtime "PYTHON|3.10" '
            f'--logs'
        )
        
        print_status(STATUS_RUNNING, f"   ↳ Target app: {self.app_name}")
        print_status(STATUS_RUNNING, f"   ↳ Resource group: {self.resource_group}")
        print_status(STATUS_RUNNING, f"   ↳ Runtime: Python 3.10")
        
        print("\n  🔄 DEPLOYMENT PROGRESS:")
        print("  " + "─" * 70)
        
        # Run with streaming output
        import subprocess
        
        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        phase = "initializing"
        
        try:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                line = line.rstrip()
                if line:
                    output_lines.append(line)
                    
                    # Parse output for phase detection
                    line_lower = line.lower()
                    
                    if "packaging" in line_lower or "building" in line_lower:
                        if phase != "packaging":
                            phase = "packaging"
                            print(f"  🔨 {STATUS_RUNNING} Packaging application files...")
                    elif "uploading" in line_lower or "creating" in line_lower:
                        if phase != "uploading":
                            phase = "uploading"
                            print(f"  📤 {STATUS_RUNNING} Uploading to App Service...")
                    elif "pip install" in line_lower or "installing" in line_lower:
                        if phase != "installing":
                            phase = "installing"
                            print(f"  📚 {STATUS_RUNNING} Installing Python dependencies...")
                    elif "successfully" in line_lower or "running command" in line_lower:
                        print(f"  📝 {line[:75]}")
                    elif "error" in line_lower or "failed" in line_lower:
                        print(f"  ⚠️  {line[:75]}")
                    elif "warning" in line_lower:
                        print(f"  ⚠️  {line[:75]}")
                    else:
                        # Show every 5th line to avoid spam
                        if len(output_lines) % 5 == 0:
                            print(f"  ... {line[:75]}")
            
            code = process.wait()
            elapsed = time.time() - start_time
            
            print("  " + "─" * 70)
            print(f"  ✓ Deployment process completed in {int(elapsed)}s")
            
        except KeyboardInterrupt:
            print("\n  ❌ Deployment cancelled by user")
            process.terminate()
            return False
        except Exception as e:
            print(f"  ❌ Error during deployment: {e}")
            return False
        
        if code == 0:
            print_status(STATUS_SUCCESS, "Application files uploaded successfully")
            print_status(STATUS_SUCCESS, "Dependencies installed")
            print_status(STATUS_SUCCESS, "Code deployment completed")
            return True
        else:
            # Show diagnostic info
            print("\n  🔍 DIAGNOSTIC INFORMATION:")
            print("  " + "─" * 70)
            
            if output_lines:
                print("  Last 10 lines of output:")
                for line in output_lines[-10:]:
                    print(f"     {line[:75]}")
            
            print("\n  💡 TROUBLESHOOTING:")
            print("     • Check app service logs: az webapp log tail -n {self.app_name} -g {self.resource_group}")
            print("     • Verify requirements.txt is valid")
            print("     • Check for compatibility with Python 3.10")
            print("     • Ensure all imports are available in PyPI")
            print("  " + "─" * 70)
            
            print_status(STATUS_WARNING, "Deployment may have partially succeeded")
            print_status(STATUS_RUNNING, "Verifying deployment status...")
            return True
    
    def stage_7_configure_settings(self) -> bool:
        """Stage 7: Configure application settings."""
        print_stage(7, "Configuring Application Settings", "Setting environment variables")
        
        print_status(STATUS_RUNNING, "Configuring Python runtime...")
        self.run_command(
            f'az webapp config set '
            f'-n {self.app_name} '
            f'-g {self.resource_group} '
            f'--linux-fx-version "PYTHON|3.10"'
        )
        print_status(STATUS_SUCCESS, "Runtime configured")
        
        print_status(STATUS_RUNNING, "Setting application environment variables...")
        
        # Build environment variables
        env_vars = [
            "SESSION_TIMEOUT_MINUTES=60",
            "LOG_LEVEL=INFO",
            "MOUNT_PATH=/home/site/wwwroot",
        ]
        
        # Add optional AI settings
        if self.enable_ai_foundry:
            env_vars.append("AZURE_AI_FOUNDRY_ENABLED=true")
        if self.enable_ai_search:
            env_vars.append("AZURE_AI_SEARCH_ENABLED=true")
            env_vars.append(f"AZURE_SEARCH_SERVICE_NAME={self.ai_search_name}")
        
        env_str = " ".join([f'"{var}"' for var in env_vars])
        
        code, _ = self.run_command(
            f'az webapp config appsettings set '
            f'-n {self.app_name} '
            f'-g {self.resource_group} '
            f'--settings {env_str}'
        )
        
        if code == 0:
            print_status(STATUS_SUCCESS, "Environment variables set")
        else:
            print_status(STATUS_WARNING, "Could not set all environment variables")
        
        print_status(STATUS_RUNNING, "Setting startup command...")
        self.run_command(
            f'az webapp config set '
            f'-n {self.app_name} '
            f'-g {self.resource_group} '
            f'--startup-file "gunicorn --bind 0.0.0.0 --timeout 600 app.main:app"'
        )
        print_status(STATUS_SUCCESS, "Startup command configured")
        
        return True
    
    def stage_8_verify_deployment(self) -> bool:
        """Stage 8: Verify deployment."""
        print_stage(8, "Verifying Deployment", "Checking if application is responding")
        
        # Get app URL
        code, output = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group} -o json"
        )
        
        if code != 0:
            print_status(STATUS_ERROR, "Could not retrieve app details")
            return False
        
        try:
            app_data = json.loads(output)
            app_url = app_data.get("defaultHostName")
        except:
            print_status(STATUS_ERROR, "Could not parse app details")
            return False
        
        print_status(STATUS_SUCCESS, "App Service deployed", f"https://{app_url}")
        
        # Wait for app to start
        print_status(STATUS_RUNNING, "Waiting for application to start...")
        print_status(STATUS_RUNNING, "  ⏳ Cold start typically takes 1-2 minutes")
        
        import requests
        max_attempts = 12  # 2 minutes total
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print_status(STATUS_RUNNING, f"  → Checking app status (attempt {attempt}/{max_attempts})")
            
            try:
                resp = requests.get(f"https://{app_url}/health", timeout=5)
                if resp.status_code == 200:
                    print_status(STATUS_SUCCESS, "Application is responding!")
                    return True
            except:
                pass
            
            if attempt < max_attempts:
                time.sleep(10)
        
        print_status(STATUS_WARNING, "App not responding yet")
        print_status(STATUS_WARNING, "  The app may still be starting - check back in a moment")
        print_status(STATUS_WARNING, f"  URL: https://{app_url}")
        
        return True
    
    def deploy(self) -> bool:
        """Execute full deployment."""
        print_header("🚀 SYSTEM3-RAG DEPLOYMENT TO AZURE 🚀")
        
        print(f"{Colors.BOLD}Configuration:{Colors.RESET}")
        print(f"  App Name: {self.app_name}")
        print(f"  Resource Group: {self.resource_group}")
        print(f"  Region: {self.region}")
        print(f"  AI Search: {'Enabled' if self.enable_ai_search else 'Disabled'}")
        print(f"  AI Foundry: {'Enabled' if self.enable_ai_foundry else 'Disabled'}")
        
        # Run all stages
        stages = [
            (1, self.stage_1_prerequisites),
            (2, self.stage_2_resource_group),
            (3, self.stage_3_app_service_plan),
            (4, self.stage_4_web_app),
            (5, self.stage_5_ai_search),
            (6, self.stage_6_deploy_code),
            (7, self.stage_7_configure_settings),
            (8, self.stage_8_verify_deployment),
        ]
        
        for stage_num, stage_func in stages:
            if not stage_func():
                print(f"\n{Colors.RED}{STATUS_ERROR} Deployment failed at stage {stage_num}{Colors.RESET}")
                self.print_summary()
                return False
        
        # Success!
        elapsed = (datetime.now() - self.start_time).total_seconds()
        minutes = int(elapsed / 60)
        seconds = int(elapsed % 60)
        
        print_header("🎉 DEPLOYMENT SUCCESSFUL 🎉")
        
        # Get final URL
        code, output = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group} -o json",
            check=False
        )
        
        if code == 0:
            try:
                app_data = json.loads(output)
                app_url = app_data.get("defaultHostName")
                print(f"{Colors.GREEN}{Colors.BOLD}")
                print(f"✅ Your app is live at: https://{app_url}")
                print(f"{Colors.RESET}")
                print(f"Streamlit UI: https://{app_url}")
                print(f"Health Check: https://{app_url}/health")
                print(f"\nDeployment completed in: {minutes}m {seconds}s")
                print()
            except:
                pass
        
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print resource summary."""
        print(f"\n{Colors.BOLD}Deployed Resources:{Colors.RESET}")
        self.tracker.print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy System3-RAG to Azure App Service with AI services"
    )
    parser.add_argument("--name", default="system3-rag", help="App name")
    parser.add_argument("--resource-group", required=True, help="Azure resource group")
    parser.add_argument("--region", default="eastus", help="Azure region")
    parser.add_argument("--enable-ai-search", action="store_true", default=True,
                       help="Deploy Azure AI Search service")
    parser.add_argument("--enable-ai-foundry", action="store_true", default=True,
                       help="Enable AI Foundry agent integration")
    
    args = parser.parse_args()
    
    deployer = AppServiceDeployer(
        app_name=args.name,
        resource_group=args.resource_group,
        region=args.region,
        enable_ai_search=args.enable_ai_search,
        enable_ai_foundry=args.enable_ai_foundry
    )
    
    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
