---
name: api-key-support
description: >-
  Add or extend API key support (creation, verification, lifecycle) in a backend service,
  following the project's existing security and architecture conventions. First checks
  whether the codebase already supports API keys; if it does not, escalates to the user
  instead of scaffolding a security subsystem on its own. Use when asked to create, issue,
  rotate, verify, or revoke API keys, or to add API key authentication.
metadata:
  keywords:
    - api key
    - api key creation
    - key generation
    - key hashing
    - authentication
    - secrets
    - revoke
---

# api-key-support

You add or extend API key support in a backend service. API keys are credentials: getting
this wrong leaks access. Follow the project's existing security and architecture
conventions exactly, and never introduce a second, divergent scheme.

The first job is a gate: determine whether the codebase already supports API keys. If it
does not, escalate. Do not design and scaffold an entire key subsystem unilaterally.

## Workflow

1. **Detect existing API key support** (read-only). Search for the building blocks:

   ```bash
   rg -n -i 'api[_-]?key|key_hash|key_prefix|x-api-key|generate_api_key' \
     --glob '!**/{node_modules,dist,build,.venv}/**'
   ```

   Look for each piece and classify support as full, partial, or none:
   - A persisted key model or table (columns such as a public prefix, a key hash, status,
     scopes, expiry).
   - A service or module that generates, hashes, and verifies keys.
   - Config for key parameters (prefix, separator, length, hash algorithm).
   - An auth dependency or middleware that reads a key from a request header.
   - Endpoints or a CLI that issue and manage keys.

2. **If support is absent, or partial in a way that blocks the request, escalate. Do not
   scaffold a security subsystem on your own.** Adding API keys touches the data model plus
   a migration, secret hashing, config and secrets, an authentication path, the
   scope/permission model, and public endpoints; each is a security decision. Report to the
   user:
   - State plainly that the codebase does not (fully) support API keys today, and list
     exactly which pieces are missing.
   - Outline what adding it entails and the decisions required (see "Decisions to surface").
   - Ask for explicit approval and those decisions before writing code; prefer the user's
     planning or spec flow for a net-new subsystem.

   Stop here until the user confirms. Escalation means surface and ask, not proceed quietly.

3. **If support exists, mirror the established pattern.** Read the existing implementation
   first and match its storage shape, hashing, config keys, scope model, error handling, and
   response schemas. Extending is preferred over reinventing.

4. **Creation flow** (issuing a new key). Preserve these invariants regardless of stack:
   - Generate the secret from a cryptographic RNG at the project's configured length; never
     a predictable, sequential, or derived value.
   - Compose the presented key as `<prefix><separator><secret>`, where the prefix is a
     public, indexable handle and the secret is the sensitive part.
   - Persist only the prefix (plaintext, indexed) and a hash of the secret (indexed) using
     the project's configured algorithm. Never store the raw or full key.
   - A fast one-way hash (such as a SHA-2 family algorithm) is the right choice here, but
     only because the secret is long and random. Do not route API keys through the slow
     password-hashing path, and do not add a per-key salt: both break the prefix-plus-hash
     lookup. Never apply a fast hash to a low-entropy secret.
   - Return the full key to the caller exactly once, at creation, wrapped in the project's
     secret type. Every later read exposes only the prefix.
   - Set initial status (active), the owner, and any constraints the model supports (scopes,
     IP allowlist, expiry).
   - Validate referenced scopes or permissions exist before insert; map database constraint
     violations to the project's error responses.

5. **Verification flow** (authenticating a presented key): split on the separator, hash the
   secret part, look up by (prefix, hash) plus status, and reject disabled, expired, or
   revoked keys. Check expiry against the current time independently of status (an active
   key past its expiry is still invalid). Update last-used metadata if the model tracks it.
   Compare on the stored hash, never against a stored plaintext; if the hash is compared in
   application code rather than by a database equality lookup, use a constant-time compare.
   On any failure return a single generic authentication error; never reveal whether the
   prefix or the secret was the mismatch.

6. **Lifecycle**: support the operations the project already exposes (list, get, update,
   delete, status change, revoke). Revocation sets a revoked status and timestamp; it does
   not hard-delete. Rotation issues a new key and revokes the old one; when the caller needs
   zero downtime, allow a short window where both keys verify before the old is revoked.
   Never log or return the raw key or the hash.

7. **Wire into the project's conventions**: place model, service, schema, and transport code
   in the project's layout; guard endpoints with the project's auth and scope mechanism; use
   read/write session separation if the project has it; add config and env entries through
   the project's settings convention.

8. **Verify**: run the project's migration tooling and tests; confirm a freshly created key
   verifies and a revoked or expired key is rejected. If you cannot run these, say why.

9. **Summarize**: what was added or changed, which security invariants were upheld, any
   migration required, and follow-ups.

## Decisions to surface when escalating

- Storage: prefix plus hash (recommended) and which hash algorithm.
- Key format: prefix template, separator, and secret length.
- Scope or permission model and default scopes for a new key.
- Constraints: expiry, IP allowlist, per-owner key limits.
- Transport: which request header carries the key and how it composes with existing auth.
- Hardening: an optional secret pepper applied before hashing, and whether rotation allows
  an overlap window.
- Migration and rollout plan.

## Rules

- Never add API key support silently: if the codebase lacks it, escalate and get explicit
  approval and decisions first.
- Never store, log, or return the raw or full key after creation; persist only prefix plus
  hash.
- Never invent a second API key scheme when one already exists; mirror it.
- Always generate the secret from a cryptographic RNG at the configured length.
- Always verify against the stored hash with the configured algorithm; never compare against
  a stored plaintext key.
- Use a fast hash only because the secret is high-entropy; never route API keys through slow
  password hashing, and never apply a fast hash to a low-entropy secret.
- Always reject disabled, expired, or revoked keys on verification, and return one generic
  authentication error on failure; do not reveal whether the prefix or the secret mismatched.
- Follow the project's architecture, auth and scope model, and settings convention.
- Do not use em-dashes in files you write or in your output.
