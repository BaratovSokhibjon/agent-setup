---
name: resource-scaffold
description: >-
  Scaffold a new feature as a vertical slice that mirrors the project's convention: a data
  model, an I/O schema family, a service of business-logic operations, and a guarded
  transport/router, wired into routing, authorization, error handling, and config. Use when
  adding a new resource, entity, endpoint group, or CRUD feature to a service that already
  organizes code into per-feature slices.
metadata:
  keywords:
    - resource scaffold
    - vertical slice
    - crud
    - endpoint
    - router
    - service layer
    - schema
---

# resource-scaffold

You add a new feature to a backend service as a self-contained vertical slice, following the
project's existing per-feature convention exactly. The goal is a slice that looks like it was
written by whoever wrote the others: same module roles, same layering, same naming, same
wiring. Do not invent a new structure.

## Orient first

Find an existing slice to use as the template of record, and read it end to end:

```bash
rg -n -i 'router|service|schema|repository|handler|controller' --files-with-matches \
  --glob '!**/{node_modules,dist,build,.venv}/**' | head
```

Pick the sibling closest to what you are adding (similar shape, relationships, or
operations). If the project has no per-feature slice convention, this is not a scaffold task:
say so and either follow the project's actual structure or, for a net-new convention, surface
that and get direction before imposing one.

## The slice shape

A slice is role-named modules under one feature directory, each a layer, with a strict
dependency direction (transport depends on service, service depends on the data model; the
I/O schemas are the contract). Match the project's exact names; the common roles are:

- **Data model**: the persisted entity, its fields and types, constraints, indexes, computed
  attributes, and relationships to other entities.
- **Schemas**: the I/O contract as a family of models built from shared base types, typically
  a base with shared fields and validation, a create input, an update input (fields
  optional), an output (adds id and timestamps, reads from the model), a list-item output
  (adds a self link), and the response envelopes for one item and for a paginated list.
- **Service**: business-logic operations, one function per operation (list, get, create,
  update, delete, plus domain verbs), that call the data layer and translate typed lower-layer
  errors into coded errors at the boundary.
- **Transport/router**: one endpoint per operation, each declaring its summary, response
  model, status code, documented error responses, and authorization, delegating to the
  service.

## Workflow

1. **Analyze the target**: settle the entity name, its fields and types, relationships,
   which operations it needs (full CRUD or a subset plus domain actions), and the
   authorization scopes it should require. Note where you inferred versus need confirmation.

2. **Model the data**: define the entity with typed fields, constraints, indexes, and
   relationships, mirroring how the sibling declares them. Reuse the project's base model
   type and naming.

3. **Write the schema family**: create the base, input, update, output, list-item, and
   response-envelope models, composed from the project's shared schema base types. Carry
   field titles, descriptions, examples, and validation the way the sibling does. Keep the
   update model's fields optional.

4. **Write the service**: one operation per function following the project's signature
   convention (session or connection, request context, identifiers or input models). Call the
   data layer through its helpers, and translate typed domain or storage errors into the
   project's coded errors at the boundary (see the api-responses convention). Do not leak raw
   lower-layer errors.

5. **Write the router**: derive the resource name once, one endpoint per operation with its
   response model, status code, and documented error responses. Guard each endpoint with the
   project's authorization mechanism and the scopes for this resource, following the
   project's combining semantics (see the rbac-support convention). Use read versus write
   data access separation if the project has it. Delegate to the service and return through
   the project's response envelope.

6. **Wire it in**: register the router where the app assembles routes, add the resource's
   scopes to the authorization seed and catalog, add any new error codes to the central
   catalog, and read settings through the project's config convention. Leave no endpoint
   unguarded.

7. **Match naming exactly**: directory, model, schema family, resource name, and scopes must
   follow the same casing and pattern as the siblings. A reader should not be able to tell the
   new slice from the old ones.

8. **Verify**: run the project's migration tooling and tests; exercise create, read, list,
   update, and delete; confirm authorization is enforced, pagination and links work, and
   errors come back in the project's envelope. If you cannot run these, say why.

9. **Summarize**: files added, how the slice was wired (routing, scopes, error codes,
   migration), and any field or operation left for confirmation.

## Rules

- Mirror an existing slice; never introduce a second structure or naming style.
- Keep each responsibility in its role module and preserve the dependency direction; no
  business logic in the transport layer, no transport concerns in the data model.
- Guard every state-changing endpoint with the project's authorization and this resource's
  scopes; never ship an unguarded endpoint.
- Translate typed lower-layer errors into coded errors at the service boundary; never leak a
  raw storage or validation error.
- Return through the project's response envelope; do not hand-assemble a bare payload.
- Register the router, seed the scopes, and add a migration; a slice that is not wired in is
  not done.
- Preserve behavior and naming of existing slices; do not refactor them while adding a new one.
- Do not use em-dashes in files you write or in your output.
