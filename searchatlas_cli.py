#!/usr/bin/env python3
"""SearchAtlas MCP CLI — command-line client for the Agentic Omnichannel Marketing MCP.

Wraps the 112-tool MCP server at mcp.searchatlas.com into a direct CLI usable
by Claude, OpenClaw, or any terminal workflow.

Usage:
  searchatlas tools                              # List all 112 tools
  searchatlas tools --category otto              # Filter by category
  searchatlas discover project_management list_otto_projects  # Schema discovery
  searchatlas call project_management list_otto_projects      # Execute a tool
  searchatlas call brand_vault get_brand_vault_overview --params '{"hostname":"searchatlas.com"}'
  searchatlas status <task_id>                   # Poll async task
  searchatlas playbook list                      # List 15 summit playbooks
  searchatlas playbook show 3                    # Show playbook details
  searchatlas playbook run 1                     # Show step-by-step execution plan

Requires: MCP_API_KEY env var (or --api-key flag)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()
log = logging.getLogger("searchatlas")

MCP_ENDPOINT = "https://mcp.searchatlas.com/api/v1/mcp"
PLAYBOOK_FILE = Path(__file__).parent / "summit-challenge-playbooks.json"

# ---------------------------------------------------------------------------
# MCP JSON-RPC transport
# ---------------------------------------------------------------------------


class MCPClient:
    """Thin JSON-RPC 2.0 client for the SearchAtlas MCP server."""

    def __init__(self, api_key: str, endpoint: str = MCP_ENDPOINT):
        self.api_key = api_key
        self.endpoint = endpoint
        self._http = httpx.Client(
            timeout=60.0,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key,
            },
        )
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def list_tools(self) -> dict:
        """Call tools/list to discover all available tools."""
        return self._jsonrpc("tools/list", {})

    def call_tool(self, name: str, op: str, params: dict | None = None) -> dict:
        """Call tools/call with a specific tool, operation, and params."""
        arguments = {"op": op, "params": params or {}}
        return self._jsonrpc("tools/call", {"name": name, "arguments": arguments})

    def discover_schema(self, name: str, op: str) -> dict:
        """Send an intentionally empty call to discover the real schema.

        The MCP server returns the expected schema in error responses (Golden Rule 1).
        """
        return self.call_tool(name, op, {})

    def _jsonrpc(self, method: str, params: dict) -> dict:
        """Send a JSON-RPC 2.0 request."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }
        log.debug("POST %s method=%s", self.endpoint, method)
        log.debug("Payload: %s", json.dumps(payload, indent=2))

        resp = self._http.post(self.endpoint, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            log.debug("RPC error: %s", data["error"])

        return data

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOOL_CATEGORIES = {
    "otto": {
        "label": "OTTO SEO",
        "tools": [
            "image_upload",
            "indexing_management",
            "knowledge_graph",
            "OTTO_Installations",
            "quota_management",
            "project_management",
            "recrawl_management",
            "schema_markup",
            "seo_analysis",
            "audit_management",
            "seo_deployment",
            "suggestion_management",
            "attachments",
            "task_management",
            "wildfire",
        ],
    },
    "ppc": {
        "label": "PPC / Google Ads",
        "tools": [
            "ads_account_crud",
            "ads_account_mgmt",
            "campaign",
            "product_crud",
            "product_mgmt",
            "business_crud",
            "business_mgmt",
            "task",
            "ad_group",
            "ad_content",
            "keyword_cluster",
            "keyword",
        ],
    },
    "site": {
        "label": "Site Explorer",
        "tools": [
            "backlinks",
            "organic",
            "analysis",
            "adwords",
            "brand_signals",
            "holistic_audit",
            "keyword_research",
            "projects",
        ],
    },
    "content": {
        "label": "Content Genius",
        "tools": [
            "content_generation",
            "article_management",
            "dkn",
            "content_retrieval",
            "content_publication",
            "folder_management",
            "topical_maps",
        ],
    },
    "gbp": {
        "label": "Google Business Profile",
        "tools": [
            "connections",
            "gbp_locations_crud",
            "gbp_locations_deployment",
            "gbp_locations_recommendations",
            "gbp_locations_categories_crud",
            "gbp_locations_services_crud",
            "gbp_locations_attributes_crud",
            "gbp_locations_medias_crud",
            "posts_crud",
            "posts_generation",
            "posts_automation",
            "posts_social",
            "reviews",
            "stats",
            "tasks",
            "utility",
        ],
    },
    "local": {
        "label": "Local SEO",
        "tools": [
            "business",
            "grids",
            "data",
            "analytics",
            "ai",
            "citation",
        ],
    },
    "pr": {
        "label": "Press Release",
        "tools": ["content", "distribution", "knowledge_graph", "payment"],
    },
    "cloud": {
        "label": "Cloud Stack",
        "tools": ["content", "distribution", "knowledge_graph", "payment"],
    },
    "dpr": {
        "label": "Digital PR",
        "tools": ["campaigns", "inbox", "templates", "opportunities"],
    },
    "linklab": {
        "label": "LinkLab",
        "tools": ["articles", "orders", "projects", "publications"],
    },
    "geo": {
        "label": "LLM Visibility / GEO",
        "tools": [
            "visibility",
            "sentiment",
            "citations",
            "topics",
            "queries",
            "prompt_simulator",
        ],
    },
    "brand": {
        "label": "Brand Vault",
        "tools": ["brand_vault"],
    },
    "studio": {
        "label": "Website Studio",
        "tools": ["website_studio_tools"],
    },
    "gsc": {
        "label": "GSC Tools",
        "tools": ["GSC_Performance_Tool", "GSC_Site_Events_Tool"],
    },
    "util": {
        "label": "Utilities",
        "tools": ["batch", "reports"],
    },
}


def _get_api_key(ctx_key: str | None) -> str:
    key = ctx_key or os.environ.get("MCP_API_KEY")
    if not key:
        console.print(
            "[red]Error:[/red] MCP_API_KEY not set. "
            "Pass --api-key or set the MCP_API_KEY environment variable."
        )
        sys.exit(1)
    return key


def _load_playbooks() -> list[dict]:
    if not PLAYBOOK_FILE.exists():
        console.print(f"[red]Error:[/red] Playbook file not found: {PLAYBOOK_FILE}")
        sys.exit(1)
    data = json.loads(PLAYBOOK_FILE.read_text())
    return data.get("playbooks", [])


def _output(data: dict, fmt: str) -> None:
    """Output response in requested format."""
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        # Extract the meaningful content
        if "result" in data:
            result = data["result"]
            if isinstance(result, list) and len(result) == 1:
                content = result[0]
                if isinstance(content, dict) and "text" in content:
                    try:
                        parsed = json.loads(content["text"])
                        console.print(Syntax(json.dumps(parsed, indent=2), "json"))
                    except (json.JSONDecodeError, TypeError):
                        console.print(content["text"])
                else:
                    console.print(Syntax(json.dumps(content, indent=2), "json"))
            elif isinstance(result, list):
                console.print(Syntax(json.dumps(result, indent=2), "json"))
            else:
                console.print(Syntax(json.dumps(result, indent=2), "json"))
        elif "error" in data:
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            console.print(f"[red]Error:[/red] {msg}")
            # Show the full error for schema discovery
            if isinstance(err, dict) and "data" in err:
                console.print(Syntax(json.dumps(err["data"], indent=2), "json"))
        else:
            console.print(Syntax(json.dumps(data, indent=2), "json"))


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.option("--api-key", default=None, envvar="MCP_API_KEY", help="MCP API key.")
@click.option("-v", "--verbose", is_flag=True, help="Debug logging.")
@click.pass_context
def cli(ctx, api_key, verbose):
    """SearchAtlas MCP CLI — 112 omnichannel marketing tools at your fingertips."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key


# ---------------------------------------------------------------------------
# tools — list all available MCP tools
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--category",
    "-c",
    default=None,
    type=click.Choice(list(TOOL_CATEGORIES.keys())),
    help="Filter by tool category.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def tools(ctx, category, fmt):
    """List all 112 MCP tools (or filter by category)."""
    if category:
        cat = TOOL_CATEGORIES[category]
        if fmt == "json":
            click.echo(json.dumps(cat, indent=2))
            return
        table = Table(
            title=f"{cat['label']} Tools",
            show_header=True,
            expand=True,
        )
        table.add_column("#", style="dim", max_width=4)
        table.add_column("Tool Name", style="cyan")
        for i, t in enumerate(cat["tools"], 1):
            table.add_row(str(i), t)
        console.print(table)
        return

    # Live discovery from MCP server
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(
            "[bold blue]Fetching tool list from MCP server...[/bold blue]"
        ):
            resp = client.list_tools()

    if fmt == "json":
        click.echo(json.dumps(resp, indent=2))
        return

    tool_list = resp.get("result", {}).get("tools", [])
    if not tool_list:
        # Try alternate response shapes
        tool_list = resp.get("result", [])
        if isinstance(tool_list, dict):
            tool_list = tool_list.get("tools", [])

    table = Table(
        title=f"MCP Tools ({len(tool_list)})",
        show_header=True,
        expand=True,
    )
    table.add_column("#", style="dim", max_width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Description", ratio=1)

    for i, t in enumerate(tool_list, 1):
        name = t.get("name", "?") if isinstance(t, dict) else str(t)
        desc = t.get("description", "")[:80] if isinstance(t, dict) else ""
        table.add_row(str(i), name, desc)

    console.print(table)


# ---------------------------------------------------------------------------
# discover — schema discovery (Golden Rule 1)
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("tool_name")
@click.argument("operation")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def discover(ctx, tool_name, operation, fmt):
    """Discover the real schema for a tool+operation by sending an empty call.

    The MCP server returns expected parameter schemas in error responses.
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(
            f"[bold blue]Discovering schema: {tool_name} -> {operation}[/bold blue]"
        ):
            resp = client.discover_schema(tool_name, operation)

    if fmt == "json":
        click.echo(json.dumps(resp, indent=2))
    else:
        console.print(
            Panel(
                f"[bold cyan]{tool_name}[/bold cyan] -> [yellow]{operation}[/yellow]",
                title="Schema Discovery",
                border_style="blue",
            )
        )
        _output(resp, "rich")


# ---------------------------------------------------------------------------
# call — execute any tool + operation
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("tool_name")
@click.argument("operation")
@click.option("--params", "-p", default="{}", help="JSON params (default: {}).")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.option("--dry-run", is_flag=True, help="Show the request without sending.")
@click.pass_context
def call(ctx, tool_name, operation, params, fmt, dry_run):
    """Execute an MCP tool call.

    Examples:
      searchatlas call project_management list_otto_projects
      searchatlas call brand_vault get_brand_vault_overview -p '{"hostname":"searchatlas.com"}'
      searchatlas call seo_analysis get_project_issues_summary -p '{"project_uuid":"abc123"}'
    """
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON params:[/red] {exc}")
        sys.exit(1)

    if dry_run:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {"op": operation, "params": params_dict},
            },
        }
        console.print("[yellow]DRY RUN[/yellow] — would send:")
        console.print(Syntax(json.dumps(payload, indent=2), "json"))
        return

    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool_name} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool_name, operation, params_dict)

    _output(resp, fmt)


