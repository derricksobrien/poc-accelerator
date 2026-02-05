#!/usr/bin/env python3
"""
Azure App Service Deployment Script for System3-RAG

Deploys to Azure App Service (no containers, no ACR needed)
Pure Python runtime with automatic scaling.

Usage:
    python deploy_app_service.py --name system3-rag --resource-group my-rg --region eastus

Stages:
    1. Check prerequisites
    2. Create resource group
    3. Create App Service Plan
    4. Create Web App
    5. Deploy code
    6. Configure secrets
    7. Verify deployment
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Tuple
import time

class AppServiceDeployer:
    """Deploys System3-RAG to Azure App Service."""
    
    def __init__(
        self,
        app_name: str,
        resource_group: str,
        region: str = "eastus",
        runtime: str = "PYTHON|3.10"
    ):
        self.app_name = app_name
        self.resource_group = resource_group
        self.region = region
        self.runtime = runtime
        self.app_service_plan = f"{app_name}-plan"
        
    def run_command(self, cmd: str, check: bool = True) -> Tuple[int, str]:
        """Execute Azure CLI command."""
        print(f"\n📋 Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0 and check:
            print(f"❌ Error: {result.stderr}")
            sys.exit(1)
        
        if result.stdout:
            print(f"✅ {result.stdout.strip()[:100]}")
        
        return result.returncode, result.stdout.strip()
    
    def stage_1_prerequisites(self) -> bool:
        """Stage 1: Check prerequisites."""
        print("\n" + "="*70)
        print("STAGE 1: Checking Prerequisites")
        print("="*70)
        
        # Check Azure CLI
        code, _ = self.run_command("az --version", check=False)
        if code != 0:
            print("❌ Azure CLI not installed. Install from: https://aka.ms/azcliinstaller")
            return False
        print("✅ Azure CLI installed")
        
        # Check authentication
        code, out = self.run_command("az account show", check=False)
        if code != 0:
            print("⚠️  Not authenticated. Run: az login")
            return False
        print("✅ Authenticated with Azure")
        
        # Show current subscription
        self.run_command("az account show -o json")
        
        return True
    
    def stage_2_resource_group(self) -> bool:
        """Stage 2: Create/verify resource group."""
        print("\n" + "="*70)
        print("STAGE 2: Creating/Verifying Resource Group")
        print("="*70)
        
        # Check if RG exists
        code, _ = self.run_command(
            f"az group exists -n {self.resource_group}",
            check=False
        )
        
        if code == 0:
            print(f"✅ Resource group '{self.resource_group}' already exists")
            return True
        
        # Create RG
        print(f"Creating resource group: {self.resource_group}")
        self.run_command(
            f"az group create -n {self.resource_group} -l {self.region}"
        )
        print(f"✅ Resource group created in {self.region}")
        
        return True
    
    def stage_3_app_service_plan(self) -> bool:
        """Stage 3: Create App Service Plan."""
        print("\n" + "="*70)
        print("STAGE 3: Creating App Service Plan")
        print("="*70)
        
        # Check if plan exists
        code, _ = self.run_command(
            f"az appservice plan show -n {self.app_service_plan} -g {self.resource_group}",
            check=False
        )
        
        if code == 0:
            print(f"✅ App Service Plan '{self.app_service_plan}' already exists")
            return True
        
        # Create plan (B1 = basic, good for testing; B2/B3 for production)
        print(f"Creating App Service Plan: {self.app_service_plan}")
        self.run_command(
            f"az appservice plan create "
            f"-n {self.app_service_plan} "
            f"-g {self.resource_group} "
            f"-l {self.region} "
            f"--is-linux "
            f"--sku B1"
        )
        print("✅ App Service Plan created (B1 tier - $13/mo)")
        
        return True
    
    def stage_4_web_app(self) -> bool:
        """Stage 4: Create Web App."""
        print("\n" + "="*70)
        print("STAGE 4: Creating Web App")
        print("="*70)
        
        # Check if app exists
        code, _ = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group}",
            check=False
        )
        
        if code == 0:
            print(f"✅ Web App '{self.app_name}' already exists")
            return True
        
        # Create web app
        print(f"Creating Web App: {self.app_name}")
        self.run_command(
            f'az webapp create '
            f'-n {self.app_name} '
            f'-g {self.resource_group} '
            f'--plan {self.app_service_plan} '
            f'--runtime "{self.runtime}"'
        )
        print("✅ Web App created")
        
        # Get the URL
        code, url = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group} "
            f"--query defaultHostName -o tsv"
        )
        
        print(f"🌐 Web App URL: https://{url.strip()}")
        
        return True
    
    def stage_5_deploy_code(self) -> bool:
        """Stage 5: Deploy code."""
        print("\n" + "="*70)
        print("STAGE 5: Deploying Code")
        print("="*70)
        
        # Check if we're in the right directory
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt not found. Make sure you're in System3-RAG directory")
            return False
        
        print("Current directory has System3-RAG code ✅")
        
        # Deploy using az webapp up (simplest method)
        print(f"Deploying code to {self.app_name}...")
        self.run_command(
            f'az webapp up '
            f'--name {self.app_name} '
            f'--resource-group {self.resource_group} '
            f'--runtime "{self.runtime}" '
            f'--logs'
        )
        
        print("✅ Code deployed successfully")
        
        return True
    
    def stage_6_configuration(self) -> bool:
        """Stage 6: Configure app settings."""
        print("\n" + "="*70)
        print("STAGE 6: Configuring Application Settings")
        print("="*70)
        
        # Set startup command for Streamlit + FastAPI
        print("Configuring startup command...")
        
        # For App Service, we need to run both services
        # Option 1: Run FastAPI on default port, Streamlit on another
        startup_cmd = "gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app"
        
        self.run_command(
            f"az webapp config set "
            f"-n {self.app_name} "
            f"-g {self.resource_group} "
            f"--startup-file '{startup_cmd}'"
        )
        
        # Set environment variables
        env_vars = {
            "FASTAPI_HOST": "0.0.0.0",
            "FASTAPI_PORT": "8000",
            "LOG_LEVEL": "INFO",
            "SESSION_TIMEOUT_MINUTES": "60",
            "MAX_SESSIONS": "100"
        }
        
        settings_str = " ".join([f"{k}='{v}'" for k, v in env_vars.items()])
        
        self.run_command(
            f"az webapp config appsettings set "
            f"-n {self.app_name} "
            f"-g {self.resource_group} "
            f"--settings {settings_str}"
        )
        
        print("✅ Application settings configured")
        
        return True
    
    def stage_7_verify(self) -> bool:
        """Stage 7: Verify deployment."""
        print("\n" + "="*70)
        print("STAGE 7: Verifying Deployment")
        print("="*70)
        
        # Get app details
        code, info = self.run_command(
            f"az webapp show -n {self.app_name} -g {self.resource_group} -o json"
        )
        
        if code == 0:
            details = json.loads(info)
            print(f"\n✅ Web App Status:")
            print(f"   State: {details.get('state', 'Unknown')}")
            print(f"   URL: https://{details.get('defaultHostName', 'unknown')}")
            
            # Wait for app to start
            print("\n⏳ Waiting for app to start (this takes 1-2 minutes)...")
            for i in range(12):  # Try for 2 minutes
                time.sleep(10)
                import requests
                try:
                    resp = requests.get(f"https://{details.get('defaultHostName')}/health", timeout=5)
                    if resp.status_code == 200:
                        print("✅ Application is responding!")
                        print(f"\n🎉 Deployment successful!")
                        print(f"\n📌 Access your app at: https://{details.get('defaultHostName')}")
                        return True
                except:
                    print(f"   Attempt {i+1}/12 - Still starting...")
            
            print("⚠️  App is deployed but still warming up. Check back in a moment.")
            print(f"   https://{details['url']}")
            return True
        
        return False
    
    def run_full_deployment(self):
        """Run all stages."""
        stages = [
            ("Prerequisites", self.stage_1_prerequisites),
            ("Resource Group", self.stage_2_resource_group),
            ("App Service Plan", self.stage_3_app_service_plan),
            ("Web App", self.stage_4_web_app),
            ("Deploy Code", self.stage_5_deploy_code),
            ("Configuration", self.stage_6_configuration),
            ("Verify", self.stage_7_verify),
        ]
        
        print("\n" + "🚀" * 35)
        print("SYSTEM3-RAG → AZURE APP SERVICE DEPLOYMENT")
        print("🚀" * 35)
        
        completed = 0
        for stage_name, stage_func in stages:
            try:
                if stage_func():
                    completed += 1
                else:
                    print(f"\n❌ Stage failed: {stage_name}")
                    print("Fix the issue and run: python deploy_app_service.py ...")
                    sys.exit(1)
            except Exception as e:
                print(f"\n❌ Stage failed with error: {e}")
                sys.exit(1)
        
        print("\n" + "="*70)
        print(f"✅ DEPLOYMENT COMPLETE ({completed}/{len(stages)} stages)")
        print("="*70)
        print("""
