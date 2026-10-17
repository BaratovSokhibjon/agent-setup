# agent-setup

My library of Claude Code skills for development. Install what you need and Claude picks up
the matching skill automatically when the task fits.

## Install

```bash
npx skills add BaratovSokhibjon/agent-setup            # everything
npx skills add BaratovSokhibjon/agent-setup --skill <name>   # just one
npx skills add BaratovSokhibjon/agent-setup --list     # see the full list
```

## What you get

- **Ship code cleanly** - review any diff and refactor it without changing behavior, for
  Python, JavaScript, TypeScript, Go, or language-agnostic, then commit it in clean
  Conventional Commits. The review step writes a report the refactor step reads.
- **Stand up a backend, fast** - one orchestrator (`build-service`) builds a complete,
  secured service by wiring together the focused pieces: project bootstrap, layered config,
  a response and error-code convention, authentication, role/scope authorization, API keys,
  and per-feature CRUD scaffolding. Each piece also works on its own to extend an existing
  service.
- **Get the database right** - best-practice guidance for PostgreSQL, MySQL, Vitess, and
  Neki: schema, indexing, query tuning, and scaling.
- **Write in your own voice** - draft or revise outgoing work and casual messages with
  `write-like-sokhibjon` to match Sokhibjon's English, Uzbek, or mixed Discord style.
- **Daily Progress & Planning** - `progress-planning` writes the day's P&P from tracked time
  and real activity, adds it as a tab in a shared doc, and posts it to hstaff. It sequences
  one fast, token-light source skill per tool: `hubstaff-pnp` (time), `hstaff-pnp` (history
  and posting), `linear-pnp`, `github-pnp`, `discord-pnp` and `telegram-pnp` (evidence).

Run `--list` for the complete, per-skill breakdown, or browse `skills/`.

## Attribution

The database skills (PostgreSQL, MySQL, Vitess, Neki) are vendored from
[planetscale/database-skills](https://github.com/planetscale/database-skills), MIT licensed,
Copyright (c) PlanetScale. The upstream license is preserved at `skills/database/LICENSE`.
