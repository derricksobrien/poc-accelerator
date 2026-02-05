"""
Ingest cloned GitHub repos into the vector store
Extracts README, key files, and metadata for indexing
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from ingestion.github_crawler import GitHubRepoCrawler
from models.schemas import CatalogItem, CatalogData
from vector_store.store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepoIngester:
    """Ingest GitHub repos into vector store."""
    
    def __init__(self, registry_path: str = "repos-registry.json", 
                 repos_dir: str = "./repos",
                 catalog_path: str = "catalog.json",
                 persist_dir: str = ".chroma"):
        self.crawler = GitHubRepoCrawler(registry_path, repos_dir)
        self.catalog_path = Path(catalog_path)
        self.vector_store = VectorStore(persist_dir=persist_dir)
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> CatalogData:
        """Load existing catalog."""
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r') as f:
                data = json.load(f)
            return CatalogData(**data)
        else:
            return CatalogData(
                catalog_metadata={
                    "version": "1.0.0",
                    "last_updated": "2026-01-20",
                    "authoritative_source": "GitHub Repos Ingestion"
                },
                solution_accelerators=[]
            )
    
    def ingest_all_repos(self) -> Dict[str, bool]:
        """Ingest all enabled repos into vector store."""
        results = {}
        
        repos = self.crawler.list_repos()
        logger.info(f"🔄 Ingesting {len(repos)} repos...")
        
        for repo_config in repos:
            if repo_config.get("enabled", True):
                repo_id = repo_config["id"]
                try:
                    success = self._ingest_repo(repo_config)
                    results[repo_id] = success
                    if success:
                        logger.info(f"✅ Ingested {repo_id}")
                    else:
                        logger.warning(f"⚠️  Partial ingest for {repo_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to ingest {repo_id}: {e}")
                    results[repo_id] = False
        
        # Save updated catalog
        self._save_catalog()
        
        # Ingest into vector store
        logger.info("📚 Indexing into vector store...")
        self.vector_store.ingest_accelerators(self.catalog.solution_accelerators)
        logger.info("✅ Vector store updated")
        
        return results
    
    def _ingest_repo(self, repo_config: Dict) -> bool:
        """Ingest a single repo."""
        repo_id = repo_config["id"]
        
        # Extract README
        readme = self.crawler.extract_readme(repo_id)
        if not readme:
            logger.warning(f"No README found for {repo_id}")
            return False
        
        # Get list of files
        files = self.crawler.get_repo_files(repo_id)
        file_count = len(files)
        
        # Check if repo already in catalog
        existing = next(
            (item for item in self.catalog.solution_accelerators if item.id == repo_id),
            None
        )
        
        if existing:
            # Update existing
            existing.description = readme
            logger.info(f"Updated existing catalog item: {repo_id}")
        else:
            # Create new catalog item
            item = CatalogItem(
                id=repo_id,
                name=repo_config["name"],
                solution_area=repo_config["solution_area"],
                delivery_readiness="Gold Standard",
                technical_complexity=repo_config["technical_complexity"],
                repository_url=repo_config["github_url"],
                description=readme,
                products_and_services=self._extract_products(readme),
                languages=self._extract_languages(files),
                prerequisites=self._extract_prerequisites(readme),
                responsible_ai_tag=repo_config.get("responsible_ai_tag", False),
                deployment_type="Git/Source"
            )
            
            self.catalog.solution_accelerators.append(item)
            logger.info(f"Added new catalog item: {repo_id} ({file_count} files)")
        
        return True
    
    def _extract_products(self, readme: str) -> List[str]:
        """Extract Azure products mentioned in README."""
        products = set()
        keywords = {
            "azure ai": "Azure AI Foundry",
            "azure openai": "Azure OpenAI Service",
            "fabric": "Microsoft Fabric",
            "cosmos db": "Azure Cosmos DB",
            "blob storage": "Azure Blob Storage",
            "app service": "Azure App Service",
            "agent framework": "Agent Framework",
            "foundry": "Azure AI Foundry",
            "purview": "Microsoft Purview",
            "databricks": "Azure Databricks",
            "container apps": "Azure Container Apps"
        }
        
        readme_lower = readme.lower()
        for keyword, product in keywords.items():
            if keyword in readme_lower:
                products.add(product)
        
        return list(products) if products else ["Azure Services"]
    
    def _extract_languages(self, files: List[Dict]) -> List[str]:
        """Extract programming languages from file extensions."""
        languages = set()
        extension_map = {
            ".py": "Python",
            ".ts": "TypeScript",
            ".js": "JavaScript",
            ".json": "JSON",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".bicep": "Bicep",
            ".sh": "Shell"
        }
        
        for file_info in files:
            ext = file_info.get("extension", "")
            if ext in extension_map:
                languages.add(extension_map[ext])
        
        return list(languages) if languages else ["Python"]
    
    def _extract_prerequisites(self, readme: str) -> List[str]:
        """Extract prerequisites from README."""
        prerequisites = [
            "Azure Subscription",
            "Git CLI",
            "Azure Developer CLI (azd)"
        ]
        
        readme_lower = readme.lower()
        
        if "openai" in readme_lower:
            prerequisites.append("Azure OpenAI Service access")
        if "fabric" in readme_lower:
            prerequisites.append("Microsoft Fabric capacity")
        if "databricks" in readme_lower:
            prerequisites.append("Azure Databricks workspace")
        if "purview" in readme_lower:
            prerequisites.append("Microsoft Purview instance")
        if "agent" in readme_lower:
            prerequisites.append("Azure AI Foundry subscription")
        
        return prerequisites
    
    def _save_catalog(self):
        """Save updated catalog to file."""
        catalog_dict = {
            "catalog_metadata": {
                "version": self.catalog.catalog_metadata.version,
                "last_updated": "2026-01-20",
                "authoritative_source": self.catalog.catalog_metadata.authoritative_source,
                "governance_standard": self.catalog.catalog_metadata.governance_standard
            },
            "solution_accelerators": [
                json.loads(item.model_dump_json()) for item in self.catalog.solution_accelerators
            ]
        }
        
        with open(self.catalog_path, 'w') as f:
            json.dump(catalog_dict, f, indent=2)
        
        logger.info(f"💾 Saved catalog with {len(self.catalog.solution_accelerators)} items")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🚀 GitHub Repo Ingestion Pipeline")
    print("="*60 + "\n")
    
    ingester = RepoIngester()
    results = ingester.ingest_all_repos()
    
    print("\n" + "="*60)
    print("📊 Ingestion Summary")
    print("="*60)
    
    successful = [r for r, success in results.items() if success]
    failed = [r for r, success in results.items() if not success]
    
    print(f"\n✅ Successful: {len(successful)}")
    for repo_id in successful:
        print(f"   - {repo_id}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for repo_id in failed:
            print(f"   - {repo_id}")
    
    print(f"\n📚 Vector store updated with {len(ingester.catalog.solution_accelerators)} total accelerators")
    print("✨ Ready to query via API!\n")


if __name__ == "__main__":
    main()
