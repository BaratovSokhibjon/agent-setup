---
name: hubstaff-pnp
description: >-
  Fetch one person's Hubstaff tracked time for a work date, grouped by project and task, as a
  compact table for writing a Progress & Planning report. Use when progress-planning needs
  the day's time backbone, or when asked how much time went to which task on a given day.
  Read-only; two calls at most for a normal day.
metadata:
  keywords:
    - hubstaff
    - tracked time
    - timesheet
    - p&p
    - progress and planning
---

# hubstaff-pnp

Return the day's tracked time per task, nothing else. Rule: no em-dashes in output.

## Fixed ids

- Organization `HumbleBeeAI`: `542238`
- Sokhibjon: user `2841882`
- Hubstaff profile timezone: Asia/Seoul. Report timezone: UZT (UTC+5). Work date D in UZT
  is the UTC window `D-1T19:00:00Z` to `DT19:00:00Z`.

Skip `list_organizations`, `list_endpoints` and `describe_endpoint`; the calls below are
already known.

## Calls

**Normal day (all work before 20:00 UZT, which is KST midnight):** one call.

```
call_endpoint get_organizations_organization_id_activities_daily
  {organization_id: 542238, user_ids: [2841882],
   date: {start: D, stop: D}, include: ["projects", "tasks"]}
```

Rows give `project_id`, `task_id`, `tracked` (seconds), `created_at` (first activity) and
`updated_at`. Side-loaded `projects[].name` and `tasks[].summary` give the names.

**Late day (tracking after 20:00 UZT) or exact boundaries needed:** use 10-minute slots.

```
call_endpoint get_organizations_organization_id_activities
  {organization_id: 542238, user_ids: [2841882],
   time_slot: {start: "<D-1>T19:00:00Z", stop: "<D>T19:00:00Z"}, include: ["projects", "tasks"]}
```

Sum `tracked` per `task_id`; first and last `time_slot` give the task's time range. Page
with `page_start_id` while the response has `pagination.next_page_start_id`.

**Fallback:** hstaff `get_task_time(date)` returns the same time grouped by project and task.

## Output

One line per task, sorted by project then tracked time descending:

```
<project name> | <task_id> | <task summary> | <H:MM> | <first UTC>..<last UTC>
```

- `H:MM` = seconds rounded to the nearest minute. Tasks under 1 minute are left out.
- Strip a leading `# ` from task summaries.
- End with `TOTAL | <H:MM>` and one `PROJECT | <name> | <H:MM>` line per project.

Do not interpret the work; matching time to evidence happens in `progress-planning`.
