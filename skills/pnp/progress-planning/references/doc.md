# The Progress & Planning doc

One Claude Doc, ids in [../config.md](../config.md). Use the Claude Docs tools (`batch`,
`update`, `read`); if no docs skill or guide is loaded, call `guide(items: ["topic.index",
"topic.tabs"])` once first.

## Layout

- **Overview** tab (order `a0`): title, one-line lead, and a **Log** table, newest row first:
  `| Date | Tracked | hstaff | Notes |`. `hstaff` is `posted`, `updated` or `not posted`.
- One **month** tab per month, named `October 2026`, order `b` + `(999999 - YYYYMM)` so the
  newest month sorts first (October 2026: `b797389`).
- One **day** tab per work date, nested under its month (`subtabOf` = month tab id), named
  `YYYY-MM-DD`, order `c` + `(99999999 - YYYYMMDD)` (2026-10-16: `c79738983`). File
  `birthName` is `YYYY-MM-DD.ldoc`.

## Day tab content

1. The report exactly as posted to hstaff (starting `## YYYY-MM-DD`).
2. `## Run notes` with short bullets:
   - `Tracked X:XX, reported Y:YY`
   - `Dropped (no evidence): <task> [H:MM], ...`
   - `Stale To Do (n entries): <item>`
   - `hstaff: posted id=<id>` or `hstaff: not posted, <error>`
   - `Sources missing: <source, reason>` when any failed

## Steps

1. `read(ref: {"object":"project","id":"<doc id>"})` and check `files[]` for a tab named D.
2. **Month tab missing:** create it (file + prose node + file update + tabs patch), in the same
   batch as the day tab. Add the new month's tab id to config.md in the repo.
3. **Day tab missing:** one `batch` on the doc container with: create file `D.ldoc`, create a
   prose node under it with the content, update the file to point at the node, and patch
   `tabs.<new tab>` = `{name: D, order, subtabOf: <month tab id>}`.
4. **Day tab exists (rerun):** read its body outline and `replace` its blocks with the new
   content; never create a second tab for the same date.
5. **Overview log:** insert the new row as the first data row of the Log table (or replace
   that date's row on a rerun).
