#!/usr/bin/env bash
# http_demo.sh - call the server over Streamable HTTP with plain curl.
# First, in another terminal:  python paper_server.py --http
URL=http://127.0.0.1:8000/mcp
META='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}'

call () {  # $1 = method, $2 = extra params (JSON fragment), $3 = tool/prompt name for Mcp-Name header
  echo; echo "=== $1 ==="
  curl -s -X POST "$URL" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -H "Mcp-Method: $1" \
    ${3:+-H "Mcp-Name: $3"} \
    -H 'MCP-Protocol-Version: 2026-07-28' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":{$2$META}}"
  echo
}

call server/discover ""
call tools/list ""
# New in 2026-07-28: tools/call must also send Mcp-Name, matching the body (so proxies can route without parsing JSON)
call tools/call '"name":"search_papers","arguments":{"query":"rag"},' search_papers
