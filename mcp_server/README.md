# FixIt MCP server

Lets an MCP-capable agent find, read and assign FixIt tickets as a warden.

```bash
python -m venv .venv-mcp && source .venv-mcp/bin/activate   # Windows: .venv-mcp\Scripts\activate
pip install -r mcp_server/requirements.txt
python -m pytest mcp_server/tests -q                       # no API or network needed
```

To use it, start the API (`make seed && make run`), log in as the warden and export the
token, then register the server with your agent (example `.mcp.json`):

```json
{"mcpServers": {"fixit": {"command": "python", "args": ["mcp_server/server.py"],
  "env": {"FIXIT_TOKEN": "<token>"}}}}
```

Do not commit a `.mcp.json` that contains a real token.