# ---------------------------------------------------------------------------
# status — poll async task status
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("task_id")
@click.option(
    "--tool",
    "tool_type",
    type=click.Choice(["otto", "ppc"]),
    default="otto",
    show_default=True,
    help="Which task management tool to use.",
)
@click.option("--poll", is_flag=True, help="Poll until SUCCESS/FAILURE (5s intervals).")
@click.option(
    "--timeout", default=120, show_default=True, help="Max poll time in seconds."
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def status(ctx, task_id, tool_type, poll, timeout, fmt):
    """Check or poll async task status.

    OTTO tasks: uses task_management -> get_otto_task_status
    PPC tasks:  uses task -> get_otto_ppc_task_status
    """
    tool_map = {
        "otto": ("task_management", "get_otto_task_status"),
        "ppc": ("task", "get_otto_ppc_task_status"),
    }
    tool_name, op_name = tool_map[tool_type]
    key = _get_api_key(ctx.obj["api_key"])

    with MCPClient(key) as client:
        start = time.time()
        while True:
            with console.status(f"[bold blue]Checking task {task_id}...[/bold blue]"):
                resp = client.call_tool(tool_name, op_name, {"task_id": task_id})

            _output(resp, fmt)

            if not poll:
                break

            # Check if done
            result_text = ""
            result = resp.get("result", [])
            if isinstance(result, list) and result:
                item = result[0]
                if isinstance(item, dict):
                    result_text = item.get("text", "")

            status_val = ""
            try:
                parsed = json.loads(result_text)
                status_val = str(parsed.get("status", parsed.get("state", ""))).upper()
            except (json.JSONDecodeError, TypeError, AttributeError):
                status_val = result_text.upper() if result_text else ""

            if status_val in ("SUCCESS", "COMPLETED", "FAILED", "ERROR"):
                console.print(f"[bold]Final status: {status_val}[/bold]")
                break

            if time.time() - start > timeout:
                console.print("[yellow]Timeout reached — task still running.[/yellow]")
                break

            console.print("[dim]Waiting 5s...[/dim]")
            time.sleep(5)


# ---------------------------------------------------------------------------
# wait — convenience wrapper for otto_wait
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--seconds", "-s", default=5, show_default=True, help="Seconds to wait.")
@click.option(
    "--tool",
    "tool_type",
    type=click.Choice(["otto", "ppc"]),
    default="otto",
    show_default=True,
)
@click.pass_context
def wait(ctx, seconds, tool_type):
    """Server-side wait (calls otto_wait on the MCP server)."""
    tool_map = {"otto": "task_management", "ppc": "task"}
    tool_name = tool_map[tool_type]
    key = _get_api_key(ctx.obj["api_key"])

    with MCPClient(key) as client:
        with console.status(f"[bold blue]Waiting {seconds}s...[/bold blue]"):
            resp = client.call_tool(tool_name, "otto_wait", {})
    _output(resp, "rich")


# ---------------------------------------------------------------------------
# playbook — summit challenge playbook management
# ---------------------------------------------------------------------------


@cli.group()
def playbook():
    """Summit challenge playbooks — 15 ready-to-run marketing workflows."""
    pass


@playbook.command("list")
def playbook_list():
    """List all 15 summit challenge playbooks."""
    playbooks = _load_playbooks()

    table = Table(
        title="Summit Challenge Playbooks (15)",
        show_header=True,
        expand=True,
    )
    table.add_column("#", style="dim", max_width=4)
    table.add_column("Day", style="yellow", max_width=4)
    table.add_column("Playbook", style="cyan", ratio=1)
    table.add_column("Time", max_width=8)
    table.add_column("Agents", style="dim")

    for i, pb in enumerate(playbooks, 1):
        table.add_row(
            str(i),
            str(pb.get("day", "?")),
            pb["name"],
            pb.get("time_estimate", "?"),
            ", ".join(pb.get("agent_namespaces", [])),
        )

    console.print(table)


@playbook.command("show")
@click.argument("number", type=int)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
def playbook_show(number, fmt):
    """Show details of a specific playbook by number (1-15)."""
    playbooks = _load_playbooks()
    if number < 1 or number > len(playbooks):
        console.print(f"[red]Invalid playbook number. Choose 1-{len(playbooks)}.[/red]")
        sys.exit(1)

    pb = playbooks[number - 1]

    if fmt == "json":
        click.echo(json.dumps(pb, indent=2))
        return

    console.print(
        Panel(
            f"[bold]{pb['name']}[/bold]\n\n"
            f"Day {pb.get('day', '?')} | Action #{pb.get('action_number', '?')} | "
            f"Est. {pb.get('time_estimate', '?')}\n\n"
            f"[dim]{pb.get('description', '')}[/dim]",
            title=f"[bold blue]Playbook #{number}[/bold blue]",
            border_style="blue",
        )
    )

    console.print()
    console.print(
        Panel(
            pb.get("instruction", "No instructions."),
            title="Instructions",
            border_style="green",
        )
    )

    benefits = pb.get("expected_benefits", [])
    if benefits:
        console.print()
        for b in benefits:
            console.print(f"  [green]+[/green] {b}")

    sample = pb.get("sample_prompt") or pb.get("sample_chat")
    if sample:
        console.print()
        console.print(f"[dim]Sample: {sample}[/dim]")


@playbook.command("run")
@click.argument("number", type=int)
def playbook_run(number):
    """Show the MCP tool calls needed to execute a playbook.

    Extracts tool references from the playbook instructions and maps them
    to concrete CLI commands.
    """
    playbooks = _load_playbooks()
    if number < 1 or number > len(playbooks):
        console.print(f"[red]Invalid playbook number. Choose 1-{len(playbooks)}.[/red]")
        sys.exit(1)

    pb = playbooks[number - 1]
    instruction = pb.get("instruction", "")

    console.print(
        Panel(
            f"[bold]{pb['name']}[/bold] — Day {pb.get('day', '?')}",
            title=f"[bold blue]Execution Plan: Playbook #{number}[/bold blue]",
            border_style="blue",
        )
    )
    console.print()

    # Extract tool calls from instruction text (pattern: "Use tool_name" or "tool -> op")
    import re

    # Find patterns like "tool_name → operation" in instruction text
    arrow_refs = re.findall(r"(\w+)\s*(?:→|->)\s*(\w+)", instruction)

    if arrow_refs:
        console.print("[bold]Detected MCP tool calls:[/bold]")
        console.print()
        for tool, op in arrow_refs:
            cmd = f"searchatlas call {tool} {op}"
            console.print(f"  [cyan]$[/cyan] {cmd}")
        console.print()

    console.print("[bold]Full instructions:[/bold]")
    console.print()
    console.print(Markdown(instruction))


# ---------------------------------------------------------------------------
# Convenience category commands
# ---------------------------------------------------------------------------


@cli.command("brand")
@click.argument("operation", default="list_brand_vaults")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option("--hostname", "-h", default=None, help="Shortcut: set hostname param.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def brand(ctx, operation, params, hostname, fmt):
    """Brand Vault operations.

    Common ops: list_brand_vaults, retrieve_brand_vault_details,
    get_brand_vault_overview, get_brand_vault_business_info,
    ask_brand_vault, update_brand_vault, get_knowledge_graph
    """
    params_dict = json.loads(params)
    if hostname:
        params_dict["hostname"] = hostname
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]brand_vault -> {operation}...[/bold blue]"):
            resp = client.call_tool("brand_vault", operation, params_dict)
    _output(resp, fmt)


@cli.command("otto")
@click.argument("tool", default="project_management")
@click.argument("operation", default="list_otto_projects")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def otto(ctx, tool, operation, params, fmt):
    """OTTO SEO operations.

    Tools: project_management, seo_analysis, audit_management,
    schema_markup, indexing_management, wildfire, seo_deployment,
    suggestion_management, recrawl_management, knowledge_graph
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool, operation, json.loads(params))
    _output(resp, fmt)


@cli.command("geo")
@click.argument("operation", default="get_brand_overview")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def geo(ctx, operation, params, fmt):
    """LLM Visibility / GEO operations.

    Common ops: get_brand_overview, get_visibility_trend,
    get_competitor_share_of_voice, get_sentiment_overview,
    get_citations_overview, submit_prompts, list_topics, list_queries
    """
    # Route to the right tool based on operation name
    op_tool_map = {
        "get_brand_overview": "visibility",
        "get_visibility_trend": "visibility",
        "get_competitor_share_of_voice": "visibility",
        "get_competitor_visibility_rank": "visibility",
        "get_competitor_visibility_trend": "visibility",
        "get_queries_overview": "visibility",
        "get_topics_overview": "visibility",
        "get_sentiment_overview": "sentiment",
        "get_sentiment_trend": "sentiment",
        "get_citations_overview": "citations",
        "get_citations_urls": "citations",
        "submit_prompts": "prompt_simulator",
        "list_prompt_analyses": "prompt_simulator",
        "get_prompt_analysis": "prompt_simulator",
        "check_ps_status": "prompt_simulator",
        "get_ps_responses": "prompt_simulator",
        "get_ps_summary": "prompt_simulator",
        "get_ps_visibility": "prompt_simulator",
        "add_topic": "topics",
        "list_topics": "topics",
        "remove_topic": "topics",
        "add_query": "queries",
        "list_queries": "queries",
        "remove_query": "queries",
    }
    tool_name = op_tool_map.get(operation, "visibility")
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool_name} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool_name, operation, json.loads(params))
    _output(resp, fmt)


@cli.command("gbp")
@click.argument("tool", default="gbp_locations_crud")
@click.argument("operation", default="list_locations")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def gbp(ctx, tool, operation, params, fmt):
    """Google Business Profile operations.

    Tools: gbp_locations_crud, gbp_locations_deployment,
    gbp_locations_recommendations, posts_crud, posts_generation,
    posts_automation, reviews, connections
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool, operation, json.loads(params))
    _output(resp, fmt)


