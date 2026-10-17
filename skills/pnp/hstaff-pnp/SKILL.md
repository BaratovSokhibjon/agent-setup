---
name: hstaff-pnp
description: >-
  Read and write Progress & Planning entries in hstaff (HumbleBeeAI's staff system): fetch
  recent P&Ps and their To Do lists for carry-over, check a date's status (on_time, late,
  missed, day_off), and create or update the entry for a date. Use when progress-planning
  needs history or is ready to post, or when asked about P&P history, missed days, or to
  post or fix a P&P in hstaff.
metadata:
  keywords:
    - hstaff
    - progress planning
    - p&p
    - post p&p
    - missed p&p
---

# hstaff-pnp

hstaff holds the official P&P. The status-bot mirrors each entry into the person's Discord
P&P thread, so posting here is posting everywhere. Rule: no em-dashes in output.

## Calls

**History (carry-over and status):**

```
get_progress_planning_by_date_range(start_date: D-7, end_date: D-1)
```

Optional `status` filter: `on_time`, `late`, `missed`, `day_off`. Take the newest entry with
content. Use `get_progress_planning_by_id(id)` only when a list row lacks full content.

**Post:**

```
create_progress_planning(date: D, content: "<report markdown>")
```

If it refuses because an entry exists for D, send the same arguments to
`update_progress_planning`. Edits are allowed only within hstaff's allowed days back; a
refusal there is final, so report it.

**Tracked time helper:** `get_task_time(date: D)` (same data as Hubstaff, grouped by project).

## Deadline

21:00 KST (12:00Z). The bot reminds at 11:30Z, and marks the day `missed` at 22:00Z; in
between it is `late`. In UZT: on time until 17:00, late until 03:00 next day.

## Fallback when hstaff fails

A `401 TOKEN_MISSING` means the hstaff connector is not signed in; nothing will post until
the user reconnects it. Then:

- History: read the Discord P&P thread `1279361405249650802` (guild `1138065656915443722`)
  with Discord `read_messages(limit: 30)`. Status-bot messages starting `## YYYY-MM-DD` are
  past entries; `P&P Missed` messages mark missed days.
- Posting: do not post anywhere else. Return the failure so the caller records it.

## Output

- History: `<date> | <status> | <id>` per entry, then the newest entry's To Do lines verbatim,
  each with the number of consecutive entries it has appeared in.
- Post: `posted <date> id=<id>` or `failed <date>: <error>`.
