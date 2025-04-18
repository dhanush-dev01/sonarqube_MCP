# SonarQube MCP Server

This is a FastMCP server that provides a bridge to interact with SonarQube APIs. The server offers various tools to monitor and analyze code quality using SonarQube.

## Features

### 1. Health Check
- Endpoint: `sonar_health_check`
- Checks the status of your SonarQube server
- Returns the current health status and connection information

### 2. Token Validation
- Endpoint: `get_token_info`
- Validates the SonarQube authentication token
- Returns authentication status and associated user information

### 3. Project Issues
- Endpoint: `get_project_issues`
- Fetches unresolved issues for a specific project
- Returns detailed information about:
  - Bugs
  - Code smells
  - Vulnerabilities
  - Issue severity and status
  - File location and line numbers

### 4. Project Listing
- Endpoint: `list_projects`
- Lists all accessible SonarQube projects
- Provides project keys, names, and visibility settings

### 5. Project Metrics
- Endpoint: `get_project_metrics`
- Retrieves key quality metrics for a project including:
  - Bug count
  - Vulnerability count
  - Code smell count
  - Code coverage
  - Duplicated lines density
  - Reliability rating
  - Security rating
  - Maintainability rating (SQALE)

## Configuration

The server uses the following environment variables:

```env
SONARQUBE_URL=http://localhost:9000  # Default SonarQube server URL
SONARQUBE_TOKEN=                     # Your SonarQube authentication token
PROJECT_KEY=default_project          # Default project key for operations
```

## Requirements

Check the `requirements.txt` file for all dependencies. The main requirements include:
- FastMCP
- Requests

## Usage

1. Set up your environment variables
2. Install the requirements
3. Run the server using Python

The server will start and provide MCP-compliant endpoints for interacting with your SonarQube instance.

## Docker Usage

### Security Notice
For security reasons, sensitive environment variables like `SONARQUBE_TOKEN` and `PROJECT_KEY` should not be stored in the Dockerfile. Instead, they should be passed at runtime using environment variables or environment files.

### Building the Image

To build the Docker image:

```bash
docker build -t sonarqube-mcp .
```

### Adding it in MCP server

use it in you MCP cli by adding

```bash
      "sonarqubemcp": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "--init",
          "-e",
          "SONARQUBE_URL",
          "-e",
          "SONARQUBE_TOKEN",
          "-e",
          "PROJECT_KEY",
          "mcp-sonarqube-node"
        ],
        "env": {
          "SONARQUBE_URL": "http://52.184.147.19:9000",
          "SONARQUBE_TOKEN" : "squ_111508df0789913de879c34f492f6402b5c2bff5",
          "PROJECT_KEY": "AITest"
        }
      }
```

```bash
docker build -t sonarqube-mcp .
```

### Running the Container

Run the container with your SonarQube configuration:



### Environment Variables

When running the container, configure these required environment variables:
- `SONARQUBE_URL`: URL of your SonarQube server
- `SONARQUBE_TOKEN`: Your SonarQube authentication token
- `PROJECT_KEY`: The default project key to analyze


The server runs on Python 3.10 and uses the `uv` package manager for dependency management and execution.

## Error Handling

The server includes comprehensive error handling for:
- Connection issues
- Authentication failures
- Permission problems
- Invalid project keys
- General API errors

Each endpoint returns detailed error messages to help diagnose issues.