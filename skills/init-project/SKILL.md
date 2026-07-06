---
name: init-project
description: >-
  Bootstrap a project from the best-matching humblebeeai template. Lists the org's template
  repositories programmatically, picks the one that fits the project's language and purpose,
  and falls back to base-template when nothing matches. Then adapts every template-specific
  value to the target. Use when the user asks to init, scaffold, bootstrap, or set up a
  project, or to adopt a humblebeeai template into an existing repo. Never carries the
  template git history into the target.
metadata:
  keywords:
    - init project
    - scaffold
    - bootstrap
    - humblebeeai template
    - base-template
    - project setup
    - pre-commit
    - release tooling
---

# init-project

You bootstrap a project from a humblebeeai template. First discover which templates the org
publishes, match one to the project's context, then bring its setup into the target and
rewrite every template-specific value so nothing still points at the template. When no
template fits, fall back to `base-template`, the org's language-agnostic standards scaffold.

Org: `humblebeeai`. Fallback template: `base-template`.

## Decide the mode first

Inspect the current directory before doing anything:

```bash
pwd
git rev-parse --is-inside-work-tree 2>/dev/null
ls -A
```

- **New project**: the target does not exist yet, or the current directory is empty. You
  will scaffold from scratch.
- **Adopt into existing project**: the current directory already has code or git history.
  You will layer the scaffolding in without clobbering existing files.

If it is ambiguous, ask the user which they want before writing anything.

## Workflow

1. **List the org's templates programmatically**. Query the GitHub API for repos flagged as
   templates (requires `gh` to be authenticated):

   ```bash
   gh api "orgs/humblebeeai/repos?per_page=100" \
     --jq '.[] | select(.is_template==true) | "\(.name)\t\(.description // "")"'
   ```

   This is the authoritative list; the roster changes over time, so do not rely on a
   hardcoded set. If `gh` is missing or unauthenticated, say so and fall back to
   `base-template`.

2. **Detect the project context**. Read what the target already is, using whichever signals
   are present:
   - Language and package manifests: `pyproject.toml`, `setup.py`, `requirements*.txt`,
     `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`.
   - Frameworks and libraries in those manifests (e.g. `fastapi`, `sqlalchemy`/`alembic`,
     `torch`/`tensorflow`/`scikit-learn`, `mkdocs`, `zensical`, `nginx`).
   - File layout, existing config, README, and anything the user states about intent.
   - If the target is empty, ask the user what they are building (a web API, an ML model,
     a Python library, a docs site, a server, etc.).

3. **Match a template to the context**. Score each listed template by its name and
   description against the detected signals. Typical mappings (verify against the live list,
   do not assume these exact names still exist):
   - FastAPI service with an ORM (SQLAlchemy/Alembic) -> `rest-fastapi-orm-template`.
   - FastAPI service without an ORM -> `rest-fastapi-template`.
   - AI/ML model module (torch, tensorflow, scikit-learn, model artifacts) ->
     `model-python-template`.
   - Plain Python module or library -> `module-python-template`.
   - Documentation site with MkDocs -> `docs-mkdocs-template`; with Zensical ->
     `docs-zensical-template`.
   - NGINX server, reverse proxy, or web-server stack -> `server-nginx-template`.
   - Nothing fits confidently -> `base-template`.

   State the chosen template and the reason. If two templates tie or the signal is weak,
   ask the user to confirm before cloning.

4. **Create the project from the template.** The path depends on the mode. Set
   `TEMPLATE="<chosen-template-name>"` first.

   - **New project that wants a GitHub repo** (recommended for new work): use GitHub's
     native template generation. Because these are real template repos, this produces a
     fresh single-commit history and creates the remote in one step, with no `.git` to
     strip. Confirm owner, name, and visibility with the user first:

     ```bash
     gh repo create "<owner>/<name>" --template "humblebeeai/${TEMPLATE}" --private --clone
     cd "<name>"
     ```

     Then skip to step 7 (the files are already in place; there is nothing to copy).

   - **New project, local only, or adopt into an existing project**: clone the template
     shallow into a temp dir, never into the target, so the template `.git` never mixes
     with the target. Copy happens in step 6:

     ```bash
     TEMPLATE_DIR="$(mktemp -d)"
     git clone --depth 1 "https://github.com/humblebeeai/${TEMPLATE}" "$TEMPLATE_DIR"
     rm -rf "$TEMPLATE_DIR/.git"
     ```

