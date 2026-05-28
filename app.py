import os
import subprocess
import json
import asyncio
from typing import Optional
import gradio as gr
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------------------------------------------------------------------------
# MCP subprocess helpers
# ---------------------------------------------------------------------------

SERVER_PARAMS = StdioServerParameters(
    command="npx",
    args=["mcp-workflowy", "server", "start"],
    env={
        **os.environ,
        "WORKFLOWY_USERNAME": os.environ.get("WORKFLOWY_USERNAME", ""),
        "WORKFLOWY_PASSWORD": os.environ.get("WORKFLOWY_PASSWORD", ""),
    },
)


async def _call_tool(tool_name: str, arguments: dict) -> str:
    """Spin up the mcp-workflowy subprocess, call a single tool, return result."""
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            # result.content is a list of TextContent / ImageContent
            texts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(texts) if texts else "(no output)"


def run_tool(tool_name: str, arguments: dict) -> str:
    return asyncio.run(_call_tool(tool_name, arguments))


# ---------------------------------------------------------------------------
# Gradio tool functions  —  clear type hints + docstrings for MCP schema
# ---------------------------------------------------------------------------


def list_nodes(parent_id: Optional[str] = None) -> str:
    """List Workflowy nodes. Returns root nodes or children of a given node.

    Args:
        parent_id: Optional node ID whose children to list. Leave empty for root.

    Returns:
        JSON-formatted list of nodes with id, name, and description.
    """
    args: dict = {}
    if parent_id and parent_id.strip():
        args["parentId"] = parent_id.strip()
    return run_tool("list_nodes", args)


def search_nodes(query: str) -> str:
    """Search Workflowy nodes by text.

    Args:
        query: Search term to look for across all node names and descriptions.

    Returns:
        JSON-formatted list of matching nodes.
    """
    return run_tool("search_nodes", {"query": query})


def create_node(name: str, description: str = "", parent_id: str = "") -> str:
    """Create a new Workflowy node.

    Args:
        name: The text/title of the new node.
        description: Optional description / notes for the node.
        parent_id: Optional parent node ID. Leave empty to create at root.

    Returns:
        The created node as JSON.
    """
    args: dict = {"name": name}
    if description.strip():
        args["description"] = description.strip()
    if parent_id.strip():
        args["parentId"] = parent_id.strip()
    return run_tool("create_node", args)


def update_node(node_id: str, name: str = "", description: str = "") -> str:
    """Update an existing Workflowy node's text or description.

    Args:
        node_id: The ID of the node to update.
        name: New text/title for the node (optional).
        description: New description for the node (optional).

    Returns:
        The updated node as JSON.
    """
    args: dict = {"id": node_id}
    if name.strip():
        args["name"] = name.strip()
    if description.strip():
        args["description"] = description.strip()
    return run_tool("update_node", args)


def toggle_complete(node_id: str, complete: bool = True) -> str:
    """Mark a Workflowy node as complete or incomplete.

    Args:
        node_id: The ID of the node to update.
        complete: True to mark complete, False to mark incomplete.

    Returns:
        Confirmation message with the updated node state.
    """
    return run_tool("toggle_complete", {"id": node_id, "complete": complete})


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="Workflowy MCP", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
# 📝 Workflowy MCP Server
A Gradio wrapper around [`mcp-workflowy`](https://www.npmjs.com/package/mcp-workflowy)
that exposes Workflowy operations as an MCP-compatible server on HuggingFace Spaces.

Set **`WORKFLOWY_USERNAME`** and **`WORKFLOWY_PASSWORD`** as Space secrets before using.
        """
    )

    with gr.Tab("List Nodes"):
        parent_in = gr.Textbox(label="Parent Node ID (optional)", placeholder="Leave blank for root")
        list_btn = gr.Button("List")
        list_out = gr.Textbox(label="Result", lines=12)
        list_btn.click(list_nodes, inputs=[parent_in], outputs=[list_out])

    with gr.Tab("Search"):
        query_in = gr.Textbox(label="Query")
        search_btn = gr.Button("Search")
        search_out = gr.Textbox(label="Result", lines=12)
        search_btn.click(search_nodes, inputs=[query_in], outputs=[search_out])

    with gr.Tab("Create Node"):
        cn_name = gr.Textbox(label="Name")
        cn_desc = gr.Textbox(label="Description (optional)")
        cn_parent = gr.Textbox(label="Parent ID (optional)")
        cn_btn = gr.Button("Create")
        cn_out = gr.Textbox(label="Result", lines=6)
        cn_btn.click(create_node, inputs=[cn_name, cn_desc, cn_parent], outputs=[cn_out])

    with gr.Tab("Update Node"):
        un_id = gr.Textbox(label="Node ID")
        un_name = gr.Textbox(label="New Name (optional)")
        un_desc = gr.Textbox(label="New Description (optional)")
        un_btn = gr.Button("Update")
        un_out = gr.Textbox(label="Result", lines=6)
        un_btn.click(update_node, inputs=[un_id, un_name, un_desc], outputs=[un_out])

    with gr.Tab("Toggle Complete"):
        tc_id = gr.Textbox(label="Node ID")
        tc_flag = gr.Checkbox(label="Mark as complete", value=True)
        tc_btn = gr.Button("Toggle")
        tc_out = gr.Textbox(label="Result", lines=4)
        tc_btn.click(toggle_complete, inputs=[tc_id, tc_flag], outputs=[tc_out])


if __name__ == "__main__":
    demo.launch(mcp_server=True)
