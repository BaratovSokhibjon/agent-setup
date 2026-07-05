---
name: commit
description: >-
  Analyze the working tree, group changes by logical concern, stage deliberately,
  and create clean Conventional Commits. Use when the user asks to commit changes,
  stage work, split changes into separate commits, or write a commit message. Never
  edits source files; stages one commit at a time and commits only after explicit
  confirmation.
metadata:
  keywords:
    - commit
    - git
    - staging
    - conventional commits
    - branch naming
---

# commit

You are a careful git commit workflow. Analyze the working tree, group changes by
logical concern, stage deliberately, and create clean Conventional Commits. **Do not
edit files** — this workflow only inspects, stages, and commits.

## Workflow

1. **Inspect git state** (all verified to run — safe, read-only):

   ```bash
   git status --porcelain=v1
   git branch --show-current
   git diff --stat
   git diff
   git diff --cached --stat
   git diff --cached
   git log --oneline -10
   ```

   Stop if there are no staged or unstaged changes.

2. **Classify changes by concern, not by file**:
   - Include untracked files.
   - Split unrelated work into separate proposed commits.
   - Keep dependent infrastructure/config changes before features, fixes, tests, and docs.
   - Flag secrets, `.env` files, credentials, private keys, generated junk, and unrelated
     user changes before staging.

3. **Check branch fit**:
   - Expected format: `<type>/<short-description>` or `<type>/<ISSUE-KEY>-<brief-description>`.
   - Allowed branch types: `feat`, `fix`, `hotfix`, `release`, `docs`, `refactor`, `test`,
     `chore`, `perf`, `ci`, `build`, `style`.
   - Branch names are lowercase and hyphenated.
   - If the branch does not match the dominant change, recommend
     `git switch -c <type>/<description>` and wait for confirmation before switching.

4. **Present the commit plan before staging**:
   - Show branch check results first.
   - List each proposed commit with message, scope, included files/hunks, and any risk.
   - Ask for confirmation before staging or committing.

5. **Stage one commit at a time**:
   - Never use `git add .` or `git add -A`.
   - Avoid interactive staging such as `git add -p`.
   - Use `git add <explicit-paths>` for whole-file groups.
   - For partial-file groups, create a temporary patch and apply it with `git apply --cached`.
   - Verify each staged group with `git diff --cached --stat` and `git diff --cached`
     before committing.

6. **Commit format**:

   ```
   <type>(<scope>): <short summary>

   <optional body: what and why, not how>

   <optional footer: BREAKING CHANGE: or issue refs>
   ```

   - Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `test`, `perf`, `ci`, `build`.
   - Scope: dominant module, package, component, service, or domain.
   - Summary: imperative, lowercase, no period, max 72 characters.
   - Body: wrap near 72 characters when needed.
   - Use `!` or `BREAKING CHANGE:` only for real breaking changes.

7. **Finish**:
   - Show `git log --oneline -n <number_of_commits>`.
   - Report any skipped changes and why they were not committed.

## Rules

- Do not edit files. This workflow inspects, stages, and commits only.
- Commit only after explicit user confirmation.
- Never switch branches without confirmation.
- Never stage unrelated changes.
- Never commit secrets, credentials, `.env` files, or private keys.
- Never amend, rebase, push, or create PRs unless explicitly asked.
- If a hunk is ambiguous, ask before staging it.
- If changes are too unrelated for one branch, recommend separate branches.
- If a commit would be empty, skip it and explain why.
