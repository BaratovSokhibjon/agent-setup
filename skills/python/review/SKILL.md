---
name: python-review
description: >-
  Review changed Python code against the Google Python Style Guide and produce a structured
  feedback report with PR and security checklists. Works from the current git diff. Use when
  the user asks to review, audit, or check Python changes or a Python PR. Never edits source;
  writes a read-only report to a per-project path the refactor skill can consume.
metadata:
  keywords:
    - python
    - code review
    - pr review
    - security review
    - google python style guide
    - pep 8
    - type hints
---

# python-review

You are a read-only Python code review workflow. Analyze recent changes against the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), PEP 8, and
Python best practices, then produce a structured report. Never modify source code; the only
file you write is the report.

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
   - Logic errors, off-by-one, `None`/`KeyError`/`IndexError` risks.
   - Mutable default arguments (`def f(x=[])`).
   - Unhandled edge cases: empty inputs, boundary values, concurrent access.
   - Incorrect `is` vs `==` usage; truthiness bugs on `0`, `""`, empty collections.

   ### Python Style (Google Python Style Guide + PEP 8)
   - Naming: `snake_case` functions/variables, `CapWords` classes, `CONSTANT_CASE`
     constants, leading underscore for internal names.
   - Type hints on public functions and methods; modern generics (`list[str]`, `X | None`).
   - Google-style docstrings (summary, `Args:`/`Returns:`/`Raises:`); no module-top
     docstrings; no `from __future__ import annotations`.
   - Imports grouped stdlib / third-party / local, sorted, no unused, no wildcard imports.
   - f-strings over `%`/`.format()`; functions over ~40 lines want decomposition.

   ### Security (CRITICAL, treat all client input as UNTRUSTED)
   - All inputs validated: headers, query/path params, request body, file uploads.
   - No SQL injection (parameterized queries, never f-string SQL), no shell injection
     (`subprocess` with lists, never `shell=True` on user input), no path traversal.
   - Never `eval`/`exec`/`pickle.loads` on untrusted data; safe YAML (`safe_load`).
   - No hardcoded secrets, tokens, or credentials.
   - Auth check runs before protected logic (no IDOR); no PII in logs; no wildcard CORS on
     authenticated APIs; CSRF protection on state-changing endpoints.

   ### Performance
   - N+1 queries, missing DB indexes, missing pagination on list endpoints.
   - Blocking calls inside `async` functions.
   - Unbounded list/dict growth; repeated work that belongs outside a loop.

   ### Logging
   - Structured logging via the `logging` module, not `print`.
   - No secrets or PII in log fields; correct log level; `request_id`/`trace_id` in
     distributed contexts.

   ### Maintainability
   - Dead code, unused imports, bare `except:`, swallowed exceptions.
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
