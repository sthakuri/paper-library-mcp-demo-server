# Paper Library – MCP demo server

A small MCP server for the Graduate Seminar talk. Uses protocol version **2026-07-28** (the stateless version).

| Primitive | Name | What it shows |
|---|---|---|
| Resource | `papers://reading-list` | Data / context the app can load |
| Tool | `search_papers(query)` | Read-only action (`readOnlyHint: true`) |
| Tool | `add_note(paper_id, note)` | State-changing action |
| Resource template (extra) | `papers://{paper_id}` | Parameterized resource |
| Prompt (extra) | `review_paper(paper_id)` | Reusable user-picked template |

## Setup
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install "mcp>=2.2"
```

## Demo options (pick one or more)
1. **Raw JSON-RPC over stdio** (best for showing the wire format):
   `python wire_demo.py --pause` — press Enter between the 11 steps.
2. **SDK client** (what a host does internally): `python sdk_client.py`
3. **Streamable HTTP**: `python paper_server.py --http`, then in another terminal `bash http_demo.sh`
4. **MCP Inspector** (visual UI, needs Node): `npx @modelcontextprotocol/inspector python paper_server.py`
5. **In a real host** (e.g. Claude Desktop / Claude Code / VS Code). Example config:
   ```json
   { "mcpServers": { "paper-library": { "command": "python", "args": ["/full/path/paper_server.py"] } } }
   ```
   Then ask: *"Find papers about tool use and add a note to ReAct saying 'discuss in week 6'."*
   Hosts that still speak the older handshake protocol may need `pip install "mcp<2"` and the v1 `FastMCP` import; test before class.

## Backup
If the live demo fails, `sample_output.txt` has the full output of `wire_demo.py`.

## Things to point out live
- `server/discover` replaces the old `initialize` handshake. Every request carries version + capabilities in `_meta`.
- The tool list has JSON Schemas built from Python type hints.
- Step 9: a bad `paper_id` returns `isError: true` with a helpful message, so the model can fix its own call.
- Step 10: the note added by a tool shows up when you read the resource — tool = action, resource = data.
