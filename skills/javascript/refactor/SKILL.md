---
name: javascript-refactor
description: >-
  Refactor changed JavaScript code to the Google JavaScript Style Guide with the smallest
  safe, behavior-preserving edits. Works from the current git diff. Use when the user asks
  to refactor, clean up, tidy, or improve the readability of JavaScript code without
  changing behavior, exports, public APIs, routes, or schemas. Enforces const/let, ES
  modules, strict equality, JSDoc, and modern idioms.
metadata:
  keywords:
    - javascript
    - refactor
    - clean up
    - readability
    - google javascript style guide
    - eslint
    - prettier
    - behavior-preserving
---

# javascript-refactor

You are a strict, pragmatic JavaScript refactor workflow. Work from the current diff. Make
the smallest safe edits that make changed JavaScript easier to scan, name, and maintain
**without changing behavior, exports, public APIs, routes, schemas, or unrelated code**.

Follow project conventions first (existing ESLint, Prettier, `package.json` config), then
the [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html), then
general modern JS idioms.

## Workflow

1. **Inspect the worktree** (read-only):

   ```bash
   git status --porcelain=v1
   git diff HEAD
   git diff --cached
   ```

   If there is no diff, ask which files or range to refactor.

2. **Use optional review context** at `/tmp/<dirname>/code-review.md` (`<dirname>` is the
   current directory name):

   ```bash
   cat "/tmp/$(basename "$PWD")/code-review.md" 2>/dev/null
   ```

   If present, fix CRITICAL findings first, then WARNING, then SUGGESTION.

3. **Find project conventions**: inspect `.eslintrc*`, `.prettierrc*`, `package.json`
   (`type`, scripts), and nearby files for quote style, semicolons, indentation, and module
   system (ESM vs CommonJS). The repo's configured style wins over defaults. Do not switch
   module systems or impose structure the repo does not already use.

4. **Apply Google JavaScript Style Guide conventions** (only on changed code):
   - **Declarations**: never `var`; use `const` by default and `let` only when reassigned.
   - **Naming**: `camelCase` for variables, functions, and methods; `PascalCase` for classes
     and constructors; `CONSTANT_CASE` for module-level immutable constants. Fix misleading
     names introduced in the diff.
   - **Equality**: `===`/`!==`, never `==`/`!=` (except `== null` only if the repo uses it).
   - **Strings**: prefer template literals over string concatenation; keep the repo's quote
     style (Google prefers single quotes).
   - **Functions**: prefer arrow functions for callbacks and non-method closures; keep `this`
     semantics correct. Prefer `async`/`await` over raw `.then()` chains when it reads better.
   - **Modules**: follow the repo's system consistently; remove unused imports; group and
     order imports the way the codebase does.
   - **Objects/arrays**: prefer destructuring, spread, and shorthand properties where they
     improve clarity; avoid mutating shared inputs.
   - **JSDoc**: keep and correct JSDoc on exported functions and public methods; do not
     delete meaningful JSDoc. Do not add trivial JSDoc that only restates the signature.
   - **Control flow**: guard clauses and early returns over deep nesting; always brace blocks.

5. **Normalize em-dashes globally**:

   ```bash
   rg -n -P '\x{2014}'
   perl -CSD -0pi -e 's/\x{2014}/-/g' <files>
   ```

   Skip semantic data values, snapshots, fixtures, URLs, or tests where the character matters.

6. **Normalize section markers** to a single canonical form: `// MARK: <label>`. Find
   variants first with `rg -n -i 'mark:?\b'` and rewrite alternates (missing colon, wrong
   case, no spacing, `// MARK: - label` dash decoration). Skip matches inside strings or docs.

7. **Analyze changed code**: naming consistency across analogous modules; dead imports and
   unreachable code; long functions and deep nesting; duplicated logic; magic values wanting
   named constants; floating promises and unhandled rejections; error handling and logging.

8. **Classify risk before editing**:
   - Low: unused imports, local renames, `var`->`const`/`let`, `==`->`===`, template
     literals, guard clauses, tiny helper extraction.
   - Medium: reordering within a module, reworking private helpers, promise-to-async
     conversion, changing internal imports.
   - High: file moves, renaming exports, route/schema changes, module-system changes, broad
     renames, new modules, public API changes, test rewrites.
   - Apply low-risk directly. Apply medium-risk only when the readability win is clear. Ask
     before high-risk changes unless the user requested them.

9. **Apply focused edits**: edit only files needed for the refactor. Preserve behavior,
   public interfaces, dependency shape, and unrelated user changes. After moves/renames,
   remove orphan directories and update imports and tests.

10. **Verify** with the nearest discoverable tools, preferring targeted runs:

    ```bash
    npx eslint <files> ; npx prettier --check <files>
    npm test        # or the project's configured test command, for behavioral safety
    ```

    Run the full suite for rename/move batches. If verification cannot run, say why.

11. **Summarize**: files changed and why, risky refactors skipped, verification results.

## Rules

- Never change observable behavior unless explicitly asked.
- Never remove or rename exported symbols unless explicitly asked.
- Never switch module systems (ESM <-> CommonJS) unless explicitly asked.
- Never use `var` or `==`/`!=` in changed code (except `== null` if that is the repo idiom).
- Never replace structured logging with `console.log`.
- Never delete meaningful JSDoc on exported symbols.
- Never stage unrelated files.
- Never force generic architecture on a repo with its own convention.
- Always normalize existing section markers to a single `// MARK: <label>` format.
- Prefer code a human understands on first pass over cleverness.
- If a file is already clean, skip it and say so.
</content>
