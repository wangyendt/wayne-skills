---
name: alapi
description: Comprehensive ALAPI skill covering the full bundled ALAPI OpenAPI catalog. Use when the user mentions ALAPI, alapi, ALAPI_TOKEN, openapi.json, or an ALAPI path like /api/..., or asks to find which ALAPI API matches a business need, choose between similar ALAPI endpoints, explain request fields, prepare or execute a request, or troubleshoot an ALAPI response. Covers inspirational content, articles, news and hotlists, AI chat/translation/NLP, OCR and document recognition, weather and calendar data, IP/phone/ID/domain/ICP/enterprise lookup and verification, finance/exchange/gold/oil/crypto market data, music/media/video/TTS, URL/QR tools, and related utility APIs.
---

# ALAPI

## Overview

Use this skill to work against the full ALAPI OpenAPI catalog without hand-parsing the schema each time. The skill bundles the raw OpenAPI source, a generated endpoint catalog, an auth guide, and a reusable request script.

## Workflow

1. Confirm whether `ALAPI_TOKEN` is available.
2. If the token is missing, tell the user to request one from `https://apifox.com/apihub/`, then ask them to send it back.
3. After the user sends the token, persist it to the active shell profile, export it in the current session, and avoid echoing it back in logs.
4. Use `references/intent-router.md` first to map a user request to the most likely endpoint with minimal context cost.
5. Open `references/api-catalog.md` only for the exact endpoint you selected.
6. Use `scripts/alapi_request.py` for real calls instead of rewriting HTTP boilerplate.
7. If the OpenAPI source changes, replace `references/openapi-source.json` and rerun `scripts/generate_references.py`.

## Authentication

- ALAPI uses header auth: `token: $ALAPI_TOKEN`
- All endpoints in the bundled OpenAPI spec use `POST`
- All endpoints use `application/json` request bodies
- Base URL: `https://v3.alapi.cn`

## Token Handling

Run `printenv ALAPI_TOKEN` first.

If the token is missing:

- Tell the user to申请或管理 ALAPI token at `https://apifox.com/apihub/`
- Ask the user to send the token
- After receiving it, persist it based on the active shell:
  - `zsh`: append `export ALAPI_TOKEN='...'` to `~/.zshrc`
  - `bash`: append `export ALAPI_TOKEN='...'` to `~/.bashrc`
- Also export it in the current shell before making API calls

Do not invent or reuse placeholder tokens for real requests.

## References

- `references/auth-and-usage.md`: auth model, calling conventions, error-handling checklist
- `references/intent-router.md`: lowest-cost full routing table from common intent to endpoint
- `references/api-catalog.md`: endpoint-by-endpoint reference including purpose and request schema
- `references/openapi-source.json`: bundled ALAPI OpenAPI source of truth

Use `rg '^### /api/' references/api-catalog.md` to jump to a path quickly.

## Scripts

- `scripts/alapi_request.py`: send authenticated ALAPI requests with JSON bodies
- `scripts/generate_references.py`: regenerate the reference markdown files from `references/openapi-source.json`

## Response Discipline

When answering a user with this skill:

- State the selected endpoint path explicitly
- Explain why that endpoint matches the request
- Show the required JSON body fields
- Mention that auth is via `ALAPI_TOKEN`
- Summarize the API response instead of dumping raw JSON unless the user asks for the full payload
