# Agent Playbook — MCP Summit Execution

> **Purpose:** Step-by-step instructions for any Claude agent to execute the 5-day marketing summit via SearchAtlas MCP tools without repeating mistakes from previous runs.
> **Last updated:** 2026-02-22 (Run 4 — Full Tool Registry Rediscovery)

---

## GOLDEN RULES (Read Before Doing ANYTHING)

### Rule 1: Schema Discovery First — ALWAYS
**Before calling ANY MCP tool for the first time**, send an intentionally wrong or empty call to discover the real schema. The MCP server returns the expected schema in error responses.

```
# Example: discover create_project schema
curl -s -X POST "$API" -H "Content-Type: application/json" -H "X-API-KEY: $KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"website_studio_tools","arguments":{"op":"create_project","params":{}}}}'
# Response will include: "Expected Schema: { name (REQUIRED), mode, user_prompt, source_url, campaign_id }"
```

**Why:** Documentation has wrong parameter names for many tools. The MCP server is the single source of truth. Agents that trusted docs without verifying failed 60% of tasks in Run 1.

### Rule 2: Read Error Messages Carefully
- **"Parameter Validation Error"** = you used wrong param names or missing required fields. The response contains the correct schema — READ IT and adapt.
- **"Internal Server Error"** = the backend is down or overloaded. This is NOT a parameter issue. Try again later or report as backend blocker.
- **"credentials not provided for X"** / **"Authentication Failed"** = genuine auth block. The API key doesn't have scope for this tool.
- **"Tool 'X' not found in registry"** = the tool name has changed. Use `tools/list` to get current names.
- **"Unsupported operation"** = you hit a tool name collision. The same name maps to a different tool than expected. See Rule 6.
- **DO NOT** confuse "invalid operation name" with "auth blocked." They are completely different errors.

### Rule 3: Don't Fabricate Timelines
Always report actual timestamps from the API response, never guess durations.

### Rule 4: Use the MCP Tool (not curl) When Possible
When running inside Claude Code, use ToolSearch to load MCP tools then call them directly. Only fall back to curl when debugging.

### Rule 5: Poll Async Tasks Properly
Many operations return a `task_id` and process in the background. Use:
```
task → get_otto_ppc_task_status { task_id: "<uuid>" }
task → otto_wait { }  # waits 5 seconds
```
For OTTO SEO tasks:
```
task_management → get_otto_task_status { task_id: "<uuid>" }
task_management → otto_wait { }
```
Poll every 5-10 seconds until status = SUCCESS. Don't assume failure on first poll.

### Rule 6: Watch for Tool Name Collisions
**CRITICAL:** Multiple tools share the same short name. The MCP server routes to the FIRST match in the registry. Known collisions:

