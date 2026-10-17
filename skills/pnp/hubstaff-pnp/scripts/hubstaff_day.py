#!/usr/bin/env python3
"""Print one work day's Hubstaff tracked time per project and task.

Port of the Hubstaff collector in bride-sh/int-agent-bride-pnp, standard library only.
One paginated /activities call for the day's UTC window, then one lookup per task and
project id. Tasks under 5 minutes are dropped; durations round up to 5 minutes.

Env:
  HUBSTAFF_REFRESH_TOKEN  required unless HUBSTAFF_ACCESS_TOKEN is set
  HUBSTAFF_ACCESS_TOKEN   optional, used first
  HUBSTAFF_ORG_ID         default 542238 (HumbleBeeAI)
  HUBSTAFF_TOKEN_FILE     optional; rotated tokens are written here (mode 600)
  PNP_TIMEZONE            optional override; default is the Hubstaff profile time_zone

Usage: hubstaff_day.py [YYYY-MM-DD] [--json]
Exit code 0 with "status: ok", or 1 with "status: error" and the reason.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

API_URL = "https://api.hubstaff.com/v2"
DISCOVERY_URL = "https://account.hubstaff.com/.well-known/openid-configuration"
TIMEOUT_SECONDS = 15
MIN_TASK_SECONDS = 5 * 60


class HubstaffError(RuntimeError):
    """Raised when a Hubstaff request fails."""


def _http(method, url, *, token=None, params=None, form=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    data = urllib.parse.urlencode(form).encode() if form else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, {"error": exc.read()[:200].decode(errors="replace")}


def _save_tokens(access_token, refresh_token):
    path = os.environ.get("HUBSTAFF_TOKEN_FILE")
    if not path:
        return
    token_file = Path(path)
    token_file.touch(mode=0o600, exist_ok=True)
    token_file.chmod(0o600)
    token_file.write_text(
        f"HUBSTAFF_ACCESS_TOKEN={access_token}\nHUBSTAFF_REFRESH_TOKEN={refresh_token}\n"
    )


def refresh_access_token():
    refresh_token = os.environ.get("HUBSTAFF_REFRESH_TOKEN")
    if not refresh_token:
        raise HubstaffError("HUBSTAFF_REFRESH_TOKEN is not set")
    status, discovery = _http("GET", DISCOVERY_URL)
    if status != 200 or "token_endpoint" not in discovery:
        raise HubstaffError("OpenID discovery did not return a token endpoint")
    status, payload = _http(
        "POST",
        discovery["token_endpoint"],
        form={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    access_token = payload.get("access_token")
    if status != 200 or not access_token:
        raise HubstaffError(f"token exchange failed ({status}): {payload}")
    rotated = payload.get("refresh_token") or refresh_token
    if rotated != refresh_token:
        print("note: Hubstaff rotated the refresh token", file=sys.stderr)
    os.environ["HUBSTAFF_REFRESH_TOKEN"] = rotated
    os.environ["HUBSTAFF_ACCESS_TOKEN"] = access_token
    _save_tokens(access_token, rotated)
    return access_token


def api_get(path, params=None):
    """GET an API path, refreshing the token once on 401."""
    token = os.environ.get("HUBSTAFF_ACCESS_TOKEN") or refresh_access_token()
    status, payload = _http("GET", f"{API_URL}{path}", token=token, params=params)
    if status == 401:
        status, payload = _http(
            "GET", f"{API_URL}{path}", token=refresh_access_token(), params=params
        )
    return status, payload


def day_window(date_text, timezone_name):
    zone = ZoneInfo(timezone_name)
    if date_text:
        day = datetime.strptime(date_text, "%Y-%m-%d")
        start = datetime(day.year, day.month, day.day, tzinfo=zone)
    else:
        now = datetime.now(zone)
        start = datetime(now.year, now.month, now.day, tzinfo=zone)
    stop = start + timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    utc = ZoneInfo("UTC")
    return start.astimezone(utc).strftime(fmt), stop.astimezone(utc).strftime(fmt), start


def fetch_activities(org_id, user_id, start, stop):
    params = {"time_slot[start]": start, "time_slot[stop]": stop, "user_ids[]": user_id}
    entries = []
    while True:
        status, payload = api_get(f"/organizations/{org_id}/activities", params)
        if status != 200:
            raise HubstaffError(f"activities failed ({status}): {payload}")
        entries.extend(payload.get("activities", []))
        next_id = payload.get("pagination", {}).get("next_page_start_id")
        if not next_id:
            return entries
        params["page_start_id"] = next_id


def fetch_name(kind, item_id):
    if not item_id:
        return f"(no {kind})"
    status, payload = api_get(f"/{kind}s/{item_id}")
    if status != 200:
        return f"{kind}:{item_id}"
    record = payload.get(kind, {})
    name = record.get("summary") if kind == "task" else record.get("name")
    return (name or f"{kind}:{item_id}").lstrip("# ").strip()


def format_duration(seconds):
    """H:MM rounded up to the nearest five minutes."""
    minutes = math.ceil((seconds / 60) / 5) * 5
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}"


def aggregate(entries, task_names, project_names):
    totals = defaultdict(int)
    first_seen, last_seen = {}, {}
    for entry in entries:
        key = (
            project_names.get(entry.get("project_id"), "(no project)"),
            task_names.get(entry.get("task_id"), "(no task)"),
        )
        totals[key] += entry.get("tracked", 0)
        slot = entry.get("time_slot") or entry.get("starts_at") or ""
        if slot:
            first_seen[key] = min(first_seen.get(key, slot), slot)
            last_seen[key] = max(last_seen.get(key, slot), slot)

    projects = defaultdict(list)
    dropped = []
    for (project, task), seconds in totals.items():
        item = {
            "task": task,
            "seconds": seconds,
            "duration": format_duration(seconds),
            "first": first_seen.get((project, task), ""),
            "last": last_seen.get((project, task), ""),
        }
        if seconds < MIN_TASK_SECONDS:
            dropped.append({"project": project, **item})
            continue
        projects[project].append(item)
    for tasks in projects.values():
        tasks.sort(key=lambda item: item["seconds"], reverse=True)
    return dict(projects), dropped


def collect(date_text=None):
    org_id = os.environ.get("HUBSTAFF_ORG_ID", "542238")
    status, payload = api_get("/users/me")
    if status != 200:
        raise HubstaffError(f"users/me failed ({status}): {payload}")
    user = payload.get("user", {})
    timezone_name = os.environ.get("PNP_TIMEZONE") or user.get("time_zone") or "UTC"
    start, stop, local_day = day_window(date_text, timezone_name)
    entries = fetch_activities(org_id, user["id"], start, stop)

    task_ids = sorted({e["task_id"] for e in entries if e.get("task_id")})
    project_ids = sorted({e["project_id"] for e in entries if e.get("project_id")})
    with ThreadPoolExecutor(max_workers=8) as pool:
        task_names = dict(zip(task_ids, pool.map(lambda i: fetch_name("task", i), task_ids)))
        project_names = dict(
            zip(project_ids, pool.map(lambda i: fetch_name("project", i), project_ids))
        )

    projects, dropped = aggregate(entries, task_names, project_names)
    total = sum(item["seconds"] for tasks in projects.values() for item in tasks)
    return {
        "status": "ok",
        "user": user.get("name"),
        "date": local_day.strftime("%Y-%m-%d"),
        "timezone": timezone_name,
        "window_utc": [start, stop],
        "total_seconds": total,
        "total": format_duration(total),
        "projects": projects,
        "dropped_under_5_min": dropped,
    }


def render(result):
    start, stop = result["window_utc"]
    lines = [
        f"status: ok | {result['date']} ({result['timezone']}) | total {result['total']}",
        f"WINDOW | {start} | {stop}",
    ]
    ordered = sorted(
        result["projects"].items(),
        key=lambda pair: sum(item["seconds"] for item in pair[1]),
        reverse=True,
    )
    for project, tasks in ordered:
        project_seconds = sum(item["seconds"] for item in tasks)
        lines.append(f"PROJECT | {project} | {format_duration(project_seconds)}")
        for item in tasks:
            span = f"{item['first']}..{item['last']}" if item["first"] else ""
            lines.append(f"  [{item['duration']}] {item['task']} | {span}")
    for item in result["dropped_under_5_min"]:
        lines.append(f"DROPPED | {item['project']} | {item['task']} | {item['seconds']}s")
    return "\n".join(lines)


def main(argv):
    as_json = "--json" in argv
    args = [arg for arg in argv if arg != "--json"]
    try:
        result = collect(args[0] if args else None)
    except (HubstaffError, KeyError, urllib.error.URLError) as exc:
        error = {"status": "error", "error": str(exc)}
        print(json.dumps(error) if as_json else f"status: error | {exc}")
        return 1
    print(json.dumps(result, indent=2) if as_json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
