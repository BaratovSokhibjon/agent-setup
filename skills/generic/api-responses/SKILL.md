---
name: api-responses
description: >-
  Add or extend a service's API response envelope and structured error codes: one consistent
  response shape for success and error, a central error-code catalog, coded errors raised or
  returned per the language's idiom, typed domain and storage errors translated at the
  boundary, and a central layer that normalizes every error. Use when adding an error code,
  returning a response, translating an error, or documenting error shapes in a service that
  follows this convention.
metadata:
  keywords:
    - api responses
    - error codes
    - response envelope
    - error handling
    - error translation
    - http errors
    - openapi responses
---

# api-responses

You add or extend how a service shapes its API responses and errors. Consistency is the
whole point: clients parse one response shape and branch on stable error codes. Follow the
project's existing convention exactly; do not introduce a second response shape or a parallel
error taxonomy.

## The convention

- **One envelope for every response.** Success and error share a single shape, commonly
  `message`, `data`, `links`, `meta`, and `error`. On success `error` is null; on failure
  `data` is null and `error` is populated. List responses add pagination links.
- **Central error-code catalog.** Every error is a record in one place with a stable,
  machine-readable string code plus a name, HTTP status, human message, description, and
  optional detail. The common code format is `<status>_<category>_<sequence>` (for example
  `401_01000` for a missing token, `401_02001` for an invalid API key), so a client can
  branch on the code independently of the HTTP status or wording.
- **Fail with a code.** Business logic raises or returns a coded error carrying an entry from
  the catalog, using the language's idiom (a shared exception type where the language uses
  exceptions, a typed error value in Go, Rust, and similar), never an ad-hoc dict or bare
  string. Overrides (message, description, detail, headers) travel with the code.
- **Typed domain and storage errors.** Lower layers surface specific typed errors (unique
  violation, null constraint, foreign key, and similar). Services handle these at the boundary
  and translate them to a coded HTTP error; raw low-level errors never reach the client.
- **A central layer normalizes everything.** A registered error-normalization layer
  (middleware, handler, or interceptor) converts framework errors too (not found, method not
  allowed, validation, server error) into the same envelope with the right code, so no
  endpoint emits an off-convention shape.
- **Secure rendering.** The response builder strips internal `error.detail` on 5xx outside
  debug, sets no-cache headers on errors, and attaches correlation and version headers (an
  error-code header, a request id, API and system versions).
- **Documented error shapes.** Endpoints declare typed per-status error response models so the
  generated API docs show the error envelope for each status.

## Workflow

1. **Orient in the actual project** (names and framework differ; do not assume):

   ```bash
   rg -n -i 'response|envelope|error.?code|error.?handler|middleware|http.?exception' \
     --glob '!**/{node_modules,dist,build,.venv}/**'
   ```

   Find the envelope schema, the error-code catalog, the coded-error type, the response
   builder, and the error-normalization layer. Read them before writing anything.

2. **If the project has no unified envelope or error catalog, do not silently retrofit one.**
   Introducing an envelope or code taxonomy touches every endpoint and error path. Surface it:
   state that responses are currently ad hoc, outline the envelope and catalog you would add
   and the decisions involved (envelope fields, code format, which errors to enumerate), and
   get approval before a sweeping change. Adding a single response or error to an existing
   convention needs no such escalation.

3. **Add an error code**: add one entry to the central catalog, reusing the project's code
   format and picking the next sequence in the right status and category. Give it a clear
   name, message, and description. Do not duplicate an existing code or reuse a number.

4. **Fail with it**: from business logic, raise or return the coded error with the new catalog
   entry (per the language's idiom), passing a specific message or detail when it helps the
   caller. Never return an ad-hoc error dict or leak an internal error.

5. **Translate lower-layer errors**: handle typed domain or storage errors at the service
   boundary and map each to the appropriate coded HTTP error (for example a unique violation
   to a conflict or unprocessable-entity code). Never let a raw storage or validation error
   reach the client.

6. **Return a success response**: build it through the project's response type or schema so
   the envelope, links, meta, and headers are filled consistently. Do not hand-assemble a
   bare dict that bypasses the envelope.

7. **Document error responses**: declare the typed per-status error response models on the
   endpoint so the API docs advertise the error shapes it can return.

8. **Preserve secure rendering**: keep internal detail out of 5xx responses outside debug,
   keep the no-cache and correlation headers, and do not widen what errors expose.

9. **Verify**: exercise the success path and each new error path; confirm the response matches
   the envelope, the code and headers are present, and a 5xx hides internal detail outside
   debug. If you cannot run these, say why.

10. **Summarize**: codes added, where they are raised or returned, errors translated,
    endpoints documented, and any envelope or normalization-layer change.

## Rules

- Never introduce a second response shape or a parallel error taxonomy; extend the existing
  one.
- Never return an ad-hoc error dict or leak a raw error; use the shared coded type, raised or
  returned per the language's idiom.
- Never reuse or duplicate an error code; add the next one in the correct status and category.
- Always translate typed domain and storage errors to coded HTTP errors at the boundary.
- Always route errors through the central normalization layer so framework errors share the
  envelope.
- Always keep internal `error.detail` out of 5xx responses outside debug, and preserve the
  no-cache and correlation headers.
- Do not silently retrofit an envelope or catalog across an existing API; surface that change
  and get approval first.
- Do not use em-dashes in files you write or in your output.
