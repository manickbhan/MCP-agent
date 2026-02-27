# MCP Agent — Project Context

## What This Is

AI agent orchestration framework for executing marketing workflows via the [SearchAtlas](https://searchatlas.com) MCP (Model Context Protocol). This repo contains playbooks, tool references, and execution guides for programmatically running end-to-end digital marketing campaigns through 112 MCP tools across 13 product areas.

## MCP Server

- **Endpoint:** `https://mcp.searchatlas.com/api/v1/mcp`
- **Protocol:** JSON-RPC 2.0, method `tools/call`
- **Auth Header:** `X-API-KEY`

## Key Files

| File | Purpose |
|------|---------|
| `AGENT_PLAYBOOK.md` | **Start here.** Golden rules, full 112-tool registry with schemas, verified workflows. |
| `summit-challenge-playbooks.json` | 15 ready-to-run playbook definitions from the AI Search Summit challenge (Days 2–3). |
| `README.md` | Project overview, tool categories, setup instructions. |
| `discover_tools.sh` | Batch tool discovery script — use to verify current tool names and schemas. |
| `EXECUTION_REPORT.md` | Historical log from 4 execution runs showing progression from 40% to 78% success rate. |

## How to Call a Tool

```bash
curl -s -X POST "https://mcp.searchatlas.com/api/v1/mcp" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $MCP_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"<TOOL_NAME>","arguments":{"op":"<OPERATION>","params":{...}}}}'
```

## Golden Rules (Summary)

1. **Schema Discovery First** — Always send an empty call to discover the real schema. Documentation may have wrong parameter names.
2. **Read Error Messages** — Distinguish between param validation, auth blocks, and backend errors.
3. **Don't Fabricate Timelines** — Use actual API timestamps.
4. **Poll Async Tasks** — Many operations return a `task_id`. Poll until `SUCCESS`.
5. **Watch for Tool Name Collisions** — Multiple tools share short names. The MCP server routes to the first match.
6. **Never Invent Tool Names** — If `tools/list` doesn't show it, it doesn't exist.

See `AGENT_PLAYBOOK.md` for the complete golden rules with examples and the full tool registry.

## Tool Categories (112 tools)

| Category | Tools | Key Operations |
|----------|-------|----------------|
| OTTO SEO | 15 | Project management, audits, schema markup, knowledge graphs, indexing, wildfire backlinks |
| PPC / Google Ads | 13 | Business setup, campaign creation, ad groups, keywords, product feeds |
| Site Explorer | 8 | Organic keywords, backlinks, competitor analysis, keyword research |
| Content Genius | 7 | Article generation, topical maps, DKN, publication to 11+ CMS platforms |
| GBP | 16 | Locations, posts, reviews, categories, services, attributes, media, automation |
| Local SEO | 7 | Business profiles, heatmap grids, analytics, citations, AI recommendations |
| Press Release | 4 | Knowledge graphs, content creation, distribution |
| Cloud Stack | 4 | Content syndication to 14+ cloud providers |
| Digital PR | 4 | Campaigns, templates, outreach opportunities, inbox management |
| LinkLab | 4 | Link building projects, publications, articles, orders |
| LLM Visibility | 8 | Brand visibility across LLMs, sentiment, citations, prompt simulation |
| Brand Vault | 1 | Brand identity and voice profile management |
| Website Studio | 1 | AI website generation and publishing |
