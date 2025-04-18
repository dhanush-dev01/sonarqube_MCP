FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including Node.js (with npm & npx)
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv
# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .


# DO NOT put secrets in ENV in real prod (use --env or --env-file instead)
ENV SONARQUBE_URL=""
ENV SONARQUBE_TOKEN=""
ENV PROJECT_KEY=""

# Start the MCP server
CMD ["uv", "run", "--with", "mcp[cli]", "mcp", "run", "server.py"]
