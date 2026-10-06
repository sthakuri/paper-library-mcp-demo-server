"""
sdk_client.py - same demo using the official Python SDK client (what a host does internally).

    python sdk_client.py
"""

import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main():
    params = StdioServerParameters(command=sys.executable, args=["paper_server.py"])
    async with Client(params) as client:   # the host creates ONE client per server
        print("Server:", client.server_info.name if client.server_info else "?")
        print("Capabilities:", client.server_capabilities.model_dump(exclude_none=True))

        tools = await client.list_tools()
        print("\nTools:", [t.name for t in tools.tools])

        resources = await client.list_resources()
        print("Resources:", [str(r.uri) for r in resources.resources])

        result = await client.call_tool("search_papers", {"query": "agents"})
        print("\nsearch_papers('agents') ->", result.structured_content)

        result = await client.call_tool("add_note", {"paper_id": "mcp-spec", "note": "Stateless since 2026-07-28"})
        print("add_note ->", result.content[0].text)

        data = await client.read_resource("papers://mcp-spec")
        print("\npapers://mcp-spec ->\n", data.contents[0].text)


asyncio.run(main())
