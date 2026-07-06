---
name: rbac-support
description: >-
  Add or extend role- and scope-based access control (RBAC) in a backend service: scopes as
  atomic permissions, roles as scope bundles, user-role and role-scope assignments,
  permission resolution, and endpoint scope enforcement. First checks whether the codebase
  already has an RBAC model; if it does, extend it following the convention; if it does not,
  escalate instead of scaffolding an authorization system on its own. Use when asked to add
  a permission or scope, a role, guard an endpoint, or change who can do what.
metadata:
  keywords:
    - rbac
    - authorization
    - permissions
    - scopes
    - roles
    - access control
    - scope enforcement
---

# rbac-support

You add or extend role- and scope-based access control in a backend service. Authorization
decides who can do what: too permissive leaks data, too restrictive breaks users. Follow the
project's existing RBAC model exactly, and never introduce a second, divergent permission
scheme.

The first job is a gate: determine whether the codebase already has an RBAC model. If it
does, extending it (a new scope, a role change, a guarded endpoint) is the common, low-risk
case. If it does not, escalate. Do not scaffold an authorization system unilaterally.

## Workflow

1. **Detect existing RBAC support** (read-only). Search for the building blocks:

   ```bash
   rg -n -i 'scope|role|permission|rbac|security_scopes|allowed_scopes|:read|:write' \
     --glob '!**/{node_modules,dist,build,.venv}/**'
   ```

   Look for each piece and classify support as full, partial, or none:
   - A scope entity or enum of named permissions.
   - A role entity that bundles scopes, and join tables for role-scope and user-role.
   - Permission resolution that flattens a subject's roles into an effective scope set.
   - Enforcement at the endpoint or handler that compares required scopes to the subject's.
   - A seed or config of default scopes and roles.

2. **If an RBAC model is absent, escalate. Do not scaffold an authorization system on your
   own.** It touches the data model plus a migration, permission resolution, every guarded
   endpoint, and how scopes reach the request (embedded in a token, resolved live, or both);
   each is a security decision. Report to the user:
   - State plainly that the codebase has no RBAC model today, and list which pieces exist.
   - Outline what adding it entails and the decisions required (see "Decisions to surface").
   - Ask for explicit approval and those decisions before writing code; prefer the user's
     planning or spec flow for a net-new authorization model.

   Stop here until the user confirms. Escalation means surface and ask, not proceed quietly.

3. **If an RBAC model exists, mirror it.** Read the existing scope catalog, roles, resolution
   code, and enforcement first. Match the naming convention, the combining semantics, the
   seed format, and the response codes. Extending is the norm; do not reinvent.

## The model

RBAC here is three tiers, each a many-to-many below the next:

- **Scope**: the atomic permission (for example `users:read`). Often carries a flag marking
  system scopes that must not be edited or deleted through the API.
- **Role**: a named bundle of scopes (for example `admin`, `user`), also often protected.
- **Subject to role**: a user (or other principal) is assigned one or more roles.

A subject's effective permissions are the union of the scopes of all its roles. Resolve once
and reuse; do not recompute per check.

## Scope naming

Follow the project's existing convention. The common shape is `resource:action` with two
special forms:

- A per-resource wildcard `resource:all` that stands in for every action on that resource.
- A single global superscope (such as `all`) that satisfies every check.

Nested resources extend the colon path (`me:api-keys:create`). Actions are typically
`read`, `write`, `create`, `update`, `delete`, plus resource-specific verbs. Keep new scopes
consistent with the existing catalog; do not invent a parallel naming style.

## Enforcement semantics

Read the existing check and preserve its exact combining rule, because OR versus AND is a
security decision:

- An endpoint declares the scopes that grant access. The common rule is ANY-of: the subject
  passes if the intersection of required and held scopes is non-empty (holding any one listed
  scope suffices), and the global superscope always passes. Confirm whether the project is
  ANY-of or ALL-of before you change a guard.
- A delegated credential (an API key or a narrowly issued token) may only narrow, never
  widen: its effective scopes are the intersection of the owner's scopes and the credential's
  allowed scopes. Never let a credential grant a scope its owner lacks.
- On failure, return the project's forbidden response for insufficient permission; do not
  reveal which scope was missing beyond what the project already does.
- If access tokens embed scopes at issuance, a role or scope change does not take effect for
  a subject until the next token issuance. Call this out; refresh or re-login is the boundary.

## Common tasks

4. **Add a scope**: add it to the scope catalog and seed, following the naming convention,
   with a description and the protected flag if it is a system scope. Grant it to the roles
   that should have it. Then declare it on the endpoints it guards.

5. **Add or change a role**: define the role and its scope set (least privilege by default),
   mark it protected if it is a system role, and add it to the seed. Changing a role's scopes
   changes every assigned subject's effective permissions.

6. **Guard an endpoint**: attach the project's scope-enforcement dependency with the accepted
   scopes, matching the combining semantics. Include the per-resource wildcard among accepted
   scopes if that is the project's pattern. Never leave a state-changing endpoint unguarded.

7. **Manage protected entities**: do not delete or mutate protected system roles or scopes
   except through the guarded administrative path the project provides. Role deletion must be
   blocked while the role is still assigned.

8. **Seeding and migration**: keep the default scopes and roles in the project's config or
   seed source; when adding scopes or roles, update both the seed and the migration so fresh
   and existing databases converge.

9. **Verify**: run the project's migration tooling and tests; confirm a subject with the role
   passes the guarded endpoint, a subject without it gets the forbidden response, the global
   superscope passes, and a delegated credential cannot exceed its owner's scopes. If you
   cannot run these, say why.

10. **Summarize**: scopes and roles added or changed, endpoints guarded, seed and migration
    updates, and any note about token re-issuance being required to take effect.

## Decisions to surface when escalating

- Granularity: coarse roles only, or fine-grained scopes bundled into roles (recommended).
- Naming convention for scopes (`resource:action`, wildcards, a global superscope).
- Combining semantics at endpoints: ANY-of versus ALL-of.
- Where scopes are enforced from: embedded in the access token, resolved live per request, or
  both, and the staleness tradeoff that implies.
- Delegation: whether API keys or issued tokens can carry a narrowed scope subset.
- Protected system roles and scopes, and who may administer them.
- Seed of default scopes and roles, and the migration and rollout plan.

## Rules

- Never add an RBAC model silently: if the codebase lacks one, escalate and get explicit
  approval and decisions first.
- Never invent a second permission scheme when one exists; mirror the naming, resolution, and
  enforcement already in place.
- Never change a guard's combining rule (ANY-of versus ALL-of) without confirming it is
  intentional; it silently widens or narrows access.
- Never let a delegated credential hold a scope its owner does not have; credentials narrow,
  never widen.
- Always default new roles to least privilege; grant the narrowest scope that satisfies the
  need.
- Always guard state-changing endpoints; never ship one unprotected.
- Always update both the seed and a migration when adding scopes or roles.
- Follow the project's architecture, token model, and settings convention.
- Do not use em-dashes in files you write or in your output.
