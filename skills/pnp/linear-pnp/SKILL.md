---
name: linear-pnp
description: >-
  Fetch the Linear issues a person touched on a work date (assigned, created, or referenced
  by key) with status, assignee and linked PRs, as compact evidence lines for a Progress &
  Planning report. Also surfaces repos linked from issues so GitHub lookups can cover them.
  Use when progress-planning needs Linear evidence or To Do candidates.
metadata:
  keywords:
    - linear
    - issues
    - p&p
    - progress and planning
    - issue tracking
---

# linear-pnp

Return only issues that changed in the window or that the day's other evidence mentions.
Rule: no em-dashes in output.

## Fixed values

- User: Sokhibjon Baratov (`sokhibjon@wakil.ai`), use `"me"`
- Team: Wakil AI, key `WK`
- Issue link: `https://linear.app/wakilai/issue/<KEY-N>`

## Calls

Always pass a small `fields` list; the default payload is large.

1. Issues he owns that moved:
   ```
   list_issues(assignee: "me", updatedAt: "<D-1>", limit: 50,
               fields: ["id", "title", "url", "status", "assignee", "updatedAt"])
   list_issues(creator: "me", updatedAt: "<D-1>", limit: 50, fields: same)
   ```
   Keep rows with `updatedAt` inside the work date's UTC window.
2. Keys from elsewhere: collect every `[A-Z]+-\d+` found in Hubstaff task summaries, PR titles
   and branches, Discord or Telegram messages, and the previous P&P's To Do. For each key not
   already fetched:
   ```
   get_issue(id: "<KEY-N>", fields: ["id", "title", "url", "status", "assignee", "attachments", "updatedAt"])
   ```
   `attachments` holds linked PRs (`github.com/<owner>/<repo>/pull/<n>`) and repos.
3. Only when a Hubstaff task is about reviewing or commenting: `list_comments(issueId)` and keep
   comments by him inside the window.

## Output

```
<KEY-N> | <title> | <status> | <assignee> | <url> | PRs: <owner/repo#n, ...>
```

Then one line `REPOS | <owner/repo>, ...` listing every repo seen in attachments, for
`github-pnp`.
