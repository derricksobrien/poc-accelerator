#!/usr/bin/env python3
"""
System2 RAG - FastAPI Backend with Catalog Integration
Serves both the frontend web interface and REST API endpoints
Ingests real solution accelerators from catalog.json
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
from collections import Counter
from typing import List, Dict, Optional

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
catalog_file = Path(__file__).parent.parent / "catalog.json"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Load catalog from JSON
def load_catalog():
    """Load solution accelerators from catalog.json"""
    if catalog_file.exists():
        with open(catalog_file, 'r') as f:
            data = json.load(f)
            return data.get("solution_accelerators", [])
    return []

SOLUTIONS = load_catalog()

# Simple Vector Store for semantic search (TF-IDF like matching)
class VectorStore:
    def __init__(self, solutions):
        self.solutions = solutions
        self._build_index()
    
    def _build_index(self):
        """Build search index from solutions"""
        self.index = {}
        for sol in self.solutions:
            # Index key fields
            texts = [
                sol.get("name", ""),
                sol.get("description", ""),
                sol.get("solution_area", ""),
                " ".join(sol.get("key_technologies", [])),
                " ".join(sol.get("use_cases", []))
            ]
            combined_text = " ".join(texts).lower()
            words = combined_text.split()
            
            for word in set(words):
                if word and len(word) > 2:
                    if word not in self.index:
                        self.index[word] = []
                    self.index[word].append(sol["id"])
    
    def search(self, query: str, top_k: int = 5, area_filter: Optional[str] = None) -> List[Dict]:
        """Semantic search with optional area filter"""
        query_words = query.lower().split()
        scores = Counter()
        
        # Score solutions based on word matches
        for word in query_words:
            if word in self.index:
                for sol_id in self.index[word]:
                    scores[sol_id] += 1
        
        # Get solutions and apply filter
        results = []
        for sol_id, score in scores.most_common(20):
            sol = next((s for s in self.solutions if s["id"] == sol_id), None)
            if sol:
                if area_filter and sol.get("solution_area", "").lower() != area_filter.lower():
                    continue
                results.append({
                    "id": sol["id"],
                    "name": sol["name"],
                    "solution_area": sol["solution_area"],
                    "technical_complexity": sol.get("technical_complexity", "N/A"),
                    "description": sol["description"][:200] + "...",
                    "key_technologies": sol.get("key_technologies", []),
                    "relevance_score": min(0.95 + (score / 100), 1.0)
                })
        
        return results[:top_k]

# Initialize vector store
vector_store = VectorStore(SOLUTIONS)

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
    """Generate a POC based on the provided parameters using catalog data"""
    try:
        # Generate POC ID
        poc_id = f"poc-{request.poc_title.lower().replace(' ', '-')}"
        
        # Search for relevant solutions
        relevant_solutions = vector_store.search(
            request.query,
            top_k=request.top_results,
            area_filter=request.solution_area
        )
        
        # If no specific area matches, search all
        if not relevant_solutions:
            relevant_solutions = vector_store.search(request.query, top_k=request.top_results)
        
        # Build comprehensive POC proposal
        poc = {
            "poc_id": poc_id,
            "solution_area": request.solution_area,
            "poc_title": request.poc_title,
            "query": request.query,
            "status": "generated",
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_solutions": relevant_solutions,
            "instructions": f"""
# POC: {request.poc_title}
# Area: {request.solution_area}
# Query: {request.query}

## Overview
Proof of Concept for {request.solution_area}: {request.query}

## Recommended Solutions
Based on semantic search and area filtering, the following solutions are recommended:

{chr(10).join([
    f"- **{sol['name']}** ({sol['technical_complexity']}): {sol['description']}"
    for sol in relevant_solutions[:3]
])}

## Key Technologies
{chr(10).join([
    f"- {tech}"
    for tech_list in [sol.get('key_technologies', []) for sol in relevant_solutions[:3]]
    for tech in tech_list
])}

## Prerequisites
- Azure subscription with appropriate permissions
- Required Azure services configured
- Access to documentation and samples

## Architecture Approach
1. Evaluate recommended solutions
2. Select best fit for requirements
3. Deploy to development environment
4. Validate with stakeholders
5. Plan production rollout

## Next Steps
1. Review recommended solutions
2. Set up Azure resources
3. Deploy POC infrastructure
4. Execute testing plan
5. Gather feedback and iterate

## Success Criteria
✓ All endpoints responding correctly
✓ Integration with recommended solutions working
✓ Performance within acceptable thresholds
✓ Security controls in place
✓ Stakeholder approval obtained

---
Generated by System2 RAG on {datetime.utcnow().isoformat()}
            """.strip()
        }
        
        # Store in history
        poc_history.append(poc)
        
        return poc
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/rag/search")
async def search(request: SearchRequest):
    """Search for relevant solutions using semantic search"""
    try:
        # Use vector store for semantic search
        results = vector_store.search(request.query, top_k=request.top_k)
        
        # Optionally include synthesis (summary of collective insights)
        synthesis = ""
        if request.include_synthesis and results:
            technologies = set()
            areas = set()
            for result in results:
                technologies.update(result.get("key_technologies", []))
                areas.add(result.get("solution_area", ""))
            
            synthesis = f"""
Based on the search for '{request.query}', we found {len(results)} relevant solutions across {len(areas)} solution areas.

Key technologies identified: {', '.join(list(technologies)[:5])}
Solution areas: {', '.join(list(areas))}

These solutions provide a foundation for building solutions in the {request.query} space.
            """.strip()
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "synthesis": synthesis if request.include_synthesis else None,
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
    """Get list of available solutions from catalog"""
    return {
        "solutions": [
            {
                "id": sol["id"],
                "name": sol["name"],
                "solution_area": sol["solution_area"],
                "technical_complexity": sol.get("technical_complexity", "N/A"),
                "description": sol["description"][:150] + "...",
                "key_technologies": sol.get("key_technologies", [])
            }
            for sol in SOLUTIONS
        ],
        "count": len(SOLUTIONS),
        "catalog_version": "2.0.0",
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