@cli.command("ppc")
@click.argument("tool", default="business_crud")
@click.argument("operation", default="list_all")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def ppc(ctx, tool, operation, params, fmt):
    """PPC / Google Ads operations.

    Tools: business_crud, business_mgmt, campaign, product_crud,
    product_mgmt, ads_account_crud, ads_account_mgmt, ad_group,
    ad_content, keyword_cluster, keyword
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool, operation, json.loads(params))
    _output(resp, fmt)


@cli.command("site")
@click.argument("tool", default="projects")
@click.argument("operation", default="list_sites")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def site(ctx, tool, operation, params, fmt):
    """Site Explorer operations.

    Tools: organic, backlinks, analysis, adwords, brand_signals,
    keyword_research, projects, holistic_audit
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool, operation, json.loads(params))
    _output(resp, fmt)


@cli.command("content")
@click.argument("tool", default="content_generation")
@click.argument("operation", default="topic_suggestions")
@click.option("--params", "-p", default="{}", help="JSON params.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["rich", "json"]),
    default="rich",
    show_default=True,
)
@click.pass_context
def content_cmd(ctx, tool, operation, params, fmt):
    """Content Genius operations.

    Tools: content_generation, article_management, dkn,
    content_retrieval, content_publication, folder_management,
    topical_maps
    """
    key = _get_api_key(ctx.obj["api_key"])
    with MCPClient(key) as client:
        with console.status(f"[bold blue]{tool} -> {operation}...[/bold blue]"):
            resp = client.call_tool(tool, operation, json.loads(params))
    _output(resp, fmt)


if __name__ == "__main__":
    cli()
