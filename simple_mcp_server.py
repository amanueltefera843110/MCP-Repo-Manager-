#!/usr/bin/env python3
"""
Simple MCP Server for GitHub Repository Creation
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub configuration - load from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logger.error("GITHUB_TOKEN not found in environment variables. Please set it in your .env file or environment.")
    sys.exit(1)
GITHUB_API_URL = "https://api.github.com/user/repos"

class SimpleMCPServer:
    def __init__(self):
        self.server_name = "github-repo-creator"
        self.server_version = "1.0.0"
        
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        method = message.get("method")
        msg_id = message.get("id")
        
        if method == "initialize":
            return self.handle_initialize(message, msg_id)
        elif method == "tools/list":
            return self.handle_list_tools(msg_id)
        elif method == "tools/call":
            return await self.handle_call_tool(message, msg_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def handle_initialize(self, message: Dict[str, Any], msg_id: int) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.server_name,
                    "version": self.server_version
                }
            }
        }
    
    def handle_list_tools(self, msg_id: int) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "create_github_repository",
                        "description": "Create a new GitHub repository",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the repository to create"
                                },
                                "private": {
                                    "type": "boolean",
                                    "description": "Whether the repository should be private",
                                    "default": False
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the repository"
                                },
                                "auto_init": {
                                    "type": "boolean",
                                    "description": "Initialize repository with README",
                                    "default": True
                                }
                            },
                            "required": ["name"]
                        }
                    },
                    {
                        "name": "delete_github_repository",
                        "description": "Delete a GitHub repository",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the repository to delete"
                                }
                            },
                            "required": ["name"]
                        }
                    }
                ]
            }
        }
    
    async def handle_call_tool(self, message: Dict[str, Any], msg_id: int) -> Dict[str, Any]:
        """Handle tools/call request"""
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "create_github_repository":
            result = await self.create_github_repository(arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
        if tool_name == "delete_github_repository":
            result = await self.delete_github_repository(arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    async def create_github_repository(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a GitHub repository"""
        try:
            repo_name = arguments.get("name")
            if not repo_name:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: Repository name is required"
                        }
                    ],
                    "isError": True
                }
            
            # Prepare GitHub API request
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            
            json_data = {
                "name": repo_name,
                "private": arguments.get("private", False),
                "auto_init": arguments.get("auto_init", True)
            }
            
            if "description" in arguments:
                json_data["description"] = arguments["description"]
            
            # Call GitHub API
            async with httpx.AsyncClient() as client:
                response = await client.post(GITHUB_API_URL, json=json_data, headers=headers)
            
            if response.status_code == 201:
                repo_data = response.json()
                repo_url = repo_data.get("html_url", "Unknown")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Successfully created GitHub repository '{repo_name}'!\n\nRepository URL: {repo_url}\nClone URL: {repo_data.get('clone_url', 'Unknown')}"
                        }
                    ]
                }
            else:
                error_data = response.json()
                error_message = error_data.get("message", "Unknown error")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Failed to create repository: {error_message} (Status: {response.status_code})"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error creating repository: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def delete_github_repository(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a GitHub repository"""
        try:
            repo_name = arguments.get("name")
            if not repo_name:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: Repository name is required"
                        }
                    ],
                    "isError": True
                }
            
            # Prepare GitHub API request
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            
            # Get the username from the token
            async with httpx.AsyncClient() as client:
                # First, get user info to get the username
                user_response = await client.get("https://api.github.com/user", headers=headers)
                if user_response.status_code != 200:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Failed to get user info: {user_response.status_code}"
                            }
                        ],
                        "isError": True
                    }
                
                user_data = user_response.json()
                username = user_data.get("login")
                
                # Now delete the repository using the full path
                delete_url = f"https://api.github.com/repos/{username}/{repo_name}"
                response = await client.delete(delete_url, headers=headers)
            
            if response.status_code == 204:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Successfully deleted GitHub repository '{repo_name}'"
                        }
                    ]
                }
            else:
                error_data = response.json()
                error_message = error_data.get("message", "Unknown error")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Failed to delete repository: {error_message} (Status: {response.status_code})"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error deleting repository: {str(e)}"
                    }
                ],
                "isError": True
            }

async def main():
    """Main function to run the MCP server"""
    server = SimpleMCPServer()
    
    print(f"🚀 Starting {server.server_name} MCP server...", file=sys.stderr)
    print("Ready to receive MCP messages on stdin/stdout", file=sys.stderr)
    
    # Read from stdin, write to stdout
    while True:
        try:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            # Parse the JSON message
            message = json.loads(line.strip())
            
            # Handle the message
            response = await server.handle_message(message)
            
            # Send the response
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }), flush=True)
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }), flush=True)

if __name__ == "__main__":
    asyncio.run(main()) 