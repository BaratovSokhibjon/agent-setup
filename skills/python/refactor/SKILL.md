---
name: python-refactor
description: >-
  Refactor changed Python code to the Google Python Style Guide with the smallest safe,
  behavior-preserving edits. Works from the current git diff. Use when the user asks to
  refactor, clean up, tidy, or improve the readability of Python code without changing
  behavior, exports, public APIs, routes, or schemas. Enforces Google-style docstrings,
  PEP 8 layout, type hints, and Python-specific cleanup.
metadata:
  keywords:
    - python
    - refactor
    - clean up
    - readability
    - google python style guide
    - pep 8
    - type hints
    - behavior-preserving
---

# python-refactor

You are a strict, pragmatic Python refactor workflow. Work from the current diff. Make the
smallest safe edits that make changed Python code easier to scan, name, and maintain
**without changing behavior, exports, public APIs, routes, schemas, or unrelated code**.

Follow project conventions first (existing `pyproject.toml`, `ruff`, `black`, `flake8`,
`isort`, `mypy` config), then the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
and PEP 8, then general Python idioms.

## Workflow

1. **Inspect the worktree** (read-only):

   ```bash
   git status --porcelain=v1
   git diff HEAD
   git diff --cached
   ```

   If there is no diff, ask which files or range to refactor.

2. **Use optional review context** at the per-project path so concurrent refactors never
   collide: `/tmp/<dirname>/code-review.md` (`<dirname>` is the current directory name).

   ```bash
   cat "/tmp/$(basename "$PWD")/code-review.md" 2>/dev/null
   ```

   If present, fix CRITICAL findings first, then WARNING, then SUGGESTION.

3. **Find project conventions**: inspect `pyproject.toml`, `setup.cfg`, `ruff.toml`,
   `.flake8`, tooling config, tests, imports, and names. The repo's configured line length,
   quote style, and import order win over defaults. Do not impose `src/` layout, mirrored
   `tests/`, or other structure the repo does not already use.

4. **Apply mandatory Python cleanup**:
   - Remove Python file-top/module docstrings.
   - Do not remove function, class, or method docstrings.
   - Remove `from __future__ import annotations` anywhere it appears.
   - Keep retained docstrings concise and Google-style: one-line summary, optional blank
     line, then `Args:` / `Returns:` / `Raises:` sections only when they add information.

5. **Apply Google Python Style Guide conventions** (only on changed code, never rewrite
   unrelated lines):
   - **Naming**: `snake_case` for functions, methods, variables, and modules; `CapWords`
     for classes; `CONSTANT_CASE` for module-level constants; leading underscore for
     internal/private names. Fix misleading or off-convention names introduced in the diff.
   - **Imports**: import modules and packages, not individual names, when it aids clarity
     (`from x import y` is fine for common symbols; avoid `from x import *`). Group as
     standard library, third-party, then local, with a blank line between groups; sort
     within a group. Remove unused imports.
   - **Type hints**: add or correct annotations on changed public functions and methods.
     Prefer built-in generics (`list[str]`, `dict[str, int]`) and `X | None` over
     `Optional[X]` on modern targets; match the project's existing style.
   - **Strings**: prefer f-strings over `%` and `.format()`. Keep the repo's quote style.
   - **Defaults**: never use mutable default arguments (`def f(x=[])`); use `None` and
     initialize inside.
   - **Control flow**: prefer guard clauses and early returns over deep nesting; prefer
     comprehensions over manual accumulation loops when they stay readable (avoid nested or
     side-effecting comprehensions).
   - **Resources**: use `with` context managers for files, locks, and connections.
   - **Exceptions**: catch specific exceptions, never bare `except:`; do not swallow errors
     silently.
   - **Comparisons**: `is`/`is not` only for `None` and singletons; use `==` for values.

6. **Normalize em-dashes globally**:

   ```bash
   rg -n -P '\x{2014}'
   perl -CSD -0pi -e 's/\x{2014}/-/g' <files>
   ```

   Skip semantic data values, snapshots, fixtures, URLs, or tests where the exact
   character matters.

7. **Normalize section markers** to a single canonical form: `# MARK: <label>` (comment
   leader, space, `MARK:`, space, label). Find variants first with
   `rg -n -i 'mark:?\b'` and rewrite alternates (missing colon, wrong case, no spacing,
   dash decoration). Skip matches inside strings, data, or docs.

8. **Analyze changed code**: naming consistency across analogous modules; dead imports and
   unreachable code; long functions, deep nesting, duplicated logic; magic values that want
   named constants; unclear error handling and logging.

9. **Classify risk before editing**:
   - Low: unused imports, local renames, docstring cleanup, f-string conversion, guard
     clauses, tiny helper extraction.
   - Medium: reordering within a module, reworking private helpers, changing internal
     imports.
   - High: file moves, renaming exported symbols, route/schema changes, broad renames, new
     modules, public API changes, test rewrites.
   - Apply low-risk directly. Apply medium-risk only when the readability win is clear. Ask
     before high-risk changes unless the user requested them.

10. **Apply focused edits**: edit only files needed for the refactor. Preserve behavior,
    public interfaces, dependency shape, and unrelated user changes. After moves/renames,
    remove orphan directories and update imports and tests.

11. **Verify** with the nearest discoverable tools, preferring targeted runs:

    ```bash
    ruff check <files> ; ruff format <files>   # or black / isort / flake8 if configured
    mypy <files>                                # if the project uses it
    pytest <nearest test path>                  # for behavioral safety
    ```

    Run the full suite for rename/move batches. If verification cannot run, say why.

12. **Summarize**: files changed and why, risky refactors skipped, verification results.

## Rules

- Never change observable behavior unless explicitly asked.
- Never remove or rename exported symbols unless explicitly asked.
- Never remove function, class, or method docstrings.
- Always remove Python file-top/module docstrings.
- Always remove `from __future__ import annotations` from Python source.
- Never replace structured logging with `print`.
- Never use bare `except:` or mutable default arguments in changed code.
- Never stage unrelated files.
- Never force generic architecture on a repo with its own convention.
- Always normalize existing section markers to a single `# MARK: <label>` format.
- Prefer code a human understands on first pass over cleverness.
- If a file is already clean, skip it and say so.
</content>
