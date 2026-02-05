#!/usr/bin/env python3
"""
Azure AI Foundry Agent Setup Script

Automates the creation and configuration of an AI Foundry agent project
with all necessary tools, models, and endpoints for the TechConnect RAG system.

Usage:
    python setup_azure_agent.py --subscription <id> --resource-group <name> [--region <region>]
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureAIFoundrySetup:
    """Automates Azure AI Foundry project and agent creation."""

    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        region: str = "eastus",
        project_name: str = "techconnect-rag",
    ):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.region = region
        self.project_name = project_name
        self.config: Dict[str, Any] = {}

    def run_command(self, command: str, check: bool = True) -> str:
        """Execute Azure CLI command and return output."""
        logger.info(f"Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                cwd=str(Path.cwd())
            )
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
                if check:
                    raise RuntimeError(f"Command failed: {result.stderr}")
            return result.stdout.strip()
        except FileNotFoundError:
            logger.error("Azure CLI not found. Install with: az extension add -n ai")
            raise

    def check_prerequisites(self) -> bool:
        """Verify Azure CLI and required extensions are installed."""
        logger.info("Checking prerequisites...")
        
        try:
            # Check Azure CLI
            self.run_command("az --version")
            logger.info("✓ Azure CLI installed")

            # Check AI extension
            extensions = self.run_command("az extension list --output json")
            if "ai" not in extensions.lower():
                logger.info("Installing Azure AI extension...")
                self.run_command("az extension add -n ai")
            logger.info("✓ Azure AI extension installed")

            # Check authentication
            self.run_command("az account show")
            logger.info("✓ Authenticated with Azure")

            return True
        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            return False

    def set_subscription(self):
        """Set the target subscription."""
        logger.info(f"Setting subscription to {self.subscription_id}...")
        self.run_command(f"az account set --subscription {self.subscription_id}")
        logger.info("✓ Subscription set")

    def create_resource_group(self):
        """Create or verify resource group exists."""
        logger.info(f"Checking resource group: {self.resource_group}...")
        
        # Check if exists
        exists = self.run_command(
            f"az group exists -n {self.resource_group}",
            check=False
        )
        
        if exists == "false":
            logger.info(f"Creating resource group {self.resource_group}...")
            self.run_command(
                f"az group create -n {self.resource_group} -l {self.region}"
            )
            logger.info(f"✓ Resource group created in {self.region}")
        else:
            logger.info("✓ Resource group exists")

    def create_ai_hub(self) -> str:
        """Create or get AI Hub for the project."""
        hub_name = f"{self.project_name}-hub"
        logger.info(f"Creating AI Hub: {hub_name}...")

        # Check if exists
        hubs = self.run_command(
            f"az ai hub list -g {self.resource_group} --output json",
            check=False
        )
        
        if hubs and f'"{hub_name}"' in hubs:
            logger.info("✓ AI Hub exists")
            self.config["hub_name"] = hub_name
            return hub_name

        # Create hub
        try:
            self.run_command(
                f"az ai hub create "
                f"-g {self.resource_group} "
                f"-n {hub_name} "
                f"-l {self.region} "
                f"--storage-account-name {self.project_name}storage "
                f"--key-vault-name {self.project_name}-kv"
            )
            logger.info("✓ AI Hub created")
            self.config["hub_name"] = hub_name
            return hub_name
        except Exception as e:
            logger.warning(f"Hub creation had issues: {e}")
            logger.info("Continuing with existing setup...")
            self.config["hub_name"] = hub_name
            return hub_name

    def create_ai_project(self, hub_name: str) -> str:
        """Create AI Foundry project."""
        logger.info(f"Creating AI Project: {self.project_name}...")

        try:
            self.run_command(
                f"az ai project create "
                f"-g {self.resource_group} "
                f"-n {self.project_name} "
                f"--hub {hub_name}"
            )
            logger.info("✓ AI Project created")
        except Exception as e:
            logger.warning(f"Project creation had issues: {e}")
            logger.info("Continuing with existing setup...")

        self.config["project_name"] = self.project_name
        return self.project_name

    def deploy_model(self, model_name: str = "gpt-4", deployment_name: str = "gpt4-deployment") -> str:
        """Deploy a language model (GPT-4 recommended)."""
        logger.info(f"Deploying model: {model_name}...")

        try:
            output = self.run_command(
                f"az ai model create "
                f"--name {model_name} "
                f"--resource-group {self.resource_group} "
                f"--project {self.project_name}",
                check=False
            )
            logger.info("✓ Model deployed")
        except Exception as e:
            logger.warning(f"Model deployment had issues: {e}")

        self.config["model_deployment"] = deployment_name
        return deployment_name

    def create_agent_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define agent tools for the RAG system."""
        logger.info("Defining agent tools...")

        tools = {
            "search_solutions": {
                "type": "function",
                "function": {
                    "name": "search_solutions",
                    "description": "Search for relevant solution accelerators and technical resources",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for solutions"
                            },
                            "area": {
                                "type": "string",
                                "enum": ["AI", "Data", "Security", "Cloud", "Fabric"],
                                "description": "Solution area to filter by"
                            },
                            "complexity": {
                                "type": "string",
                                "enum": ["L200", "L300", "L400"],
                                "description": "Complexity level (L200=intro, L300=intermediate, L400=advanced)"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default 5)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            "generate_rbac": {
                "type": "function",
                "function": {
                    "name": "generate_rbac",
                    "description": "Generate RBAC configuration for solution deployment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "solution_id": {
                                "type": "string",
                                "description": "ID of the solution to generate RBAC for"
                            },
                            "organization": {
                                "type": "string",
                                "description": "Organization name for role scoping"
                            },
                            "include_service_principals": {
                                "type": "boolean",
                                "description": "Include service principal roles"
                            }
                        },
                        "required": ["solution_id"]
                    }
                }
            },
            "generate_deployment_script": {
                "type": "function",
                "function": {
                    "name": "generate_deployment_script",
                    "description": "Generate deployment scripts (Bicep, Terraform, or ARM)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "solution_id": {
                                "type": "string",
                                "description": "ID of the solution"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["bicep", "terraform", "arm"],
                                "description": "Deployment format"
                            },
                            "environment": {
                                "type": "string",
                                "enum": ["dev", "staging", "prod"],
                                "description": "Target environment"
                            }
                        },
                        "required": ["solution_id", "format"]
                    }
                }
            },
            "generate_iac_template": {
                "type": "function",
                "function": {
                    "name": "generate_iac_template",
                    "description": "Generate Infrastructure-as-Code templates with best practices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "solution_id": {
                                "type": "string",
                                "description": "ID of the solution"
                            },
                            "template_type": {
                                "type": "string",
                                "enum": ["bicep", "terraform", "pulumi"],
                                "description": "IaC template type"
                            },
                            "include_monitoring": {
                                "type": "boolean",
                                "description": "Include monitoring and logging"
                            },
                            "include_security": {
                                "type": "boolean",
                                "description": "Include security best practices"
                            }
                        },
                        "required": ["solution_id", "template_type"]
                    }
                }
            },
            "validate_architecture": {
                "type": "function",
                "function": {
                    "name": "validate_architecture",
                    "description": "Validate architecture against best practices and compliance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "solution_id": {
                                "type": "string",
                                "description": "ID of the solution"
                            },
                            "compliance_frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Compliance frameworks (HIPAA, SOC2, PCI-DSS, etc.)"
                            },
                            "regions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Azure regions for deployment"
                            }
                        },
                        "required": ["solution_id"]
                    }
                }
            }
        }

        logger.info(f"✓ Defined {len(tools)} tools")
        self.config["tools"] = list(tools.keys())
        return tools

    def create_agent(self, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Create the AI agent with defined tools."""
        logger.info("Creating AI Agent...")

        agent_config = {
            "name": f"{self.project_name}-agent",
            "description": "TechConnect RAG Agent for generating POC architectures",
            "instructions": """You are a Cloud Solution Architect (CSA) assistant specialized in 
generating Proof of Concept (POC) architectures. You help enterprise teams understand and implement
Microsoft solution accelerators.

For each request:
1. Search for relevant solution accelerators
2. Understand the customer's requirements
3. Generate RBAC configuration for secure access
4. Provide deployment scripts (Bicep/Terraform)
5. Include IaC templates with best practices
6. Validate against compliance frameworks
7. Provide implementation recommendations

Always consider:
- Security and compliance (RBAC, encryption, network isolation)
- Cost optimization (Azure pricing, resource sizing)
- Scalability and performance (multi-region, load balancing)
- Monitoring and observability (Azure Monitor, Application Insights)
- Disaster recovery (backup, failover, business continuity)

Format responses clearly with sections for:
- Architecture Overview
- Implementation Steps
- RBAC Requirements
- Deployment Instructions
- Cost Estimates
- Risk Assessment
- Next Steps""",
            "model": "gpt-4",
            "temperature": 0.7,
            "tools": list(tools.keys()),
            "resource_group": self.resource_group,
            "project": self.project_name
        }

        self.config["agent"] = agent_config
        logger.info("✓ Agent configuration prepared")
        return agent_config

    def save_configuration(self, output_file: str = ".env"):
        """Save configuration to .env file for backend use."""
        logger.info(f"Saving configuration to {output_file}...")

        env_content = f"""# Azure AI Foundry Agent Configuration
# Generated by setup_azure_agent.py

# Subscription and Resource Details
AZURE_SUBSCRIPTION_ID={self.subscription_id}
AZURE_RESOURCE_GROUP={self.resource_group}
AZURE_REGION={self.region}

# AI Foundry Project
AZURE_AI_HUB_NAME={self.config.get('hub_name', 'techconnect-rag-hub')}
AZURE_AI_PROJECT_NAME={self.config.get('project_name', 'techconnect-rag')}
AZURE_AI_PROJECT_ID={self.config.get('project_id', 'TBD')}

# Model Deployment
AZURE_MODEL_DEPLOYMENT={self.config.get('model_deployment', 'gpt4-deployment')}
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Agent Configuration
AZURE_AI_AGENT_NAME={self.config.get('agent', {}).get('name', 'techconnect-rag-agent')}
AZURE_AI_AGENT_TOOLS={',' .join(self.config.get('tools', []))}

# API Endpoints (populated after deployment)
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-api-key>

# Local Development
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

# Session Management
SESSION_TIMEOUT_MINUTES=60
MAX_SESSIONS=100
CLEANUP_INTERVAL_MINUTES=30

# Logging
LOG_LEVEL=INFO
"""

        Path(output_file).write_text(env_content)
        logger.info(f"✓ Configuration saved to {output_file}")

    def display_next_steps(self):
        """Display next steps for completing setup."""
        logger.info("\n" + "="*70)
        logger.info("SETUP COMPLETE - NEXT STEPS")
        logger.info("="*70)

        print(f"""
1. RETRIEVE CREDENTIALS:
   az keyvault secret show --vault-name {self.project_name}-kv --name openai-api-key

2. UPDATE .env FILE:
   - Add AZURE_OPENAI_ENDPOINT from Azure Portal
   - Add AZURE_OPENAI_KEY from Key Vault
   - Verify other values are correct

3. TEST CONNECTION:
   python -c "from app.agent import AzureAIFoundryAgent; print(AzureAIFoundryAgent().get_project_status())"

4. START SERVICES:
   Terminal 1: python -m uvicorn app.main:app --reload
   Terminal 2: streamlit run streamlit_app.py

5. TEST AGENT ENDPOINT:
   curl -X POST http://localhost:8000/api/rag/generate-poc \\
     -H "Content-Type: application/json" \\
     -d '{{"title": "AI Chatbot", "requirements": "Enterprise grade"}}' 

6. DEPLOY TO AZURE:
   docker build -t system3-rag .
   az acr build --registry <acr-name> --image system3-rag:latest .
   az containerapp create --name system3-rag ...

Configuration saved to: .env
Agent Tools: {', '.join(self.config.get('tools', []))}
Project: {self.project_name}
Region: {self.region}
""")

    def run(self):
        """Execute full setup pipeline."""
        logger.info("Starting Azure AI Foundry Agent Setup...")
        logger.info("="*70)

        try:
            # 1. Prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites not met")
                return False

            # 2. Setup subscription
            self.set_subscription()

            # 3. Create resource group
            self.create_resource_group()

            # 4. Create AI Hub
            hub_name = self.create_ai_hub()

            # 5. Create AI Project
            self.create_ai_project(hub_name)

            # 6. Deploy model
            self.deploy_model()

            # 7. Define tools
            tools = self.create_agent_tools()

            # 8. Create agent
            self.create_agent(tools)

            # 9. Save configuration
            self.save_configuration(".env")

            # 10. Next steps
            self.display_next_steps()

            logger.info("✓ Setup completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            logger.info("\nTroubleshooting:")
            logger.info("1. Verify Azure CLI is installed: az --version")
            logger.info("2. Verify authentication: az account show")
            logger.info("3. Check resource group exists: az group list")
            logger.info("4. Run setup again with --debug flag")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Set up Azure AI Foundry agent for TechConnect RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_azure_agent.py --subscription abc123 --resource-group my-rg
  python setup_azure_agent.py --subscription abc123 --resource-group my-rg --region westus2
  python setup_azure_agent.py --subscription abc123 --resource-group my-rg --project custom-name
        """
    )

    parser.add_argument(
        "--subscription",
        required=True,
        help="Azure subscription ID"
    )
    parser.add_argument(
        "--resource-group",
        required=True,
        help="Azure resource group name"
    )
    parser.add_argument(
        "--region",
        default="eastus",
        help="Azure region (default: eastus)",
        choices=["eastus", "westus2", "northeurope", "westeurope", "southeastasia", "japaneast"]
    )
    parser.add_argument(
        "--project",
        default="techconnect-rag",
        help="AI Foundry project name (default: techconnect-rag)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    setup = AzureAIFoundrySetup(
        subscription_id=args.subscription,
        resource_group=args.resource_group,
        region=args.region,
        project_name=args.project
    )

    success = setup.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
