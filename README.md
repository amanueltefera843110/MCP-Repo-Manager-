# GitHub Repository Manager MCP Server

A Model Context Protocol (MCP) server that allows AI assistants to create and delete GitHub repositories.

## Features

- ✅ **Create GitHub repositories** with customizable settings
- ✅ **Delete GitHub repositories** (permanent deletion)
- ✅ **MCP protocol compliant** - works with Claude Desktop and other MCP clients
- ✅ **Simple setup** - just configure and restart your AI assistant
- ✅ **Secure** - uses environment variables for sensitive data

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Your GitHub Token
1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate a new token with **"repo"** permissions
3. Copy the token

### 3. Create Environment File
Create a `.env` file in the same directory as `simple_mcp_server.py`:
```bash
# .env file
GITHUB_TOKEN=your_actual_github_token_here
```

**⚠️ Important:** Never commit your `.env` file to Git! It contains sensitive information.

### 4. Configure Claude Desktop
1. Open: `~/Library/Application Support/Claude/config.json`
2. Replace the content with:
```json
{
  "darkMode": "dark",
  "scale": 0,
  "mcpServers": {
    "github-repo-creator": {
      "command": "python3",
      "args": ["/path/to/your/simple_mcp_server.py"],
      "env": {}
    }
  }
}
```

**Note:** No need to set `GITHUB_TOKEN` in the config anymore - it's loaded from the `.env` file.

### 5. Restart Claude Desktop
- Quit and reopen Claude Desktop

### 6. Test It!
Ask Claude:
- "What tools do you have available?"
- "Create a repository called 'my-test-repo'"
- "Delete the repository called 'my-test-repo'"

## Available Tools

### `create_github_repository`
Creates a new GitHub repository.

**Parameters:**
- `name` (required): Repository name
- `private` (optional): Make it private (default: false)
- `description` (optional): Repository description
- `auto_init` (optional): Initialize with README (default: true)

### `delete_github_repository`
Deletes an existing GitHub repository.

**Parameters:**
- `name` (required): Repository name to delete

## Files

- `simple_mcp_server.py` - The MCP server implementation
- `requirements.txt` - Python dependencies
- `claude_config_example.json` - Example Claude Desktop configuration
- `.env.example` - Example environment file (copy to `.env` and add your token)
- `README.md` - This file

## Security Notes

- ⚠️ **Never commit your `.env` file to Git**
- ⚠️ **Never commit your real GitHub token to Git**
- ⚠️ **Repository deletion is permanent**
- ✅ **Use environment variables for sensitive data**
- ✅ **Regularly rotate your tokens**
- ✅ **Add `.env` to your `.gitignore` file**

## Environment Variables

The server uses these environment variables:

- `GITHUB_TOKEN` - Your GitHub personal access token (required)

## Troubleshooting

### "GITHUB_TOKEN not found" error
- Make sure you created a `.env` file
- Check that `GITHUB_TOKEN=your_token` is in the `.env` file
- Ensure the `.env` file is in the same directory as `simple_mcp_server.py`

### "Repository not found" error
- Check that the repository name is correct (case-sensitive)
- Ensure your token has the right permissions
- Verify the repository exists in your account

### MCP server not loading
- Check the file path in your config
- Ensure the script is executable: `chmod +x simple_mcp_server.py`
- Restart Claude Desktop after config changes

## Example Usage

Once configured, you can ask Claude:

- "Create a private repository called 'secret-project' with description 'My secret project'"
- "Make a public repository named 'open-source-tool'"
- "Delete the repository called 'old-test-repo'"
- "What tools do you have available?"

## License

MIT License - feel free to use and modify! # MCP-Repo-Manager-
