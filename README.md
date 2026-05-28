---
title: Workflowy MCP
emoji: 📝
colorFrom: teal
colorTo: green
sdk: docker
pinned: false
---

# Workflowy MCP Server on HuggingFace Spaces

A **Gradio** wrapper around [`mcp-workflowy`](https://www.npmjs.com/package/mcp-workflowy) that exposes Workflowy operations as a fully MCP-compatible server hosted on HuggingFace Spaces.

## Setup

### 1. Set Secrets

In your Space settings → **Secrets**, add:

| Secret | Value |
|---|---|
| `WORKFLOWY_USERNAME` | Your Workflowy email |
| `WORKFLOWY_PASSWORD` | Your Workflowy password |

### 2. Deploy

Push this repo to a HuggingFace Space with the **Docker** SDK (already set in the README front-matter). The Space will automatically build and launch.

## Available MCP Tools

| Tool | Description |
|---|---|
| `list_nodes` | List root nodes or children of a node |
| `search_nodes` | Full-text search across all nodes |
| `create_node` | Create a new node (optionally under a parent) |
| `update_node` | Update name / description of an existing node |
| `toggle_complete` | Mark a node complete or incomplete |

## Using as an MCP Server

Once the Space is running, add it to any MCP client by pointing to:

```
https://<your-hf-username>-workflowy-mcp.hf.space/gradio_api/mcp/sse
```

Or use the **Add to MCP tools** button that appears on the Space card (the Space will show the grey **MCP** badge automatically).

## Local Development

```bash
# Requires Node 18+ and Python 3.11+
npm install -g mcp-workflowy
pip install "gradio[mcp]>=4.40.0" mcp

export WORKFLOWY_USERNAME=you@example.com
export WORKFLOWY_PASSWORD=yourpassword

python app.py
```

## Architecture

```
HuggingFace Space (Docker)
└── Gradio app  (app.py)
    └── mcp_server=True  → exposes /gradio_api/mcp/sse
        └── Each tool spins up npx mcp-workflowy via MCP stdio transport
            └── mcp-workflowy  →  Workflowy API
```

## License

MIT
