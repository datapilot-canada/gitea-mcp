"""
Gitea MCP Server

This module implements a Model Context Protocol (MCP) server for Gitea, allowing AI agents
to interact with Gitea repositories and issues.

The server exposes the following tools:

1. Repository Management:
   - list_repositories: List repositories for the authenticated user.
   - create_repository: Create a new repository for the authenticated user.
   - create_org_repository: Create a new repository in an organization.
   - get_repository: Get a specific repository.
   - delete_repository: Delete a repository.
   - list_org_repositories: List an organization's repositories.
   - fork_repository: Fork a repository.
   - search_repositories: Search for repositories.
   - update_repository: Update repository settings (description, website, privacy, etc.).

2. Issue Tracking:
   - create_issue: Create a new issue in a repository.
   - search_issues: Search for issues in a repository.
   - update_issue: Update an issue (e.g., close it, change title).
   - get_issue: Get a specific issue.
   - list_issue_comments: List all comments on an issue.
   - create_issue_comment: Create a comment on an issue.
   - add_issue_label: Add labels to an issue.
   - remove_issue_label: Remove a label from an issue.
   - list_labels: List labels for a repository.
   - create_label: Create a label for a repository.

Configuration:
    The server requires GITEA_MCP_API_URL and GITEA_ACCESS_TOKEN environment variables.
"""
import os
import sys
import logging
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger("gitea_mcp")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded.")

# Initialize FastMCP server
mcp = FastMCP(name="gitea", port=8000)

# Configuration
GITEA_MCP_API_URL = os.getenv("GITEA_MCP_API_URL")
GITEA_ACCESS_TOKEN = os.getenv("GITEA_ACCESS_TOKEN")

if not GITEA_MCP_API_URL or not GITEA_ACCESS_TOKEN:
    # Try loading from the project root relative to this file (useful for local dev)
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        GITEA_MCP_API_URL = os.getenv("GITEA_MCP_API_URL")
        GITEA_ACCESS_TOKEN = os.getenv("GITEA_ACCESS_TOKEN")

if not GITEA_MCP_API_URL or not GITEA_ACCESS_TOKEN:
    raise ValueError("GITEA_MCP_API_URL and GITEA_ACCESS_TOKEN environment variables are required. Please check your .env file.")

