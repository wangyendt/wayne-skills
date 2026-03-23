#!/usr/bin/env python3
"""Generate ALAPI markdown references from the bundled OpenAPI source."""

from __future__ import annotations

import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path


BASE_URL = "https://v3.alapi.cn"


def pointer_get(root: dict, pointer: str):
    if not pointer.startswith("#/"):
        raise ValueError(f"Unsupported ref: {pointer}")
    current = root
    for part in pointer[2:].split("/"):
        current = current[part]
    return current


def merge_all_of(parts: list[dict]) -> dict:
    merged: dict = {"type": "object", "properties": {}, "required": []}
    for part in parts:
        for key, value in part.items():
            if key == "properties":
                merged.setdefault("properties", {}).update(value)
            elif key == "required":
                merged.setdefault("required", [])
                for item in value:
                    if item not in merged["required"]:
                        merged["required"].append(item)
            elif key not in {"allOf"}:
                merged[key] = value
    return merged


def resolve_schema(schema: dict | None, root: dict) -> dict:
    if not schema:
        return {}
    if "$ref" in schema:
        target = deepcopy(pointer_get(root, schema["$ref"]))
        other = {k: deepcopy(v) for k, v in schema.items() if k != "$ref"}
        resolved = resolve_schema(target, root)
        resolved.update(other)
        return resolved
    if "allOf" in schema:
        resolved_parts = [resolve_schema(part, root) for part in schema["allOf"]]
        merged = merge_all_of(resolved_parts)
        for key, value in schema.items():
            if key != "allOf":
                merged[key] = deepcopy(value)
        return merged
    resolved = deepcopy(schema)
    if "properties" in resolved:
        resolved["properties"] = {
            key: resolve_schema(value, root) for key, value in resolved["properties"].items()
        }
    if resolved.get("items"):
        resolved["items"] = resolve_schema(resolved["items"], root)
    return resolved


def schema_type(schema: dict) -> str:
    if not schema:
        return "object"
    if schema.get("enum"):
        return "enum[" + ", ".join(map(str, schema["enum"])) + "]"
    kind = schema.get("type", "object")
    if kind == "array":
        return f"array<{schema_type(schema.get('items', {}))}>"
    if kind == "object" and schema.get("properties"):
        props = ", ".join(f"{name}:{schema_type(value)}" for name, value in schema["properties"].items())
        return f"object{{{props}}}"
    return str(kind)


def sample_value(name: str, schema: dict):
    if "default" in schema:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    kind = schema.get("type", "object")
    if kind == "string":
        lower = name.lower()
        if "url" in lower:
            return "https://example.com"
        if "date" in lower:
            return "2024-01-01"
        if "time" in lower:
            return "12:00:00"
        if "mobile" in lower or "phone" in lower:
            return "13800138000"
        if lower in {"ip", "ipv4"}:
            return "8.8.8.8"
        if "idcard" in lower or lower == "id":
            return "110101199003071234"
        if "text" in lower or "content" in lower:
            return "示例文本"
        if "lang" in lower or lower == "to":
            return "en"
        if "model" in lower:
            return "gpt-4o-mini"
        return f"{name}_example"
    if kind == "integer":
        return 1
    if kind == "number":
        return 1
    if kind == "boolean":
        return bool(schema.get("default", False))
    if kind == "array":
        return [sample_value(f"{name}_item", schema.get("items", {}))]
    if kind == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", list(properties.keys()))
        data = {}
        for key in required:
            if key in properties:
                data[key] = sample_value(key, properties[key])
        return data
    return None


def fields_from_schema(schema: dict) -> list[dict]:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    rows = []
    for name, value in properties.items():
        rows.append(
            {
                "name": name,
                "type": schema_type(value),
                "required": "yes" if name in required else "no",
                "default": json.dumps(value.get("default"), ensure_ascii=False) if "default" in value else "",
                "description": (value.get("description") or "").replace("\n", " ").strip(),
            }
        )
    return rows


def json_block(value) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def bash_block(url: str, body) -> str:
    body_json = json.dumps(body, ensure_ascii=False, indent=2)
    return (
        "```bash\n"
        f"curl -X POST '{url}' \\\n"
        "  -H 'token: $ALAPI_TOKEN' \\\n"
        "  -H 'Content-Type: application/json' \\\n"
        f"  -d '{body_json}'\n"
        "```"
    )


def response_summary(example) -> str:
    if not isinstance(example, dict):
        return "返回 `application/json`。具体结构见 `references/openapi-source.json`。"
    top_keys = list(example.keys())
    detail = f"顶层常见字段: {', '.join(top_keys)}。"
    data = example.get("data")
    if isinstance(data, dict):
        sample_keys = list(data.keys())[:10]
        if sample_keys:
            detail += f" `data` 常见字段: {', '.join(sample_keys)}。"
    return detail


