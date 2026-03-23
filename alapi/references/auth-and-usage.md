# Authentication And Usage

## Authentication

- Header name: `token`
- Header location: `header`
- Environment variable: `ALAPI_TOKEN`
- Base URL: `https://v3.alapi.cn`

## Common Request Pattern

- Method: `POST`
- Content-Type: `application/json`
- Auth header: `token: $ALAPI_TOKEN`
- Success shape: ALAPI generally returns JSON containing fields such as `code`, `message`, `success`, `data`, `request_id`, `time`, and `usage`

## Missing Token

If `ALAPI_TOKEN` is missing:

1. Tell the user to request or manage a token at `https://apifox.com/apihub/`
2. Ask the user to send the token back
3. Persist it to the active shell profile and export it in the current shell before calling the API

## Reusable Caller

Use `scripts/alapi_request.py`:

```bash
python3 scripts/alapi_request.py /api/ip --body '{"ip":"8.8.8.8"}'
```

Or load the request body from a file:

```bash
python3 scripts/alapi_request.py /api/ai/translate --body-file /tmp/body.json
```

## Reference Navigation

- `references/api-index.md`: category index
- `references/api-catalog.md`: endpoint-by-endpoint catalog
- `references/openapi-source.json`: raw source of truth