def get_headers():
    """Constructs the headers for Gitea API requests.

    Returns:
        dict: A dictionary containing Authorization, Content-Type, and Accept headers.
    """
    return {
        "Authorization": f"token {GITEA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def make_request(method, endpoint, data=None, params=None):
    """Makes an HTTP request to the Gitea API.

    Args:
        method (str): The HTTP method (e.g., "GET", "POST", "PATCH").
        endpoint (str): The API endpoint (relative to /api/v1/).
        data (dict, optional): The JSON data to send in the body. Defaults to None.
        params (dict, optional): The query parameters. Defaults to None.

    Returns:
        dict or None: The JSON response from the API, or None if status is 204.
                      Returns a dictionary with "error" key if an exception occurs.
    """
    url = f"{GITEA_MCP_API_URL}/api/v1/{endpoint}"
    headers = get_headers()
    
    logger.info(f"Request: {method} {url}")

    with httpx.Client() as client:
        response = client.request(method, url, headers=headers, json=data, params=params)
        try:
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP Error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            return {"error": str(e)}

@mcp.tool()
def list_repositories():
    """List repositories for the authenticated user.

    Returns:
        list: A list of repository dictionaries.
    """
    return make_request("GET", "user/repos")

@mcp.tool()
def create_repository(name: str, description: str = None, private: bool = False, auto_init: bool = False, gitignores: str = None, license: str = None, readme: str = None, issue_labels: str = None, default_branch: str = "main"):
    """Create a new repository for the authenticated user.

    Args:
        name: The name of the repository.
        description: A short description of the repository.
        private: Whether the repository is private.
        auto_init: Whether to initialize the repository with a selected README and license.
        gitignores: Gitignore template to use.
        license: License template to use.
        readme: Readme template to use.
        issue_labels: Issue Label set to use.
        default_branch: Default branch name.

    Returns:
        dict: The created repository data.
    """
    data = {
        "name": name,
        "private": private,
        "auto_init": auto_init,
        "default_branch": default_branch
    }
    if description:
        data["description"] = description
    if gitignores:
        data["gitignores"] = gitignores
    if license:
        data["license"] = license
    if readme:
        data["readme"] = readme
    if issue_labels:
        data["issue_labels"] = issue_labels
        
    return make_request("POST", "user/repos", data=data)

@mcp.tool()
def create_org_repository(org: str, name: str, description: str = None, private: bool = False, auto_init: bool = False, gitignores: str = None, license: str = None, readme: str = None, issue_labels: str = None, default_branch: str = "main"):
    """Create a new repository in an organization.

    Args:
        org: The name of the organization.
        name: The name of the repository.
        description: A short description of the repository.
        private: Whether the repository is private.
        auto_init: Whether to initialize the repository with a selected README and license.
        gitignores: Gitignore template to use.
        license: License template to use.
        readme: Readme template to use.
        issue_labels: Issue Label set to use.
        default_branch: Default branch name.

    Returns:
        dict: The created repository data.
    """
    data = {
        "name": name,
        "private": private,
        "auto_init": auto_init,
        "default_branch": default_branch
    }
    if description:
        data["description"] = description
    if gitignores:
        data["gitignores"] = gitignores
    if license:
        data["license"] = license
    if readme:
        data["readme"] = readme
    if issue_labels:
        data["issue_labels"] = issue_labels
        
    return make_request("POST", f"orgs/{org}/repos", data=data)

@mcp.tool()
def get_repository(owner: str, repo: str):
    """Get a specific repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.

    Returns:
        dict: The repository data.
    """
    return make_request("GET", f"repos/{owner}/{repo}")

@mcp.tool()
def delete_repository(owner: str, repo: str):
    """Delete a repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.

    Returns:
        dict: A success message or error.
    """
    return make_request("DELETE", f"repos/{owner}/{repo}")

@mcp.tool()
def list_org_repositories(org: str):
    """List an organization's repositories.

    Args:
        org: The name of the organization.

    Returns:
        list: A list of repository dictionaries.
    """
    return make_request("GET", f"orgs/{org}/repos")

@mcp.tool()
def fork_repository(owner: str, repo: str, organization: str = None):
    """Fork a repository.

    Args:
        owner: The owner of the repository to fork.
        repo: The name of the repository to fork.
        organization: The name of the organization to fork into (optional).

    Returns:
        dict: The forked repository data.
    """
    data = {}
    if organization:
        data["organization"] = organization
        
    return make_request("POST", f"repos/{owner}/{repo}/forks", data=data)

@mcp.tool()
def search_repositories(q: str, topic: bool = False, include_desc: bool = False, uid: int = None, priority_owner_id: int = None, starred_by: int = None, private: bool = None, is_profile: bool = None, template: bool = None, archived: bool = None, mode: str = None, exclusive: bool = None, sort: str = None, order: str = None, page: int = None, limit: int = None):
    """Search for repositories.

    Args:
        q: Keyword to search for.
        topic: Search in topics.
        include_desc: Search in description.
        uid: Search only for repositories that belong to the given user ID.
        priority_owner_id: Prioritize repositories that belong to the given user ID.
        starred_by: Search only for repositories starred by the given user ID.
        private: Include private repositories (requires authentication).
        is_profile: Search only for repositories that are user profiles.
        template: Search only for repositories that are templates.
        archived: Search only for repositories that are archived.
        mode: Search mode (source, fork, mirror, collaborative).
        exclusive: If true, only return repositories that match the query exactly.
        sort: Sort by (alpha, created, updated, size, id).
        order: Order by (asc, desc).
        page: Page number.
        limit: Page size.

    Returns:
        dict: Search results including a list of repositories.
    """
    params = {"q": q}
    if topic: params["topic"] = topic
    if include_desc: params["includeDesc"] = include_desc
    if uid: params["uid"] = uid
    if priority_owner_id: params["priority_owner_id"] = priority_owner_id
    if starred_by: params["starredBy"] = starred_by
    if private is not None: params["private"] = private
    if is_profile is not None: params["is_profile"] = is_profile
    if template is not None: params["template"] = template
    if archived is not None: params["archived"] = archived
    if mode: params["mode"] = mode
    if exclusive is not None: params["exclusive"] = exclusive
    if sort: params["sort"] = sort
    if order: params["order"] = order
    if page: params["page"] = page
    if limit: params["limit"] = limit
    
    return make_request("GET", "repos/search", params=params)

@mcp.tool()
def update_repository(owner: str, repo: str, description: str = None, website: str = None, private: bool = None, has_issues: bool = None, has_wiki: bool = None):
    """Update a repository's settings.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        description: A short description of the repository.
        website: A URL for the repository.
        private: Whether the repository is private.
        has_issues: Whether to enable issues.
        has_wiki: Whether to enable the wiki.

    Returns:
        dict: The updated repository data.
    """
    data = {}
    if description is not None:
        data["description"] = description
    if website is not None:
        data["website"] = website
    if private is not None:
        data["private"] = private
    if has_issues is not None:
        data["has_issues"] = has_issues
    if has_wiki is not None:
        data["has_wiki"] = has_wiki
        
    return make_request("PATCH", f"repos/{owner}/{repo}", data=data)

@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: str, milestone_id: int = None, labels: list[int] = None):
    """Create a new issue in a repository.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        title: The title of the issue.
        body: The body content of the issue.
        milestone_id: Optional ID of the milestone to assign.
        labels: Optional list of label IDs to assign.

    Returns:
        dict: The created issue data.
    """
    data = {
        "title": title,
        "body": body
    }
    if milestone_id:
        data["milestone"] = milestone_id
    if labels:
        data["labels"] = labels
        
    return make_request("POST", f"repos/{owner}/{repo}/issues", data=data)

