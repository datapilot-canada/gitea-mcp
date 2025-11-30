# Datapilot Canada - Gitea MCP Server

MCP Server Implementation for interacting with Gitea.

## Features

- Connect to a self-hosted Gitea instance
- Repository Management (List, Create, Delete, Search, Update)
- Issue Tracking (Create, Search, Update, Comment, Label)

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Note: You may need to create a `requirements.txt` or install `mcp`, `httpx`, `python-dotenv` manually)

    Or if using `uv`:
    ```bash
    uv add mcp httpx python-dotenv
    ```

2.  **Configuration:**
    Copy `.env.example` to `.env` and fill in your Gitea details:
    ```bash
    cp .env.example .env
    ```
    Edit `.env`:
    ```
    GITEA_MCP_API_URL=https://your-gitea-instance.com
    GITEA_ACCESS_TOKEN=your_access_token_here
    ```

## Usage with MCP Client (e.g. Claude Desktop, VS Code)

Add the server to your MCP configuration. A sample configuration is provided in `mcp_config.json`.

To run manually:
```bash
python src/datapilot_gitea_mcp/server.py
```

## Docker Usage

You can also run this server using Docker.

1.  **Build the image:**
    ```bash
    docker build -t datapilotgiteamcp .
    ```

2.  **Run the container:**
    Since MCP uses stdio for communication, you need to run the container interactively and pass environment variables.

    ```bash
    docker run -i --rm \
      -e GITEA_MCP_API_URL=https://your-gitea-instance.com \
      -e GITEA_ACCESS_TOKEN=your_access_token_here \
      datapilotgiteamcp
    ```

    **Note:** When configuring this in an MCP client (like Claude Desktop), use the `docker` command in the configuration.

    Example `claude_desktop_config.json`:
    ```json
    {
      "mcpServers": {
        "gitea": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITEA_MCP_API_URL=https://your-gitea-instance.com",
            "-e",
            "GITEA_ACCESS_TOKEN=your_token",
            "datapilotgiteamcp"
          ]
        }
      }
    }
    ```

### Using Self-Signed Certificates

If your Gitea instance uses a self-signed certificate, you can mount your certificate into the container and configure the environment variables to trust it.

1.  **Mount the certificate:**
    Use the `-v` flag to mount your certificate file into the container.
2.  **Set environment variables:**
    Set `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` to point to the mounted certificate.

    ```bash
    docker run -i --rm \
      -e GITEA_API_URL=https://your-gitea-instance.com \
      -e GITEA_ACCESS_TOKEN=your_token \
      -v /path/to/your/cert.crt:/usr/local/share/ca-certificates/custom-cert.crt \
      -e SSL_CERT_FILE=/usr/local/share/ca-certificates/custom-cert.crt \
      -e REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/custom-cert.crt \
      datapilotgiteamcp
    ```

## Remote Deployment

You can run this MCP server on a remote machine and connect to it securely via SSH. This is useful if you want to keep the server running on a central host or closer to your Gitea instance.

### 1. Prepare the Remote Host
Ensure the remote machine has Docker installed and the user has permissions to run containers.
Transfer your Docker image to the remote host:
```bash
# Save image locally and load it on the remote host
docker save datapilotgiteamcp | ssh user@your-remote-host "docker load"
```

### 2. Configure VS Code (Local)
Use the `gitea-docker-ssh` configuration provided in `mcp_config.json`.

**Important Notes:**
*   **SSH Keys:** You must have SSH key-based authentication set up (passwordless login) for this to work seamlessly.
*   **Environment Variables:** Since the process runs remotely, you must pass the environment variables explicitly in the `args` list, or mount a `.env` file that exists on the *remote* filesystem.

## Troubleshooting

### "Request URL is missing an 'http://' or 'https://' protocol"

This error means the `GITEA_MCP_API_URL` environment variable is not set or is invalid.

- **If running via Docker:** Ensure you are passing the environment variables correctly.
  - If using `--env-file .env`, make sure the `.env` file exists **in the directory where you are running the command** (or VS Code workspace root) and contains `GITEA_MCP_API_URL`.
  - If running from a different workspace, you may need to provide the absolute path to your `.env` file in the `mcp.json` configuration:
    ```json
    "--env-file", "C:/path/to/your/project/.env"
    ```
- **If running locally:** Ensure `.env` is in the project root or the same directory as `server.py`.


# Prompt Samples
## Creating an issue
Create a new issue in the 'datapilot-gitea-mcp' repository to track the implementation of the new feature. Add the 'enhancement' label to it.
