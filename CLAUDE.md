# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`agent-setup` is a personal **library of Claude Code skills** authored as Markdown, not an
application. There is no build, test, or lint toolchain; the "source" is `SKILL.md` files.
Skills are consumed by end users via the `skills` CLI:

```bash
npx skills add BaratovSokhibjon/agent-setup            # install everything
npx skills add BaratovSokhibjon/agent-setup --skill <name>   # install one skill by frontmatter name
npx skills add BaratovSokhibjon/agent-setup --list     # list what is available
```

"Working in this repo" means authoring and editing skills, so the checks that matter are
content conventions, verified with ripgrep/grep rather than a test runner (see Conventions).

## Catalog layout and the install contract

Skills live under `skills/<category>/<name>/SKILL.md`. The **category directory is purely
organizational**; what a user installs with `--skill` is the `name` in the skill's
frontmatter, which must be globally unique across the catalog. Root-level skills (no
category dir) exist for cross-cutting workflows: `commit`, `init-project`, `build-service`.

Every skill's frontmatter follows one shape:

```yaml
---
name: <kebab-name>
description: >-
  <folded multi-line description; say what it does and when to use it>
metadata:
  keywords:
    - ...
---
```

`README.md` holds a catalog table of every skill. **Editing the skill set and the README
table go together**: adding, renaming, moving, or removing a skill must update its row.

## Skill families and how they relate

The catalog is not a flat pile; several skills are designed to compose. Reading only one
SKILL.md misses these relationships:

- **review / refactor pairs** (`generic` plus `python`, `javascript`, `typescript`, `go`):
  the `review` skill writes a report to `/tmp/<dirname>/code-review.md` (per-project path so
  concurrent runs never collide), which the matching `refactor` skill reads to prioritize
  fixes. Pick the language variant matching the diff; fall back to `generic`.
- **The `-support` security skills** (`api-key-support`, `oauth-support`, `rbac-support` in
  `generic`, plus `configify` and `api-responses`): each follows the same gate,
  **detect -> (if absent) analyze the app and propose a tailored design -> escalate for
  approval -> else mirror the existing convention**. They interlock (auth guards raise
  `api-responses` codes; credentials narrow `rbac-support` scopes), and their security
  invariants must never be loosened by a caller.
- **`resource-scaffold`** generates a feature slice (model, schemas, service, router) that
  is guarded by `rbac-support` scopes, raises `api-responses` codes, and reads config via
  `configify`.
- **`build-service`** is the orchestrator: it asks the user which components to configure,
  then sequences the skills above (plus `init-project`, the database skills, and `commit`)
  in dependency order. It delegates to each sub-skill rather than reimplementing them.
- **`init-project`** bootstraps a repo from the humblebeeai template org; `commit` creates
  Conventional Commits and strips agent/AI co-author trailers.

## How skills get derived: the `.reference/` workflow

`.reference/` (gitignored) holds full clones of real codebases used as source material to
derive skills from. Many of the `generic` and `python` skills were extracted by studying
`.reference/rest-core-api` (a humblebeeai FastAPI service). When deriving or updating a
skill from a reference:

- **Genericize.** A skill must not carry source-specific identifiers (project names, class
  names like `*ORM`/`*PM`, internal library names, real env prefixes, domain scopes). Study
  the concrete code, then describe the *pattern* abstractly so it applies to any project
  following that convention. After editing, grep the skill for reference-specific tokens.
- Language-portability matters: `generic` skills are phrased to fit exception-based and
  error-value languages alike (say "raise or return a coded error per the language's
  idiom", not "raise an exception").

`skills/database/*` (`mysql`, `postgres`, `vitess`, `neki`) are **vendored, not derived**:
copied from `planetscale/database-skills` (MIT). They keep their `references/` subdirectories
and the upstream license at `skills/database/LICENSE`; attribution is noted in the README.

## Conventions (enforce when authoring or editing a skill)

- **No em-dashes** anywhere in skill content or in your own output. Every skill states this
  rule; verify with `rg -n -P '\x{2014}' <file>`.
- Keep behavior and security invariants of composed skills intact; do not have one skill
  loosen another's guarantees.
- When you add a new skill that `build-service` could orchestrate, **ask the user whether to
  add it to `build-service`** (as a new selectable component and a phase in the right
  dependency position). Do not silently extend or ignore the orchestrator.
- After creating or renaming a skill, update the `README.md` catalog table in the same change.
