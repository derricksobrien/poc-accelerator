"""
Skillable Simulator: Lab Instructions Generator
Demonstrates how the Skillable Gen AI agent consumes TechConnect context blocks
to generate automated lab instructions and deployment guides.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys
import re

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import ContextBlock


class XMLParser:
    """Simple XML parser for extracting items from tagged content."""
    
    @staticmethod
    def extract_items(xml_str: str, tag: str) -> List[str]:
        """
        Extract items from XML structure like <tag><item>value</item>...</tag>
        
        Args:
            xml_str: XML string to parse
            tag: Tag name to extract (e.g., "prerequisites")
            
        Returns:
            List of item values
        """
        if not xml_str or f"<{tag}>" not in xml_str:
            return []
        
        # Find all <item>...</item> patterns
        pattern = r'<item>(.*?)</item>'
        matches = re.findall(pattern, xml_str)
        return matches


class LabInstructionGenerator:
    """
    Generates lab instructions from TechConnect ContextBlocks.
    This simulates the Skillable Gen AI agent's instruction generation.
    """
    
    def __init__(self):
        self.xml_parser = XMLParser()
    
    def generate_lab_guide(self, context_block: ContextBlock) -> Dict:
        """
        Generate a complete lab guide from a ContextBlock.
        
        Args:
            context_block: ContextBlock from TechConnect broker
            
        Returns:
            Dict with structured lab instructions
        """
        prerequisites = self.xml_parser.extract_items(context_block.prerequisites_xml, "prerequisites")
        products = self.xml_parser.extract_items(context_block.products_xml, "products")
        
        estimated_duration = self._estimate_duration(context_block.complexity_level)
        
        guide = {
            "lab_metadata": {
                "title": f"Lab: Deploy {context_block.solution_name}",
                "solution_id": context_block.catalog_item_id,
                "complexity_level": context_block.complexity_level,
                "solution_area": context_block.solution_area,
                "estimated_duration": estimated_duration,
                "duration": estimated_duration,
                "repository_url": context_block.repository_url
            },
            "overview": {
                "objective": self._generate_objective(context_block),
                "description": context_block.architecture_summary,
                "learning_outcomes": self._generate_learning_outcomes(context_block)
            },
            "prerequisites": {
                "required": prerequisites,
                "validation_steps": self._generate_validation_steps(prerequisites)
            },
            "technologies": {
                "services": products,
                "languages": self._infer_languages(context_block)
            },
            "safety_guardrails": {
                "required": context_block.rai_disclaimer is not None,
                "disclaimer": context_block.rai_disclaimer
            },
            "lab_steps": self._generate_lab_steps(context_block, prerequisites, products),
            "validation": {
                "success_criteria": self._generate_success_criteria(context_block),
                "troubleshooting": self._generate_troubleshooting_guide(context_block)
            }
        }
        
        return guide
    
    def _estimate_duration(self, complexity: str) -> str:
        """Estimate lab duration based on complexity level."""
        duration_map = {
            "L200": "30-45 minutes",
            "L300": "1-2 hours",
            "L400": "2-4 hours"
        }
        return duration_map.get(complexity, "1-2 hours")
    
    def _generate_objective(self, context_block: ContextBlock) -> str:
        """Generate lab objective statement."""
        return f"Deploy and configure {context_block.solution_name} in your Azure environment."
    
    def _generate_learning_outcomes(self, context_block: ContextBlock) -> List[str]:
        """Generate learning outcomes for the lab."""
        outcomes = [
            f"Understand the architecture of {context_block.solution_name}",
            "Configure required Azure services and prerequisites",
            "Deploy the solution using provided templates",
            "Validate the deployment and verify functionality"
        ]
        
        if "AI" in context_block.solution_area:
            outcomes.append("Implement responsible AI governance practices")
        
        return outcomes
    
    def _generate_validation_steps(self, prerequisites: List[str]) -> List[Dict]:
        """Generate steps to validate prerequisites."""
        steps = []
        for i, prereq in enumerate(prerequisites, 1):
            steps.append({
                "step": i,
                "action": f"Verify: {prereq}",
                "validation_command": self._generate_validation_command(prereq),
                "expected_result": "Success/Confirmed"
            })
        return steps
    
    def _generate_validation_command(self, prerequisite: str) -> str:
        """Generate a validation command for a prerequisite."""
        if "subscription" in prerequisite.lower():
            return "az account show --query id"
        elif "openai" in prerequisite.lower():
            return "az cognitiveservices account list --resource-group <rg>"
        elif "foundry" in prerequisite.lower():
            return "az providerhub show --namespace Microsoft.AIServices"
        else:
            return f"# Verify: {prerequisite}"
    
    def _infer_languages(self, context_block: ContextBlock) -> List[str]:
        """Infer programming languages from solution."""
        # This would come from catalog in production
        language_keywords = {
            "Python": ["python", "notebooks", "sdk"],
            "TypeScript": ["typescript", "javascript", "node"],
            "Bicep": ["bicep", "iac", "infrastructure"],
            "SQL": ["database", "sql", "analytics"]
        }
        
        inferred = []
        description = context_block.architecture_summary.lower()
        for lang, keywords in language_keywords.items():
            if any(kw in description for kw in keywords):
                inferred.append(lang)
        
        return inferred if inferred else ["Python", "TypeScript"]
    
    def _generate_lab_steps(self, context_block: ContextBlock, 
                           prerequisites: List[str], 
                           products: List[str]) -> List[Dict]:
        """Generate step-by-step lab instructions."""
        steps = [
            {
                "section": "1. Setup",
                "steps": [
                    {
                        "number": "1.1",
                        "title": "Verify prerequisites",
                        "description": f"Ensure all {len(prerequisites)} prerequisites are met",
                        "action": "Run validation script",
                        "time_estimate": "5 minutes"
                    },
                    {
                        "number": "1.2",
                        "title": "Clone repository",
                        "description": f"Clone from {context_block.repository_url}",
                        "action": "git clone <repo-url>",
                        "time_estimate": "3 minutes"
                    }
                ]
            },
            {
                "section": "2. Configuration",
                "steps": [
                    {
                        "number": "2.1",
                        "title": "Configure Azure services",
                        "description": f"Set up required services: {', '.join(products[:3])}...",
                        "action": "Follow service setup guides",
                        "time_estimate": "15-20 minutes"
                    },
                    {
                        "number": "2.2",
                        "title": "Configure environment",
                        "description": "Set environment variables and credentials",
                        "action": "cp .env.example .env && populate values",
                        "time_estimate": "5 minutes"
                    }
                ]
            },
            {
                "section": "3. Deployment",
                "steps": [
                    {
                        "number": "3.1",
                        "title": "Deploy infrastructure",
                        "description": "Deploy resources using IaC",
                        "action": "bicep deploy or terraform apply",
                        "time_estimate": f"{self._get_deploy_time(context_block.complexity_level)}"
                    },
                    {
                        "number": "3.2",
                        "title": "Deploy application",
                        "description": "Deploy application code",
                        "action": "az container app deploy or similar",
                        "time_estimate": "10-15 minutes"
                    }
                ]
            },
            {
                "section": "4. Validation",
                "steps": [
                    {
                        "number": "4.1",
                        "title": "Test endpoints",
                        "description": "Verify service endpoints are responding",
                        "action": "curl or Postman tests",
                        "time_estimate": "5 minutes"
                    },
                    {
                        "number": "4.2",
                        "title": "Validate functionality",
                        "description": f"Run solution-specific tests for {context_block.solution_name}",
                        "action": "pytest or integration tests",
                        "time_estimate": "10 minutes"
                    }
                ]
            }
        ]
        
        return steps
    
    def _get_deploy_time(self, complexity: str) -> str:
        """Get estimated deployment time by complexity."""
        times = {
            "L200": "20-30 minutes",
            "L300": "30-45 minutes",
            "L400": "45-60 minutes"
        }
        return times.get(complexity, "30-45 minutes")
    
    def _generate_success_criteria(self, context_block: ContextBlock) -> List[str]:
        """Generate success criteria for lab completion."""
        criteria = [
            "All prerequisites verified",
            "Azure resources successfully deployed",
            "Application endpoints responding",
            "Functionality tests passing",
            "No critical errors in logs"
        ]
        
        if context_block.rai_disclaimer:
            criteria.append("RAI governance policies documented and implemented")
        
        return criteria
    
    def _generate_troubleshooting_guide(self, context_block: ContextBlock) -> Dict:
        """Generate common troubleshooting steps."""
        return {
            "common_issues": [
                {
                    "issue": "Prerequisite validation fails",
                    "cause": "Missing or incorrect setup",
                    "resolution": "Review prerequisites section and re-run validation"
                },
                {
                    "issue": "Deployment timeout",
                    "cause": "Resource creation taking longer than expected",
                    "resolution": "Wait 2-3 minutes and check Azure portal for resource status"
                },
                {
                    "issue": "Authentication errors",
                    "cause": "Incorrect credentials or permissions",
                    "resolution": "Verify credentials in .env file and Azure RBAC assignments"
                },
                {
                    "issue": "Service unavailable",
                    "cause": "Service not fully initialized",
                    "resolution": "Wait 1-2 minutes and retry endpoint calls"
                }
            ],
            "support_resources": [
                f"Repository: {context_block.repository_url}",
                "Azure Support: https://support.microsoft.com/en-us",
                "Skillable Support: https://www.skillable.com/support"
            ]
        }
    
    def generate_deployment_script(self, context_block: ContextBlock) -> str:
        """
        Generate a deployment bash script from context block.
        """
        prerequisites = self.xml_parser.extract_items(context_block.prerequisites_xml, "prerequisites")
        
        script = f'''#!/bin/bash
# Auto-generated deployment script for: {context_block.solution_name}
# Solution ID: {context_block.catalog_item_id}
# Complexity: {context_block.complexity_level}
# Generated by Skillable Gen AI Lab Generator

set -e

echo "=========================================="
echo "Deploying: {context_block.solution_name}"
echo "=========================================="

# Step 1: Validate prerequisites
echo ""
echo "[1/4] Validating prerequisites..."
'''
        
        for prereq in prerequisites:
            script += f'\necho "  • Checking: {prereq}"\n'
        
        script += f'''
# Step 2: Clone repository
echo ""
echo "[2/4] Cloning repository..."
REPO_URL="{context_block.repository_url}"
REPO_NAME=$(basename $REPO_URL .git)
git clone $REPO_URL $REPO_NAME
cd $REPO_NAME

# Step 3: Configure environment
echo ""
echo "[3/4] Configuring environment..."
if [ ! -f .env ]; then
    echo "  • Creating .env file from template"
    cp .env.example .env || echo "  • No .env.example found, please create .env manually"
fi

# Step 4: Deploy resources
echo ""
echo "[4/4] Deploying resources..."
echo "  • This may take several minutes..."

# Deploy using appropriate method (uncomment one):
# bicep deploy -f main.bicep -g $RESOURCE_GROUP
# terraform apply -auto-approve
# az container app deploy -g $RESOURCE_GROUP -n $APP_NAME

echo ""
echo "=========================================="
echo "✓ Deployment completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify deployment: az resource list -g $RESOURCE_GROUP"
echo "2. Test endpoints"
echo "3. Review logs for errors"
'''
        
        if context_block.rai_disclaimer:
            script += '\necho ""\necho "⚠️  RAI GOVERNANCE NOTICE:"\necho "' + context_block.rai_disclaimer.replace('\n', '\necho "') + '"\n'
        
        return script
    
    def generate_lab_report(self, context_block: ContextBlock, 
                           guide: Dict, 
                           completion_status: str = "Not Started") -> str:
        """
        Generate a formatted lab report for the Skillable LMS.
        """
        prerequisites = self.xml_parser.extract_items(context_block.prerequisites_xml, "prerequisites")
        products = self.xml_parser.extract_items(context_block.products_xml, "products")
        
        report = f'''
╔════════════════════════════════════════════════════════════════╗
║  SKILLABLE LAB INSTRUCTIONS REPORT                             ║
╚════════════════════════════════════════════════════════════════╝

LAB METADATA
────────────────────────────────────────────────────────────────
Title:              {guide['lab_metadata']['title']}
Solution ID:        {context_block.catalog_item_id}
Complexity Level:   {context_block.complexity_level}
Solution Area:      {context_block.solution_area}
Duration:           {guide['lab_metadata']['estimated_duration']}
Repository:         {context_block.repository_url}
Status:             {completion_status}

OBJECTIVE
────────────────────────────────────────────────────────────────
{guide['overview']['objective']}

DESCRIPTION
────────────────────────────────────────────────────────────────
{context_block.architecture_summary}

LEARNING OUTCOMES
────────────────────────────────────────────────────────────────
'''
        
        for i, outcome in enumerate(guide['overview']['learning_outcomes'], 1):
            report += f"{i}. {outcome}\n"
        
        report += f'''
PREREQUISITES ({len(prerequisites)})
────────────────────────────────────────────────────────────────
'''
        
        for i, prereq in enumerate(prerequisites, 1):
            report += f"{i}. {prereq}\n"
        
        report += f'''
TECHNOLOGIES & SERVICES ({len(products)})
────────────────────────────────────────────────────────────────
'''
        
        for i, product in enumerate(products, 1):
            report += f"{i}. {product}\n"
        
        if context_block.rai_disclaimer:
            report += f'''
⚠️  RESPONSIBLE AI GOVERNANCE REQUIRED
────────────────────────────────────────────────────────────────
{context_block.rai_disclaimer}

IMPLEMENTATION REQUIREMENTS:
✓ Enable monitoring for model outputs
✓ Implement human review workflows
✓ Document AI capabilities and limitations
✓ Ensure Microsoft RAI compliance
✓ Setup audit logging and tracking

'''
        
        report += f'''
SUCCESS CRITERIA
────────────────────────────────────────────────────────────────
To successfully complete this lab, you must:
'''
        
        for i, criteria in enumerate(guide['validation']['success_criteria'], 1):
            report += f"{i}. {criteria}\n"
        
        report += f'''
TIME ESTIMATE
────────────────────────────────────────────────────────────────
Estimated total time: {guide['lab_metadata']['duration']}

SUPPORT & RESOURCES
────────────────────────────────────────────────────────────────
Repository:  {context_block.repository_url}
Documentation: See repo /docs folder
Support: Skillable Labs team

════════════════════════════════════════════════════════════════
Generated by: Skillable Gen AI Lab Instructions Generator
Powered by: TechConnect Contextual Broker
════════════════════════════════════════════════════════════════
'''
        
        return report