def category_key(path: str) -> str:
    return path.removeprefix("/api/").split("/")[0]


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def build_auth_doc(spec: dict) -> str:
    scheme = spec["components"]["securitySchemes"]["apiKey"]
    return f"""# Authentication And Usage

## Authentication

- Header name: `{scheme['name']}`
- Header location: `{scheme['in']}`
- Environment variable: `ALAPI_TOKEN`
- Base URL: `{BASE_URL}`

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
python3 scripts/alapi_request.py /api/ip --body '{{"ip":"8.8.8.8"}}'
```

Or load the request body from a file:

```bash
python3 scripts/alapi_request.py /api/ai/translate --body-file /tmp/body.json
```

## Reference Navigation

- `references/api-index.md`: category index
- `references/api-catalog.md`: endpoint-by-endpoint catalog
- `references/openapi-source.json`: raw source of truth
"""


def build_router(spec: dict) -> str:
    lines = [
        "# Intent Router",
        "",
        "Read this file first when you need to map a user goal to one ALAPI endpoint with minimal token usage.",
        "",
        f"- Total endpoints: `{len(spec['paths'])}`",
        "- Rule: find the closest business intent here first, then open `api-catalog.md` only for the selected endpoint.",
        "",
        "| Endpoint | Summary | Typical intent / when to use |",
        "| --- | --- | --- |",
    ]
    for path, methods in sorted(spec["paths"].items()):
        op = methods["post"]
        summary = (op.get("summary") or "").replace("|", "\\|").replace("\n", " ").strip()
        description = (op.get("description") or summary).replace("|", "\\|").replace("\n", " ").strip()
        if len(description) > 120:
            description = description[:117] + "..."
        lines.append(f"| `{path}` | {summary} | {description} |")
    return "\n".join(lines)


def build_catalog(spec: dict) -> str:
    grouped: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for path, methods in sorted(spec["paths"].items()):
        grouped[category_key(path)].append((path, methods["post"]))

    lines = [
        "# API Catalog",
        "",
        "This file is generated from `references/openapi-source.json`.",
        "",
        "## Table Of Contents",
        "",
    ]
    for key, items in sorted(grouped.items()):
        lines.append(f"- `{key}`: {len(items)} endpoints")

    for key, items in sorted(grouped.items()):
        lines.extend(["", f"## {key}", ""])
        for path, op in items:
            summary = op.get("summary", path)
            description = (op.get("description") or summary).replace("\n", " ").strip()
            schema = resolve_schema(op["requestBody"]["content"]["application/json"]["schema"], spec)
            fields = fields_from_schema(schema)
            body_example = sample_value("body", schema)
            lines.append(f"### {path}")
            lines.append("")
            lines.append(f"- 功能: {summary}")
            lines.append(f"- 用途: {description}")
            lines.append("- 调用方法:")
            lines.append(f"  - Method: `POST`")
            lines.append(f"  - URL: `{BASE_URL}{path}`")
            lines.append("  - Headers: `token: $ALAPI_TOKEN`, `Content-Type: application/json`")
            if fields:
                lines.append("")
                lines.append("| Field | Type | Required | Default | Description |")
                lines.append("| --- | --- | --- | --- | --- |")
                for field in fields:
                    default = field["default"].replace("|", "\\|")
                    description_text = field["description"].replace("|", "\\|")
                    lines.append(
                        f"| `{field['name']}` | `{field['type']}` | {field['required']} | {default} | {description_text} |"
                    )
            else:
                lines.append("")
                lines.append("- Request body: `{}`")
            lines.append("")
            lines.append("请求示例:")
            lines.append("")
            lines.append(bash_block(f"{BASE_URL}{path}", body_example))
            example = (
                op.get("responses", {})
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("example")
            )
            lines.append("")
            lines.append(f"- 成功响应说明: {response_summary(example)}")
            if example is not None:
                lines.append("")
                lines.append("响应示例:")
                lines.append("")
                lines.append(json_block(example))
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    skill_dir = Path(__file__).resolve().parents[1]
    references_dir = skill_dir / "references"
    spec = json.loads((references_dir / "openapi-source.json").read_text())
    write_text(references_dir / "auth-and-usage.md", build_auth_doc(spec))
    write_text(references_dir / "intent-router.md", build_router(spec))
    write_text(references_dir / "api-catalog.md", build_catalog(spec))


if __name__ == "__main__":
    main()
