"""
Paper Library - a small MCP server for the Graduate Seminar demo.

Exposes:
  Resource            papers://reading-list         -> the seminar reading list (data / context)
  Tool                search_papers(query)          -> searches the library (read-only action)
  Tool                add_note(paper_id, note)      -> saves a note on a paper (write action)

Extras (to show the other primitives):
  Resource template   papers://{paper_id}           -> one paper's details
  Prompt              review_paper(paper_id)        -> reusable "critique this paper" template

Run (stdio):            python paper_server.py
Run (Streamable HTTP):  python paper_server.py --http      -> http://127.0.0.1:8000/mcp
Inspect:                npx @modelcontextprotocol/inspector python paper_server.py
Requires:               pip install "mcp>=2.2"   (protocol version 2026-07-28)
"""

import json
import sys

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("paper-library")

# A tiny in-memory "database". A real server would use files, SQL, an API, etc.
PAPERS = {
    "mcp-spec": {
        "title": "Model Context Protocol Specification (2026-07-28)",
        "authors": "MCP maintainers",
        "year": 2026,
        "tags": ["mcp", "agents", "protocol"],
    },
    "react": {
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "authors": "Yao et al.",
        "year": 2023,
        "tags": ["agents", "tool use", "reasoning"],
    },
    "toolformer": {
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "authors": "Schick et al.",
        "year": 2023,
        "tags": ["tool use", "function calling"],
    },
    "rag": {
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": "Lewis et al.",
        "year": 2020,
        "tags": ["rag", "retrieval"],
    },
}
NOTES: dict[str, list[str]] = {}


# ---------- RESOURCE: provides data / context (application-controlled) ----------
@mcp.resource(
    "papers://reading-list",
    name="reading-list",
    title="Seminar Reading List",
    description="All papers in the seminar library, with any saved notes.",
    mime_type="application/json",
)
def reading_list() -> str:
    items = [{"id": pid, **p, "notes": NOTES.get(pid, [])} for pid, p in PAPERS.items()]
    return json.dumps(items, indent=2)


# ---------- RESOURCE TEMPLATE: parameterized resource (RFC 6570 URI template) ----------
@mcp.resource(
    "papers://{paper_id}",
    name="paper",
    title="Paper Details",
    description="Details for one paper, by id.",
    mime_type="application/json",
)
def paper_details(paper_id: str) -> str:
    if paper_id not in PAPERS:
        raise ResourceNotFoundError(f"Unknown paper id: {paper_id}")
    return json.dumps({"id": paper_id, **PAPERS[paper_id], "notes": NOTES.get(paper_id, [])}, indent=2)


# ---------- TOOL 1: performs an action (model-controlled) - read-only ----------
@mcp.tool(
    title="Search Papers",
    description="Search the seminar library by keyword in title, author, or tag. Returns matching paper ids.",
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
)
def search_papers(query: str) -> list[dict]:
    q = query.lower()
    return [
        {"id": pid, "title": p["title"], "year": p["year"]}
        for pid, p in PAPERS.items()
        if q in p["title"].lower() or q in p["authors"].lower() or any(q in t for t in p["tags"])
    ]


# ---------- TOOL 2: performs an action - changes state ----------
@mcp.tool(
    title="Add Note",
    description="Save a short note on a paper in the library. Use the paper id from search_papers.",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False),
)
def add_note(paper_id: str, note: str) -> str:
    if paper_id not in PAPERS:
        # Tool execution error -> returned with isError: true so the model can self-correct
        raise ToolError(f"Unknown paper id '{paper_id}'. Valid ids: {', '.join(PAPERS)}")
    NOTES.setdefault(paper_id, []).append(note)
    return f"Saved note #{len(NOTES[paper_id])} on '{PAPERS[paper_id]['title']}'."


# ---------- PROMPT: reusable interaction template (user-controlled) ----------
@mcp.prompt(title="Review a Paper", description="Ask the model for a structured seminar-style critique.")
def review_paper(paper_id: str) -> str:
    p = PAPERS.get(paper_id, {"title": paper_id})
    return (
        f"You are a discussant in a graduate seminar. Critique '{p['title']}'.\n"
        "Cover: (1) the problem, (2) the key idea, (3) evidence, (4) weaknesses, "
        "(5) two questions for the class. Keep it under 250 words."
    )


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()  # stdio
