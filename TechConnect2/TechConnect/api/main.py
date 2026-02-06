"""
Module D: Context Provider - A2A Interface
FastAPI REST service that returns structured context blocks for downstream agents.
Ingests catalog, searches vector store, and formats output with XML tagging.
"""

from typing import Optional, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import textwrap

from models.schemas import ContextBlock, CatalogItem
from ingestion.scraper import CatalogScraper
from ingestion.github_crawler import GitHubRepoCrawler
from vector_store.store import VectorStore


# ============================================================================
# Request/Response Models
# ============================================================================

class ContextRequest(BaseModel):
    """Request body for context block endpoint."""
    scenario_title: str
    solution_area: Optional[str] = None
    complexity: Optional[str] = None
    num_results: int = 3


class AddRepoRequest(BaseModel):
    """Request to add a new repo to the registry."""
    repo_id: str
    name: str
    github_url: str
    solution_area: str
    technical_complexity: str
    responsible_ai_tag: bool = False


class RepoInfo(BaseModel):
    """Info about a registered repo."""
    id: str
    name: str
    github_url: str
    solution_area: str
    technical_complexity: str
    responsible_ai_tag: bool
    enabled: bool
    description: Optional[str] = None


class ContextResponse(BaseModel):
    """Response containing context blocks for agent consumption."""
    request_id: str
    blocks: List[ContextBlock]
    count: int


# ============================================================================
# Initialize FastAPI and Modules
# ============================================================================

app = FastAPI(
    title="TechConnect Contextual Broker",
    version="1.0.0",
    description="RAG system providing context blocks for instruction-generating agents"
)

# Initialize scraper and vector store (singleton pattern for MVP)
_scraper: Optional[CatalogScraper] = None
_vector_store: Optional[VectorStore] = None
_repo_crawler: Optional[GitHubRepoCrawler] = None


def get_scraper() -> CatalogScraper:
    """Lazy-load catalog scraper."""
    global _scraper
    if _scraper is None:
        # Assumes catalog.json in project root
        catalog_path = Path(__file__).parent.parent / "catalog.json"
        _scraper = CatalogScraper(catalog_path)
    return _scraper


def get_vector_store() -> VectorStore:
    """Lazy-load vector store and ingest catalog."""
    global _vector_store
    if _vector_store is None:
        # Use persistent storage in .chroma directory
        persist_dir = Path(__file__).parent.parent / ".chroma"
        _vector_store = VectorStore(persist_dir=persist_dir)
        
        # Ingest catalog if store is empty
        scraper = get_scraper()
        catalog = scraper.load_catalog()
        _vector_store.ingest_accelerators(catalog.solution_accelerators)
    
    return _vector_store


def get_repo_crawler() -> GitHubRepoCrawler:
    """Lazy-load repo crawler."""
    global _repo_crawler
    if _repo_crawler is None:
        registry_path = Path(__file__).parent.parent / "repos-registry.json"
        repos_dir = Path(__file__).parent.parent / "repos"
        _repo_crawler = GitHubRepoCrawler(str(registry_path), str(repos_dir))
    return _repo_crawler


# ============================================================================
# Utility Functions
# ============================================================================

def _compact_description(description: str, max_tokens: int = 150) -> str:
    """
    Compact description to token budget (~150 tokens ≈ 600 chars for MVP).
    
    Args:
        description: Original description
        max_tokens: Max token approximation
        
    Returns:
        Compacted description
    """
    # Rough approximation: 1 token ≈ 4 chars
    max_chars = max_tokens * 4
    
    if len(description) <= max_chars:
        return description
    
    # Truncate and add ellipsis
    return description[:max_chars].rstrip() + "..."


def _format_prerequisites_xml(prerequisites: List[str]) -> str:
    """Format prerequisites as XML for efficient downstream parsing."""
    if not prerequisites:
        return "<prerequisites />"
    
    items = "".join([f"<item>{p}</item>" for p in prerequisites])
    return f"<prerequisites>{items}</prerequisites>"


def _format_products_xml(products: List[str]) -> str:
    """Format products and services as XML."""
    if not products:
        return "<products />"
    
    items = "".join([f"<product>{p}</product>" for p in products])
    return f"<products>{items}</products>"


def _get_rai_disclaimer(responsible_ai_tag: bool, solution_area: str) -> Optional[str]:
    """Generate RAI disclaimer if required."""
    if not responsible_ai_tag or solution_area != "AI":
        return None
    
    return textwrap.dedent("""
        ⚠️ RESPONSIBLE AI DISCLAIMER (RAI):
        This AI solution must be deployed with governance guardrails including:
        - Monitoring of model outputs for bias and accuracy
        - Human review of high-impact decisions
        - Transparency about AI capabilities and limitations to end users
        - Compliance with Microsoft Responsible AI principles
    """).strip()


def _create_context_block(
    accelerator: CatalogItem,
    similarity_score: Optional[float] = None
) -> ContextBlock:
    """
    Transform a CatalogItem into a ContextBlock for agent consumption.
    Includes XML tagging and RAI disclaimers.
    
    Args:
        accelerator: The catalog item to transform
        similarity_score: Optional relevance score from vector search
        
    Returns:
        ContextBlock: Formatted context for downstream agent
    """
    block = ContextBlock(
        catalog_item_id=accelerator.id,
        solution_name=accelerator.name,
        solution_area=accelerator.solution_area,
        complexity_level=accelerator.technical_complexity,
        architecture_summary=_compact_description(accelerator.description),
        prerequisites_xml=_format_prerequisites_xml(accelerator.prerequisites),
        products_xml=_format_products_xml(accelerator.products_and_services),
        rai_disclaimer=_get_rai_disclaimer(
            accelerator.responsible_ai_tag,
            accelerator.solution_area
        ),
        repository_url=accelerator.repository_url
    )
    
    return block


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TechConnect Contextual Broker"
    }


