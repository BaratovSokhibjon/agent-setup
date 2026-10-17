---
name: hstaff-pnp
description: >-
  Read and write Progress & Planning entries in hstaff (HumbleBeeAI's staff system): fetch
  the last 4 days of P&Ps as context, check a date's status (on_time, late,
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

## Steps

Primary path is the bundled script; it talks to the hstaff MCP server directly, so no
connector is needed. Auth from the environment: `HSTAFF_TOKEN` (an hstaff API token) if set,
otherwise `HSTAFF_EMAIL` and `HSTAFF_PASSWORD`, which it exchanges for a JWT through the
server's login tool.

1. **History (context and status):**
   ```bash
   python3 -I skills/pnp/hstaff-pnp/scripts/hstaff_pnp.py history <D-4> <D-1>
   ```
   Returns `entries` with date, status and content. Reject entries outside the range.
   History is context only: it never shapes today's structure and its content is never
   today's work.
2. **Post:** write the report to a temp file, then
   ```bash
   python3 -I skills/pnp/hstaff-pnp/scripts/hstaff_pnp.py post <D> <report.md>
   ```
   It checks whether D already has an entry and creates or updates it. Edits are allowed only
   within hstaff's allowed days back; a refusal there is final, so report it.
3. **Script fails** (`"status": "error"`): use the hstaff connector tools if this session has
   them (`get_progress_planning_by_date_range`, `create_progress_planning`,
   `update_progress_planning`, same arguments). Otherwise use the fallback below.

## Deadline

21:00 KST (12:00Z). The bot reminds at 11:30Z, and marks the day `missed` at 22:00Z; in
between it is `late`. Convert to the run's timezone when reporting.

## Fallback when hstaff fails

`set HSTAFF_TOKEN, or HSTAFF_EMAIL and HSTAFF_PASSWORD`, `Invalid email or password` or
`401 TOKEN_MISSING` means no working
credentials; nothing will post until they are added to the environment. Then:

- History: read the Discord P&P thread `1279361405249650802` (guild `1138065656915443722`)
  with Discord `read_messages(limit: 30)`. Status-bot messages starting `## YYYY-MM-DD` are
  past entries; `P&P Missed` messages mark missed days.
- Posting: do not post anywhere else. Return the failure so the caller records it.

## Output

- History: `<date> | <status> | <id>` per entry, then each entry's TODO lines verbatim with
  its date.
- Post: `posted <date> id=<id>` or `failed <date>: <error>`.
