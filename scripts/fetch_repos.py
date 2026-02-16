#!/usr/bin/env python3
"""
Fetch markdown files from all configured repositories and organize them for MkDocs.
"""

import os
import sys
import shutil
import requests
import base64
import yaml
from pathlib import Path
from typing import List, Dict, Any

# Repositories to fetch from
REPOSITORIES = [
    "at1337github/evidence-corpus-pipeline",
    "at1337github/Codex_corpus_analysis",
    "at1337github/Matrix_project",
    "at1337github/3track",
    "at1337github/Pattern_Extraction_Pattern_hub",
    "at1337github/Discovery_SMS_hub",
    "at1337github/discovery_sms_corpus_analysis_10_34_01_pm",
    "at1337github/discovery_sms_corpus_analysis_trash_local",
    "at1337github/discovery_sms_corpus_analysis",
    "at1337github/pattern_analysis_forensic_subproject",
    "at1337github/pattern_analysis_workspace",
    "at1337github/pattern_repo_review_copy",
    "at1337github/pattern_extraction_local",
    "at1337github/pattern",
]


class GitHubFetcher:
    """Fetch markdown files from GitHub repositories."""
    
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        })
        self.base_url = 'https://api.github.com'
    
    def get_default_branch(self, repo: str) -> str:
        """Get the default branch for a repository."""
        url = f'{self.base_url}/repos/{repo}'
        response = self.session.get(url)
        
        if response.status_code == 404:
            print(f"⚠️  Repository {repo} not found or not accessible")
            return None
        elif response.status_code != 200:
            print(f"⚠️  Error fetching {repo}: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        return data.get('default_branch', 'main')
    
    def fetch_tree(self, repo: str, branch: str) -> List[Dict[str, Any]]:
        """Fetch the git tree recursively."""
        url = f'{self.base_url}/repos/{repo}/git/trees/{branch}'
        params = {'recursive': '1'}
        response = self.session.get(url, params=params)
        
        if response.status_code != 200:
            print(f"⚠️  Error fetching tree for {repo}: {response.status_code}")
            return []
        
        data = response.json()
        return data.get('tree', [])
    
    def fetch_file_content(self, repo: str, path: str) -> str:
        """Fetch the content of a file."""
        url = f'{self.base_url}/repos/{repo}/contents/{path}'
        response = self.session.get(url)
        
        if response.status_code != 200:
            print(f"⚠️  Error fetching {path} from {repo}: {response.status_code}")
            return None
        
        data = response.json()
        if data.get('encoding') == 'base64':
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            return content
        
        return None
    
    def fetch_repo_markdown_files(self, repo: str) -> Dict[str, str]:
        """Fetch all markdown files from a repository."""
        print(f"\n📦 Fetching from {repo}...")
        
        # Get default branch
        branch = self.get_default_branch(repo)
        if not branch:
            return {}
        
        # Fetch the git tree
        tree = self.fetch_tree(repo, branch)
        if not tree:
            return {}
        
        # Filter markdown files
        md_files = [item for item in tree if item['type'] == 'blob' and item['path'].endswith('.md')]
        
        print(f"   Found {len(md_files)} markdown file(s)")
        
        files_content = {}
        for item in md_files:
            path = item['path']
            print(f"   📄 {path}")
            content = self.fetch_file_content(repo, path)
            if content:
                files_content[path] = content
        
        return files_content


def save_files(repo: str, files: Dict[str, str], docs_dir: Path):
    """Save fetched files to the docs directory."""
    # Extract repo name from full path
    repo_name = repo.split('/')[-1]
    repo_dir = docs_dir / repo_name
    
    for file_path, content in files.items():
        # Create full path
        full_path = repo_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)


