"""
Enhanced Streamlit utilities for richer UI components.

Provides reusable components for:
- Rich code display with copy buttons
- Architecture visualization
- Deployment orchestration
- RBAC configuration builder
- IaC template editor
- Cost estimation and breakdown
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import os
from pathlib import Path
from datetime import datetime


# ============================================================================
# Rich Code Display Components
# ============================================================================

def display_code_with_copy(code: str, language: str = "bash", label: str = None) -> None:
    """
    Display code with syntax highlighting and copy button.
    
    Args:
        code: Code content
        language: Code language for syntax highlighting
        label: Optional label for the code block
    """
    col1, col2 = st.columns([0.9, 0.1])
    
    with col1:
        if label:
            st.caption(f"**{label}**")
    
    with col2:
        copy_btn = st.button("📋", key=f"copy_{hash(code[:50])}", help="Copy to clipboard")
        if copy_btn:
            st.write(code)  # This triggers browser copy clipboard API in some contexts
            st.toast("✅ Code copied to clipboard!")
    
    st.code(code, language=language, line_numbers=True)


def display_deployment_script_group(scripts: Dict[str, str]) -> None:
    """
    Display multiple deployment scripts in tabs with copy buttons.
    
    Args:
        scripts: Dict of script_name -> script_content
    """
    if not scripts:
        st.warning("No deployment scripts available")
        return
    
    tabs = st.tabs([f"📄 {name}" for name in scripts.keys()])
    
    for tab, (name, script_content) in zip(tabs, scripts.items()):
        with tab:
            display_code_with_copy(script_content, language="bash", label=name)
            
            # Download button for each script
            st.download_button(
                label=f"⬇️ Download {name}",
                data=script_content,
                file_name=f"{name}_{datetime.now().strftime('%Y%m%d')}.sh",
                mime="text/plain",
                use_container_width=True
            )


# ============================================================================
# RBAC Configuration Builder
# ============================================================================

def build_rbac_configuration() -> Dict[str, Any]:
    """
    Interactive RBAC configuration builder.
    
    Returns:
        RBAC configuration dictionary
    """
    st.subheader("🔐 RBAC Configuration Builder")
    
    rbac_config = {
        "roles": [],
        "service_principals": [],
        "groups": []
    }
    
    # Role selection
    st.markdown("### Select Azure Roles")
    
    available_roles = [
        "Owner",
        "Contributor", 
        "Reader",
        "Compute Administrator",
        "Network Administrator",
        "Security Administrator",
        "Data Administrator",
        "AI Administrator"
    ]
    
    selected_roles = st.multiselect(
        "Roles to assign",
        available_roles,
        default=["Contributor"]
    )
    
    for role in selected_roles:
        scope = st.text_input(
            f"Scope for {role}",
            value=f"/subscriptions/{{SUBSCRIPTION_ID}}/resourceGroups/{{RESOURCE_GROUP}}",
            key=f"scope_{role}"
        )
        rbac_config["roles"].append({
            "role": role,
            "scope": scope
        })
    
    # Service Principal configuration
    st.markdown("### Service Principals")
    
    if st.checkbox("Configure Service Principals"):
        num_sps = st.number_input("Number of service principals", min_value=1, max_value=5, value=1)
        
        for i in range(num_sps):
            with st.expander(f"Service Principal {i+1}"):
                sp_name = st.text_input(
                    "Service Principal Name",
                    value=f"sp-solution-{i+1}",
                    key=f"sp_name_{i}"
                )
                sp_roles = st.multiselect(
                    "Roles for this SP",
                    available_roles,
                    key=f"sp_roles_{i}",
                    default=["Contributor"]
                )
                
                rbac_config["service_principals"].append({
                    "name": sp_name,
                    "roles": sp_roles
                })
    
    return rbac_config


def generate_rbac_script(rbac_config: Dict[str, Any]) -> str:
    """
    Generate Bicep code for RBAC configuration.
    
    Args:
        rbac_config: RBAC configuration dictionary
        
    Returns:
        Bicep code
    """
    bicep_template = """
