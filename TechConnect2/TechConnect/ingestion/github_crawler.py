"""
GitHub Repo Crawler - Fetch and index repos from registry
Supports local cloning and remote GitHub API calls
"""

import json
import subprocess
import tempfile
import shutil
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubRepoCrawler:
    """Crawl and ingest GitHub repositories into the catalog."""
    
    def __init__(self, registry_path: str = "repos-registry.json", local_repos_dir: str = "./repos"):
        """
        Args:
            registry_path: Path to repos-registry.json
            local_repos_dir: Directory to clone repos into
        """
        self.registry_path = Path(registry_path)
        self.local_repos_dir = Path(local_repos_dir)
        self.local_repos_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry = self._load_registry()
        self.crawler_config = self.registry.get("crawler_config", {})
    
    def _load_registry(self) -> Dict:
        """Load repos-registry.json."""
        if not self.registry_path.exists():
            logger.warning(f"Registry not found at {self.registry_path}")
            return {"repositories": [], "crawler_config": {}}
        
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def add_repo(self, repo_id: str, name: str, github_url: str, 
                 solution_area: str, complexity: str, responsible_ai: bool = False) -> bool:
        """Add a new repo to the registry."""
        # Check if repo already exists
        if any(r["id"] == repo_id for r in self.registry["repositories"]):
            logger.warning(f"Repo {repo_id} already exists in registry")
            return False
        
        new_repo = {
            "id": repo_id,
            "name": name,
            "github_url": github_url,
            "solution_area": solution_area,
            "technical_complexity": complexity,
            "responsible_ai_tag": responsible_ai,
            "enabled": True,
            "description": f"Added on {datetime.now().isoformat()}"
        }
        
        self.registry["repositories"].append(new_repo)
        self._save_registry()
        logger.info(f"✅ Added repo: {repo_id}")
        return True
    
    def remove_repo(self, repo_id: str) -> bool:
        """Remove a repo from the registry."""
        initial_len = len(self.registry["repositories"])
        self.registry["repositories"] = [
            r for r in self.registry["repositories"] if r["id"] != repo_id
        ]
        
        if len(self.registry["repositories"]) < initial_len:
            self._save_registry()
            logger.info(f"✅ Removed repo: {repo_id}")
            return True
        
        logger.warning(f"Repo {repo_id} not found")
        return False
    
    def list_repos(self) -> List[Dict]:
        """List all repos in registry."""
        return self.registry.get("repositories", [])
    
    def _save_registry(self):
        """Save updated registry back to file."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def clone_repo(self, repo_id: str, github_token: Optional[str] = None) -> Optional[Path]:
        """
        Clone a repo from registry locally.
        
        Args:
            repo_id: Repository ID from registry
            github_token: GitHub PAT for authenticated access (avoid rate limits)
            
        Returns:
            Path to cloned repo or None if failed
        """
        repo_config = next(
            (r for r in self.registry["repositories"] if r["id"] == repo_id),
            None
        )
        
        if not repo_config:
            logger.error(f"Repo {repo_id} not found in registry")
            return None
        
        if not repo_config.get("enabled", True):
            logger.warning(f"Repo {repo_id} is disabled in registry")
            return None
        
        github_url = repo_config["github_url"]
        repo_name = repo_config["name"].lower().replace(" ", "-")
        local_path = self.local_repos_dir / repo_name
        
        # Remove existing if present
        if local_path.exists():
            logger.info(f"Removing existing clone at {local_path}")
            shutil.rmtree(local_path)
        
        # Prepare URL with token if provided
        if github_token:
            url_with_auth = github_url.replace("https://", f"https://{github_token}@")
        else:
            url_with_auth = github_url
        
        try:
            logger.info(f"📥 Cloning {repo_name} from {github_url}...")
            
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url_with_auth, str(local_path)],
                capture_output=True,
                timeout=self.crawler_config.get("timeout_seconds", 300),
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return None
            
            logger.info(f"✅ Cloned {repo_name} to {local_path}")
            return local_path
        
        except subprocess.TimeoutExpired:
            logger.error(f"Clone timeout for {repo_id}")
            return None
        except Exception as e:
            logger.error(f"Clone failed for {repo_id}: {e}")
            return None
    
    def clone_all_repos(self, github_token: Optional[str] = None) -> Dict[str, bool]:
        """Clone all enabled repos from registry."""
        results = {}
        
        for repo_config in self.registry.get("repositories", []):
            if repo_config.get("enabled", True):
                repo_id = repo_config["id"]
                path = self.clone_repo(repo_id, github_token)
                results[repo_id] = path is not None
        
        return results
    
    def extract_readme(self, repo_id: str) -> Optional[str]:
        """Extract README.md content from cloned repo."""
        repo_config = next(
            (r for r in self.registry["repositories"] if r["id"] == repo_id),
            None
        )
        
        if not repo_config:
            return None
        
        repo_name = repo_config["name"].lower().replace(" ", "-")
        readme_path = self.local_repos_dir / repo_name / "README.md"
        
        if not readme_path.exists():
            logger.warning(f"README not found for {repo_id}")
            return None
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:2000]  # Return first 2000 chars as summary
        except Exception as e:
            logger.error(f"Failed to read README for {repo_id}: {e}")
            return None
    
    def get_repo_files(self, repo_id: str) -> List[Dict]:
        """Get list of files in cloned repo (filtered by config)."""
        repo_config = next(
            (r for r in self.registry["repositories"] if r["id"] == repo_id),
            None
        )
        
        if not repo_config:
            return []
        
        repo_name = repo_config["name"].lower().replace(" ", "-")
        repo_path = self.local_repos_dir / repo_name
        
        if not repo_path.exists():
            return []
        
        include_extensions = self.crawler_config.get("include_extensions", [".md", ".py"])
        exclude_dirs = set(self.crawler_config.get("exclude_dirs", []))
        max_depth = self.crawler_config.get("depth", 3)
        
        files = []
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                # Check depth
                relative = file_path.relative_to(repo_path)
                if len(relative.parts) > max_depth:
                    continue
                
                # Check excluded dirs
                if any(exc in relative.parts for exc in exclude_dirs):
                    continue
                
                # Check extensions
                if file_path.suffix in include_extensions:
                    files.append({
                        "path": str(relative),
                        "size_bytes": file_path.stat().st_size,
                        "extension": file_path.suffix
                    })
        
        return files
