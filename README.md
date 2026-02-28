# MCP Agent — Build and Conquer Your Digital Empire

Your AI-powered command center for creating and conquering digital empires. This framework turns the [SearchAtlas](https://searchatlas.com) MCP (Model Context Protocol) into a programmable army of 112 tools that build your online presence, crush competitors in search, and establish dominance across every digital channel — all on autopilot.

## Playbook of Playbooks

The complete 5-day challenge journey — Pre-Work through Day 5 — with all 15 playbooks, 112 MCP tools, and 17 agent namespaces mapped out.

<p align="center">
  <a href="playbook-of-playbooks.html">
    <img src="playbook-of-playbooks.png" alt="5-Day Digital Empire Blueprint — Playbook of Playbooks" width="720">
  </a>
</p>

<p align="center"><i>Click the image to open the <a href="playbook-of-playbooks.html">full interactive HTML version</a> with the SearchAtlas dark theme.</i></p>

## The 5-Day Empire Blueprint

One agent. 112 tools. Five days to total digital dominance.

| Day | Mission | Arsenal |
|-----|---------|---------|
| **1** | **Establish Your Kingdom** — Build your digital HQ, lock in brand identity, claim your territory on Google | Website Studio, Brand Vault, GBP, Local SEO |
| **2** | **Content Domination** — Flood the SERPs with authority content, outrank competitors with topical maps, own every keyword | Content Genius, OTTO SEO, Site Explorer |
| **3** | **Build Your Alliance Network** — Earn backlinks, place press releases on Tier 1 publishers, deploy cloud stacks, launch outreach campaigns | Press Release, Cloud Stack, Digital PR, LinkLab, Citations |
| **4** | **Expand Your Reach** — Activate paid channels, launch Google Ads, amplify through social | PPC/Google Ads, GBP Posts |
| **5** | **Intelligence & Scale** — Monitor your empire, track rankings, measure AI visibility, identify the next territory to conquer | LLM Visibility, Site Explorer, Local SEO Heatmaps |

## MCP Server

```
Endpoint: https://mcp.searchatlas.com/api/v1/mcp
Protocol: JSON-RPC 2.0
Auth:     X-API-KEY header
```

### Calling a Tool

```bash
export MCP_API_KEY="your-api-key"

curl -s -X POST "https://mcp.searchatlas.com/api/v1/mcp" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $MCP_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "project_management",
      "arguments": {
        "op": "list_otto_projects",
        "params": {}
      }
    }
  }'
```

### Listing All Tools

```bash
curl -s -X POST "https://mcp.searchatlas.com/api/v1/mcp" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $MCP_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Your Arsenal (112 tools)

| Category | Tools | What It Conquers |
|----------|-------|------------------|
| **OTTO SEO** | 15 | On-page optimization, schema markup, knowledge graphs, instant indexing, wildfire backlinks |
| **PPC / Google Ads** | 13 | Campaign creation, ad groups, keyword targeting, product feeds, bid management |
| **Site Explorer** | 8 | Competitor intelligence, organic keyword gaps, backlink analysis, keyword research |
| **Content Genius** | 7 | AI article generation, topical authority maps, DKN, publishing to 11+ CMS platforms |
| **GBP** | 16 | Location management, automated posting, review responses, local search domination |
| **Local SEO** | 7 | Heatmap tracking, citation building, AI recommendations, local rank monitoring |
| **Press Release** | 4 | Tier 1 publisher distribution, knowledge graphs, brand mention campaigns |
| **Cloud Stack** | 4 | Authority backlinks across 14+ cloud providers |
| **Digital PR** | 4 | Publisher outreach campaigns, email templates, inbox management |
| **LinkLab** | 4 | Guest post placements, publisher marketplace, editorial link building |
| **LLM Visibility** | 8 | Brand presence across AI models, sentiment tracking, citation monitoring, prompt simulation |
| **Brand Vault** | 1 | Brand identity, voice profiles, company intelligence |
| **Website Studio** | 1 | AI website generation and one-click publishing |

## Summit Challenge Playbooks

[`summit-challenge-playbooks.json`](summit-challenge-playbooks.json) contains **15 battle-tested playbook definitions** from the AI Search & Agentic Marketing Summit weekly challenge. Each playbook is a complete mission briefing:

- Step-by-step instructions telling the agent exactly which MCP tools to deploy and in what order
- Pre-work checklist with setup URLs
- Sample prompts you can paste directly into Atlas Brain
- Expected impact for each campaign

**Your Playbook Library:**

| # | Mission | Day | Time |
|---|---------|-----|------|
| 1 | Review & Complete Brand Vault | 2 | 5 min |
| 2 | Build Topical Map Content Strategy | 2 | 15 min |
| 3 | Increase Organic Traffic with Quality Content | 2 | 20 min |
| 4 | AI-Optimized Industry Leader Listicle Builder | 2 | 15 min |
| 5 | AI-Optimized Head-to-Head Content | 2 | 15 min |
| 6 | AI Optimized About Us Page Creator | 2 | 10 min |
| 7 | AI-Optimized Industry Leader Content Creation | 2 | 15 min |
| 8 | Automated GBP Review Response & Amplification Engine | 2 | 15 min |
| 9 | Gain Media Coverage and Brand Mentions | 3 | 10 min |
| 10 | Deploy Single Cloud Stack Authority Order | 3 | 10 min |
| 11 | Deploy Link Labs Guest Post Campaign | 3 | 15 min |
| 12 | Create Local Directory Citations | 3 | 5 min |
| 13 | Strengthen On-Page SEO for Priority Pages | 3 | 15 min |
| 14 | Publisher Prospecting Outreach Playbook | 3 | 15 min |
| 15 | Business Prospecting Outreach Playbook | 3 | 15 min |

Load the JSON into your agent or paste individual playbook instructions into Atlas Brain to execute the full challenge workflow programmatically.

## Repo Structure

```
README.md                          # This file — your empire-building guide
CLAUDE.md                          # Project context for Claude Code agents
AGENT_PLAYBOOK.md                  # Golden rules, full 112-tool registry, verified schemas
summit-challenge-playbooks.json    # 15 ready-to-run summit challenge playbooks
playbook-of-playbooks.html         # Interactive visual diagram of the full 5-day challenge
EXECUTION_REPORT.md                # Historical log from 4 execution runs (40% -> 78%)
discover_tools.sh                  # Batch tool schema discovery script
examples/
  citation_test.json               # Sample citation submission payload
  omni_law_current.json            # Example GBP location API response
```

## Golden Rules

Hard-won lessons from 4 execution runs:

1. **Schema Discovery First** -- Always send an empty call to discover the real schema. Documentation has wrong parameter names for many tools.
2. **Read Error Messages** -- Distinguish between param validation, auth blocks, and backend errors.
3. **Don't Fabricate Timelines** -- Use actual API timestamps.
4. **Poll Async Tasks** -- Many operations return a `task_id`. Poll with `get_otto_task_status` until `SUCCESS`.
5. **Watch for Tool Name Collisions** -- Multiple tools share the same short name. The MCP server routes to the first match in the registry.

See [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md) for the full battle manual.

## Quick Start

1. Get an API key for the SearchAtlas MCP server
2. Set it as an environment variable:
   ```bash
   export MCP_API_KEY="your-api-key"
   ```
3. Run tool discovery:
   ```bash
   ./discover_tools.sh
   ```
4. Start conquering.

## License

Proprietary -- [SearchAtlas](https://searchatlas.com)
