"""
System3-RAG Streamlit Application

Interactive POC Generator with Azure AI Foundry Agent Integration
Uses Streamlit for beautiful, reactive UI with rich productivity features
Calls FastAPI backend for agent orchestration and session management
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import os
import subprocess
from io import StringIO
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="System3-RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
def get_api_base_url():
    """Get API base URL based on environment."""
    if "localhost" in st.session_state.get("hostname", "localhost"):
        return "http://localhost:8000/api"
    else:
        # For deployed Azure, use relative path
        return "/api"

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# ============================================================================
# Session State Initialization
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "poc_history" not in st.session_state:
    st.session_state.poc_history = []

if "show_poc_results" not in st.session_state:
    st.session_state.show_poc_results = False

if "hostname" not in st.session_state:
    import socket
    st.session_state.hostname = socket.gethostname()

# ============================================================================
# Utility Functions
# ============================================================================

def make_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make HTTP request to FastAPI backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}


def create_session():
    """Create a new session."""
    try:
        response = make_request("/rag/session/create", method="POST", data={
            "metadata": {
                "created_from": "Streamlit",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        if "session_id" in response:
            st.session_state.session_id = response["session_id"]
            st.success(f"✅ New session created: {response['session_id'][:8]}...")
            return response["session_id"]
        else:
            st.error("Failed to create session")
            return None
    
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None


def export_session():
    """Export current session data."""
    if not st.session_state.session_id:
        st.warning("No active session")
        return None
    
    try:
        response = make_request(
            f"/rag/session/{st.session_state.session_id}/export",
            method="GET"
        )
        return response
    except Exception as e:
        st.error(f"Error exporting session: {str(e)}")
        return None


def generate_poc(solution_area: str, poc_title: str, query: str, top_results: int) -> Dict:
    """Generate a POC using agent."""
    if not st.session_state.session_id:
        st.warning("Creating new session...")
        create_session()
    
    try:
        response = make_request(
            f"/rag/generate-poc?session_id={st.session_state.session_id}",
            method="POST",
            data={
                "solution_area": solution_area,
                "poc_title": poc_title,
                "query": query,
                "top_results": top_results
            }
        )
        return response
    except Exception as e:
        st.error(f"Error generating POC: {str(e)}")
        return {"error": str(e)}


def search_solutions(query: str, top_k: int, include_synthesis: bool) -> Dict:
    """Search solution catalog."""
    if not st.session_state.session_id:
        st.warning("Creating new session...")
        create_session()
    
    try:
        response = make_request(
            f"/rag/search?session_id={st.session_state.session_id}",
            method="POST",
            data={
                "query": query,
                "top_k": top_k,
                "include_synthesis": include_synthesis
            }
        )
        return response
    except Exception as e:
        st.error(f"Error searching: {str(e)}")
        return {"error": str(e)}


def get_history() -> Dict:
    """Get POC generation history."""
    if not st.session_state.session_id:
        st.warning("No active session")
        return {}
    
    try:
        response = make_request(
            f"/rag/history?session_id={st.session_state.session_id}",
            method="GET"
        )
        return response
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")
        return {}


def get_system_status() -> Dict:
    """Get system status."""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"status": "unknown"}


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Session"):
            create_session()
    
    with col2:
        if st.button("💾 Export Session"):
            session_data = export_session()
            if session_data:
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(session_data, indent=2),
                    file_name=f"system3-session-{st.session_state.session_id[:8]}.json",
                    mime="application/json"
                )
    
    st.divider()
    
    st.markdown("### 📊 Session Info")
    if st.session_state.session_id:
        st.info(f"**Session ID:** `{st.session_state.session_id[:12]}...`")
        st.caption(f"POCs Generated: {len(st.session_state.poc_history)}")
    else:
        st.warning("No active session. Click 'New Session' to start.")
    
    st.divider()
    
    st.markdown("### 🔧 System Status")
    if st.button("🔍 Check Health"):
        status = get_system_status()
        if "status" in status:
            st.success("✅ System is healthy")
            with st.expander("Details"):
                st.json(status)
        else:
            st.error("❌ System status unknown")
    
    st.divider()
    
    st.markdown("### 📚 About System3-RAG")
    st.caption("""
    **Azure AI Foundry Agent-Based POC Generator**
    
    - Session-based conversation management
    - Agent-powered intelligence
    - Grounded retrieval from catalog
    - Enterprise-grade recommendations
    
    [Documentation](https://github.com/microsoft/system3-rag)
    """)


# ============================================================================
# Main Header
# ============================================================================

st.markdown(
    """
    <div style="text-align: center;">
        <h1>🤖 System3-RAG</h1>
        <p style="color: #666; font-size: 1.1em;">Azure AI Foundry Agent-Based POC Generator</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ============================================================================
# Navigation Tabs
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🚀 Generate POC", "💬 Agent Chat", "🔍 Search", "📋 History", "⚙️ Status"]
)