| Short Name | Registry Index | Actual Tool | Category |
|------------|---------------|-------------|----------|
| `project_management` | #6 | OTTO Project Management | project_management |
| `project_management` | #45 | Content Genius Projects | project_management |
| `knowledge_graph` | #3 | OTTO Knowledge Graph | knowledge_management |
| `knowledge_graph` | #75 | Press Release KG | press_release |
| `knowledge_graph` | #81 | Cloud Stack KG | cloud_stack |
| `content` | #73 | Press Release Content | press_release |
| `content` | #79 | Cloud Stack Content | cloud_stack |
| `distribution` | #74 | PR Distribution | press_release |
| `distribution` | #80 | CS Distribution | cloud_stack |
| `quota_management` | #5 | OTTO Quota | quota_management |
| `quota` | #71 | Local SEO Quota | quota_management |
| `quota` | #77 | PR Quota | quota_management |
| `quota` | #83 | CS Quota | quota_management |
| `quota` | #104 | LLM Visibility Quota | llm_visibility_quota |
| `brand_vault` | multiple (#16,29,38,48,72,78,84,87,92,97,99,108,110) | Same BrandVault tool | BrandVault |
| `attachments` | #13, #47 | Same attachments tool | Attachments |

**Workaround:** When calling via Claude Code MCP client, use `select:mcp__searchatlas__<name>` queries and verify which tool responds by checking the category/operations. When calling via curl, the first-registered tool wins for duplicate names.

---

## MCP CONNECTION INFO

```
Endpoint: https://mcp.searchatlas.com/api/v1/mcp
Protocol: JSON-RPC 2.0, method "tools/call"
Auth Header: X-API-KEY: <YOUR_MCP_API_KEY>
Tool List: method "tools/list"
```

---

## COMPLETE TOOL REGISTRY (Run 4 — Feb 22, 2026)

**112 tools, ~350+ operations total**

### OTTO SEO (15 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 1 | `image_upload` | `upload_image` | media_management |
| 2 | `indexing_management` | `add_custom_indexing_urls`, `add_indexing_sitemap`, `delete_custom_indexing_url`, `delete_indexing_sitemap`, `get_custom_indexing_urls`, `get_indexing_sitemaps`, `select_urls_for_indexing`, `toggle_sitemap_indexing` | instant_indexing |
| 3 | `knowledge_graph` | `get_knowledge_graph`, `update_knowledge_graph`, `update_refine_prompt` | knowledge_management |
| 4 | `OTTO_Installations` | `check_cloudflare_worker_status`, `get_cloudflare_installation_guide`, `get_otto_installation_guide`, `install_cloudflare_worker`, `uninstall_cloudflare_worker` | installation_management |
| 5 | `quota_management` | `get_otto_quota`, `show_otto_quota` | quota_management |
| 6 | `project_management` | `disengage_otto_project`, `engage_otto_project`, `find_project_by_hostname`, `freeze_otto_project`, `get_otto_project_details`, `get_public_share_url`, `list_otto_pixel_installed_projects`, `list_otto_projects`, `manual_reprocess_autopilot`, `unfreeze_otto_project`, `update_crawl_settings`, `verify_otto_installation`, `work_summary_export` | project_management |
| 7 | `recrawl_management` | `trigger_recrawl` | recrawl_management |
| 8 | `schema_markup` | `delete_page_level_schema`, `deploy_domain_level_schema`, `deploy_page_level_schema`, `edit_page_level_schema`, `generate_page_level_schema`, `get_schema_detail`, `list_domain_level_schemas`, `list_page_level_schemas` | seo_optimization |
| 9 | `seo_analysis` | `generate_bulk_recommendations`, `generate_single_recommendation`, `get_project_issues_summary`, `get_website_issues_by_type` | seo_optimization |
| 10 | `audit_management` | `create_audit`, `get_site_audit_by_id` | seo_audit |
| 11 | `seo_deployment` | `deploy_seo_fixes`, `rollback_seo_fixes` | seo_optimization |
| 12 | `suggestion_management` | `delete_suggestion`, `edit_suggestion`, `edit_suggestions_bulk`, `export_suggestions` | suggestion_management |
| 13 | `attachments` | `view_uploaded_attachment` | Attachments |
| 14 | `task_management` | `get_otto_task_status`, `otto_wait` | task_management |
| 15 | `wildfire` | `deploy_wildfire_link`, `list_pending_outlinks`, `list_wildfire_backlinks`, `list_wildfire_links`, `list_wildfire_outlinks`, `undeploy_wildfire_link` | wildfire |

**NEW in Run 4:** `OTTO_Installations` (5 ops — Cloudflare Worker install/uninstall), `image_upload`, expanded `project_management` (13 ops, was 11), `wildfire` now has 6 ops (was 6).

### PPC / Google Ads (13 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 16 | `brand_vault` | (shared — see BrandVault section) | BrandVault |
| 17 | `ads_account_crud` | `delete`, `get`, `get_customer_ads_accounts`, `list`, `update` | ads_accounts |
| 18 | `ads_account_mgmt` | `check_conversions`, `check_write_permissions`, `connect_new_account`, `get_ads_account_conversions`, `get_sync_status`, `sync_from_google` | ads_accounts |
| 19 | `campaign` | `import_campaigns`, `list_campaign_performance`, `list_campaigns_with_metrics`, `send_to_google_ads_account` | campaign |
| 20 | `product_crud` | `add_product`, `bulk_create_keyword_clusters`, `generate_product_details`, `get`, `list`, `list_grouped_keywords`, `review_products`, `update` | product |
| 21 | `product_mgmt` | `bulk_approve_products`, `bulk_create_campaign_budget`, `bulk_delete_products`, `bulk_disapprove_products`, `bulk_restore_products`, `bulk_update_remote_status`, `bulk_validate_landing_page_urls` | product_management |
| 22 | `business_crud` | `create`, `delete`, `get`, `list`, `list_all`, `update` | business |
| 23 | `business_mgmt` | `create_products`, `discover_products`, `generate_form_suggestions`, `geo_search`, `get_geo_suggestions`, `get_phones`, `get_target_languages`, `set_primary_phone` | business |
| 24 | `task` | `get_otto_ppc_task_status`, `otto_wait` (assumed — needs verify) | task |
| 25 | `ad_group` | `list`, `list_ad_group_performance`, `list_ad_groups_with_metrics` | ad_group |
| 26 | `ad_content` | `bulk_approve_ad_contents`, `bulk_delete_ad_contents`, `bulk_disapprove_ad_contents`, `bulk_update_ad_content_remote_status`, `update_ad_content`, `list_ad_content_performance`, `list_ad_contents_with_metrics` | ad_content |
| 27 | `keyword_cluster` | `bulk_approve_keyword_clusters`, `bulk_create_ad_contents`, `bulk_delete_keyword_clusters`, `bulk_disapprove_keyword_clusters`, `bulk_keyword_operation`, `bulk_update_remote_status`, `get`, `list`, `update` | keyword_cluster |
| 28 | `keyword` | `list_keyword_performance` | keyword |

**Name changes from Runs 1-3:**
- `otto_ppc_business_crud` → `business_crud`
- `otto_ppc_business_mgmt` → `business_mgmt`
- `otto_ppc_ads_account_crud` → `ads_account_crud`
- `otto_ppc_ads_account_mgmt` → `ads_account_mgmt`
- `otto_ppc_campaign` → `campaign`
- `otto_ppc_ad_group` → `ad_group`
- `otto_ppc_ad_content` → `ad_content`
- `otto_ppc_keyword_cluster` → `keyword_cluster`
- `otto_ppc_keyword` → `keyword`
- `otto_ppc_product_crud` → `product_crud`
- `otto_ppc_product_mgmt` → `product_mgmt`
- `otto_ppc_task` → `task`

### Site Explorer (8 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 30 | `backlinks` | `get_site_anchor_text_analysis`, `get_site_backlinks`, `get_site_link_network_graph`, `get_site_outgoing_domains`, `get_site_outgoing_links`, `get_site_referring_domains`, `get_site_referring_ips` | site_explorer_competitor_research |
| 31 | `organic` | `get_organic_competitors`, `get_organic_keywords`, `get_organic_pages`, `get_organic_position_changes`, `get_organic_subdomains`, `get_site_indexed_pages` | site_explorer_competitor_research |
| 32 | `analysis` | `get_educational_backlinks`, `get_historical_trends`, `get_keyword_intent_analysis`, `get_position_distribution`, `get_serp_features` | site_explorer_deep_analysis |
| 33 | `adwords` | `get_adwords_adhistory`, `get_adwords_adtrend`, `get_adwords_competitors`, `get_adwords_copies`, `get_adwords_keywords`, `get_adwords_pages`, `get_adwords_position_changes`, `get_adwords_subdomains` | site_explorer_adwords |
| 34 | `brand_signals` | `retrieve_brand_signal_score`, `submit_brand_signal_score` | site_explorer_brand |
| 35 | `holistic_audit` | `get_holistic_seo_pillar_scores` | seo_audit |
| 36 | `keyword_research` | `create_keyword_research_project`, `delete_keyword_research_project`, `get_keyword_research_details`, `get_serp_overview`, `list_keyword_research_projects`, `search_keyword_research_projects`, `update_keyword_research_project` | site_explorer_keyword_research |
| 37 | `projects` | `create_site_explorer`, `delete_site_explorer`, `get_site_explorer_details`, `list_sites` | site_explorer_management |

**Name changes:** `Site_Explorer_Organic_Tool` → `organic`, `Site_Explorer_Backlinks_Tool` → `backlinks`, etc.

### Content Genius (7 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 39 | `content_generation` | `auto_generate_article`, `create_content_instance`, `generate_complete_article`, `poll_headings_outline`, `poll_information_retrieval`, `start_headings_outline`, `start_information_retrieval`, `topic_suggestions`, `update_article_headings` | content_generation |
| 40 | `article_management` | `edit_article_content`, `export_article_to_google_doc`, `get_article_details`, `insert_article_links`, `list_recent_articles`, `list_trash_articles`, `manage_article_keywords`, `reassign_article_brand_vault`, `regenerate_article`, `run_content_grader`, `update_article_status` | article_management |
| 41 | `dkn` | `bulk_generate_articles_from_dkn_nodes`, `bulk_update_dkn_nodes`, `create_vibe_transaction`, `generate_article_from_dkn_node`, `get_dkn_node_article_status`, `get_dkn_filter_options`, `get_dkn_node`, `get_dkn_overview_metrics`, `get_vibe_transaction_result`, `list_dkn_nodes`, `update_dkn_node` | content_genius |
| 42 | `content_retrieval` | `advanced_filter_articles`, `count_articles`, `filter_articles_by_status`, `filter_articles_by_tags`, `get_article_summary`, `get_assigned_articles`, `get_high_quality_articles`, `get_project_articles`, `get_published_articles`, `get_recent_articles`, `get_scheduled_articles`, `search_articles` | content_retrieval |
| 43 | `content_publication` | `cancel_cms_article`, `cancel_wordpress_article`, `draft_cms_article`, `draft_wordpress_article`, `get_article_details`, `get_article_publication_status`, `get_cms_connectors`, `get_cms_dynamic_field_schema`, `get_cms_form_schema`, `get_current_datetime_approx`, `get_wordpress_website_options`, `list_published_articles`, `list_scheduled_articles`, `publish_cms_article`, `publish_wordpress_article`, `schedule_cms_article`, `schedule_wordpress_article` | content_publication |
| 44 | `folder_management` | `create_brand_vault`, `fetch_brand_vault`, `get_brand_vault_by_uuid`, `list_all_brand_vaults`, `get_brand_vault_for_domain` | folder_management |
| 46 | `topical_maps` | `create_topical_map`, `search_topical_maps` | content_strategy |

**NEW:** `dkn` (Domain Knowledge Network, 11 ops), expanded `content_publication` (17 ops), `article_management` (11 ops).

### GBP (16 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 49 | `connections` | `all_available_locations`, `manage_connections` | gbp_connection_management |
| 50 | `gbp_locations_crud` | `get_location`, `get_location_stats`, `list_locations`, `load_location`, `set_location_lock`, `update_location`, `update_open_hours`, `update_open_info`, `update_special_hours` | gbp_location_management |
| 51 | `gbp_locations_deployment` | `bulk_deploy_locations`, `deploy_location`, `suggest_description` | gbp_location_deployment |
| 52 | `gbp_locations_recommendations` | `apply_location_recommendation`, `bulk_apply_location_recommendations`, `delete_location_recommendation`, `generate_location_recommendations`, `get_location_recommendation_details`, `get_location_recommendations`, `suggest_service_description` | gbp_location_recommendations |
| 53 | `gbp_locations_categories_crud` | `bulk_add_additional_categories`, `list_categories`, `remove_categories`, `replace_primary_category` | gbp_location_management |
| 54 | `gbp_locations_services_crud` | `bulk_remove_services`, `bulk_upsert_custom_services`, `bulk_upsert_standard_services`, `list_services` | gbp_location_management |
| 55 | `gbp_locations_attributes_crud` | `bulk_upsert_attributes`, `list_attributes`, `remove_attributes` | gbp_location_management |
| 56 | `gbp_locations_medias_crud` | `list_medias` | gbp_location_management |
| 57 | `posts_crud` | `approve_post`, `delete_post`, `get_post`, `list_posts`, `publish_post`, `unapprove_post`, `unpublish_post`, `update_post` | gbp_posts_management |
| 58 | `posts_generation` | `ai_generate_post_image`, `bulk_create_posts`, `bulk_generate_posts` | gbp_posts_generation |
| 59 | `posts_automation` | `disable_automated_posting`, `enable_automated_posting`, `get_automated_posting_settings`, `update_automated_posting_settings` | gbp_posts_automation |
| 60 | `posts_social` | `list_facebook_pages`, `list_instagram_accounts`, `list_twitter_accounts` | gbp_posts_social |
| 61 | `reviews` | `ai_generate_review_reply`, `get_review`, `get_review_reply_automation_settings`, `get_review_reply_stats`, `get_review_star_rating_stats`, `list_reviews`, `publish_review_reply`, `unpublish_review_reply`, `update_review_reply`, `update_review_reply_automation_settings` | gbp_reviews_management |
| 62 | `stats` | `bulk_refresh_stats` | gbp_stats_management |
| 63 | `tasks` | `bulk_approve_tasks`, `list_location_tasks`, `refresh_location_tasks`, `set_location_task_ignored` | gbp_task_management |
| 64 | `utility` | `bulk_import_locations_entity`, `generate_share_hash` | gbp_utility |

**NEW in Run 4:** `gbp_locations_categories_crud` (4 ops), `gbp_locations_services_crud` (4 ops), `gbp_locations_attributes_crud` (3 ops), `gbp_locations_medias_crud` (1 op). These are granular sub-tools broken out from the old `gbp_locations_crud`.

**Name changes:** `gbp_connection` → `connections`, `gbp_posts_crud` → `posts_crud`, etc.

### Local SEO (7 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 65 | `business` | `bulk_create_local_seo_businesses_with_grids`, `create_local_seo_business`, `delete_local_seo_business`, `extract_local_seo_business_details`, `get_local_seo_business`, `list_local_seo_businesses`, `update_local_seo_business` | local_seo_business_management |
| 66 | `grids` | `bulk_refresh_grids`, `bulk_remove_grids`, `bulk_update_grids`, `get_heatmap_quota`, `refresh_grid`, `setup_grids`, `update_grid` | local_seo_grid_management |
| 67 | `data` | `get_grid_details`, `get_grids_by_cid`, `get_grids_history`, `get_heatmap_preview`, `get_heatmap_snapshot`, `get_rank`, `list_grids` | local_seo_data_reporting |
| 68 | `analytics` | `available_dates`, `competitor_report`, `location_report`, `remove_snapshot` | local_seo_analytics |
| 69 | `ai` | `recommend_keywords` | gmb_ai_features |
| 70 | `citation` | `delete_citation`, `export_citation`, `get_aggregator_details`, `get_aggregator_networks`, `get_citation_business_categories`, `preview_citation_data`, `submit_citation` | local_seo_citation_management |
| 71 | `quota` | (collision — see note) | quota_management |

**Name changes:** `local_seo_business` → `business`, `local_seo_grids` → `grids`, `local_seo_data` → `data`, `local_seo_citation` → `citation`, `local_seo_ai` → `ai`.

### Press Release (4 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 73 | `content` | `create`, `delete`, `get`, `list`, `list_content_types`, `write_press_release` | press_release |
| 74 | `distribution` | `get_press_release_categories`, `get_press_release_distributions`, `publish_press_release` | press_release |
| 75 | `knowledge_graph` | (collision with OTTO KG — first-match wins) | press_release |
| 76 | `payment` | `get_hdc_balance`, `get_hdc_usage_history`, `purchase_hdc_credits` | press_release |

**Name changes:** `press_release_content` → `content`, `press_release_distribution` → `distribution`, `press_release_knowledge_graph` → `knowledge_graph`.
**NEW:** `payment` tool with HDC balance/history/purchase ops (but auth-blocked for HyperdriveCredits).

### Cloud Stack (4 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 79 | `content` | (collision — PR content tool responds first) | cloud_stack |
| 80 | `distribution` | (collision — PR distribution responds first) | cloud_stack |
| 81 | `knowledge_graph` | (collision — OTTO KG responds first) | cloud_stack |
| 82 | `payment` | (collision — PR payment responds first) | cloud_stack |

**CRITICAL:** Cloud Stack tools are UNREACHABLE via curl due to name collisions with PR tools. The MCP client may be able to differentiate by registry index, but curl cannot.

### Digital PR (4 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 88 | `campaigns` | `create_campaign`, `get_campaign`, `get_settings`, `list_campaign`, `list_projects`, `toggle_campaign`, `update_campaign`, `update_settings` | campaign |
| 89 | `inbox` | `get_email_thread`, `list_linked_emails`, `manage_sent_items`, `monitor_inbox`, `reply_to_email` | inbox |
| 90 | `templates` | `create`, `get`, `list`, `update` | template |
| 91 | `opportunities` | `list`, `schedule_bulk`, `toggle_opportunity` | opportunity |

**Name changes:** `digital_pr_campaign_service` → `campaigns`, `digital_pr_inbox_service` → `inbox`, `digital_pr_template_service` → `templates`, `digital_pr_opportunity_service` → `opportunities`.

### LinkLab (4 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 93 | `articles` | `create_article`, `delete_article`, `get_article_details`, `list_articles`, `update_article` | article |
| 94 | `orders` | `add_to_cart`, `checkout_cart`, `clear_cart`, `get_details`, `list`, `list_payment_methods`, `remove_from_cart`, `update_cart_item`, `validate_content`, `view_cart` | order |
| 95 | `projects` | `create_site_explorer`, `delete_site_explorer`, `get_site_explorer_details`, `list_sites` | project |
| 96 | `publications` | `get_details`, `list`, `list_categories` | publication |

**Name changes:** `linklab_article_service` → `articles`, `linklab_order_service` → `orders`, `linklab_project_service` → `projects`, `linklab_publication_service` → `publications`.

**NOTE:** `projects` collides with Site Explorer `projects` (#37). First-match wins.

### LLM Visibility (8 tools)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 100 | `projects` | (collision with SE projects) | llm_visibility_management |
| 101 | `visibility` | `get_brand_overview`, `get_competitor_share_of_voice`, `get_competitor_visibility_rank`, `get_competitor_visibility_trend`, `get_queries_overview`, `get_topics_overview`, `get_visibility_trend` | llm_visibility_analysis |
| 102 | `sentiment` | `get_sentiment_overview`, `get_sentiment_trend` | llm_visibility_sentiment |
| 103 | `citations` | `get_citations_overview`, `get_citations_urls` | llm_visibility_citations |
| 104 | `quota` | (collision) | llm_visibility_quota |
| 105 | `topics` | `add_topic`, `list_topics`, `remove_topic` | llm_visibility_topics |
| 106 | `queries` | `add_query`, `list_queries`, `remove_query` | llm_visibility_queries |
| 107 | `prompt_simulator` | `check_ps_status`, `get_prompt_analysis`, `get_ps_responses`, `get_ps_summary`, `get_ps_visibility`, `list_prompt_analyses`, `submit_prompts` | prompt_simulator |

**Name changes:** `Visibility Analysis Tools` → `visibility`, `Sentiment Analysis Tools` → `sentiment`, `Citation Analysis Tools` → `citations`, `Prompt Simulator Tools` → `prompt_simulator`, `Topic Management Tools` → `topics`, `Query Management Tools` → `queries`.

### BrandVault (1 tool, registered 13+ times)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 16+ | `brand_vault` | `archive_brand_vault`, `ask_brand_vault`, `create_brand_vault`, `get_brand_vault_business_info`, `get_brand_vault_index_status`, `get_brand_vault_overview`, `get_knowledge_graph`, `list_archived_brand_vaults`, `list_brand_vaults`, `list_voice_profiles`, `list_voice_templates`, `restore_brand_vault`, `retrieve_brand_vault_details`, `select_voice_profile`, `update_brand_vault`, `update_brand_vault_business_info`, `update_knowledge_graph` | BrandVault |

**RUN 4 BREAKTHROUGH: BrandVault is NOW WORKING.** Was auth-blocked in Runs 1-3. Now returns data. brand vaults returned successfully.
- `get_brand_vault_overview` requires `hostname` (string, e.g. "searchatlas.com"), NOT `brand_vault_id`.

### Website Studio (1 tool)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 109 | `website_studio_tools` | `bulk_send_message`, `create_project`, `ensure_containers_running`, `get_credit_status`, `get_project`, `list_projects`, `ppc_sync`, `publish_project` | website_studio |

**NEW ops:** `bulk_send_message`, `ensure_containers_running`, `get_credit_status`, `ppc_sync` (8 total, was 4).
**`create_project` STILL BROKEN** — returns Internal Server Error (tested Feb 22, 2026).

### GSC Tools (2 tools — NEW)

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 111 | `GSC_Performance_Tool` | `compare_performance`, `get_gsc_sites`, `get_keyword_performance`, `get_page_keywords`, `get_page_performance`, `get_page_summary`, `get_site_property_performance` | gsc_performance |
| 112 | `GSC_Site_Events_Tool` | `create_automatic_event`, `create_site_event`, `get_site_events` | gsc_site_events |

**Completely NEW in Run 4.** Not present in any previous run.

### Utilities

| # | Tool Name | Operations | Category |
|---|-----------|-----------|----------|
| 85 | `batch` | `check_status`, `download_report`, `list`, `submit`, `view_details` | indexer |
| 98 | `reports` | `get_report_data_sources`, `get_report_details`, `list_reports`, `list_reports_paginated` | reports |

**Name changes:** `rb_report_tools` → `reports`, `indexer_batch_service` → `batch`.

---

## WHAT WORKS vs. WHAT'S BLOCKED (Run 4 — Feb 22, 2026)

### CONFIRMED WORKING
| Tool | Verified | Notes |
|------|----------|-------|
| `project_management` (OTTO) | list_otto_projects returns data | projects returned successfully |
| `seo_analysis` | Works | 48K+ issues across projects |
| `audit_management` | Works | |
| `knowledge_graph` (OTTO) | Works | |
| `indexing_management` | Works | |
| `wildfire` | Works (0 links seeded) | |
| `website_studio_tools` (list/get) | Works | 23 projects (was 18) |
| `website_studio_tools` (create) | **STILL BROKEN** | Internal Server Error |
| `gbp_locations_crud` | Works | 2 locations |
| `gbp_locations_recommendations` | Works | |
| `gbp_locations_deployment` | Works | |
| `connections` | Works | |
| `posts_crud` / `posts_generation` | Works | |
| `reviews` | Works | |
| **`brand_vault`** | **NOW WORKS** | Was blocked in Runs 1-3! 8 vaults exist |
| `business_crud` (PPC) | Works | |
| `business_mgmt` (PPC) | Works | |
| `ads_account_crud` | Works | |
| All other PPC tools | Works | |
| `content` (PR) | Works | |
| `distribution` (PR) | Works | |
| `visibility` | Works | searchatlas.com: 18/100 |
| `sentiment` | Works | |
| `citations` | Works | |
| `prompt_simulator` | Works | |
| `topics` / `queries` | Works | |
| `business` (Local SEO) | Works | 1 business (Digital Agency) |
| `grids` / `data` | Works | |
| **`citation`** | **NOW WORKS** | Was blocked in Runs 1-3! Returns schema |
| `campaigns` (DPR) | Works | |
| `templates` (DPR) | Works | |
| `articles` (LinkLab) | Works | |
| `orders` (LinkLab) | Works | |
| `reports` | Works | 5 reports |
| `content_generation` | Works | |
| `content_publication` | Works | |
| `topical_maps` | Works | |
| `GSC_Performance_Tool` | NEW — untested | |
| `GSC_Site_Events_Tool` | NEW — untested | |

### STILL BLOCKED
| Tool | Error | Fix |
|------|-------|-----|
| `payment` (HDC credits) | "Authentication Failed for HyperdriveCredits" | Need API key scope fix |
| `website_studio_tools → create_project` | Internal Server Error | SA DevOps — backend still down |
| Cloud Stack tools (`content`/`distribution` at indices 79-80) | Name collision — PR tools respond first | SA Backend — need unique tool names |

### NEWLY UNBLOCKED (Run 4)
| Tool | Was | Now | Impact |
|------|-----|-----|--------|
| `brand_vault` | Auth blocked | **WORKING** | Unblocks Day 1.1 (Brand Vaults), Day 2.3 (Articles), Day 2.4 (Topical Maps) |
| `citation` | Auth blocked | **WORKING** (schema returned) | Unblocks Day 3.4 (Citations) |

---

## VERIFIED SCHEMAS (Run 4)

### brand_vault → get_brand_vault_overview
```json
{
  "hostname": "string (REQUIRED — e.g. 'searchatlas.com')"
}
```
**WRONG (old):** `brand_vault_id` — does not exist. Use `hostname`.

### website_studio_tools → create_project
```json
{
  "name": "string (REQUIRED)",
  "mode": "free | clone | clone_seo | clone_ppc (default: free)",
  "user_prompt": "string (REQUIRED for free mode)",
  "source_url": "string (REQUIRED for clone modes)",
  "campaign_id": "string (REQUIRED for clone_ppc mode)"
}
```
**Status:** Correct params, but backend returns 500. Unchanged from Run 2.

### citation → submit_citation
```json
{
  "aggregators": ["dataaxle", "neustar", "ypnetwork", "gpsnetwork", "foursquare"],
  "business_name": "string (REQUIRED)",
  "website_address": "string (REQUIRED)",
  "campaign_name": "string (REQUIRED)",
  "campaign_country": "string (3-letter code)"
}
```
**Status:** Schema returned! Was auth-blocked before. Needs full param discovery for remaining 40+ fields.

---

## PPC CAMPAIGN BUILD — STEP-BY-STEP (Updated Tool Names)

### Step 1: Generate AI Suggestions
```
business_mgmt → generate_form_suggestions {
  website_url: "https://example.com",
  field_types: ["business_revenue_model_suggestion", "business_brand_identity_suggestion", "business_value_proposition_suggestion"]
}
```

### Step 2: Create Business
```
business_crud → create {
  name: "Business Name",
  website_url: "https://example.com",
  google_ads_account: 89,
  location_data: [{ locationId: 2840 }],
  target_language: "1000",
  description: "<from step 1>",
  revenue_model: "<from step 1>",
  brand_identity: "<from step 1>",
  value_proposition: "<from step 1>"
}
```

### Step 3: Discover Products
```
business_mgmt → discover_products { business_id: <id> }
```

### Step 4: Review & Approve
```
product_crud → review_products { business_id: <id> }
product_mgmt → bulk_approve_products { business_id: <id> }
```

### Step 5: Create Campaigns
```
business_mgmt → create_products { business_id: <id>, bidding_strategy_type: "MAXIMIZE_CLICKS" }
```

### Step 6: Create Keyword Clusters
```
product_crud → bulk_create_keyword_clusters { business_id: <id> }
```

### Step 7: Approve Keyword Clusters
```
keyword_cluster → bulk_approve_keyword_clusters { business_id: <id> }
```

### Step 8: Create Ad Contents
```
keyword_cluster → bulk_create_ad_contents { business_id: <id> }
```

### Step 9: Approve Ad Contents
```
ad_content → bulk_approve_ad_contents { business_id: <id> }
```

### Step 10: Set Budget
```
product_mgmt → bulk_create_campaign_budget { business_id: <id>, amount_micros: 1000000 }
```

### STOP HERE unless explicitly told to launch.

---

## EXISTING ASSETS ON STAGING (Run 4 — Feb 22, 2026)

### OTTO Projects (5)
searchatlas.com, signalgenesys.com, backlinko.com, verdeoro.shop, moz.com

### Website Studio Projects (23 — was 18)
Including: remrsh SEO Services, Sabor Colombiano Miami, La Familia Taqueria, Product Showcase, Crown & Brim Co, Cats for Programmers, Manick's House Medellin, + 16 more. Most containers Stopped.

### Brand Vaults (8 — NEW DATA)
searchatlas.com, backlinko.com, signalgenesys.com, moz.com, supdogdaycare.com, aitoolreviewguide.com, + 2 more. All have incomplete configs.

### GBP Locations (2)
- Digital Agency (#272, Cali Colombia, verified, 61.9%)
- Omni Law (#271, Los Angeles, not verified, 57.1%)

### PPC (from Run 2)
Business 672 — 9 campaigns, 117 keyword clusters, 349 ads. NOT launched.

### Local SEO (1 business)
Digital Agency (ID 770) — 3 grids, avg position 13.0

### Press Releases (3 from Run 1 + 2 from Run 2)
All Generated, none distributed (HDC blocked).

### Cloud Stacks
CS #231 Published to 14 providers. #232-235 HDC-blocked.

---

## QUOTAS (Run 4)
- OTTO AI Suggestions: **6,000/6,000 MAXED** — blocked
- HDC Credits: **~5 remaining** (75 total) — auth-blocked on `payment` tool
- Content Generation: ~99K
- Heatmap Points: ~12K
- Outreach Emails: 75K

---

## REFERENCE

### Google Ads Geo Targets
| Location | ID |
|----------|----|
| United States | 2840 |
| United Kingdom | 2826 |
| Canada | 2124 |
| Australia | 2036 |

### Languages
| Language | ID |
|----------|----|
| English | 1000 |
| Spanish | 1003 |
| French | 1002 |

### Staging Accounts
| Account | Internal ID | Google Client ID |
|---------|-------------|-----------------|
| Nevu | 89 | 7564782868 |
