#!/usr/bin/env bash
API="https://mcp.searchatlas.com/api/v1/mcp"
KEY="${MCP_API_KEY:?Set MCP_API_KEY env var}"
call() {
  local name=$1 id=$2
  echo "=== $name ==="
  curl -s -X POST "$API" -H "Content-Type: application/json" -H "X-API-KEY: $KEY" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$id,\"method\":\"tools/call\",\"params\":{\"name\":\"$name\",\"arguments\":{\"op\":\"help\",\"params\":{}}}}" 2>&1 | head -c 1500
  echo ""
}

# GBP tools batch 1
call "connections" 1 &
call "gbp_locations_crud" 2 &
call "gbp_locations_deployment" 3 &
call "gbp_locations_recommendations" 4 &
call "gbp_locations_categories_crud" 5 &
call "gbp_locations_services_crud" 6 &
call "gbp_locations_attributes_crud" 7 &
call "gbp_locations_medias_crud" 8 &
wait

# GBP tools batch 2
call "posts_crud" 9 &
call "posts_generation" 10 &
call "posts_automation" 11 &
call "posts_social" 12 &
call "reviews" 13 &
call "stats" 14 &
call "tasks" 15 &
call "utility" 16 &
wait

# Local SEO tools
call "business" 17 &
call "grids" 18 &
call "data" 19 &
call "analytics" 20 &
call "ai" 21 &
call "citation" 22 &
wait

echo "DONE"