def generate_navigation(docs_dir: Path) -> List[Dict[str, Any]]:
    """Generate navigation structure based on discovered files."""
    nav = [{'Home': 'index.md'}]
    
    # Get all repo directories
    repo_dirs = sorted([d for d in docs_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
    
    for repo_dir in repo_dirs:
        repo_name = repo_dir.name
        
        # Find all markdown files in this repo
        md_files = sorted(repo_dir.rglob('*.md'))
        
        if not md_files:
            continue
        
        # Create navigation structure for this repo
        repo_nav = {}
        
        for md_file in md_files:
            rel_path = md_file.relative_to(docs_dir)
            rel_path_str = str(rel_path).replace('\\', '/')
            
            # Create a nice display name
            file_name = md_file.stem
            if file_name.lower() == 'readme':
                display_name = f"{repo_name} Overview"
            else:
                # Convert filename to title case
                display_name = file_name.replace('_', ' ').replace('-', ' ').title()
            
            # Build nested structure based on directory depth
            parts = rel_path.parts[1:]  # Skip repo name
            if len(parts) == 1:
                # File is at root of repo
                repo_nav[display_name] = rel_path_str
            else:
                # File is in subdirectory - create nested structure
                current = repo_nav
                for part in parts[:-1]:
                    section_name = part.replace('_', ' ').replace('-', ' ').title()
                    if section_name not in current:
                        current[section_name] = {}
                    if not isinstance(current[section_name], dict):
                        # Convert to dict if it was a string
                        old_val = current[section_name]
                        current[section_name] = {'Overview': old_val}
                    current = current[section_name]
                
                current[display_name] = rel_path_str
        
        # Add repo to main nav
        if repo_nav:
            nav.append({repo_name: repo_nav})
    
    return nav


def update_mkdocs_config(nav: List[Dict[str, Any]], config_path: Path):
    """Update mkdocs.yml with the generated navigation."""
    # Read the existing config as text to preserve special YAML tags
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Generate the navigation YAML string
    nav_yaml = yaml.dump({'nav': nav}, default_flow_style=False, sort_keys=False, allow_unicode=True)
    # Remove the wrapping braces if any and get just the nav section
    nav_yaml = nav_yaml.strip()
    
    # Find and replace the nav section in the original content
    # Pattern: find "nav:" followed by everything until the end of file or next top-level key
    import re
    # Match from "nav:" to either end of file or start of next non-indented line
    pattern = r'^nav:.*?(?=\n\S|\Z)'
    replacement = nav_yaml
    
    updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write back the updated content
    with open(config_path, 'w') as f:
        f.write(updated_content)


def main():
    """Main function."""
    # Get token from environment
    token = os.environ.get('DOCS_PAT')
    if not token:
        print("❌ Error: DOCS_PAT environment variable not set")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / 'docs'
    config_path = base_dir / 'mkdocs.yml'
    
    # Clean docs directory (except index.md)
    if docs_dir.exists():
        for item in docs_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.name != 'index.md':
                item.unlink()
    else:
        docs_dir.mkdir()
    
    # Initialize fetcher
    fetcher = GitHubFetcher(token)
    
    # Fetch from all repositories
    print("🚀 Starting to fetch markdown files from repositories...\n")
    
    all_repos_data = {}
    for repo in REPOSITORIES:
        files = fetcher.fetch_repo_markdown_files(repo)
        if files:
            save_files(repo, files, docs_dir)
            all_repos_data[repo] = len(files)
    
    # Generate navigation
    print("\n📝 Generating navigation...")
    nav = generate_navigation(docs_dir)
    
    # Update mkdocs.yml
    print("📝 Updating mkdocs.yml...")
    update_mkdocs_config(nav, config_path)
    
    # Print summary
    print("\n✅ Done!")
    print(f"\nSummary:")
    print(f"  Total repositories processed: {len(all_repos_data)}")
    print(f"  Total markdown files fetched: {sum(all_repos_data.values())}")
    
    for repo, count in all_repos_data.items():
        print(f"    {repo}: {count} file(s)")


if __name__ == '__main__':
    main()