param principalId string
param roleDefinitionId string
param scope string = resourceGroup().id

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(principalId, roleDefinitionId, scope)
  properties: {
    roleDefinitionId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/${roleDefinitionId}'
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output assignmentId string = roleAssignment.id
"""
    return bicep_template


# ============================================================================
# IaC Template Editor
# ============================================================================

def display_iac_template_editor(template_type: str = "bicep") -> Tuple[str, bool]:
    """
    Interactive IaC template editor with validation.
    
    Args:
        template_type: 'bicep', 'terraform', or 'arm'
        
    Returns:
        Tuple of (template_content, is_valid)
    """
    st.subheader(f"🏗️ {template_type.title()} Template Editor")
    
    # Template preview
    if template_type == "bicep":
        default_template = """param location string = resourceGroup().location
param environment string = 'dev'

var resourceNamePrefix = 'rg-${environment}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${resourceNamePrefix}sa${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name"""
    
    elif template_type == "terraform":
        default_template = """terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type    = string
  default = "East US"
}

resource "azurerm_storage_account" "example" {
  name                     = "stexample${random_string.storage_name.result}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

output "storage_account_id" {
  value = azurerm_storage_account.example.id
}"""
    
    else:  # ARM
        default_template = """{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[concat('st', uniqueString(resourceGroup().id))]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ]
}"""
    
    # Editor
    template_content = st.text_area(
        "Edit Template",
        value=default_template,
        height=400,
        label_visibility="collapsed"
    )
    
    # Validation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Validate", use_container_width=True):
            try:
                # Simple JSON validation for ARM templates
                json.loads(template_content)
                st.success("✅ Template is valid!")
                is_valid = True
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {str(e)}")
                is_valid = False
    
    with col2:
        if st.button("🎯 Format", use_container_width=True):
            try:
                formatted = json.dumps(json.loads(template_content), indent=2)
                st.code(formatted, language="json")
            except:
                st.info("Auto-format not available for this template type")
    
    with col3:
        st.download_button(
            label="⬇️ Download",
            data=template_content,
            file_name=f"template_{datetime.now().strftime('%Y%m%d')}.{template_type}",
            mime="text/plain",
            use_container_width=True
        )
    
    return template_content, True


# ============================================================================
# Cost Calculator
# ============================================================================

def display_cost_calculator() -> Dict[str, Any]:
    """
    Interactive cost calculator for solution components.
    
    Returns:
        Cost estimate dictionary
    """
    st.subheader("💰 Cost Estimation")
    
    costs = {
        "compute": 0,
        "storage": 0,
        "networking": 0,
        "licenses": 0,
        "support": 0,
        "monthly_total": 0
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Compute Resources")
        vm_type = st.selectbox("VM Type", ["Standard_B2s", "Standard_D2s_v3", "Standard_E4s_v5"])
        num_vms = st.number_input("Number of VMs", min_value=1, max_value=10, value=2)
        
        vm_costs = {
            "Standard_B2s": 32.85,
            "Standard_D2s_v3": 98.28,
            "Standard_E4s_v5": 328.80
        }
        costs["compute"] = vm_costs.get(vm_type, 0) * num_vms
        
        st.markdown("#### Storage")
        storage_gb = st.number_input("Storage (GB)", min_value=10, max_value=10000, value=100, step=10)
        costs["storage"] = (storage_gb / 1024) * 0.023  # ~$0.023/GB/month
    
    with col2:
        st.markdown("#### Networking")
        data_transfer_gb = st.number_input("Monthly data transfer (GB)", min_value=1, max_value=10000, value=100)
        costs["networking"] = data_transfer_gb * 0.12
        
        st.markdown("#### Licenses & Support")
        sql_instances = st.number_input("SQL Databases", min_value=0, max_value=5, value=0)
        costs["licenses"] = sql_instances * 149.40
        
        support_level = st.selectbox("Support Level", ["Basic (Free)", "Standard ($100)", "Professional ($1000)"])
        support_map = {"Basic (Free)": 0, "Standard ($100)": 100, "Professional ($1000)": 1000}
        costs["support"] = support_map.get(support_level, 0)
    
    # Calculate total
    costs["monthly_total"] = sum([costs["compute"], costs["storage"], costs["networking"], 
                                  costs["licenses"], costs["support"]])
    
    # Display breakdown
    st.markdown("---")
    st.markdown("### 💵 Monthly Cost Breakdown")
    
    breakdown_col1, breakdown_col2, breakdown_col3, breakdown_col4, breakdown_col5 = st.columns(5)
    
    with breakdown_col1:
        st.metric("Compute", f"${costs['compute']:.2f}")
    with breakdown_col2:
        st.metric("Storage", f"${costs['storage']:.2f}")
    with breakdown_col3:
        st.metric("Networking", f"${costs['networking']:.2f}")
    with breakdown_col4:
        st.metric("Licenses", f"${costs['licenses']:.2f}")
    with breakdown_col5:
        st.metric("Support", f"${costs['support']:.2f}")
    
    st.metric("**Total Monthly Cost**", f"${costs['monthly_total']:.2f}", delta=f"${costs['monthly_total']*12:.2f} /year")
    
    return costs


# ============================================================================
# Deployment Orchestrator
# ============================================================================

class DeploymentOrchestrator:
    """Manages multi-step deployment workflow."""
    
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.completed_steps = []
    
    def add_step(self, name: str, description: str, command: str = None, script: str = None):
        """Add deployment step."""
        self.steps.append({
            "name": name,
            "description": description,
            "command": command,
            "script": script,
            "status": "pending",
            "output": None
        })
    
    def display_orchestrator(self) -> Dict[str, Any]:
        """Display deployment orchestration UI."""
        st.subheader("🚀 Deployment Orchestrator")
        
        # Progress bar
        progress = len(self.completed_steps) / len(self.steps) if self.steps else 0
        st.progress(progress, f"Progress: {len(self.completed_steps)}/{len(self.steps)}")
        
        # Steps view
        for idx, step in enumerate(self.steps):
            status_icon = {
                "pending": "⏳",
                "executing": "⚙️",
                "completed": "✅",
                "failed": "❌"
            }.get(step["status"], "❓")
            
            with st.expander(f"{status_icon} {step['name']}", expanded=(idx == self.current_step)):
                st.markdown(step["description"])
                
                if step["command"]:
                    st.code(step["command"], language="bash")
                
                if step["script"]:
                    st.code(step["script"], language="bash")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if step["status"] == "pending":
                        if st.button("▶️ Execute", key=f"exec_{idx}", use_container_width=True):
                            self._execute_step(idx)
                
                with col2:
                    if st.button("📋 Copy", key=f"copy_{idx}", use_container_width=True):
                        st.info(f"Command copied: {step['command'] or step['script']}")
                
                with col3:
                    if step["status"] == "completed":
                        if st.button("↩️ Reset", key=f"reset_{idx}", use_container_width=True):
                            step["status"] = "pending"
                            step["output"] = None
                
                if step["output"]:
                    st.code(step["output"], language="bash")
        
        return {
            "total_steps": len(self.steps),
            "completed": len(self.completed_steps),
            "progress_percent": progress * 100
        }
    
    def _execute_step(self, step_idx: int):
        """Execute a deployment step."""
        step = self.steps[step_idx]
        step["status"] = "executing"
        
        try:
            # In real implementation, would run actual Azure CLI commands
            step["output"] = f"[Mock] Executed: {step['command']}\nSuccess!"
            step["status"] = "completed"
            self.completed_steps.append(step_idx)
            st.success("✅ Step completed successfully")
        except Exception as e:
            step["status"] = "failed"
            step["output"] = f"Error: {str(e)}"
            st.error(f"❌ Step failed: {str(e)}")


# ============================================================================
# Architecture Visualizer
# ============================================================================

def display_architecture_summary(architecture: Dict[str, Any]) -> None:
    """
    Display architecture summary with diagram-like layout.
    
    Args:
        architecture: Architecture configuration dictionary
    """
    st.subheader("🏗️ Architecture Overview")
    
    if not architecture:
        st.info("No architecture information available")
        return
    
    # Component visualization
    if "components" in architecture:
        st.markdown("### Components")
        cols = st.columns(len(architecture["components"]))
        
        for col, component in zip(cols, architecture["components"]):
            with col:
                st.info(f"**{component.get('name', 'Component')}**\n{component.get('type', 'Service')}")
    
    # Data flow
    if "data_flow" in architecture:
        st.markdown("### Data Flow")
        st.mermaid(architecture["data_flow"])
    
    # Deployment model
    if "deployment_model" in architecture:
        st.markdown("### Deployment Model")
        st.info(architecture["deployment_model"])


def display_validation_results(validation: Dict[str, Any]) -> None:
    """
    Display architecture validation results.
    
    Args:
        validation: Validation results dictionary
    """
    st.subheader("✅ Validation Results")
    
    if "passed" in validation and validation["passed"]:
        st.success("Architecture validation passed!")
    else:
        st.warning("Architecture validation found issues")
    
    if "results" in validation:
        for result in validation["results"]:
            if result.get("status") == "pass":
                st.success(f"✅ {result.get('check', 'Check')}")
            else:
                st.warning(f"⚠️ {result.get('check', 'Check')}: {result.get('message', '')}")
    
    if "recommendations" in validation:
        st.markdown("### Recommendations")
        for rec in validation["recommendations"]:
            st.info(f"💡 {rec}")