@app.post("/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """
    Main endpoint: Return context blocks for a given scenario.
    
    Workflow:
    1. Parse request (scenario title + optional filters)
    2. Search vector store for relevant accelerators
    3. Format results as ContextBlocks with XML tagging
    4. Inject RAI disclaimers if needed
    
    Args:
        request: ContextRequest with scenario_title and optional filters
        
    Returns:
        ContextResponse: List of ContextBlock objects
    """
    try:
        vector_store = get_vector_store()
        
        # Search vector store
        search_results = vector_store.search(
            query=request.scenario_title,
            n_results=request.num_results,
            solution_area=request.solution_area,
            complexity=request.complexity
        )
        
        # If no results, return empty response
        if not search_results or not search_results['ids']:
            return ContextResponse(
                request_id=f"req_{hash(request.scenario_title)}",
                blocks=[],
                count=0
            )
        
        # Retrieve full accelerator details for context blocks
        scraper = get_scraper()
        blocks = []
        
        for accelerator_id in search_results['ids']:
            accelerator = scraper.get_accelerator_by_id(accelerator_id)
            if accelerator:
                block = _create_context_block(accelerator)
                blocks.append(block)
        
        return ContextResponse(
            request_id=f"req_{hash(request.scenario_title)}",
            blocks=blocks,
            count=len(blocks)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accelerators", response_model=List[dict])
async def list_accelerators():
    """List all accelerators in the vector store."""
    try:
        vector_store = get_vector_store()
        return vector_store.list_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accelerators/{accelerator_id}", response_model=ContextBlock)
async def get_accelerator(accelerator_id: str):
    """Retrieve a specific accelerator as a context block."""
    try:
        scraper = get_scraper()
        accelerator = scraper.get_accelerator_by_id(accelerator_id)
        
        if not accelerator:
            raise HTTPException(status_code=404, detail="Accelerator not found")
        
        return _create_context_block(accelerator)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Repo Management Endpoints
# ============================================================================

@app.get("/repos", response_model=List[RepoInfo])
async def list_repos():
    """List all registered repos in the registry."""
    try:
        crawler = get_repo_crawler()
        repos = crawler.list_repos()
        return [RepoInfo(**repo) for repo in repos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/repos", response_model=dict)
async def add_repo(request: AddRepoRequest):
    """Add a new repo to the registry."""
    try:
        crawler = get_repo_crawler()
        success = crawler.add_repo(
            repo_id=request.repo_id,
            name=request.name,
            github_url=request.github_url,
            solution_area=request.solution_area,
            complexity=request.technical_complexity,
            responsible_ai=request.responsible_ai_tag
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Repo {request.repo_id} already exists or operation failed"
            )
        
        return {
            "status": "success",
            "message": f"Repo {request.repo_id} added to registry",
            "repo_id": request.repo_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/repos/{repo_id}")
async def remove_repo(repo_id: str):
    """Remove a repo from the registry."""
    try:
        crawler = get_repo_crawler()
        success = crawler.remove_repo(repo_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Repo {repo_id} not found")
        
        return {
            "status": "success",
            "message": f"Repo {repo_id} removed from registry"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/repos/{repo_id}/clone")
async def clone_repo(repo_id: str):
    """Clone a specific repo from GitHub."""
    try:
        crawler = get_repo_crawler()
        local_path = crawler.clone_repo(repo_id)
        
        if not local_path:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to clone repo {repo_id}. Check logs for details."
            )
        
        return {
            "status": "success",
            "message": f"Repo {repo_id} cloned successfully",
            "local_path": str(local_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/repos/clone-all")
async def clone_all_repos():
    """Clone all enabled repos from the registry."""
    try:
        crawler = get_repo_crawler()
        results = crawler.clone_all_repos()
        
        successful = [repo_id for repo_id, success in results.items() if success]
        failed = [repo_id for repo_id, success in results.items() if not success]
        
        return {
            "status": "success",
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "successful_repos": successful,
            "failed_repos": failed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repos/{repo_id}/files")
async def list_repo_files(repo_id: str):
    """List all indexable files in a cloned repo."""
    try:
        crawler = get_repo_crawler()
        files = crawler.get_repo_files(repo_id)
        
        if not files:
            raise HTTPException(
                status_code=404,
                detail=f"Repo {repo_id} not found or has no indexable files"
            )
        
        return {
            "repo_id": repo_id,
            "total_files": len(files),
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repos/{repo_id}/readme")
async def get_repo_readme(repo_id: str):
    """Get README summary from a cloned repo."""
    try:
        crawler = get_repo_crawler()
        readme_content = crawler.extract_readme(repo_id)
        
        if not readme_content:
            raise HTTPException(
                status_code=404,
                detail=f"README not found for repo {repo_id}"
            )
        
        return {
            "repo_id": repo_id,
            "readme": readme_content,
            "note": "First 2000 characters of README.md"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Pre-load scraper and vector store on startup."""
    try:
        get_scraper()
        get_vector_store()
    except Exception as e:
        print(f"Warning: Could not initialize modules on startup: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
