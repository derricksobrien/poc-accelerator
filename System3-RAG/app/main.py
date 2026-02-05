"""
System3-RAG: FastAPI Backend with Azure AI Foundry Agent Integration

Serves:
- Static frontend (HTML/CSS/JS)
- REST API for POC generation with agent intelligence
- Session management
- Health checks for container orchestration
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.session import (
    get_session_manager,
    SessionManager,
    POCGeneration,
    POCStatus,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class POCRequest(BaseModel):
    """Request to generate a POC."""
    solution_area: str
    poc_title: str
    query: str
    top_results: int = 5


class SearchRequest(BaseModel):
    """Search request."""
    query: str
    top_k: int = 3
    include_synthesis: bool = True


class ChatMessage(BaseModel):
    """Chat message for agent conversation."""
    session_id: str
    content: str
    user_id: Optional[str] = None


class SessionRequest(BaseModel):
    """Request to create a session."""
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Startup/Shutdown Handlers
# ============================================================================

session_manager: Optional[SessionManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app lifecycle.
    
    - On startup: Initialize session manager
    - On shutdown: Cleanup expired sessions
    """
    global session_manager
    
    # Startup
    logger.info("Starting System3-RAG...")
    session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    session_manager = get_session_manager(session_timeout_minutes)
    logger.info("Session manager initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down System3-RAG...")
    if session_manager:
        session_manager.cleanup_expired_sessions()
    logger.info("Cleanup complete")


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="System3-RAG",
    description="Azure AI Foundry Agent-Based POC Generator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from {static_dir}")


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "System3-RAG",
        "version": "1.0.0",
    }


@app.get("/status")
async def status():
    """Get system status and statistics."""
    if not session_manager:
        return {"error": "Session manager not initialized"}
    
    stats = session_manager.get_statistics()
    return {
        "service": "System3-RAG",
        "status": "running",
        "sessions": stats,
        "agent_configured": _is_agent_configured(),
    }


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/api/rag/session/create")
async def create_session(request: SessionRequest):
    """Create a new conversation session."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    session = session_manager.create_session(
        user_id=request.user_id,
        metadata=request.metadata,
    )
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "user_id": session.user_id,
    }


@app.get("/api/rag/session/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    if not session_manager.validate_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = session_manager.get_session(session_id)
    return session.to_dict()


@app.get("/api/rag/session/{session_id}/export")
async def export_session(session_id: str):
    """Export session data."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    data = session_manager.export_session(
        session_id,
        include_messages=True,
        include_poc_details=True,
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return data


@app.delete("/api/rag/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted"}


# ============================================================================
# RAG Endpoints
# ============================================================================

@app.post("/api/rag/generate-poc")
async def generate_poc(request: POCRequest, session_id: Optional[str] = None):
    """
    Generate a CSA-level POC using agent intelligence.
    
    This would call the Azure AI Foundry agent to:
    1. Search the solution catalog
    2. Generate RBAC requirements
    3. Generate deployment scripts
    4. Generate IaC templates
    5. Provide architecture recommendations
    """
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    # Use or create session
    if session_id:
        if not session_manager.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session expired")
        session = session_manager.get_session(session_id)
    else:
        session = session_manager.create_session()
    
    # Create POC record
    poc = POCGeneration(
        title=request.poc_title,
        query=request.query,
        solution_area=request.solution_area,
        status=POCStatus.IN_PROGRESS,
    )
    session.add_poc_generation(poc)
    
    try:
        # TODO: Call Azure AI Foundry agent
        # For now, return mock response
        poc_result = {
            "poc_id": poc.id,
            "title": request.poc_title,
            "solution_area": request.solution_area,
            "query": request.query,
            "recommendations": [
                {
                    "solution": "Multi-Agent Automation",
                    "relevance": 0.95,
                    "why": "Matches enterprise automation requirements"
                },
                {
                    "solution": "Semantic Kernel",
                    "relevance": 0.87,
                    "why": "Excellent for orchestrating AI agents"
                }
            ],
            "rbac_requirements": [
                {
                    "role": "Owner",
                    "scope": "/subscriptions/{sub-id}/resourceGroups/{rg}",
                    "responsibilities": ["Full resource management"]
                },
                {
                    "role": "Contributor",
                    "scope": "/subscriptions/{sub-id}/resourceGroups/{rg}",
                    "responsibilities": ["Resource deployment and configuration"]
                }
            ],
            "deployment_script": """
# Azure CLI deployment for multi-agent system
az group create --name ${RG_NAME} --location ${LOCATION}
az containerapp env create --name ${ENV_NAME} --resource-group ${RG_NAME}
# ... more commands ...
            """.strip(),
            "iac_template": {
                "language": "bicep",
                "resources": [
                    "Container Apps Environment",
                    "Cosmos DB (state management)",
                    "Azure AI Search (semantic search)",
                    "Azure OpenAI (orchestration)"
                ]
            },
            "architecture_summary": "Deploy multi-agent system on Azure Container Apps with semantic search for orchestration",
            "estimated_setup_time_hours": 4,
            "cost_estimate": "$500-1000/month",
        }
        
        poc.status = POCStatus.COMPLETED
        poc.result = poc_result
        
        return {
            "session_id": session.session_id,
            "poc": poc.to_dict(),
            "details": poc_result,
        }
        
    except Exception as e:
        logger.error(f"Error generating POC: {e}")
        poc.status = POCStatus.FAILED
        poc.error = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate POC: {str(e)}"
        )


