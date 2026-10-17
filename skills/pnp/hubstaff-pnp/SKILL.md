---
name: hubstaff-pnp
description: >-
  Fetch one person's Hubstaff tracked time for a work date, grouped by project and task, as a
  compact table for writing a Progress & Planning report. Uses a bundled script that calls the
  Hubstaff REST API directly (one paginated activities call plus name lookups), with a single
  MCP call as fallback. Use when progress-planning needs the day's time outline.
metadata:
  keywords:
    - hubstaff
    - tracked time
    - timesheet
    - p&p
    - progress and planning
---

# hubstaff-pnp

Return the day's tracked time per task, nothing else. No em-dashes in output.

## Steps

1. **Script (primary).** Needs `HUBSTAFF_REFRESH_TOKEN` (or `HUBSTAFF_ACCESS_TOKEN`) in the
   environment.
   ```bash
   python3 -I skills/pnp/hubstaff-pnp/scripts/hubstaff_day.py <YYYY-MM-DD>
   ```
   Defaults: org `542238`, timezone `Asia/Tashkent` (override with `HUBSTAFF_ORG_ID`,
   `PNP_TIMEZONE`). Use its output as is.
2. **Fallback, only if the script prints `status: error`.** Exactly one MCP call, no
   `list_organizations`, `list_endpoints` or `describe_endpoint`:
   ```
   Hubstaff call_endpoint get_organizations_organization_id_activities
     {organization_id: 542238, user_ids: [2841882],
      time_slot: {start: "<D-1>T19:00:00Z", stop: "<D>T19:00:00Z"}, include: ["projects", "tasks"]}
   ```
   Page with `page_start_id` only while `pagination.next_page_start_id` is set. Sum `tracked`
   per task, then apply the same rules as the script: drop tasks under 5 minutes, round each
   duration up to the nearest 5 minutes, strip a leading `# ` from task names.
3. **Both fail:** return `status: error | <script error> | <mcp error>`. Never report an error
   as zero time.

## Output (what the script prints)

```
status: ok | <date> (<timezone>) | total <H:MM>
PROJECT | <project name> | <H:MM>
  [<H:MM>] <task summary> | <first slot UTC>..<last slot UTC>
DROPPED | <project> | <task> | <seconds>s
```

`DROPPED` lines are tasks under 5 minutes; they go to the run notes, not the report.

## Token note

Hubstaff may rotate the refresh token on exchange; the script then prints
`note: Hubstaff rotated the refresh token` to stderr and, when `HUBSTAFF_TOKEN_FILE` is set,
writes the new pair there. In an ephemeral cloud session the rotated token is lost, so if the
stored secret stops working, generate a new token and update the environment secret.
