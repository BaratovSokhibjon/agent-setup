---
name: refactor
description: >-
  Make the smallest safe, behavior-preserving edits that make changed code easier to
  scan, name, and maintain. Works from the current git diff. Use when the user asks to
  refactor, clean up, tidy, restructure, reorganize, or improve the readability of
  changed code without changing behavior, exports, public APIs, routes, or schemas.
metadata:
  keywords:
    - refactor
    - clean up
    - readability
    - code quality
    - behavior-preserving
    - em-dash normalization
---

# refactor

You are a strict, pragmatic refactor workflow. Work from the current diff. Make the
smallest safe edits that make changed code easier to scan, name, and maintain **without
changing behavior, exports, public APIs, routes, schemas, or unrelated code**.

Prefer project conventions first, formatter/linter rules second, official language
idioms third, and external style guides only when the repo has no clear convention.

## Workflow

1. **Inspect the worktree** (read-only):

   ```bash
   git status --porcelain=v1
   git diff HEAD
   git diff --cached
   ```

   If there is no diff, ask which files or range to refactor.

2. **Use optional review context**:

   ```bash
   cat /tmp/code-review.md 2>/dev/null
   ```

   If present, fix CRITICAL findings first, then WARNING, then SUGGESTION.

3. **Find project conventions**:
   - Inspect nearby files, package/config files, formatter/linter settings, tests,
     imports, names, and file layout.
   - Follow the local convention even when another style guide would be acceptable.
   - Do not impose generic structure such as `src/`, mirrored `tests/`, `.env.example`,
     or `VERSION` unless the repo already uses it.

4. **Apply mandatory Python cleanup**:
   - Remove Python file-top/module docstrings.
   - Do not remove function, class, or method docstrings.
   - Remove `from __future__ import annotations` anywhere it appears in Python source.
   - Keep retained Python docstrings concise and Google-style: summary line, optional
     blank line, then `Args` / `Returns` / `Raises` only when useful.

5. **Normalize em-dashes globally**:
   - Search with regex before editing (ripgrep needs `-P` for the `\x{...}` escape):

     ```bash
     rg -n -P '\x{2014}'
     ```

   - If matches are noisy, inspect or narrow with `fzf`, for example:

     ```bash
     rg -l -P '\x{2014}' | fzf --multi
     ```

   - Replace safe matches with ASCII `-`. Perl must decode UTF-8 (`-CSD`), or `\x{2014}`
     matches nothing:

     ```bash
     perl -CSD -0pi -e 's/\x{2014}/-/g' <files>
     ```

   - Skip semantic data values, snapshots, fixtures, URLs, or tests where the exact
     character matters.

6. **Analyze changed code**:
   - Naming consistency across analogous files, services, routers, helpers, and shims.
   - Dead imports, unreachable code, stale comments, boilerplate comments, and redundant
     docstrings.
   - Long functions, deep nesting, unclear control flow, duplicated logic, and misleading
     names.
   - Error handling, logging, type safety, magic values, and module boundaries.

7. **Classify risk before editing**:
   - Low risk: unused imports, local renames, stale comments, docstring cleanup, simple
     formatting, tiny helper extraction.
   - Medium risk: moving code inside a file, reorganizing private helpers, changing
     internal imports.
   - High risk: file moves, export changes, route/path changes, broad renames, new
     modules, public API changes, test rewrites.
   - Apply useful low-risk changes directly.
   - Apply medium-risk changes only when the readability win is clear.
   - Ask before high-risk changes unless the user explicitly requested them.

8. **Improve scanability**:
   - Prefer clear names, direct control flow, low nesting, and locality.
   - Group code as imports, constants, types, helpers, public API, private internals, and
     exports when that matches the file.
   - Add `MARK:`, `TODO:`, `NOTE:`, constants, helpers, or docstrings only when they solve
     a real readability problem.
   - Prefer deleting boilerplate over rewriting it.

9. **Apply focused edits**:
   - Edit only files needed for the refactor.
   - Preserve behavior, public interfaces, dependency shape, and unrelated user changes.
   - After file moves or renames, remove empty orphan directories and update affected
     imports/exports/tests.

10. **Verify**:
    - Run the nearest relevant formatter, linter, typecheck, or tests when discoverable.
    - Prefer targeted checks unless the change is broad.
    - For rename/move batches, run the full test suite and build when discoverable.
    - If verification cannot run, say why.

11. **Summarize**:
    - List files changed and why.
    - Note risky refactors skipped.
    - Report verification results.

## Rules

- Never change observable behavior unless explicitly asked.
- Never remove or rename exported symbols unless explicitly asked.
- Never remove function, class, or method docstrings.
- Always remove Python file-top/module docstrings.
- Always remove `from __future__ import annotations` from Python source.
- Never replace structured logging with `print` or `console.log`.
- Never stage unrelated files.
- Never force generic architecture on a repo with its own convention.
- Never add comments, docstrings, constants, helpers, or section markers just to satisfy
  a checklist.
- Prefer code that a human understands on first pass over cleverness.
- If a file is already clean, skip it and say so.
