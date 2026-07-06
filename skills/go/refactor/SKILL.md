---
name: go-refactor
description: >-
  Refactor changed Go code to the Google Go Style Guide and Effective Go with the smallest
  safe, behavior-preserving edits. Works from the current git diff. Use when the user asks
  to refactor, clean up, tidy, or improve the readability of Go code without changing
  behavior, exported identifiers, public APIs, routes, or schemas. Enforces gofmt, error
  wrapping, MixedCaps naming, and idiomatic Go.
metadata:
  keywords:
    - go
    - golang
    - refactor
    - clean up
    - readability
    - google go style guide
    - effective go
    - gofmt
    - behavior-preserving
---

# go-refactor

You are a strict, pragmatic Go refactor workflow. Work from the current diff. Make the
smallest safe edits that make changed Go code easier to scan, name, and maintain **without
changing behavior, exported identifiers, public APIs, routes, schemas, or unrelated code**.

Follow project conventions first, then `gofmt`/`goimports`, then the
[Google Go Style Guide](https://google.github.io/styleguide/go/) and
[Effective Go](https://go.dev/doc/effective_go), then general Go idioms.

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

3. **Find project conventions**: inspect `go.mod`, `.golangci.yml`, existing package layout,
   and nearby files. Match the module path, package naming, and error style already in use.
   Do not impose structure the repo does not already use.

4. **Apply Google Go Style Guide conventions** (only on changed code):
   - **Formatting**: code must be `gofmt`/`goimports` clean (tabs, grouped imports). Never
     hand-format against gofmt.
   - **Naming**: `MixedCaps`/`mixedCaps`, never underscores; short names in small scopes
     (`i`, `r`, `ctx`), descriptive names in wide scopes. Package names are short, lowercase,
     no underscores, and not stuttering (`chat.Message`, not `chat.ChatMessage`). Exported
     identifiers start uppercase and have doc comments beginning with the identifier name.
   - **Errors**: always check returned errors; wrap with context using `fmt.Errorf("...: %w",
     err)`; do not discard errors with `_` unless intentional and clear. Return errors, do
     not `panic` in library code. Sentinel errors compared with `errors.Is`; typed errors
     with `errors.As`.
   - **Context**: `context.Context` is the first parameter (`ctx context.Context`); never
     store a context in a struct.
   - **Interfaces**: accept interfaces, return concrete types; keep interfaces small and
     defined at the consumer.
   - **Resources/concurrency**: `defer` cleanup (`Close`, `Unlock`) right after acquisition;
     avoid goroutine leaks (ensure every goroutine can exit); guard shared state or use
     channels; prefer `sync` primitives correctly.
   - **Control flow**: guard clauses and early returns to keep the happy path un-indented;
     avoid naked returns in non-trivial functions; prefer `:=` where it reads cleanly.
   - **Doc comments**: keep and correct exported doc comments; a comment on `Foo` starts with
     `Foo ...`. Do not add trivial comments that only restate the signature.

5. **Normalize em-dashes globally**:

   ```bash
   rg -n -P '\x{2014}'
   perl -CSD -0pi -e 's/\x{2014}/-/g' <files>
   ```

   Skip semantic data values, snapshots, fixtures, URLs, or tests where the character matters.

6. **Normalize section markers** to a single canonical form: `// MARK: <label>`. Find
   variants first with `rg -n -i 'mark:?\b'` and rewrite alternates. Skip matches inside
   strings or docs.

7. **Analyze changed code**: naming and package consistency; dead code and unused
   identifiers; long functions and deep nesting; duplicated logic; magic values wanting named
   constants; unchecked errors; missing `defer` cleanup; goroutine/leak and race risks;
   logging.

8. **Classify risk before editing**:
   - Low: unused imports/vars, local renames, gofmt fixes, guard clauses, error wrapping,
     `defer` placement, doc-comment fixes.
   - Medium: reorganizing unexported helpers within a package, tightening internal error
     handling, changing internal call sites.
   - High: file moves, renaming exported identifiers, changing exported signatures,
     route/schema changes, package moves/renames, new packages, public API changes, test
     rewrites.
   - Apply low-risk directly. Apply medium-risk only when the readability win is clear. Ask
     before high-risk changes unless the user requested them.

9. **Apply focused edits**: edit only files needed for the refactor. Preserve behavior,
   exported identifiers and signatures, dependency shape, and unrelated user changes. After
   moves/renames, remove orphan directories and update imports and tests.

10. **Verify** with the nearest discoverable tools, preferring targeted runs:

    ```bash
    gofmt -l <files> ; goimports -l <files>
    go vet ./...
    golangci-lint run    # if configured
    go build ./... ; go test ./<changed package>...
    ```

    Run `go test ./...` for rename/move batches. If verification cannot run, say why.

11. **Summarize**: files changed and why, risky refactors skipped, verification results.

## Rules

- Never change observable behavior unless explicitly asked.
- Never rename exported identifiers or change exported signatures unless explicitly asked.
- Never discard errors with `_` in changed code unless clearly intentional.
- Never introduce `panic` in library code paths.
- Never leave code that is not `gofmt`/`goimports` clean.
- Never replace structured logging with `fmt.Println`.
- Never stage unrelated files.
- Never force generic architecture on a repo with its own convention.
- Always normalize existing section markers to a single `// MARK: <label>` format.
- Prefer code a human understands on first pass over cleverness.
- If a file is already clean, skip it and say so.
</content>
