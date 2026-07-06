---
name: typescript-refactor
description: >-
  Refactor changed TypeScript code to the Google TypeScript Style Guide (gts) with the
  smallest safe, behavior-preserving edits. Works from the current git diff. Use when the
  user asks to refactor, clean up, tidy, or improve the readability of TypeScript code
  without changing behavior, exports, public APIs, routes, or schemas. Enforces strict
  typing, no any, type-only imports, and modern idioms.
metadata:
  keywords:
    - typescript
    - refactor
    - clean up
    - readability
    - google typescript style guide
    - gts
    - type safety
    - behavior-preserving
---

# typescript-refactor

You are a strict, pragmatic TypeScript refactor workflow. Work from the current diff. Make
the smallest safe edits that make changed TypeScript easier to scan, name, and maintain
**without changing behavior, exports, public APIs, routes, schemas, or unrelated code**.

Follow project conventions first (existing `tsconfig.json`, ESLint/typescript-eslint,
Prettier, `gts`), then the
[Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html), then
general modern TS idioms.

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

3. **Find project conventions**: inspect `tsconfig.json` (strictness flags), `.eslintrc*`,
   `.prettierrc*`, and nearby files for quote style, semicolons, and import ordering. The
   repo's configured style and `strict` settings win over defaults. Do not loosen compiler
   strictness or impose structure the repo does not already use.

4. **Apply Google TypeScript Style Guide conventions** (only on changed code):
   - **Types**: never introduce `any`; use `unknown` plus narrowing, precise unions, or
     generics. Remove redundant annotations the compiler can infer, but keep explicit types
     on exported/public API surfaces.
   - **Null safety**: avoid non-null assertions (`!`) where a guard or optional chaining is
     clearer; handle `null`/`undefined` explicitly. Keep `strictNullChecks` behavior intact.
   - **Declarations**: `const` by default, `let` only when reassigned, never `var`.
   - **Naming**: `camelCase` variables/functions, `PascalCase` types/interfaces/classes/enums,
     `CONSTANT_CASE` module constants. Do not prefix interfaces with `I`.
   - **Modeling**: prefer `interface`/`type` and readonly fields; prefer union types over
     enums when the codebase does (Google prefers unions/`as const`); avoid `namespace` in
     favor of ES modules.
   - **Imports**: use `import type` for type-only imports; group and order as the codebase
     does; remove unused imports. Do not use `require` in ESM.
   - **Equality/strings/control flow**: `===`/`!==`; template literals over concatenation;
     guard clauses over deep nesting; exhaustive `switch` with a `never` default where the
     codebase relies on exhaustiveness.
   - **Docs**: keep and correct TSDoc/JSDoc on exported symbols; do not add trivial docs
     that only restate types.

5. **Normalize em-dashes globally**:

   ```bash
   rg -n -P '\x{2014}'
   perl -CSD -0pi -e 's/\x{2014}/-/g' <files>
   ```

   Skip semantic data values, snapshots, fixtures, URLs, or tests where the character matters.

6. **Normalize section markers** to a single canonical form: `// MARK: <label>`. Find
   variants first with `rg -n -i 'mark:?\b'` and rewrite alternates. Skip matches inside
   strings or docs.

7. **Analyze changed code**: naming consistency across analogous modules; dead imports and
   unreachable code; long functions and deep nesting; duplicated logic; magic values wanting
   named constants; floating promises and unhandled rejections; weak or evaded typing
   (`any`, unchecked casts, `as` chains); error handling and logging.

8. **Classify risk before editing**:
   - Low: unused imports, local renames, `var`->`const`/`let`, `any`->`unknown` with local
     narrowing, `import type`, redundant-annotation removal, guard clauses.
   - Medium: reordering within a module, reworking private helpers, promise-to-async
     conversion, tightening internal types, changing internal imports.
   - High: file moves, renaming exports, changing exported type signatures, route/schema
     changes, broad renames, new modules, public API changes, test rewrites.
   - Apply low-risk directly. Apply medium-risk only when the readability win is clear. Ask
     before high-risk changes unless the user requested them.

9. **Apply focused edits**: edit only files needed for the refactor. Preserve behavior,
   public interfaces, exported type signatures, dependency shape, and unrelated user
   changes. After moves/renames, remove orphan directories and update imports and tests.

10. **Verify** with the nearest discoverable tools, preferring targeted runs:

    ```bash
    npx tsc --noEmit
    npx eslint <files> ; npx prettier --check <files>
    npm test        # or the project's configured test command, for behavioral safety
    ```

    Run the full suite for rename/move batches. If verification cannot run, say why.

11. **Summarize**: files changed and why, risky refactors skipped, verification results.

## Rules

- Never change observable behavior unless explicitly asked.
- Never remove or rename exported symbols or change exported type signatures unless asked.
- Never introduce `any`; never loosen `tsconfig` strictness to make code compile.
- Never use `var` or `==`/`!=` in changed code.
- Never replace structured logging with `console.log`.
- Never delete meaningful TSDoc/JSDoc on exported symbols.
- Never stage unrelated files.
- Never force generic architecture on a repo with its own convention.
- Always normalize existing section markers to a single `// MARK: <label>` format.
- Prefer code a human understands on first pass over cleverness.
- If a file is already clean, skip it and say so.
</content>
