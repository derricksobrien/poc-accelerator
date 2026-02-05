"""
Pydantic schemas for TechConnect Contextual Broker Agent.
Matches the catalog.json structure for type-safe data handling.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class SolutionAreaEnum(str, Enum):
    """Solution area categories from the catalog."""
    AI = "AI"
    SECURITY = "Security"
    AZURE_DATA_AI = "Azure (Data & AI)"
    CLOUD_AI_PLATFORMS = "Cloud & AI Platforms"


class ComplexityLevel(str, Enum):
    """Technical complexity levels (L-scale)."""
    L200 = "L200"
    L300 = "L300"
    L400 = "L400"


class CatalogItem(BaseModel):
    """
    Core catalog item schema for solution accelerators.
    This is the structured output from Module B (Metadata Extractor).
    """
    id: str = Field(..., description="Unique identifier for the accelerator")
    name: str = Field(..., description="Display name of the solution")
    solution_area: SolutionAreaEnum = Field(..., description="Categorization of solution")
    delivery_readiness: str = Field(default="Gold Standard", description="Readiness level")
    technical_complexity: ComplexityLevel = Field(..., description="L-scale complexity (L200-L400)")
    repository_url: str = Field(..., description="GitHub repository URL")
    description: str = Field(..., description="Short description of the solution")
    products_and_services: List[str] = Field(default_factory=list, description="Azure/Microsoft services used")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    prerequisites: List[str] = Field(default_factory=list, description="Pre-requisites for deployment")
    responsible_ai_tag: bool = Field(default=False, description="Requires RAI disclaimer")
    deployment_type: str = Field(default="", description="Deployment method (e.g., Bicep/azd)")


class ContextBlock(BaseModel):
    """
    Output from Module D (Context Provider).
    Formatted context block for downstream agents.
    Includes XML tagging for token-efficient parsing.
    """
    catalog_item_id: str
    solution_name: str
    solution_area: str
    complexity_level: str
    architecture_summary: str = Field(description="Compacted description (~500 tokens)")
    prerequisites_xml: str = Field(description="<prerequisites>...</prerequisites> formatted")
    products_xml: str = Field(description="<products>...</products> formatted")
    rai_disclaimer: Optional[str] = Field(default=None, description="RAI safety disclaimer if applicable")
    repository_url: str


class CatalogMetadata(BaseModel):
    """Metadata about the catalog itself."""
    version: str
    last_updated: str
    authoritative_source: str
    governance_standard: str


class CatalogData(BaseModel):
    """Root catalog structure matching catalog.json."""
    catalog_metadata: CatalogMetadata
    solution_accelerators: List[CatalogItem]