Next steps:
1. Wait 2-3 minutes for app to fully warm up
2. Visit your app at the URL shown above
3. Try the Generate POC tab
4. Run tests: pytest test_all_endpoints.py -v
5. (Optional) Configure Azure AI agent in app settings

To configure Azure credentials:
    az webapp config appsettings set \\
      -n system3-rag \\
      -g <resource-group> \\
      --settings \\
        AZURE_OPENAI_ENDPOINT="https://..." \\
        AZURE_OPENAI_KEY="sk-..."

To scale up:
    az appservice plan update -n system3-rag-plan -g <resource-group> --sku B2
""")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy System3-RAG to Azure App Service",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--name",
        default="system3-rag",
        help="App Service name (default: system3-rag)"
    )
    parser.add_argument(
        "--resource-group",
        required=True,
        help="Azure resource group name"
    )
    parser.add_argument(
        "--region",
        default="eastus",
        help="Azure region (default: eastus)"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="Run specific stage only (1-7)"
    )
    
    args = parser.parse_args()
    
    deployer = AppServiceDeployer(
        app_name=args.name,
        resource_group=args.resource_group,
        region=args.region
    )
    
    if args.stage:
        stages = {
            1: ("Prerequisites", deployer.stage_1_prerequisites),
            2: ("Resource Group", deployer.stage_2_resource_group),
            3: ("App Service Plan", deployer.stage_3_app_service_plan),
            4: ("Web App", deployer.stage_4_web_app),
            5: ("Deploy Code", deployer.stage_5_deploy_code),
            6: ("Configuration", deployer.stage_6_configuration),
            7: ("Verify", deployer.stage_7_verify),
        }
        
        stage_name, stage_func = stages[args.stage]
        print(f"\n🎯 Running Stage {args.stage}: {stage_name}\n")
        
        if stage_func():
            print(f"✅ Stage {args.stage} completed")
        else:
            print(f"❌ Stage {args.stage} failed")
            sys.exit(1)
    else:
        deployer.run_full_deployment()


if __name__ == "__main__":
    main()
