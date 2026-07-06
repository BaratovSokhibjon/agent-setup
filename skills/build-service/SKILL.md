---
name: build-service
description: >-
  Stand up a complete, secured backend service in one guided pass by orchestrating the
  focused skills in dependency order: bootstrap, config, response and error convention, data
  store, authentication, authorization, API keys, feature slices, cleanup, and commit. Use
  when asked to build out a new service or a large slice of one from a description, not for a
  single isolated change.
metadata:
  keywords:
    - build service
    - scaffold api
    - orchestrator
    - end to end
    - backend service
    - pipeline
---

# build-service

You build out a complete backend service in one guided pass by orchestrating the focused
skills in this catalog. You are the conductor: each phase delegates to the skill that owns
it, in an order where every phase's dependencies already exist. Do not reimplement what a
sub-skill does; invoke it.

The skills you orchestrate:

- `init-project` (bootstrap from a template), `configify` (layered settings and secrets),
  `api-responses` (response envelope and error-code catalog), the database skills
  (`postgres`, `mysql`, `vitess`, `neki`) for data-store guidance, `oauth-support`
  (authentication), `rbac-support` (roles and scopes), `api-key-support` (programmatic
  access), `resource-scaffold` (feature slices), a `refactor` skill and `review` for
  cleanup, and `commit` to land the work.

## First: ask which services to configure

Before anything else, present the configurable components as a checklist and ask the user to
select which ones this run should set up. Do not assume the full set; a run may want only a
subset. Ask as a multi-select, listing each with a one-line purpose:

- **Project bootstrap** (`init-project`) - create or adapt the repository.
- **Config and secrets** (`configify`) - layered settings foundation.
- **Response and error contract** (`api-responses`) - the shared envelope and error catalog.
- **Data store** (`postgres` / `mysql` / `vitess` / `neki`) - and which engine.
- **Authentication** (`oauth-support`) - accounts, login, tokens.
- **Authorization** (`rbac-support`) - roles and scopes.
- **Programmatic access** (`api-key-support`) - API keys.
- **Feature resources** (`resource-scaffold`) - and which resources.
- **Cleanup** (`refactor` + `review`) - tidy and review the generated code.
- **Commit** (`commit`) - land the work.

If a selected component depends on one the user left out, say so and let them add it or
confirm the omission (for example, resources need the response contract and, if guarded, the
authorization model; authorization needs authentication or another subject source). Only the
selected components become phases; carry the selection through the rest of this workflow.

## Why one pass

Several sub-skills escalate and ask for decisions on a net-new build. Running them blindly in
sequence would interrupt constantly. Instead, once the selection is set, gather every decision
up front into one plan, get a single approval, then execute the selected phases with those
decisions already made. Big at once means one selection, one plan, and one approval, not one
silent sweep.

## Preflight: gather the spec and plan once

For the selected components only, settle and write down:

- The service purpose and its clients (browser, first-party API, service-to-service, mix).
- The resources or entities to build, each with its fields, relationships, and operations.
- The personas and what each may do (feeds the authorization model).
- Authentication needs (password login, tokens, refresh, verification, password reset) and
  whether programmatic API keys are needed.
- The data store, and whether it is new or existing.
- Whether the target is a fresh repository or an existing one to extend.

Then present one consolidated plan: the phases you will run, the sub-skills each uses, and the
key decisions (token strategy, hashing, scope model, data store, code format). Get explicit
approval on the whole plan before executing. This is where the sub-skills' individual
escalations are resolved in advance.

## Phases

Run only the phases the user selected, in this order; each depends on the ones before it.
Skip any unselected component and note it in the plan.

1. **Bootstrap** with `init-project`: pick and adapt the matching template, or adopt the
   existing repository. Skip if the repository is already established and suitable.

2. **Foundation config** with `configify`: establish the layered settings and secrets the
   later phases read (prefixes, durations, algorithms, data-store credentials).

3. **Response and error contract** with `api-responses`: establish the response envelope and
   the central error-code catalog first, because auth, authorization, and every resource
   raise coded errors through it.

4. **Data store** using the matching database skill (`postgres`, `mysql`, `vitess`, or
   `neki`): apply its guidance for schema design, indexing, transactions, and scaling as you
   set up the data layer the resources will persist through.

5. **Authentication** with `oauth-support`: accounts, token issuance and refresh rotation,
   and the flows the spec needs. Uses the config from phase 2 and raises codes from phase 3.

6. **Authorization** with `rbac-support`: analyze the planned resources and personas, propose
   the scope catalog and starter roles, and stand up the model. Its scopes are what the
   resource routers will require.

7. **Programmatic access** with `api-key-support`: only if the spec needs machine or
   integrator access. Keys carry a narrowed subset of their owner's scopes from phase 6.

8. **Feature slices** with `resource-scaffold`, once per resource: generate each slice
   (model, schemas, service, router), guarded by the phase 6 scopes, raising phase 3 codes,
   and persisting through the phase 4 data layer. Loop until every planned resource exists.

9. **Cleanup** with the language `refactor` skill, then `review`: tidy the generated code to
   the project's conventions and produce a review report; address its critical findings.

10. **Land** with `commit`: stage and commit the work in logical, reviewable commits (config,
    foundation, auth, authorization, then one per resource), after confirmation.

## Rules

- Delegate each phase to its sub-skill; do not reimplement a skill's behavior inline.
- Resolve the sub-skills' escalations in the preflight plan, then execute; never bypass a
  security decision, but do not ask them one interruption at a time either.
- Keep the dependency order: config, response contract, and data store before auth; auth
  before authorization; authorization before resources; cleanup and commit last.
- Honor every sub-skill's invariants (generic auth errors, refresh rotation, prefix-plus-hash
  key storage, scope narrowing, coded errors, guarded endpoints). The orchestrator never
  loosens them.
- Ask which components to configure before anything else, and run only the selected set; flag
  any dependency a selection implies but the user left out, and say what was skipped.
- If a phase cannot proceed without a new decision the plan did not cover, stop and surface
  it rather than guessing.
- Land the work as a coherent commit series, not one giant commit, and only after
  confirmation.
- Do not use em-dashes in files you write or in your output.
