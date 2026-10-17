# progress-planning config

Values the orchestrator needs. Source-specific ids live in each `*-pnp` skill.

## Time

- Report timezone: UZT, Asia/Tashkent (UTC+5). Work date D = `D-1T19:00:00Z` to
  `DT19:00:00Z`.
- hstaff counts a P&P on time until 21:00 KST (17:00 UZT), late until 22:00Z (03:00 UZT next
  day), then missed.

## Progress & Planning doc (Claude Docs)

- Link: `https://claude.ai/code/artifact/9d453c58-ecf9-4d0c-b1f6-6882120fd06d`
- Doc id: `9d453c58-ecf9-4d0c-b1f6-6882120fd06d`
- Overview tab `e3aac6e2-a95b`, body node `bc5258ea-de3e`
- Month tabs (name: tab id). Add a line when a run creates a new month:
  - October 2026: `649dc278-939e`

Ids drift if someone restructures the doc. When an id is refused, `read` the doc
(`ref: {"object":"project","id":"<doc id>"}`), find tabs by name, and fix this file.
