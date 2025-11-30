# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt README.md ./
COPY src ./src

# Install git (required for get_local_git_remotes tool)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies and the package itself
RUN pip install --no-cache-dir .

# Set environment variables to ensure output is unbuffered (crucial for MCP stdio)
ENV PYTHONUNBUFFERED=1
# Ensure Python requests/httpx libraries use the system certificate store
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Run the server
# Using -m to run as a module, assuming the package is installed
CMD ["python", "-m", "datapilot_gitea_mcp.server"]