@app.post("/api/rag/search")
async def search(request: SearchRequest, session_id: Optional[str] = None):
    """
    Search solution catalog and get recommendations.
    
    Returns top matching solutions with agent synthesis if requested.
    """
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    # Use or create session
    if session_id:
        if not session_manager.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session expired")
        session = session_manager.get_session(session_id)
    else:
        session = session_manager.create_session()
    
    try:
        # TODO: Implement semantic search using System2's vector store
        # For now, return mock search results
        results = [
            {
                "id": "multi-agent-automation",
                "title": "Multi-Agent Automation",
                "solution_area": "AI",
                "level": "L400",
                "relevance": 0.95,
                "description": "Orchestrate multiple AI agents for complex task automation",
                "url": "https://github.com/microsoft/solution-accelerators"
            },
            {
                "id": "semantic-kernel",
                "title": "Semantic Kernel",
                "solution_area": "AI",
                "level": "L300",
                "relevance": 0.87,
                "description": "SDK for building AI agents with composable plugins",
                "url": "https://github.com/microsoft/semantic-kernel"
            }
        ]
        
        # Add agent synthesis if requested
        synthesis = None
        if request.include_synthesis:
            synthesis = {
                "summary": f"Found {len(results)} relevant solutions for: {request.query}",
                "recommendations": "For enterprise automation, start with Multi-Agent Automation pattern",
                "next_steps": ["Review architecture", "Plan RBAC", "Generate deployment scripts"]
            }
        
        return {
            "session_id": session.session_id,
            "query": request.query,
            "results": results,
            "synthesis": synthesis,
        }
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/solutions")
async def list_solutions():
    """List all available solutions in the catalog."""
    try:
        # TODO: Load from System2's catalog.json
        # For now return mock data
        return {
            "total": 15,
            "solutions": [
                {
                    "id": "multi-agent-automation",
                    "name": "Multi-Agent Automation",
                    "area": "AI",
                    "level": "L400",
                },
                {
                    "id": "semantic-kernel",
                    "name": "Semantic Kernel",
                    "area": "AI",
                    "level": "L300",
                },
                # ... more solutions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/history")
async def get_history(session_id: str):
    """Get POC generation history for a session."""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not available")
    
    if not session_manager.validate_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = session_manager.get_session(session_id)
    return {
        "session_id": session.session_id,
        "total_poc_generations": len(session.poc_generations),
        "poc_generations": [poc.to_dict() for poc in session.poc_generations],
    }


# ============================================================================
# Frontend Routes
# ============================================================================

@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "System3-RAG running",
        "docs": "/docs",
        "api": "/api"
    }


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """
    Catch all routes and serve static files or index.html for SPA routing.
    """
    # Try to serve static file
    file_path = static_dir / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Fall back to index.html for SPA routing
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Default response
    return {"error": "Not found"}


# ============================================================================
# Helper Functions
# ============================================================================

def _is_agent_configured() -> bool:
    """Check if Azure AI Foundry agent is configured."""
    required_vars = [
        "AZURE_AI_FOUNDRY_ENDPOINT",
        "AZURE_AI_FOUNDRY_AGENT_ID",
    ]
    
    # API key or managed identity must be available
    has_auth = (
        os.getenv("AZURE_AI_FOUNDRY_KEY") or
        _has_managed_identity()
    )
    
    return all(os.getenv(var) for var in required_vars) and has_auth


def _has_managed_identity() -> bool:
    """Check if running with Azure Managed Identity."""
    # In Azure Container Apps, MSI is available via environment
    return "AZURE_TENANT_ID" in os.environ or "IDENTITY_ENDPOINT" in os.environ


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting System3-RAG on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "development") == "development",
    )