@mcp.tool()
def search_issues(owner: str, repo: str, q: str, state: str = "open"):
    """Search for issues in a repository.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        q: Keyword to search for.
        state: Filter by state (open, closed, all). Default is open.

    Returns:
        list: A list of matching issues.
    """
    return make_request("GET", f"repos/{owner}/{repo}/issues", params={"q": q, "state": state})

@mcp.tool()
def update_issue(owner: str, repo: str, index: int, title: str = None, body: str = None, state: str = None, milestone_id: int = None, labels: list[int] = None):
    """Update an issue in a repository.
    
    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.
        title: The title of the issue.
        body: The body content of the issue.
        state: The state of the issue (open or closed).
        milestone_id: The ID of the milestone to assign.
        labels: The list of label IDs to assign.

    Returns:
        dict: The updated issue data.
    """
    data = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if state is not None:
        data["state"] = state
    if milestone_id is not None:
        data["milestone"] = milestone_id
    if labels is not None:
        data["labels"] = labels
        
    return make_request("PATCH", f"repos/{owner}/{repo}/issues/{index}", data=data)

@mcp.tool()
def get_issue(owner: str, repo: str, index: int):
    """Get a specific issue.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.

    Returns:
        dict: The issue data.
    """
    return make_request("GET", f"repos/{owner}/{repo}/issues/{index}")

@mcp.tool()
def list_issue_comments(owner: str, repo: str, index: int):
    """List all comments on an issue.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.

    Returns:
        list: A list of comment dictionaries.
    """
    return make_request("GET", f"repos/{owner}/{repo}/issues/{index}/comments")

@mcp.tool()
def create_issue_comment(owner: str, repo: str, index: int, body: str):
    """Create a comment on an issue.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.
        body: The body of the comment.

    Returns:
        dict: The created comment data.
    """
    data = {
        "body": body
    }
    return make_request("POST", f"repos/{owner}/{repo}/issues/{index}/comments", data=data)

@mcp.tool()
def add_issue_label(owner: str, repo: str, index: int, labels: list[int]):
    """Add labels to an issue.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.
        labels: A list of label IDs to add.

    Returns:
        list: A list of label dictionaries.
    """
    data = {
        "labels": labels
    }
    return make_request("POST", f"repos/{owner}/{repo}/issues/{index}/labels", data=data)

@mcp.tool()
def remove_issue_label(owner: str, repo: str, index: int, label_id: int):
    """Remove a label from an issue.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        index: The index of the issue.
        label_id: The ID of the label to remove.

    Returns:
        dict: A success message or error.
    """
    return make_request("DELETE", f"repos/{owner}/{repo}/issues/{index}/labels/{label_id}")

@mcp.tool()
def list_labels(owner: str, repo: str, page: int = 1, limit: int = 20):
    """List labels for a repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        page: Page number of results to return (1-based).
        limit: Page size of results.

    Returns:
        list: A list of label dictionaries.
    """
    return make_request("GET", f"repos/{owner}/{repo}/labels", params={"page": page, "limit": limit})

@mcp.tool()
def create_label(owner: str, repo: str, name: str, color: str, description: str = None, exclusive: bool = False):
    """Create a label for a repository.

    Args:
        owner: The owner of the repository.
        repo: The name of the repository.
        name: The name of the label.
        color: The color of the label (6-character hex code).
        description: The description of the label.
        exclusive: Whether the label is exclusive (scoped).

    Returns:
        dict: The created label data.
    """
    data = {
        "name": name,
        "color": color,
        "exclusive": exclusive
    }
    if description:
        data["description"] = description
    return make_request("POST", f"repos/{owner}/{repo}/labels", data=data)

if __name__ == "__main__":
    logger.info("Starting Gitea MCP Server...")
    mcp.run(transport='stdio')
