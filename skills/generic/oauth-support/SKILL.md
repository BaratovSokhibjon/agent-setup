---
name: oauth-support
description: >-
  Add or extend OAuth2-style token authentication in a backend service: registration and
  email verification, password login, token issuance and grant types, refresh-token
  rotation with reuse detection, password reset, introspection, and logout/revoke. First
  checks whether the codebase already supports auth; if it does not, escalates to the user
  instead of scaffolding an auth system on its own. Use when asked to add login, signup,
  tokens, JWT auth, refresh, or password reset. Excludes third-party or wallet sign-in.
metadata:
  keywords:
    - oauth
    - authentication
    - login
    - jwt
    - access token
    - refresh token
    - token rotation
    - password reset
---

# oauth-support

You add or extend token-based authentication in a backend service. Auth is the front door:
a mistake here leaks every account. Follow the project's existing security and architecture
conventions exactly, and never introduce a second, divergent auth scheme.

The first job is a gate: determine whether the codebase already supports authentication. If
it does not, escalate. Do not design and scaffold an entire auth system unilaterally.

This skill covers first-party auth (registration, password login, token lifecycle). It does
not cover third-party or wallet-based sign-in.

## Workflow

1. **Detect existing auth support** (read-only). Search for the building blocks:

   ```bash
   rg -n -i 'login|signup|access_token|refresh_token|jwt|bearer|password_hash|oauth|authenticat' \
     --glob '!**/{node_modules,dist,build,.venv}/**'
   ```

   Look for each piece and classify support as full, partial, or none:
   - A user or account model with a password hash and a status lifecycle.
   - Token issuance and verification (a signed access token, a stored/revocable refresh
     token).
   - Login, token, and logout endpoints, plus a grant-type dispatch if OAuth2-shaped.
   - Password hashing utilities and a secrets/settings home for algorithms and durations.
   - An auth dependency or middleware that authenticates requests and resolves scopes.

2. **If support is absent, or partial in a way that blocks the request, escalate. Do not
   scaffold an auth system on your own.** Authentication touches the account model plus a
   migration, password hashing, token signing and key management, session or cookie
   handling, the scope/permission model, and public endpoints; each is a security decision.
   Report to the user:
   - State plainly that the codebase does not (fully) support auth today, and list exactly
     which pieces are missing.
   - Outline what adding it entails and the decisions required (see "Decisions to surface").
   - Ask for explicit approval and those decisions before writing code; prefer the user's
     planning or spec flow for a net-new auth system.

   Stop here until the user confirms. Escalation means surface and ask, not proceed quietly.

3. **If support exists, mirror the established pattern.** Read the existing implementation
   first and match its token strategy, signing, hashing, config keys, scope model, error
   handling, and response schemas. Extending is preferred over reinventing.

## Token model

Use two distinct token kinds; do not conflate them:

- **Access token**: stateless and self-contained. Signed, short-lived, and carrying the
  subject, issued-at, expiry, a unique id, and the authorization claims (roles and scopes)
  resolved at issuance. It is verified by signature, expiry, and required claims alone. It
  is not looked up in a store on every request.
- **Refresh, verification, and reset tokens**: backed by a revocable server-side record. The
  token the client holds wraps an opaque high-entropy secret whose hash is stored, so the
  token can be revoked and rotated. These are stateful by design.

Passwords and long-lived secret tokens are hashed differently: hash passwords with a slow,
salted password KDF (they are low-entropy human input); hash opaque token secrets with the
project's configured algorithm. Do not hash passwords with a fast hash.

## Flows

4. **Registration and verification**: create the account in an unverified/pending status
   with a slow-KDF password hash. Issue a single-use, short-lived verification token and
   deliver it out of band (email). Verification consumes the token and moves the account to
   active. Support resend. On an existing email, respond without revealing account state
   more than necessary.

