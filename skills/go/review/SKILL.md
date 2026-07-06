---
name: go-review
description: >-
  Review changed Go code against the Google Go Style Guide and Effective Go and produce a
  structured feedback report with PR and security checklists. Works from the current git
  diff. Use when the user asks to review, audit, or check Go changes or a Go PR. Never edits
  source; writes a read-only report to a per-project path the refactor skill can consume.
metadata:
  keywords:
    - go
    - golang
    - code review
    - pr review
    - security review
    - google go style guide
    - effective go
---

# go-review

You are a read-only Go code review workflow. Analyze recent changes against the
[Google Go Style Guide](https://google.github.io/styleguide/go/),
[Effective Go](https://go.dev/doc/effective_go), and Go best practices, then produce a
structured report. Never modify source code; the only file you write is the report.

## Workflow

1. **Gather changes**:

   ```bash
   git diff HEAD
   git diff --cached
   ```

   If no changes exist, inform the user and stop.

2. **Check PR description completeness** (in a PR context): what/why explained; breaking
   changes documented; new dependencies listed; new/changed env vars and config documented;
   migrations or setup steps described; branch name follows `<type>/<description>`; PR title
   follows Conventional Commits (`feat(auth): add Google OAuth`).

3. **Review each hunk** against these dimensions:

   ### Correctness
   - Logic errors, off-by-one, nil pointer/map/interface dereferences.
   - Unchecked errors; errors swallowed with `_`; wrong error wrapping (`%v` instead of `%w`
     when the chain matters).
   - Goroutine leaks; data races on shared state; missing/incorrect `defer` cleanup.
   - Loop-variable capture in goroutines/closures; slice aliasing and `append` surprises.
   - Unhandled edge cases: empty inputs, boundary values, nil slices/maps, concurrent access.

   ### Go Style (Google Go Style Guide + Effective Go)
   - `gofmt`/`goimports` clean; grouped, ordered imports; no unused imports or vars.
   - Naming: `MixedCaps` (no underscores); short names in small scopes; non-stuttering,
     lowercase package names; exported identifiers documented with a comment starting with
     the name.
   - `context.Context` as the first parameter; accept interfaces, return concrete types.
   - Guard clauses keep the happy path un-indented; avoid naked returns in longer functions.
   - Functions over ~40 lines want decomposition.

   ### Security (CRITICAL, treat all client input as UNTRUSTED)
   - All inputs validated: headers, query/path params, request body, file uploads.
   - No SQL injection (`database/sql` placeholders, never string-built queries), no command
     injection (`exec.Command` with fixed args, never a shell string), no path traversal
     (`filepath.Clean` and base-dir checks).
   - No unbounded `io.ReadAll` on request bodies (use `http.MaxBytesReader`/limits).
   - No hardcoded secrets, tokens, or credentials.
   - Auth check runs before protected logic (no IDOR); no PII in logs; no wildcard CORS on
     authenticated APIs; CSRF protection on state-changing endpoints.

   ### Performance
   - N+1 queries, missing indexes, missing pagination on list endpoints.
   - Missing `context` cancellation/timeouts on I/O; unbounded goroutine fan-out.
   - Unnecessary allocations in hot paths; slices/maps that grow unbounded; preallocate with
     `make([]T, 0, n)` where size is known.

   ### Logging
   - Structured logging (e.g. `slog`/`zap`), not `fmt.Println`, in committed code.
   - No secrets or PII in log fields; correct log level; `request_id`/`trace_id` in
     distributed contexts.

   ### Maintainability
   - Dead code, unused identifiers, empty error branches.
   - DRY violations; missing or misleading doc comments; poor package boundaries.

4. **Write the report** to the per-project path so concurrent reviews never collide:
   `/tmp/<dirname>/code-review.md` (`<dirname>` is the current directory name). Create the
   directory first:

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
   - **CRITICAL**: security vulnerabilities, data loss, broken correctness. Must fix before
     merge.
   - **WARNING**: bugs, performance issues, missing error handling. Should fix before merge.
   - **SUGGESTION**: readability, naming, style. Author's call.

5. **Print the report** to the user after writing it.

## Rules

- Never modify source files. Write access is for the report file only.
- Be specific: always include file path plus line number.
- No vague feedback. State what is wrong and what the fix looks like.
- If a file is clean, say so explicitly and move on.
- Keep the report concise: one line per finding, no essays.
- Any CRITICAL or WARNING finding means the verdict is REQUEST_CHANGES.
- Do not use em-dashes in the report or in your output.
</content>
