"""
Module A: Scraper - Data Ingestion
Processes local JSON files from catalog.json and outputs raw content metadata.
For MVP, works with catalog.json as the primary source.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from models.schemas import CatalogItem, CatalogData


class CatalogScraper:
    """
    MVP Scraper: Loads solution accelerators from catalog.json.
    In production, would fetch from GitHub API or web scraping.
    """
    
    def __init__(self, catalog_path: Path):
        """
        Initialize scraper with catalog.json path.
        
        Args:
            catalog_path: Path to catalog.json file
        """
        self.catalog_path = Path(catalog_path)
        self.catalog_data: Optional[CatalogData] = None
    
    def load_catalog(self) -> CatalogData:
        """
        Load and parse catalog.json into structured CatalogData.
        
        Returns:
            CatalogData: Parsed catalog with metadata and accelerators
            
        Raises:
            FileNotFoundError: If catalog.json not found
            ValueError: If JSON is invalid
        """
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found at {self.catalog_path}")
        
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Pydantic validation ensures schema compliance
        self.catalog_data = CatalogData(**raw_data)
        return self.catalog_data
    
    def get_accelerators(self) -> List[CatalogItem]:
        """
        Get all solution accelerators from loaded catalog.
        
        Returns:
            List[CatalogItem]: All accelerators in catalog
        """
        if not self.catalog_data:
            self.load_catalog()
        
        return self.catalog_data.solution_accelerators
    
    def get_accelerator_by_id(self, accelerator_id: str) -> Optional[CatalogItem]:
        """
        Retrieve a specific accelerator by ID.
        
        Args:
            accelerator_id: The unique ID of the accelerator
            
        Returns:
            CatalogItem or None: The matching accelerator
        """
        if not self.catalog_data:
            self.load_catalog()
        
        for accelerator in self.catalog_data.solution_accelerators:
            if accelerator.id == accelerator_id:
                return accelerator
        
        return None
    
    def search_by_area(self, solution_area: str) -> List[CatalogItem]:
        """
        Find all accelerators in a given solution area.
        
        Args:
            solution_area: Solution area to filter by (e.g., "AI")
            
        Returns:
            List[CatalogItem]: Matching accelerators
        """
        if not self.catalog_data:
            self.load_catalog()
        
        return [
            acc for acc in self.catalog_data.solution_accelerators
            if acc.solution_area == solution_area
        ]
    
    def search_by_complexity(self, complexity: str) -> List[CatalogItem]:
        """
        Find all accelerators at a specific complexity level.
        
        Args:
            complexity: Complexity level (L200, L300, L400)
            
        Returns:
            List[CatalogItem]: Matching accelerators
        """
        if not self.catalog_data:
            self.load_catalog()
        
        return [
            acc for acc in self.catalog_data.solution_accelerators
            if acc.technical_complexity == complexity
        ]
    
    def get_rai_required(self) -> List[CatalogItem]:
        """
        Get all accelerators that require RAI disclaimer.
        
        Returns:
            List[CatalogItem]: Accelerators with responsible_ai_tag=true
        """
        if not self.catalog_data:
            self.load_catalog()
        
        return [
            acc for acc in self.catalog_data.solution_accelerators
            if acc.responsible_ai_tag
        ]