# ============================================================================
# Tab 1: Generate POC (Enhanced with Agent Orchestration)
# ============================================================================

from utils_enhanced import (
    display_code_with_copy,
    display_deployment_script_group,
    build_rbac_configuration,
    generate_rbac_script,
    display_iac_template_editor,
    display_cost_calculator,
    display_architecture_summary,
    display_validation_results,
    DeploymentOrchestrator
)
from agent_orchestrator import AgentOrchestrator

with tab1:
    st.header("🚀 Generate Enterprise POC")
    st.markdown("Use Azure AI Foundry Agent to orchestrate enterprise-grade POC generation with code, RBAC, IaC, and deployment automation.")
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        solution_area = st.selectbox(
            "Solution Area",
            ["AI", "Azure (Data & AI)", "Cloud & AI Platforms", "Security", "Fabric"]
        )
        
        poc_title = st.text_input("POC Title", placeholder="Enterprise AI Automation Platform")
    
    with col2:
        top_results = st.slider("Top Solutions to Consider", 1, 10, 5)
        
        complexity = st.selectbox("Complexity Level", ["L200 (Learning)", "L300 (Intermediate)", "L400 (Advanced)"])
    
    requirements = st.text_area(
        "Detailed Requirements",
        placeholder="Describe your POC requirements, constraints, team size, timeline, budget...",
        height=150
    )
    
    col_gen, col_reset = st.columns([0.8, 0.2])
    
    with col_gen:
        generate_btn = st.button("🚀 Generate POC with Multi-Tool Agent", use_container_width=True, type="primary", key="gen_poc_btn")
    
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.poc_history = []
            st.rerun()
    
    if generate_btn:
        if not requirements.strip():
            st.error("❌ Please enter detailed requirements")
        elif not poc_title.strip():
            st.error("❌ Please enter a POC title")
        else:
            with st.spinner("🤖 Agent orchestrating multi-tool workflow..."):
                try:
                    # Initialize agent orchestrator
                    from app.agent_enhanced import AzureAIFoundryAgent
                    agent = AzureAIFoundryAgent()
                    orchestrator = AgentOrchestrator(agent)
                    
                    # Create or get session
                    if not st.session_state.session_id:
                        st.session_state.session_id = agent.create_session()
                    
                    # Execute full POC generation workflow
                    result = orchestrator.orchestrate_poc_generation(
                        session_id=st.session_state.session_id,
                        poc_title=poc_title,
                        solution_area=solution_area,
                        requirements=requirements,
                        top_results=top_results
                    )
                    
                    # Store in history
                    st.session_state.poc_history.append({
                        "title": poc_title,
                        "timestamp": datetime.now(),
                        "result": result
                    })
                    
                    st.success("✅ POC Generated Successfully with Agent Orchestration!")
                    st.session_state.show_poc_results = True
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"POC generation error: {str(e)}")
    
    # Display results if available
    if st.session_state.poc_history and st.session_state.get("show_poc_results", False):
        st.divider()
        st.markdown("---")
        
        latest_poc = st.session_state.poc_history[-1]
        result = latest_poc.get("result", {})
        details = result.get("details", {})
        
        # Results navigation tabs
        result_tabs = st.tabs([
            "📚 Recommendations",
            "🔐 RBAC Configuration", 
            "🚀 Deployment Scripts",
            "🏗️ IaC Templates",
            "✅ Validation",
            "💰 Cost Estimate",
            "📋 Workflow Log"
        ])
        
        # Tab 1: Recommendations
        with result_tabs[0]:
            st.subheader("Solution Recommendations")
            
            if details.get("recommendations"):
                for i, rec in enumerate(details["recommendations"], 1):
                    with st.container(border=True):
                        col_rank, col_relevance = st.columns([0.7, 0.3])
                        
                        with col_rank:
                            st.markdown(f"### {i}. {rec.get('title', 'Solution ' + str(i))}")
                            st.markdown(f"_{rec.get('why', 'Recommended solution')}_")
                        
                        with col_relevance:
                            relevance = int(rec.get('relevance', 0.8) * 100)
                            st.metric("Match Score", f"{relevance}%")
                        
                        if rec.get('description'):
                            st.markdown(f"**Description:** {rec['description']}")
                        
                        st.divider()
            else:
                st.info("No specific recommendations generated yet")
        
        # Tab 2: RBAC Configuration
        with result_tabs[1]:
            st.subheader("RBAC Configuration")
            
            # Show generated RBAC
            if details.get("rbac_requirements"):
                for rbac in details["rbac_requirements"]:
                    with st.container(border=True):
                        st.markdown(f"**Role:** `{rbac.get('role', 'Unknown')}`")
                        st.markdown(f"**Reason:** {rbac.get('reason', 'N/A')}")
                        
                        display_code_with_copy(
                            rbac.get('scope', '/subscriptions/{SUBSCRIPTION_ID}'),
                            language="bash",
                            label="Scope"
                        )
                        st.divider()
            
            # Interactive RBAC builder
            st.markdown("---")
            if st.checkbox("💡 Customize RBAC Configuration"):
                custom_rbac = build_rbac_configuration()
                
                if st.button("📄 Generate Bicep RBAC Code"):
                    bicep_code = generate_rbac_script(custom_rbac)
                    display_code_with_copy(bicep_code, language="bicep", label="RBAC Bicep Template")
                    
                    st.download_button(
                        label="⬇️ Download RBAC Bicep",
                        data=bicep_code,
                        file_name=f"rbac_{datetime.now().strftime('%Y%m%d')}.bicep",
                        mime="text/plain"
                    )
        
        # Tab 3: Deployment Scripts
        with result_tabs[2]:
            st.subheader("Deployment Scripts")
            
            if details.get("deployment_scripts"):
                display_deployment_script_group(details["deployment_scripts"])
            else:
                st.info("No deployment scripts generated")
            
            # Deployment Orchestrator
            st.markdown("---")
            if st.checkbox("🎯 Guided Deployment with Orchestrator"):
                orchestrator_ui = DeploymentOrchestrator()
                
                # Add steps from generated scripts
                if details.get("deployment_scripts"):
                    for script_name, script_content in details["deployment_scripts"].items():
                        orchestrator_ui.add_step(
                            name=script_name.replace("-", " ").title(),
                            description=f"Execute {script_name}",
                            script=script_content
                        )
                
                orchestrator_ui.display_orchestrator()
        
        # Tab 4: IaC Templates
        with result_tabs[3]:
            st.subheader("Infrastructure-as-Code Templates")
            
            if details.get("iac_templates"):
                template_type = st.selectbox(
                    "Select Template Format",
                    ["bicep", "terraform", "arm"]
                )
                
                if template_type in details["iac_templates"]:
                    template_content = details["iac_templates"][template_type]
                    
                    display_code_with_copy(
                        template_content,
                        language="bicep" if template_type == "bicep" else template_type,
                        label=f"{template_type.upper()} Template"
                    )
                    
                    st.download_button(
                        label=f"⬇️ Download {template_type.upper()} Template",
                        data=template_content,
                        file_name=f"infrastructure_{datetime.now().strftime('%Y%m%d')}.{template_type}",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            # Template Editor
            st.markdown("---")
            if st.checkbox("✏️ Edit or Create Template"):
                selected_type = st.selectbox("Template Type", ["bicep", "terraform", "arm"])
                template_content, is_valid = display_iac_template_editor(selected_type)
        
        # Tab 5: Validation Results
        with result_tabs[4]:
            st.subheader("Architecture Validation")
            
            if details.get("validation_results"):
                display_validation_results(details["validation_results"])
            else:
                st.info("No validation results available")
        
        # Tab 6: Cost Estimate
        with result_tabs[5]:
            st.subheader("Cost Estimation")
            
            if details.get("cost_estimate"):
                cost = details["cost_estimate"]
                
                st.metric(
                    "Estimated Monthly Cost",
                    f"${cost.get('monthly_total', 0):,.2f}",
                    delta=f"${cost.get('monthly_total', 0) * 12:,.2f}/year"
                )
                
                if "breakdown" in cost:
                    st.markdown("#### Cost Breakdown")
                    breakdown = cost["breakdown"]
                    
                    cols = st.columns(len(breakdown))
                    for col, (category, amount) in zip(cols, breakdown.items()):
                        with col:
                            st.metric(category.title(), f"${amount:,.2f}")
            else:
                # Interactive cost calculator
                costs = display_cost_calculator()
        
        # Tab 7: Workflow Log
        with result_tabs[6]:
            st.subheader("Workflow Execution Log")
            
            if result.get("workflow_tasks"):
                for task in result["workflow_tasks"]:
                    with st.expander(f"✅ {task.get('step_name', 'Step')}", expanded=False):
                        st.markdown(f"**Status:** {task.get('status', 'Unknown')}")
                        
                        if task.get("message"):
                            st.markdown(f"**Agent Response:**\n{task['message'][:500]}...")
                        
                        if task.get("tools_used"):
                            st.markdown(f"**Tools Used:** {', '.join(task['tools_used'])}")
        
        # Download complete POC
        st.divider()
        st.markdown("### 📥 Download Complete POC")
        
        col_json, col_clear = st.columns([0.8, 0.2])
        
        with col_json:
            st.download_button(
                label="📥 Download as JSON",
                data=json.dumps(result, indent=2),
                file_name=f"poc-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.show_poc_results = False
                st.rerun()


# ============================================================================
# Tab 2: Agent Chat
# ============================================================================

with tab2:
    st.header("💬 Agent Chat")
    st.markdown("Have a conversation with the AI Foundry agent about solutions, architecture, and deployment.")
    
    # Display chat history
    chat_container = st.container(height=400, border=True)
    
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            st.info("💡 Start a conversation with the agent. Ask about solutions, architecture, or deployment strategies.")
    
    # Chat input
    st.divider()
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input(
            "Ask me anything...",
            placeholder="e.g., What's the best solution for enterprise AI automation?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_btn = st.button("Send 📤", use_container_width=True)
    
    if send_btn and user_input:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get agent response (mock for now)
        with st.spinner("🤖 Agent thinking..."):
            # TODO: Call agent endpoint when available
            assistant_response = f"This is a response to: {user_input}\n\nWhen connected to Azure AI Foundry, the agent will provide intelligent recommendations based on the solution catalog."
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_response
            })
        
        st.rerun()


# ============================================================================
# Tab 3: Search Solutions
# ============================================================================

with tab3:
    st.header("🔍 Search Solutions")
    st.markdown("Search the 15-solution Microsoft accelerators catalog with semantic matching.")
    
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    
    with col1:
        search_query = st.text_input("Search Query", placeholder="e.g., cloud transformation, AI automation")
    
    with col2:
        top_k = st.slider("Results to Show", 1, 10, 5, label_visibility="visible")
    
    with col3:
        include_synthesis = st.checkbox("Include Synthesis", value=True)
    
    if st.button("🔎 Search", use_container_width=True, type="primary"):
        if not search_query.strip():
            st.error("Please enter a search query")
        else:
            with st.spinner("Searching solutions..."):
                results = search_solutions(search_query, top_k, include_synthesis)
                
                if "results" in results and results["results"]:
                    st.success(f"Found {len(results['results'])} solutions")
                    
                    # Display results
                    for idx, solution in enumerate(results["results"], 1):
                        with st.expander(
                            f"{idx}. {solution['title']} ({int(solution['relevance']*100)}% match)",
                            expanded=(idx == 1)
                        ):
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Area", solution.get("solution_area", "N/A"))
                            with col_b:
                                st.metric("Level", solution.get("level", "N/A"))
                            with col_c:
                                st.metric("Match", f"{int(solution['relevance']*100)}%")
                            
                            st.markdown(solution.get("description", "No description"))
                            
                            if "url" in solution:
                                st.link_button("🔗 View Repository", solution["url"])
                    
                    # Show synthesis if available
                    if include_synthesis and "synthesis" in results and results["synthesis"]:
                        st.divider()
                        st.markdown("### 🎯 Agent Synthesis")
                        synthesis = results["synthesis"]
                        st.markdown(f"**{synthesis.get('summary', '')}**")
                        st.info(synthesis.get("recommendations", ""))
                        if "next_steps" in synthesis:
                            st.markdown("**Next Steps:**")
                            for step in synthesis["next_steps"]:
                                st.markdown(f"- {step}")
                else:
                    st.warning("No solutions found. Try a different query.")


# ============================================================================
# Tab 4: History
# ============================================================================

with tab4:
    st.header("📋 POC Generation History")
    st.markdown("View all POCs generated in this session.")
    
    if st.button("🔄 Refresh History"):
        history = get_history()
        if "poc_generations" in history:
            st.session_state.poc_history = history["poc_generations"]
    
    if st.session_state.poc_history:
        st.success(f"Total POCs Generated: {len(st.session_state.poc_history)}")
        
        for idx, poc in enumerate(st.session_state.poc_history, 1):
            # Handle both dict and POCGeneration object formats
            if isinstance(poc, dict):
                title = poc.get("title", "Untitled POC")
                poc_id = poc.get("id", "N/A")
                status = poc.get("status", "unknown")
                created_at = poc.get("created_at", "N/A")
            else:
                title = getattr(poc, "title", "Untitled POC")
                poc_id = getattr(poc, "id", "N/A")
                status = getattr(poc, "status", "unknown")
                created_at = getattr(poc, "created_at", "N/A")
            
            with st.expander(f"{idx}. {title}", expanded=False):
                col_info = st.columns([0.3, 0.3, 0.4])
                with col_info[0]:
                    st.metric("Status", status)
                with col_info[1]:
                    st.metric("Created", created_at[:10] if isinstance(created_at, str) else "N/A")
                with col_info[2]:
                    st.code(poc_id[:12] + "..." if isinstance(poc_id, str) else str(poc_id))
                
                if isinstance(poc, dict) and "result" in poc:
                    st.json(poc["result"])
    else:
        st.info("💡 No POCs generated yet. Start in the 'Generate POC' tab.")


# ============================================================================
# Tab 5: System Status
# ============================================================================

with tab5:
    st.header("⚙️ System Status")
    st.markdown("Check System3-RAG and Azure AI Foundry configurations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Check System Health", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL.replace('/api', '')}/status", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    st.success("✅ System Healthy")
                    st.json(status)
                else:
                    st.error("❌ System Unhealthy")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("🏥 Check API Endpoint", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API Responding")
                    st.json(response.json())
                else:
                    st.error("❌ API Not Responding")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    st.markdown("### 📊 System Information")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.metric("API Endpoint", API_BASE_URL.split("/api")[0])
    
    with info_col2:
        env = "Azure Cloud" if "localhost" not in API_BASE_URL else "Local Development"
        st.metric("Environment", env)
    
    with info_col3:
        st.metric("Session Active", "Yes" if st.session_state.session_id else "No")
    
    st.divider()
    
    st.markdown("### 🔐 Configuration Status")
    
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            with st.expander("Detailed Status", expanded=False):
                st.json(status)
    except:
        st.warning("Unable to fetch detailed status")


# ============================================================================
# Footer
# ============================================================================

st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;">
        <p>© 2026 System3-RAG | Azure AI Foundry Agent-Based POC Generator</p>
        <p>Powered by Streamlit, FastAPI, and Azure</p>
    </div>
    """,
    unsafe_allow_html=True
)