5. **Read what the template actually provides** before copying. Templates differ; do not
   assume a fixed inventory. Inspect `$TEMPLATE_DIR` and note its scaffolding, config, and
   any placeholder or template-named files. For reference, `base-template` provides release
   scripts under `scripts/`, GitHub Actions under `.github/workflows/`,
   `.pre-commit-config.yaml`, `.editorconfig`, `.gitignore`, `.github/CODEOWNERS`
   (`* @humblebeeai`), a `VERSION.txt`, and empty `README.md`/`.env.example`/`Dockerfile`/
   `compose.yml` placeholders.

6. **Copy the scaffolding into the target** (skip this step if you used native template
   generation in step 4). Always copy with a tool that preserves dotfiles and permissions;
   a bare `cp -r <dir>/*` silently drops `.github/`, `.pre-commit-config.yaml`, and other
   hidden entries. Use `rsync -a` (or `cp -a` on the whole directory), and keep the trailing
   slash on the source so contents, not the directory itself, are copied.

   - **New project (local only)**: mirror the template in, including dotfiles, then start
     fresh history:

     ```bash
     rsync -a --exclude='.git' "$TEMPLATE_DIR"/ ./
     git init
     ```

   - **Existing project**: add only files the target lacks; never overwrite existing files.
     `--ignore-existing` enforces that:

     ```bash
     rsync -a --ignore-existing --exclude='.git' "$TEMPLATE_DIR"/ ./
     ```

     Then, for files present in both that should merge rather than stay untouched (commonly
     `.gitignore`, `.editorconfig`), show the diff and merge additively or ask the user
     which to keep. Preserve all existing source and history.

7. **Adapt every template-specific value** to the target. Do not leave template identity
   behind. Scan the copied files for the template and org names and rewrite them:

   ```bash
   grep -rniI "${TEMPLATE}\|humblebeeai" . --exclude-dir=.git
   ```

   Common adaptations:
   - `.github/CODEOWNERS`: replace `@humblebeeai` with the target owner or team. Ask if
     unknown.
   - Any docs or README that reference the template repo name or its clone URL: rewrite to
     the target project name.
   - `VERSION.txt` (if present): reset to a clean starting version (e.g. `0.0.0-<UTC yymmdd>`)
     unless the user wants to keep an existing version.
   - Empty placeholders (`README.md`, `.env.example`, `Dockerfile`, `compose.yml`): fill
     them for the target, or leave a clear `TODO` when the detail is not yet known. Never
     leave the README blank.
   - `.gitkeep` files: delete each once the directory has real content.

8. **Match language and tooling to the target**. If the template ships a
   `.pre-commit-config.yaml` or linters pinned to a language or version the target does not
   use, adjust them: keep the language-agnostic hooks (gitleaks, detect-secrets, shellcheck,
   generic file checks) and swap language-specific hooks for the target's toolchain. Do not
   leave hooks that will fail because the toolchain is absent.

9. **Enable the tooling** (only if the tools are installed; report if they are not):

   ```bash
   chmod +x scripts/*.sh 2>/dev/null || true
   pre-commit install 2>/dev/null || true
   pre-commit run --all-files   # optional first pass; expect formatting fixes
   ```

10. **Clean up** the temp clone (only if you made one in step 4; skipped for native
    generation):

    ```bash
    [ -n "${TEMPLATE_DIR:-}" ] && rm -rf "$TEMPLATE_DIR"
    ```

11. **Summarize**:
    - Name the template chosen and why (or that it fell back to `base-template`).
    - List files added, files adapted, and files skipped (already present).
    - Call out every value you changed (owner, version, project name, README).
    - Note anything left as a `TODO` (Docker, env vars, language hooks).
    - Report whether `pre-commit install` and any scripts ran cleanly.

## Rules

- Always list templates from the org live; never trust a hardcoded roster as current.
- Always fall back to `base-template` when no template matches or `gh` is unavailable.
- Prefer native template generation (`gh repo create --template`) for a new project that
  wants a GitHub repo; use the clone-to-temp copy only for local-only or adopt-into-existing.
- Never carry the template `.git` into the target. Use native generation, or clone to a
  temp dir and copy files with `rsync -a`/`cp -a` so dotfiles come across.
- Never overwrite existing source, config, or history in an adopt-into-existing run.
  When in doubt, show the diff and ask.
- Never leave template identity in the target: no `@humblebeeai` owner unless the user
  wants it, no template clone lines, no blank README.
- Never keep pre-commit hooks whose toolchain the target lacks.
- Confirm the template with the user when the match is weak or ambiguous.
- Do not use em-dashes in files you write or in your output.