5. **Password login**: look up the account; if it is absent, still perform comparable work
   and return the same generic error as a wrong password (defend against user enumeration
   and timing). Verify the password against the stored hash (with the project's pepper if it
   uses one). Gate on account status (pending, disabled, deleted). Resolve roles and scopes,
   then issue an access token and a refresh token. Record last-login metadata if the model
   tracks it.

6. **Token issuance and grants**: expose a token endpoint that dispatches on `grant_type`.
   Implement the grants the project needs and reject unknown grants explicitly; keep the
   dispatch open for extension. Accept the refresh token from the request body, and from a
   cookie only for browser clients. Wrap the unit of work in a transaction (commit on
   success, roll back on failure).

7. **Refresh with rotation and reuse detection**: verify the refresh token, then look up its
   server-side record. Rotate on every use: issue a new refresh token and mark the presented
   one used. Group a chain of refreshes into a family; if a token that was already used is
   presented again, treat it as theft, revoke the entire family, and reject. Reject expired,
   revoked, or blocked tokens, and re-check that the account is still active. Never extend a
   refresh token's absolute lifetime past its family's original expiry.

8. **Password reset**: on a forgot-password request, always return the same response whether
   or not the email exists (no enumeration). For a valid active account, issue a single-use,
   short-lived reset token and deliver it out of band. Reset consumes the token, sets a new
   slow-KDF hash, and invalidates outstanding sessions or refresh tokens as the project's
   policy dictates.

9. **Introspection and logout/revoke**: introspection reports whether a token is active and
   its claims. Logout and revoke invalidate the server-side token record; when revoking,
   skip the expiry check so an expired token can still be revoked. Clear auth cookies for
   browser clients.

10. **Wire into the project's conventions**: place model, service, schema, and transport
    code in the project's layout; guard endpoints with the project's auth and scope
    mechanism; use read/write session separation if the project has it; and add secrets,
    algorithms, and durations through the project's settings convention. For browser cookies,
    set them http-only, secure in non-local environments, same-site strict, and path-scoped
    to the auth routes, and account for CSRF.

11. **Verify**: run the project's migration tooling and tests; confirm the full path works
    (register, verify, log in, refresh with rotation, reuse a rotated token and see the
    family revoked, reset password, revoke). If you cannot run these, say why.

12. **Summarize**: what was added or changed, which security invariants were upheld, any
    migration required, and follow-ups.

## Decisions to surface when escalating

- Token strategy: stateless access plus stateful refresh (recommended) versus server
  sessions.
- Signing: symmetric shared secret versus asymmetric keys, and how keys are stored and
  rotated.
- Password hashing: which slow KDF, and whether a pepper is used.
- Grant types to support now and their parameters.
- Refresh rotation and reuse-detection (token family) policy, and token lifetimes.
- Account lifecycle: email verification, disable/delete states.
- Password reset and out-of-band delivery (email) dependency.
- Transport: bearer header versus browser cookies, and CSRF handling for cookies.
- Scope and role model (coordinate with the project's authorization/RBAC).
- Migration and rollout plan.

## Rules

- Never add auth support silently: if the codebase lacks it, escalate and get explicit
  approval and decisions first.
- Never invent a second auth scheme when one already exists; mirror it.
- Never store, log, or return a raw password, raw token secret, or signing key; store only
  hashes, and keep keys in the project's secret store.
- Always hash passwords with a slow, salted KDF; never a fast hash. (This is the opposite of
  high-entropy API key secrets.)
- Always return generic, indistinguishable errors for login and password reset; never reveal
  whether an account exists or which credential failed.
- Always rotate refresh tokens on use and revoke the whole family on reuse; reject expired,
  revoked, or blocked tokens and inactive accounts.
- Always verify access tokens by signature, expiry, and required claims; embed authorization
  (scopes/roles) at issuance.
- Log suspicious auth events (unknown-user login, token reuse) at a warning level without
  leaking secrets.
- Follow the project's architecture, auth and scope model, and settings convention.
- Do not use em-dashes in files you write or in your output.
