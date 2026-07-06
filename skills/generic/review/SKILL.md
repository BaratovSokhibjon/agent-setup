---
name: review
description: >-
  Review recent code changes and produce a structured feedback report with PR and
  security checklists. Works from the current git diff. Use when the user asks to review
  changes, check a diff, audit a PR, or run a code review. Never edits source; writes a
  read-only report to a per-project path that the refactor skill can consume.
metadata:
  keywords:
    - code review
    - pr review
    - security review
    - diff review
    - feedback report
---

# review

You are a read-only code review workflow. Analyze recent changes and produce a structured
review report. Never modify source code; the only file you write is the report.

## Workflow

1. **Gather changes**:

   ```bash
   git diff HEAD
   git diff --cached
   ```

   If no changes exist, inform the user and stop.

2. **Check PR description completeness** (when reviewing in a PR context):
   - What changed and why is explained clearly.
   - Breaking changes are explicitly documented.
   - New dependencies are listed.
   - New or changed environment variables and config are documented.
   - Setup requirements (migrations, scripts, config changes) are described.
   - Branch name follows `<type>/<description>` or `<type>/<ISSUE-KEY>-<description>`.
   - PR title follows Conventional Commits: `type(scope): summary` (e.g.
     `feat(auth): add Google OAuth`).

3. **Review each hunk** against these dimensions:

   ### Correctness
   - Logic errors, off-by-one, null/undefined risks.
   - Unhandled edge cases (empty inputs, boundary values, concurrent access).
   - Incorrect type usage or unsafe casts.

   ### Code Style
   - Naming conventions per language.
   - Function length and complexity (functions over 40 lines need decomposition).
   - Import ordering and grouping.
   - Docstrings, JSDoc, or GoDoc completeness.
   - Type annotations where applicable.

   ### Security (CRITICAL, treat all client input as UNTRUSTED)
   - All client inputs validated: HTTP headers, query params, path params, request body,
     file uploads, WebSocket messages.
   - Input sanitized against SQL injection, XSS, shell injection, path traversal.
   - No hardcoded secrets, tokens, keys, or credentials.
   - Auth check runs before protected logic (no IDOR).
   - No PII (names, emails, tokens) in log output.
   - No wildcard CORS on authenticated APIs.
   - CSRF protection present on state-changing endpoints.

   ### Performance
   - N+1 queries, missing DB indexes.
   - Blocking calls in async contexts.
   - Unbounded list or map growth.
   - Missing pagination on list endpoints.

   ### Logging
   - Structured JSON format used, not plain print or console.log.
   - No sensitive data (secrets, PII) in log fields.
   - Correct log level for the environment.
   - request_id or trace_id included for distributed or production context.

   ### Maintainability
   - Dead code, unused imports.
   - DRY violations.
   - Missing or misleading comments.
   - Poor separation of concerns.

4. **Write the report** to the per-project path so concurrent reviews never collide:
   `/tmp/<dirname>/code-review.md`, where `<dirname>` is the current directory's name
   (e.g. `/tmp/agent-setup/code-review.md`). Create the directory first:

   ```bash
   mkdir -p "/tmp/$(basename "$PWD")"
   ```

   Use this exact structure:

   ```markdown
   # Code Review Report
   Generated: <timestamp>

   ## PR Checklist
   - [ ] PR description: what/why/how documented
   - [ ] Breaking changes called out
   - [ ] New dependencies listed
   - [ ] New/changed env vars documented
   - [ ] Branch name follows convention
   - [ ] PR title follows Conventional Commits

   ## Summary
   <1-2 sentence overall assessment>

   ## Findings

   ### <file_path>

   #### CRITICAL
   - [ ] <finding> (line <N>)

   #### WARNING
   - [ ] <finding> (line <N>)

   #### SUGGESTION
   - [ ] <finding> (line <N>)

   ## Refactor Priorities
   1. <highest impact item>
   2. <next item>
   3. ...

   ## Verdict
   APPROVE | REQUEST_CHANGES
   CRITICALs: 0 | WARNINGs: 0 | SUGGESTIONs: 0
   ```

   Severity levels:
   - **CRITICAL**: Security vulnerabilities, data loss, broken correctness. Must fix
     before merge.
   - **WARNING**: Bugs, performance issues, missing error handling. Should fix before
     merge.
   - **SUGGESTION**: Readability, naming, style improvements. Author's call.

5. **Print the report** to the user after writing it.

## Rules

- Never modify source files. Write access is for the report file only.
- Be specific: always include file path plus line number.
- No vague feedback. State what is wrong and what the fix looks like.
- If a file is clean, say so explicitly and move on.
- Keep the report concise: one line per finding, no essays.
- Any CRITICAL or WARNING finding means the verdict is REQUEST_CHANGES.
- Do not use em-dashes in the report or in your output.
