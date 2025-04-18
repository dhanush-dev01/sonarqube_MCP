from mcp.server.fastmcp import FastMCP
import requests
from requests.auth import HTTPBasicAuth
import sys
import os
print("PYTHONPATH:", sys.path)

# ───── CONFIGURATION AREA ─────
SONARQUBE_URL = os.getenv("SONARQUBE_URL", "http://localhost:9000")
SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN", "")
PROJECT_KEY = os.getenv("PROJECT_KEY", "default_project")
AUTH = HTTPBasicAuth(SONARQUBE_TOKEN, "")

# ───── MCP SERVER INIT ─────
mcp = FastMCP("SonarQube MCP")

@mcp.tool()
def sonar_health_check() -> str:
    """ Check the health status of the SonarQube server."""
    try:
        url = f"{SONARQUBE_URL}/api/system/status"
        response = requests.get(url, auth=AUTH, timeout=10)
        response.raise_for_status()
        status = response.json().get("status", "Unknown")
        return f"🩺 SonarQube server is up! Status: {status}"
    except requests.exceptions.ConnectionError:
        return f"❌ Connection error: Unable to reach SonarQube at {SONARQUBE_URL}"
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP error: {e.response.status_code} - {e.response.reason}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
    
@mcp.tool()
def get_token_info() -> dict:
    """🧾 Validate the current token and get user info."""
    try:
        url = f"{SONARQUBE_URL}/api/authentication/validate"
        response = requests.get(url, auth=AUTH)
        response.raise_for_status()
        data = response.json()
        return {"authenticated": data.get("valid", False), "login": data.get("login", "N/A")}
    except Exception as e:
        return {"error": f"Token validation failed: {str(e)}"}

@mcp.tool()
def get_project_issues(project_key: str = PROJECT_KEY) -> dict:
    """Fetch unresolved issues (bugs, code smells, vulnerabilities) for a given project."""
    try:
        url = f"{SONARQUBE_URL}/api/issues/search"
        params = {
            "componentKeys": project_key,
            "resolved": "false",
            "ps": "100"
        }
        response = requests.get(url, params=params, auth=AUTH, timeout=15)
        response.raise_for_status()
        data = response.json()
        issues = data.get("issues", [])

        if not issues:
            # Double-check if project exists
            check_url = f"{SONARQUBE_URL}/api/projects/search"
            projects_response = requests.get(check_url, auth=AUTH)
            projects_response.raise_for_status()
            project_keys = [p["key"] for p in projects_response.json().get("components", [])]
            if project_key not in project_keys:
                return {
                    "project": project_key,
                    "error": f"Project '{project_key}' not found. Try one of these: {project_keys}"
                }

        formatted_issues = [{
            "key": i.get("key"),
            "severity": i.get("severity"),
            "type": i.get("type"),
            "message": i.get("message"),
            "component": i.get("component"),
            "line": i.get("line"),
            "status": i.get("status")
        } for i in issues]

        return {
            "project": project_key,
            "total_issues": len(formatted_issues),
            "issues": formatted_issues[:10],
            "has_more": len(formatted_issues) > 10
        }

    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        if status_code == 403:
            return {"error": "🚫 Access denied. Token lacks permission to fetch issues."}
        elif status_code == 401:
            return {"error": "🔐 Unauthorized. Invalid or expired token."}
        return {"error": f"HTTP error: {status_code} - {http_err.response.reason}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def list_projects() -> dict:
    """📦 List all accessible SonarQube projects."""
    try:
        url = f"{SONARQUBE_URL}/api/projects/search"
        response = requests.get(url, auth=AUTH, timeout=10)
        response.raise_for_status()
        projects = response.json().get("components", [])

        return {
            "total": len(projects),
            "projects": [{
                "key": p.get("key"),
                "name": p.get("name"),
                "visibility": p.get("visibility")
            } for p in projects]
        }

    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        if status_code == 403:
            return {"error": "🚫 Access denied: Token doesn't have permission to list projects. Check roles."}
        elif status_code == 401:
            return {"error": "🔐 Unauthorized: Invalid or expired token."}
        return {"error": f"HTTP error: {status_code} - {http_err.response.reason}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to list projects: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def get_project_metrics(project_key: str = PROJECT_KEY) -> dict:
    """Fetch SonarQube metrics like bugs, coverage, code smells, etc."""
    try:
        url = f"{SONARQUBE_URL}/api/measures/component"
        metrics = (
            "bugs,vulnerabilities,code_smells,coverage,"
            "duplicated_lines_density,reliability_rating,"
            "security_rating,sqale_rating"
        )
        params = {
            "component": project_key,
            "metricKeys": metrics
        }
        response = requests.get(url, params=params, auth=AUTH, timeout=10)
        response.raise_for_status()

        measures = response.json().get("component", {}).get("measures", [])
        return {
            "project": project_key,
            "metrics": {m["metric"]: m["value"] for m in measures}
        }

    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        if status_code == 403:
            return {"error": "🚫 Access denied: Token lacks permission to fetch metrics."}
        elif status_code == 401:
            return {"error": "🔐 Unauthorized: Invalid token."}
        return {"error": f"HTTP error: {status_code} - {http_err.response.reason}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Metrics fetch failed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}