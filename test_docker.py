import subprocess
import json
import sys
import os
import time

def test_docker_mcp():
    # Configuration
    IMAGE_NAME = "datapilotgiteamcp" # Default, but we'll check if user wants to override
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("Error: .env file not found in current directory.")
        return

    print(f"Testing MCP server in Docker image: {IMAGE_NAME}...")
    
    # Command to run the docker container
    # We use the same arguments as in mcp.json
    cmd = [
        "docker", "run", 
        "-i",           # Interactive (keep stdin open)
        "--rm",         # Remove container after exit
        "--env-file", ".env",
        IMAGE_NAME
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=0 # Unbuffered
        )

        # 1. Send Initialize Request
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            },
            "id": 1
        }
        
        print("\nSending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        if not response_line:
            print("Error: No response from server.")
            return

        print("Received response:")
        print(response_line.strip())
        
        response_data = json.loads(response_line)
        if "error" in response_data:
            print("Server returned error:", response_data["error"])
            return

        # 2. Send Initialized Notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        print("\nSending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()

        # 3. List Tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        print("\nSending tools/list request...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        print("Received response:")
        print(response_line.strip())
        
        tools_data = json.loads(response_line)
        if "result" in tools_data and "tools" in tools_data["result"]:
            tools = tools_data["result"]["tools"]
            print(f"\nSuccess! Found {len(tools)} tools:")
            for tool in tools:
                print(f"- {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print("Unexpected response format.")

    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed and in your PATH?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            print("\nTest finished, container stopped.")

if __name__ == "__main__":
    test_docker_mcp()
