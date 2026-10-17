#!/usr/bin/env python3
"""Read and post Progress & Planning entries in hstaff, without a connector.

Talks to the hstaff MCP server over streamable HTTP the way bride-sh/int-agent-bride-pnp
does: credentials go in X-HSTAFF-EMAIL / X-HSTAFF-PASSWORD headers. Standard library only.

Env:
  HSTAFF_EMAIL, HSTAFF_PASSWORD   required
  HSTAFF_MCP_URL                  default https://hstaff.humblebee.ai/mcp

Usage:
  hstaff_pnp.py history <start YYYY-MM-DD> <end YYYY-MM-DD>
  hstaff_pnp.py post <YYYY-MM-DD> <report.md>      create, or update if the date exists
Prints JSON. Exit code 0 on success, 1 on error.
"""

import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 30
USER_AGENT = "hstaff-pnp/1.0 (+https://github.com/BaratovSokhibjon/agent-setup)"
TOOL_PREFIXES = {
    "history": "get_progress_planning_by_date_range",
    "create": "create_progress_planning",
    "update": "update_progress_planning",
}


class HstaffError(RuntimeError):
    """Raised when the hstaff MCP server fails or refuses a call."""


class McpClient:
    def __init__(self, url, email, password):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
            "X-HSTAFF-EMAIL": email,
            "X-HSTAFF-PASSWORD": password,
        }
        self.session_id = None
        self.next_id = 1

    def _post(self, message):
        headers = dict(self.headers)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        request = urllib.request.Request(
            self.url, data=json.dumps(message).encode(), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                self.session_id = response.headers.get("Mcp-Session-Id") or self.session_id
                body = response.read().decode()
        except urllib.error.HTTPError as exc:
            raise HstaffError(f"HTTP {exc.code}: {exc.read()[:200].decode(errors='replace')}")
        if "id" not in message:
            return None
        return _parse_response(body, message["id"])

    def request(self, method, params=None):
        message = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        self.next_id += 1
        if params is not None:
            message["params"] = params
        reply = self._post(message)
        if reply.get("error"):
            raise HstaffError(f"{method}: {reply['error']}")
        return reply.get("result", {})

    def connect(self):
        self.request(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "hstaff-pnp", "version": "1.0"},
            },
        )
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def tool_name(self, prefix):
        tools = self.request("tools/list").get("tools", [])
        for tool in tools:
            if tool["name"].startswith(prefix):
                return tool["name"]
        raise HstaffError(f"no hstaff tool starting with {prefix}")

    def call(self, prefix, arguments):
        result = self.request(
            "tools/call", {"name": self.tool_name(prefix), "arguments": arguments}
        )
        payload = result.get("structuredContent")
        if payload is None:
            text = "".join(
                part.get("text", "") for part in result.get("content", [])
                if part.get("type") == "text"
            )
            try:
                payload = json.loads(text) if text else {}
            except json.JSONDecodeError:
                payload = {"text": text}
        if result.get("isError"):
            raise HstaffError(json.dumps(payload)[:500])
        return payload


def _parse_response(body, message_id):
    """Return the JSON-RPC reply for message_id from a JSON or SSE body."""
    candidates = []
    if body.lstrip().startswith("{"):
        candidates.append(body)
    else:
        candidates.extend(
            line[5:].strip() for line in body.splitlines() if line.startswith("data:")
        )
    for raw in candidates:
        try:
            reply = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if reply.get("id") == message_id:
            return reply
    raise HstaffError(f"no reply for request {message_id}: {body[:200]}")


def client_from_env():
    email = os.environ.get("HSTAFF_EMAIL")
    password = os.environ.get("HSTAFF_PASSWORD")
    if not email or not password:
        raise HstaffError("HSTAFF_EMAIL and HSTAFF_PASSWORD are not set")
    client = McpClient(
        os.environ.get("HSTAFF_MCP_URL", "https://hstaff.humblebee.ai/mcp"), email, password
    )
    client.connect()
    return client


def history(start, end):
    payload = client_from_env().call(
        TOOL_PREFIXES["history"], {"start_date": start, "end_date": end}
    )
    entries = payload.get("entries", payload if isinstance(payload, list) else [])
    kept = [e for e in entries if start <= str(e.get("date", "")) <= end]
    return {"status": "ok", "start_date": start, "end_date": end, "entries": kept}


def post(date, report_path):
    with open(report_path, encoding="utf-8") as report:
        content = report.read().strip()
    if not content:
        raise HstaffError("report is empty")
    client = client_from_env()
    existing = client.call(TOOL_PREFIXES["history"], {"start_date": date, "end_date": date})
    entries = existing.get("entries", existing if isinstance(existing, list) else [])
    has_entry = any(str(e.get("date")) == date and e.get("content") for e in entries)
    action = "update" if has_entry else "create"
    result = client.call(TOOL_PREFIXES[action], {"date": date, "content": content})
    return {"status": "ok", "action": f"{action}d", "date": date, "result": result}


def main(argv):
    try:
        if len(argv) == 3 and argv[0] == "history":
            output = history(argv[1], argv[2])
        elif len(argv) == 3 and argv[0] == "post":
            output = post(argv[1], argv[2])
        else:
            print(__doc__.strip(), file=sys.stderr)
            return 2
    except (HstaffError, OSError, urllib.error.URLError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
