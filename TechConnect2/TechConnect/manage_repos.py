#!/usr/bin/env python
"""
CLI tool for managing GitHub repos in TechConnect
Usage: python manage_repos.py <command> [args]
"""

import sys
import json
from pathlib import Path
from ingestion.github_crawler import GitHubRepoCrawler


def print_help():
    """Print help message."""
    print("""
TechConnect Repo Manager CLI
============================

Usage: python manage_repos.py <command> [args]

Commands:
  list                              List all registered repos
  add <id> <name> <url> <area> <complexity>   Add a new repo
  remove <id>                       Remove a repo from registry
  clone <id>                        Clone a specific repo
  clone-all                         Clone all enabled repos
  files <id>                        List files in a cloned repo
  readme <id>                       Show README from a cloned repo
  
Examples:
  python manage_repos.py list
  python manage_repos.py add security-hardening "Security Hardening" \\
    "https://github.com/org/security-hardening.git" Security L300 false
  python manage_repos.py clone multi-agent-automation
  python manage_repos.py clone-all
  python manage_repos.py files content-processing
  python manage_repos.py readme unified-data-fabric
""")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # Initialize crawler
    registry_path = Path(__file__).parent / "repos-registry.json"
    repos_dir = Path(__file__).parent / "repos"
    crawler = GitHubRepoCrawler(str(registry_path), str(repos_dir))
    
    if command == "list":
        repos = crawler.list_repos()
        print(f"\n📦 Registered Repositories ({len(repos)} total):\n")
        for repo in repos:
            status = "✅ Enabled" if repo.get("enabled", True) else "❌ Disabled"
            print(f"  {repo['id']:<25} {repo['name']:<40} {status}")
            print(f"     Area: {repo['solution_area']:<20} Complexity: {repo['technical_complexity']}")
        print()
    
    elif command == "add" and len(sys.argv) >= 7:
        repo_id = sys.argv[2]
        name = sys.argv[3]
        url = sys.argv[4]
        area = sys.argv[5]
        complexity = sys.argv[6]
        rai = sys.argv[7].lower() == "true" if len(sys.argv) > 7 else False
        
        success = crawler.add_repo(repo_id, name, url, area, complexity, rai)
        if success:
            print(f"✅ Added repo: {repo_id}")
        else:
            print(f"❌ Failed to add repo {repo_id}")
    
    elif command == "remove" and len(sys.argv) >= 3:
        repo_id = sys.argv[2]
        success = crawler.remove_repo(repo_id)
        if success:
            print(f"✅ Removed repo: {repo_id}")
        else:
            print(f"❌ Repo {repo_id} not found")
    
    elif command == "clone" and len(sys.argv) >= 3:
        repo_id = sys.argv[2]
        print(f"\n🔄 Cloning {repo_id}...")
        path = crawler.clone_repo(repo_id)
        if path:
            print(f"✅ Cloned to: {path}\n")
        else:
            print(f"❌ Failed to clone {repo_id}\n")
    
    elif command == "clone-all":
        print(f"\n🔄 Cloning all enabled repos...\n")
        results = crawler.clone_all_repos()
        successful = [k for k, v in results.items() if v]
        failed = [k for k, v in results.items() if not v]
        
        print(f"✅ Successful: {len(successful)}")
        for repo_id in successful:
            print(f"   - {repo_id}")
        
        if failed:
            print(f"\n❌ Failed: {len(failed)}")
            for repo_id in failed:
                print(f"   - {repo_id}")
        print()
    
    elif command == "files" and len(sys.argv) >= 3:
        repo_id = sys.argv[2]
        files = crawler.get_repo_files(repo_id)
        if files:
            print(f"\n📄 Files in {repo_id} ({len(files)} total):\n")
            for file_info in files[:20]:  # Show first 20
                print(f"  {file_info['path']:<50} {file_info['size_bytes']:<10} {file_info['extension']}")
            if len(files) > 20:
                print(f"\n  ... and {len(files) - 20} more files")
            print()
        else:
            print(f"❌ No files found in {repo_id}")
    
    elif command == "readme" and len(sys.argv) >= 3:
        repo_id = sys.argv[2]
        content = crawler.extract_readme(repo_id)
        if content:
            print(f"\n📖 README from {repo_id}:\n")
            print(content)
            print(f"\n... (truncated to 2000 chars)\n")
        else:
            print(f"❌ README not found for {repo_id}")
    
    else:
        print_help()


if __name__ == "__main__":
    main()
