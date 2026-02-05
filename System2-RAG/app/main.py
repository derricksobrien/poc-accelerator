#!/usr/bin/env python3
"""
System2 RAG - FastAPI Backend
Serves both the frontend web interface and REST API endpoints
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import random
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="System2 RAG API",
    description="Retrieval-Augmented Generation system for POC generation",
    version="1.0.0"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Pydantic models for request/response
class POCRequest(BaseModel):
    solution_area: str
    poc_title: str
    query: str
    top_results: int = 5

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    include_synthesis: bool = True

class POCResponse(BaseModel):
    poc_id: str
    solution_area: str
    poc_title: str
    status: str = "success"
    message: str = ""

# Sample data
SAMPLE_SOLUTIONS = [
    {
        "id": "azure-fabric",
        "title": "Azure Fabric Starter",
        "area": "Azure (Data & AI)",
        "description": "Build a POC that helps a customer try Microsoft Fabric and incorporate their own data"
    },
    {
        "id": "ai-automation",
        "title": "AI Automation Engine",
        "area": "AI",
        "description": "Deploy a multi-agent AI automation engine for customer workflows"
    },
    {
        "id": "content-processing",
        "title": "Content Processing Pipeline",
        "area": "Azure (Data & AI)",
        "description": "Create a content processing pipeline with Azure AI services"
    },
    {
        "id": "ai-chat",
        "title": "AI Chat with Document Search",
        "area": "AI",
        "description": "Build an AI chat application with semantic search over documents"
    },
    {
        "id": "data-governance",
        "title": "Data Governance Framework",
        "area": "Security",
        "description": "Implement data governance and security controls"
    }
]

# In-memory storage for POC history
poc_history = []

# Routes
@app.get("/")
async def root():
    """Serve the main HTML interface"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    else:
        return JSONResponse(
            {"error": "index.html not found"},
            status_code=404
        )

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "System2 RAG API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/rag/generate-poc")
async def generate_poc(request: POCRequest):
    """Generate a POC based on the provided parameters"""
    try:
        # Generate POC ID
        poc_id = f"poc-{request.poc_title.lower().replace(' ', '-')}"
        
        # Find matching solution
        matching_solution = next(
            (s for s in SAMPLE_SOLUTIONS 
             if s["area"].lower() == request.solution_area.lower()),
            None
        )
        
        if not matching_solution:
            matching_solution = SAMPLE_SOLUTIONS[0]
        
        # Create POC response
        poc = {
            "poc_id": poc_id,
            "solution_area": request.solution_area,
            "poc_title": request.poc_title,
            "query": request.query,
            "status": "generated",
            "timestamp": datetime.utcnow().isoformat(),
            "instructions": f"""
# POC: {request.poc_title}
# Area: {request.solution_area}

## Overview
Proof of Concept for {request.solution_area}: {request.query}

## Prerequisites
- Azure subscription
- Required services configured
- Access to AI services

## Architecture
Single-container deployment using Azure Container Apps.

## Deployment Steps
1. Prepare environment
2. Configure services
3. Deploy container
4. Verify functionality

## Success Criteria
- All endpoints responding (200 OK)
- Frontend loads correctly
- API calls execute successfully
- No errors in console logs

## Next Steps
- Monitor logs
- Test functionality
- Gather feedback
- Plan production deployment
            """.strip()
        }
        
        # Store in history
        poc_history.append(poc)
        
        return poc
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/rag/search")
async def search(request: SearchRequest):
    """Search for relevant solutions based on query"""
    try:
        # Filter solutions based on search query
        query_lower = request.query.lower()
        results = [
            {
                "id": s["id"],
                "title": s["title"],
                "area": s["area"],
                "description": s["description"],
                "relevance_score": 0.85 + random.random() * 0.15
            }
            for s in SAMPLE_SOLUTIONS
            if query_lower in s["title"].lower() or 
               query_lower in s["description"].lower()
        ]
        
        # Sort by relevance and limit
        results = sorted(
            results,
            key=lambda x: x["relevance_score"],
            reverse=True
        )[:request.top_k]
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rag/history")
async def get_history():
    """Get POC generation history"""
    return {
        "pocs": poc_history,
        "count": len(poc_history),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/rag/solutions")
async def get_solutions():
    """Get list of available solutions"""
    return {
        "solutions": SAMPLE_SOLUTIONS,
        "count": len(SAMPLE_SOLUTIONS),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.options("/{full_path:path}")
async def preflight(full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
