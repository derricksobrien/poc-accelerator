"""
CompositeLabGenerator: Multi-repo lab synthesis for integrated AI scenarios.

Combines instructions, architectures, and deployment steps from multiple 
accelerators to create cohesive cross-repo learning experiences.

Example:
    generator = CompositeLabGenerator(vector_store)
    lab = generator.generate_composite_lab(
        scenario_title="AI agent with governance controls",
        primary_solution_area="AI Automation",
        secondary_areas=["Governance & Security", "Data & Analytics"],
        num_repos=3
    )
"""

import json
import re
from typing import List, Dict, Optional, Any
from models.schemas import CatalogItem
from vector_store.store import VectorStore


class CompositeLabGenerator:
    """Generate labs combining instructions & assets from multiple repos."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize with vector store for repo retrieval."""
        self.vector_store = vector_store
    
    def generate_composite_lab(
        self,
        scenario_title: str,
        primary_solution_area: str,
        secondary_areas: Optional[List[str]] = None,
        num_repos: int = 2
    ) -> Dict[str, Any]:
        """
        Generate lab by combining repos across solution areas.
        
        Args:
            scenario_title: Lab title (e.g., "Build AI agent with governance")
            primary_solution_area: Main solution area for initial search
            secondary_areas: List of additional solution areas to retrieve from
            num_repos: Total number of repos to combine (default 2)
        
        Returns:
            Dict with integrated lab structure including:
            - composite_sources: List of repo IDs
            - integrated_architecture: Data flows and components
            - synthesized_instructions: LLM-generated integrated steps
            - deployment_steps: Ordered by dependencies
            - merged_assets: Combined scripts and configs
            - rai_disclaimer: Cross-system AI risks (if applicable)
        
        Raises:
            ValueError: If primary solution area returns no results
        """
        
        # 1. Retrieve context from primary solution area
        primary_context = self.vector_store.search(
            query=scenario_title,
            solution_area=primary_solution_area,
            n_results=1
        )
        
        if not primary_context or len(primary_context.get("ids", [])) == 0:
            raise ValueError(
                f"No repos found for solution area '{primary_solution_area}'. "
                f"Try: AI Automation, Data & Analytics, Governance & Security, Azure (Data & AI)"
            )
        
        primary_block = self._create_context_from_search(primary_context["ids"][0], primary_context["metadatas"][0])
        contexts = [primary_block]
        
        # 2. Retrieve contexts from secondary areas (if specified)
        if secondary_areas:
            remaining_slots = num_repos - 1
            for secondary_area in secondary_areas:
                if remaining_slots <= 0:
                    break
                
                secondary_context = self.vector_store.search(
                    query=scenario_title,
                    solution_area=secondary_area,
                    n_results=1
                )
                
                if secondary_context and len(secondary_context.get("ids", [])) > 0:
                    ctx = self._create_context_from_search(
                        secondary_context["ids"][0],
                        secondary_context["metadatas"][0]
                    )
                    contexts.append(ctx)
                    remaining_slots -= 1
        
        if len(contexts) < num_repos:
            print(
                f"⚠️  Warning: Requested {num_repos} repos, found {len(contexts)}. "
                f"Using available repos."
            )
        
        # 3. Build integrated lab structure
        lab = {
            "scenario": scenario_title,
            "composite_sources": [ctx.id for ctx in contexts],
            "source_repos": {
                ctx.id: {
                    "solution_area": ctx.solution_area,
                    "complexity": ctx.technical_complexity,
                    "description": ctx.description[:200] if hasattr(ctx, 'description') else ""
                }
                for ctx in contexts
            },
            "integrated_architecture": self._build_integrated_architecture(contexts),
            "synthesized_instructions": self._synthesize_instructions(
                scenario_title,
                contexts
            ),
            "deployment_steps": self._merge_deployment_steps(contexts),
            "merged_assets": self._merge_assets(contexts),
            "prerequisites": self._merge_prerequisites(contexts),
            "estimated_duration_hours": self._estimate_duration(contexts),
            "responsible_ai_tag": any(
                ctx.responsible_ai_tag for ctx in contexts
                if hasattr(ctx, 'responsible_ai_tag')
            ),
            "rai_disclaimer": self._get_composite_rai_disclaimer(contexts)
                if any(ctx.responsible_ai_tag for ctx in contexts if hasattr(ctx, 'responsible_ai_tag'))
                else None
        }
        
        return lab
    
    def _build_integrated_architecture(self, contexts: List[CatalogItem]) -> Dict[str, Any]:
        """Create architecture diagram showing how repos integrate."""
        
        components = []
        data_flows = []
        
        for i, ctx in enumerate(contexts):
            role = self._infer_role(ctx.solution_area)
            components.append({
                "index": i + 1,
                "repo_id": ctx.id,
                "role": role,
                "solution_area": ctx.solution_area,
                "key_services": self._extract_services(ctx),
                "layer": f"layer_{i}"
            })
            
            # Define data flows between consecutive components
            if i < len(contexts) - 1:
                data_type = self._infer_data_flow(contexts[i], contexts[i + 1])
                data_flows.append({
                    "from": contexts[i].id,
                    "to": contexts[i + 1].id,
                    "data_type": data_type,
                    "format": "JSON/API"
                })
        
        return {
            "components": components,
            "data_flows": data_flows,
            "diagram_ascii": self._render_ascii_architecture(components, data_flows),
            "integration_pattern": self._infer_integration_pattern(contexts)
        }
    
    def _synthesize_instructions(
        self,
        scenario: str,
        contexts: List[CatalogItem]
    ) -> str:
        """Generate integrated step-by-step instructions."""
        
        instructions = f"""# Integrated Lab: {scenario}

## Overview
This lab combines {len(contexts)} accelerators to build a complete solution:

"""
        
        for i, ctx in enumerate(contexts, 1):
            instructions += f"""
### {i}. {ctx.id.replace('-', ' ').title()}
**Solution Area:** {ctx.solution_area}  
**Complexity:** {ctx.technical_complexity}  
**Role in Architecture:** {self._infer_role(ctx.solution_area)}  

{ctx.description[:300] if hasattr(ctx, 'description') else 'Solution component'}
"""
        
        instructions += """

## Integration Architecture

This lab follows a multi-layer architecture:

1. **Data Layer**: Ingests and prepares data from source systems
2. **Processing Layer**: Applies AI/ML transformations or analytics
3. **Governance Layer**: Enforces compliance, auditing, and data protection policies
4. **Application Layer**: Exposes insights to end users or downstream systems

## Step-by-Step Instructions

### Phase 1: Prerequisites & Setup
- [ ] Create Azure subscription and required resources
- [ ] Configure service principal for authentication
- [ ] Set up local development environment with Python 3.10+
- [ ] Clone all required repositories

### Phase 2: Deploy Component 1 ("""

        instructions += contexts[0].id + ")\n"
        instructions += f"""- [ ] Follow deployment guide in {contexts[0].id} repository
- [ ] Configure environment variables for {self._infer_role(contexts[0].solution_area)}
- [ ] Validate component is operational
- [ ] Test core functionality

"""
        
        for ctx in contexts[1:]:
            instructions += f"""
### Phase {contexts.index(ctx) + 2}: Deploy {ctx.id.replace('-', ' ').title()}
- [ ] Follow deployment guide in {ctx.id} repository
- [ ] Establish data connection to previous component
- [ ] Configure {self._infer_role(ctx.solution_area)} settings
- [ ] Validate integration between components
"""
        
        instructions += """
### Phase Final: End-to-End Testing & Validation
- [ ] Execute full data pipeline from source to destination
- [ ] Verify all data flows match architecture diagram
- [ ] Test governance policies and audit logging
- [ ] Generate sample reports/dashboards
- [ ] Document results and lessons learned

## Data Flow

"""
        
        for flow in self._build_integrated_architecture(contexts)["data_flows"]:
            instructions += f"- **{flow['from']}** → {flow['data_type']} → **{flow['to']}**\n"
        
        instructions += """
## Success Criteria

✅ All components deployed and operational  
✅ Data flows successfully through entire pipeline  
✅ Governance policies active and auditing enabled  
✅ End-to-end test scenario completed successfully  
✅ Performance meets baseline requirements  

## Troubleshooting

See individual accelerator READMEs for component-specific troubleshooting.

## Next Steps

After completing this lab:
1. Extend with additional data sources
2. Customize business logic for your use case
3. Scale to production with monitored deployments
4. Integrate with existing enterprise systems
"""
        
        return instructions
    
    def _merge_deployment_steps(self, contexts: List[CatalogItem]) -> List[Dict[str, Any]]:
        """Order deployment steps by logical dependencies."""
        
        steps = []
        step_id = 1
        
        # Phase 1: Prerequisites
        steps.append({
            "sequence": step_id,
            "phase": "Prerequisites",
            "title": "Create Azure resources and authentication",
            "description": "Set up service principals, resource groups, and access controls",
            "commands": [
                "az group create --name tech-connect --location eastus",
                "az identity create --name techconnect-identity --resource-group tech-connect"
            ],
            "estimated_minutes": 10,
            "depends_on": []
        })
        step_id += 1
        
        # Phase 2+: Deploy each component
        prev_step = 1
        for i, ctx in enumerate(contexts):
            steps.append({
                "sequence": step_id,
                "phase": f"Deploy Component {i+1}",
                "title": f"Deploy {ctx.id}",
                "description": f"Follow {ctx.id} deployment guide",
                "repo_source": ctx.id,
                "commands": [
                    f"cd repos/{ctx.id}",
                    "az deployment group create --template-file main.bicep --resource-group tech-connect"
                ],
                "estimated_minutes": 20,
                "depends_on": [prev_step]
            })
            prev_step = step_id
            step_id += 1
        
        # Phase Final: Integration testing
        steps.append({
            "sequence": step_id,
            "phase": "Integration",
            "title": "Validate end-to-end data flow",
            "description": "Test pipeline from source through all components",
            "commands": [
                "python test_integration.py",
                "pytest --verbose"
            ],
            "estimated_minutes": 15,
            "depends_on": [prev_step]
        })
        
        return steps
    
    def _merge_assets(self, contexts: List[CatalogItem]) -> Dict[str, Any]:
        """Combine deployment scripts and configs from repos."""
        
        merged = {
            "deployment_scripts": [],
            "configuration_templates": [],
            "sample_code_languages": [],
            "integration_points": []
        }
        
        for i, ctx in enumerate(contexts):
            merged["deployment_scripts"].append({
                "repo": ctx.id,
                "script_name": f"{ctx.id}_deploy.sh",
                "execution_order": i + 1,
                "description": f"Deploy {ctx.id} component"
            })
            
            merged["configuration_templates"].append({
                "repo": ctx.id,
                "template_type": "bicep" if i == 0 else "terraform",
                "file_name": f"{ctx.id}_deploy.bicep" if i == 0 else f"{ctx.id}_deploy.tf",
                "description": f"IaC template for {ctx.id}"
            })
            
            merged["sample_code_languages"].extend([
                {"repo": ctx.id, "language": "python", "file": "main.py"},
                {"repo": ctx.id, "language": "typescript", "file": "index.ts"}
            ])
        
        # Define integration points between consecutive repos
        for i in range(len(contexts) - 1):
            merged["integration_points"].append({
                "from_repo": contexts[i].id,
                "to_repo": contexts[i + 1].id,
                "connection_type": "API" if i == 0 else "Event Hub",
                "protocol": "HTTPS",
                "authentication": "Service Principal"
            })
        
        return merged
    
    def _merge_prerequisites(self, contexts: List[CatalogItem]) -> List[str]:
        """Combine and deduplicate prerequisites from multiple repos."""
        
        all_prerequisites = set()
        
        # Add common prerequisites
        common_prereqs = [
            "Azure subscription with Contributor role",
            "Azure CLI (version 2.40+)",
            "Python 3.10+",
            "Git (version 2.30+)",
            "Visual Studio Code or IDE of choice",
            "GitHub account"
        ]
        all_prerequisites.update(common_prereqs)
        
        # Add repo-specific prerequisites
        for ctx in contexts:
            if hasattr(ctx, 'prerequisites') and ctx.prerequisites:
                all_prerequisites.update(ctx.prerequisites)
            
            # Infer prerequisites from solution area
            if "Data" in ctx.solution_area:
                all_prerequisites.update([
                    "Understanding of data warehousing concepts",
                    "Familiarity with SQL queries",
                    "Azure Synapse or Fabric knowledge"
                ])
            
            if "AI" in ctx.solution_area:
                all_prerequisites.update([
                    "Basic understanding of LLMs and embeddings",
                    "OpenAI API key or Azure OpenAI resource",
                    "Knowledge of vector databases"
                ])
            
            if "Governance" in ctx.solution_area or "Security" in ctx.solution_area:
                all_prerequisites.update([
                    "Understanding of compliance frameworks",
                    "Knowledge of data governance tools",
                    "Familiarity with audit logging"
                ])
        
        return sorted(list(all_prerequisites))
    
    def _estimate_duration(self, contexts: List[CatalogItem]) -> float:
        """Estimate total lab duration based on complexity."""
        
        # Base: 1.5 hours per L200, 2 hours per L300, 3 hours per L400
        complexity_hours = {
            "L200": 1.5,
            "L300": 2.0,
            "L400": 3.0
        }
        
        base_hours = sum([
            complexity_hours.get(ctx.technical_complexity, 2.0)
            for ctx in contexts
        ])
        
        # Add integration time (45 mins per additional repo after first)
        integration_hours = (len(contexts) - 1) * 0.75
        
        return round(base_hours + integration_hours, 1)
    
    def _get_composite_rai_disclaimer(self, contexts: List[CatalogItem]) -> str:
        """Generate RAI disclaimer for integrated AI system."""
        
        ai_repos = [
            ctx for ctx in contexts
            if hasattr(ctx, 'responsible_ai_tag') and ctx.responsible_ai_tag
        ]
        
        if not ai_repos:
            return None
        
        disclaimer = """
⚠️ **RESPONSIBLE AI NOTICE - INTEGRATED SYSTEM**

This lab combines multiple accelerators, including AI/ML components. 
Critical governance considerations:

**Component-Level Risks:**
"""
        
        for repo in ai_repos:
            disclaimer += f"""
• **{repo.id}**: 
  - Ensure input data quality before LLM processing
  - Monitor model outputs for hallucinations or bias
  - Implement comprehensive audit logging for all AI decisions
  - Set up alerts for unusual prompt patterns
"""
        
        disclaimer += """

**Cross-System Risks:**
• **Data Isolation**: Data flowing between components may leak sensitive information
  → Action: Implement encryption in transit (TLS 1.3) and at rest (AES-256)

• **Governance Ordering**: Deploy governance/Purview BEFORE AI components go live
  → Action: Configure DSPM for AI and data loss prevention policies first

• **Audit Trail**: Ensure end-to-end lineage tracking across all components
  → Action: Enable audit logging in Purview and AI services

• **Access Control**: Verify service principals have least-privilege permissions
  → Action: Review RBAC assignments regularly using Azure Policies

**Compliance Checklist:**
□ Data residency meets regulatory requirements
□ Audit logging enabled and monitored
□ Encryption configured for data in motion and at rest
□ Access controls follow principle of least privilege
□ Regular penetration testing scheduled
□ Incident response plan documented

**References:**
• Microsoft Responsible AI: https://learn.microsoft.com/en-us/ai/responsible-ai/
• Azure Security Best Practices: https://learn.microsoft.com/en-us/azure/security/
• DSPM for AI: https://learn.microsoft.com/en-us/defender-for-cloud/dspm-for-ai
"""
        
        return disclaimer.strip()
    
    # ==================== Helper Methods ====================
    
    def _create_context_from_search(self, doc_id: str, metadata: dict) -> Any:
        """Convert search result to CatalogItem-like object."""
        class MockContext:
            def __init__(self, doc_id, metadata):
                self.id = doc_id
                self.solution_area = metadata.get("solution_area", "Unknown")
                self.technical_complexity = metadata.get("technical_complexity", "L300")
                self.description = f"Solution accelerator for {self.solution_area}"
                self.responsible_ai_tag = metadata.get("responsible_ai_tag", "False") == "True"
                self.prerequisites = []
                self.github_url = metadata.get("repository_url", "")
        
        return MockContext(doc_id, metadata)
    
    def _infer_role(self, solution_area: str) -> str:
        """Map solution area to architectural role."""
        role_mapping = {
            "AI": "AI/ML Processing",
            "AI Automation": "AI/ML Processing",
            "Data": "Data Foundation",
            "Data & Analytics": "Data & Analytics",
            "Azure (Data & AI)": "Data & Analytics",
            "Governance & Security": "Compliance & Guardrails",
            "Governance": "Compliance & Guardrails",
            "Security": "Security Controls"
        }
        return role_mapping.get(solution_area, "Utility Service")
    
    def _extract_services(self, ctx: CatalogItem) -> List[str]:
        """Extract Azure service names from repo metadata."""
        service_keywords = [
            "Azure AI", "OpenAI", "Cosmos DB", "Synapse", "Fabric",
            "Purview", "App Service", "Container Apps", "AI Search",
            "Document Intelligence", "Semantic Kernel", "Agent Service",
            "OneLake", "Azure SQL", "Key Vault"
        ]
        
        desc = (ctx.description if hasattr(ctx, 'description') else "") + \
               (ctx.id.replace('-', ' '))
        
        services = [kw for kw in service_keywords if kw.lower() in desc.lower()]
        return list(set(services))[:5]  # Top 5 unique services
    
    def _infer_data_flow(
        self,
        from_ctx: CatalogItem,
        to_ctx: CatalogItem
    ) -> str:
        """Infer data connection between repos."""
        from_area = from_ctx.solution_area.lower()
        to_area = to_ctx.solution_area.lower()
        
        if "data" in from_area and "ai" in to_area:
            return "Raw Data → Vectorized Features"
        elif "ai" in from_area and ("governance" in to_area or "security" in to_area):
            return "LLM Outputs → Audit Logs"
        elif "content" in from_ctx.id and "ai" in to_area:
            return "Extracted Entities → AI Processing"
        elif "data" in from_area and "data" in to_area:
            return "Raw Data → Processed Data"
        else:
            return "Processed Data → Downstream System"
    
    def _render_ascii_architecture(
        self,
        components: List[Dict],
        flows: List[Dict]
    ) -> str:
        """Create ASCII diagram of integrated architecture."""
        if not components:
            return ""
        
        lines = []
        
        for i, comp in enumerate(components):
            # Component box
            box_width = 30
            name = comp["repo_id"][:27]
            role = comp["role"][:24]
            
            lines.append("┌─" + "─" * (box_width - 2) + "┐")
            lines.append(f"│ {name:<{box_width - 2}} │")
            lines.append(f"│ ({role:<{box_width - 4}}) │")
            lines.append("└─" + "─" * (box_width - 2) + "┘")
            
            # Data flow arrow
            if i < len(components) - 1:
                flow = flows[i] if i < len(flows) else {}
                flow_type = flow.get("data_type", "Data")[:20]
                lines.append(f"        │")
                lines.append(f"        │ {flow_type}")
                lines.append(f"        ▼")
        
        return "\n".join(lines)
    
    def _infer_integration_pattern(self, contexts: List[CatalogItem]) -> str:
        """Describe the overall integration pattern."""
        if len(contexts) == 1:
            return "Single Component"
        elif len(contexts) == 2:
            return "Two-Tier Architecture"
        elif len(contexts) <= 4:
            return "Multi-Tier Pipeline"
        else:
            return "Complex Microservices Architecture"
