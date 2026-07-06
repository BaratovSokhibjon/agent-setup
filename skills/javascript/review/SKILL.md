---
name: javascript-review
description: >-
  Review changed JavaScript code against the Google JavaScript Style Guide and produce a
  structured feedback report with PR and security checklists. Works from the current git
  diff. Use when the user asks to review, audit, or check JavaScript changes or a JS PR.
  Never edits source; writes a read-only report to a per-project path the refactor skill
  can consume.
metadata:
  keywords:
    - javascript
    - code review
    - pr review
    - security review
    - google javascript style guide
    - eslint
---

# javascript-review

You are a read-only JavaScript code review workflow. Analyze recent changes against the
[Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) and JS
best practices, then produce a structured report. Never modify source code; the only file
you write is the report.

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
   - Logic errors, off-by-one, `null`/`undefined` access, unsafe optional chaining gaps.
   - Truthiness bugs on `0`, `''`, `NaN`; `==` coercion surprises.
   - Floating promises and unhandled rejections; missing `await`; race conditions.
   - Unhandled edge cases: empty inputs, boundary values, concurrent access.

   ### JavaScript Style (Google JavaScript Style Guide)
   - `const`/`let` only, never `var`; `===`/`!==` over `==`/`!=`.
   - Naming: `camelCase` variables/functions, `PascalCase` classes, `CONSTANT_CASE`
     constants.
   - Template literals over concatenation; arrow functions for callbacks.
   - JSDoc on exported functions/public methods; functions over ~40 lines want
     decomposition.
   - Imports grouped and ordered, no unused imports, consistent module system.

   ### Security (CRITICAL, treat all client input as UNTRUSTED)
   - All inputs validated: headers, query/path params, request body, file uploads,
     WebSocket messages.
   - No XSS (`innerHTML`/`dangerouslySetInnerHTML` with unsanitized input), no SQL/NoSQL
     injection, no shell injection (`child_process` with user input), no path traversal.
   - Never `eval`/`new Function` on untrusted data; no prototype pollution via unchecked
     merges.
   - No hardcoded secrets, tokens, or credentials.
   - Auth check runs before protected logic (no IDOR); no PII in logs; no wildcard CORS on
     authenticated APIs; CSRF protection on state-changing endpoints.

   ### Performance
   - N+1 queries, missing indexes, missing pagination on list endpoints.
   - Blocking/synchronous work on the event loop; unnecessary `await` in loops that could
     be `Promise.all`.
   - Unbounded array/map growth; repeated work that belongs outside a loop.

   ### Logging
   - Structured logging, not `console.log`, in committed code.
   - No secrets or PII in log fields; correct log level; `request_id`/`trace_id` in
     distributed contexts.

   ### Maintainability
   - Dead code, unused imports, empty `catch` blocks that swallow errors.
   - DRY violations; missing or misleading comments; poor separation of concerns.

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
