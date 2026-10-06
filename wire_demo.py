"""
wire_demo.py - talks to paper_server.py over stdio with RAW JSON-RPC,
so you can see exactly what goes over the wire (protocol 2026-07-28).

    python wire_demo.py            # run all steps
    python wire_demo.py --pause    # press Enter between steps (good for live demo)
"""

import json
import subprocess
import sys

PAUSE = "--pause" in sys.argv
META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "seminar-wire-demo", "version": "1.0"},
    "io.modelcontextprotocol/clientCapabilities": {},
}

server = subprocess.Popen(
    [sys.executable, "paper_server.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
)
_next_id = 0


def rpc(method, params=None, title=""):
    global _next_id
    _next_id += 1
    msg = {"jsonrpc": "2.0", "id": _next_id, "method": method,
           "params": {**(params or {}), "_meta": META}}
    print(f"\n=== {title or method} ===")
    shown = {**msg, "params": {k: v for k, v in msg["params"].items() if k != "_meta"} | {"_meta": "{...}"}}
    print("-> " + json.dumps(shown))
    server.stdin.write(json.dumps(msg) + "\n")   # stdio framing: one JSON message per line
    server.stdin.flush()
    while True:
        reply = json.loads(server.stdout.readline())
        if reply.get("id") == _next_id:
            break
    result = reply.get("result", reply.get("error"))
    if isinstance(result, dict):
        result.pop("_meta", None)
    print("<- " + json.dumps(result, indent=2)[:2500])
    if PAUSE:
        input("   [Enter] ")
    return result


rpc("server/discover", title="1. Discovery: who are you, what can you do?")
rpc("tools/list", title="2. Tool discovery")
rpc("resources/list", title="3. Resource discovery")
rpc("resources/templates/list", title="4. Resource template discovery")
rpc("prompts/list", title="5. Prompt discovery")
rpc("resources/read", {"uri": "papers://reading-list"}, title="6. Read the resource (data/context)")
rpc("tools/call", {"name": "search_papers", "arguments": {"query": "tool use"}}, title="7. Call tool 1: search (action)")
rpc("tools/call", {"name": "add_note", "arguments": {"paper_id": "react", "note": "Discuss in week 6"}},
    title="8. Call tool 2: add_note (state-changing action)")
rpc("tools/call", {"name": "add_note", "arguments": {"paper_id": "gpt5", "note": "x"}},
    title="9. Tool error -> isError:true, model can self-correct")
rpc("resources/read", {"uri": "papers://react"}, title="10. Read via template: note now appears")
rpc("prompts/get", {"name": "review_paper", "arguments": {"paper_id": "rag"}}, title="11. Get prompt template")

server.terminate()
