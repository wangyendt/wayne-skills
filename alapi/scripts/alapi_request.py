#!/usr/bin/env python3
"""Call an ALAPI endpoint with token auth and a JSON body."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://v3.alapi.cn"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a POST request to an ALAPI endpoint using ALAPI_TOKEN."
    )
    parser.add_argument("endpoint", help="Endpoint path such as /api/ip or /api/ai/translate")
    parser.add_argument(
        "--body",
        default="{}",
        help="Inline JSON body string. Ignored when --body-file is provided.",
    )
    parser.add_argument(
        "--body-file",
        type=Path,
        help="Path to a JSON file containing the request body.",
    )
    parser.add_argument(
        "--token",
        help="Override ALAPI_TOKEN for this call. Prefer the environment variable.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="ALAPI base URL.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds.")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw response body instead of pretty JSON.",
    )
    return parser.parse_args()


def load_body(args: argparse.Namespace) -> dict | list:
    if args.body_file:
        return json.loads(args.body_file.read_text())
    return json.loads(args.body)


def normalize_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    return endpoint


def main() -> int:
    args = parse_args()
    endpoint = normalize_endpoint(args.endpoint)
    token = args.token or os.environ.get("ALAPI_TOKEN")
    if not token:
        print(
            "ALAPI_TOKEN is not set. Apply for one at https://apifox.com/apihub/ and export it first.",
            file=sys.stderr,
        )
        return 2

    try:
        body = load_body(args)
    except Exception as exc:
        print(f"Invalid JSON body: {exc}", file=sys.stderr)
        return 2

    url = f"{args.base_url.rstrip('/')}{endpoint}"
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "token": token,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {body_text}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(response_body)
        return 0

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError:
        print(response_body)
        return 0

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
