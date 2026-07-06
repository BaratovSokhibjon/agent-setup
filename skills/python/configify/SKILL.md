---
name: configify
description: >-
  Add or modify configuration in a Python service that uses a layered pydantic-settings
  convention: one concern per file, mutable plus frozen classes, hierarchical env prefixes
  built from constants, placeholder templating, layered sources (CLI, secrets, dotenv, env,
  defaults), and matching YAML runtime configs. Use when adding settings, a new config
  section, env vars, or secrets to such a project, or refactoring config to match the
  convention.
metadata:
  keywords:
    - python config
    - pydantic settings
    - settings
    - configuration
    - env vars
    - secrets
    - layered config
---

# configify

You add or modify configuration in a Python service that uses a layered pydantic-settings
convention. Follow the project's existing config architecture exactly. Do not invent a
different config style; match what the project does. The pattern is not tied to any web
framework; it is a general Python settings layout.

## The convention

Config lives under a `core/configs/` package, one concern per file, each file named
`_<concern>.py` with an `__all__` export list. Prefixes and slugs come from a
`core/constants/` module.

- **Base classes** (`_base.py`):
  - `BaseConfig(BaseSettings)`: mutable working config (`extra="allow"`,
    `validate_default`, `validate_assignment`, `arbitrary_types_allowed`).
  - `FrozenBaseConfig(BaseConfig)`: `frozen=True`; a settled, immutable leaf.
  - `BaseMainConfig(FrozenBaseConfig)`: the root; adds a CLI source when not running as a
    packaged binary.
- **Per-concern modules**: define a mutable `XxxConfig(BaseConfig)` and, when the value
  needs post-processing or placeholder resolution, a `FrozenXxxConfig(XxxConfig)` with
  `frozen=True`. Nested groups (e.g. a CORS, SSL, or gzip block) are their own classes,
  each with its own `env_prefix`.
- **Env prefixes** are hierarchical and built from constants, never hardcoded raw:
  `ENV_PREFIX = "<ROOT>_"` -> `ENV_PREFIX_<SVC> = f"{ENV_PREFIX}<SVC>_"` ->
  `f"{ENV_PREFIX_<SVC>}<SECTION>_"`. A project may define several top-level prefixes (one
  per subsystem). Nested delimiter is `__`.
- **Env binding is by declared field, not by open prefix.** A value is loaded automatically
  from env, `.env`, or `/run/secrets` when a declared field's full prefix path matches the
  variable name (e.g. a `secret` field on a section config binds to
  `<ROOT>_<SVC>_<SECTION>_SECRET`). To make a new value env-configurable, declare a field on
  the right config class; there is no need to parse env vars by hand.
- **`extra` policy governs undeclared prefixed vars.** `extra="ignore"` (the strict,
  common choice) drops any prefixed var without a matching field; `extra="allow"` attaches
  undeclared vars to the model dynamically. Match whatever the project's `BaseConfig`
  already sets; do not flip it casually, and prefer declaring a field over relying on
  `extra="allow"`.
- **Required-env enforcement**: the root config may add a `@model_validator(mode="after")`
  that raises when required secrets or connection vars are absent in staging/production
  (e.g. JWT secret, password pepper, admin password, DB DSN). When you add a field that
  must be provided by the environment in those tiers, extend that validator rather than
  giving it an insecure default.
- **Fields** use `Field(default=..., ...)` with constraints (`min_length`, `max_length`,
  `ge`, `le`, `pattern`). Secrets use `SecretStr` with a `default_factory`.
- **Placeholder templating**: string defaults may carry `{token}` placeholders resolved
  once siblings are known (e.g. `{data_dir}`, `{tmp_dir}`, a project slug, a version).
  Resolution happens in the frozen variant via `@model_validator(mode="before")`, or in
  the parent via `@field_validator(mode="after")`.
- **Mutable to frozen handoff**: the parent aggregate holds the mutable child, mutates
  cross-field values in a `@field_validator(<child>, mode="after")`, then returns
  `FrozenChildConfig(**val.model_dump())`.
- **Source precedence** (do not reorder without intent): CLI (root config only) >
  nested secrets under `/run/secrets` > dotenv (`.env`) > environment > init defaults.
- **YAML runtime config**: a `templates/configs/<concern>.yml` mirrors the defaults,
  nested to match the section's position in the tree. The loader deep-merges every YAML in
  the configs dir and passes it to the root config as `RootConfig(**dict)`.
- **Access** is via a singleton: `from <pkg>.config import config`, then
  `config.<section>...`. Never instantiate config classes elsewhere.

## Workflow

1. **Orient in the actual project** (do not assume names; the prefix, slug, package, and
   root config class differ per project):

   ```bash
   cat src/*/core/constants/_base.py          # ENV_PREFIX chain and related constants
   cat src/*/core/configs/_base.py            # base classes, source order, extra policy
   cat src/*/core/configs/_main.py            # root config, model_config, required-env checks
   ls  src/*/core/configs/ templates/configs/ 2>/dev/null
   ```

   Identify the root config class, the `extra` policy on `BaseConfig`, any
   `_check_required_envs`-style validator, and pick an existing sibling section to mirror.

2. **Decide scope**: is the new section nested under an existing aggregate, or a top-level
   field on the root config? Match the closest existing sibling.

3. **Create `_<concern>.py`**:
   - Import base classes from `._base` and the prefix constants from `core.constants`.
   - Define nested sub-config classes first, each with its own
     `SettingsConfigDict(env_prefix=...)`.
   - Define the mutable `XxxConfig(BaseConfig)`; add a `FrozenXxxConfig` only if it needs
     freezing, templating, or post-processing.
   - Use `SecretStr` for any secret; keep placeholder-secret defaults marked
     `# pragma: allowlist secret` so detect-secrets passes.
   - End with an explicit `__all__`.

4. **Wire it into the parent**:
   - Add the field with `Field(default_factory=XxxConfig)` on the chosen aggregate or the
     root config.
   - If it needs freezing or templating, add a `@field_validator("<field>", mode="after")`
     that resolves placeholders and returns the frozen variant.
   - Update the parent's imports and `__all__`.
   - Note: sub-config modules are reached through the aggregate, not star-exported.
     `configs/__init__.py` typically re-exports only the base and root modules, so a nested
     module wires into its aggregate, not into `__init__`; only a new top-level concern
     touches the root config module.

5. **Add the YAML template**: create `templates/configs/<concern>.yml` mirroring the field
   defaults, nested to match the section's position. Keep every YAML key in sync with the
   model fields.

6. **Add `.env.example` entries**: commented example vars using the full prefix path
   (e.g. `# <ROOT>_<SVC>_<SECTION>_<FIELD>=...`). If the field must be supplied by the
   environment in staging/production, add it to the root config's required-env validator
   and leave a `!!! CHANGE THIS !!!` placeholder rather than a usable default.

7. **Validate** by actually loading config, not by eyeballing:

   ```bash
   python -c "from <pkg>.config import config; print(config.<section>)"
   pytest -q tests 2>/dev/null || true
   ```

   Confirm defaults resolve, placeholders expand, and env overrides bind.

8. **Summarize**: the new/changed section, where it was wired, YAML and `.env.example`
   additions, and the validation result.

## Rules

- One concern per file, underscore-prefixed, with an explicit `__all__`.
- Build every `env_prefix` from the constants, never from a raw hardcoded string.
- Make values env-configurable by declaring a field bound to the right prefix, not by
  parsing env vars by hand. Do not change the `extra` policy to capture undeclared vars.
- For values that must come from the environment in staging/production, extend the root
  required-env validator instead of shipping an insecure default.
- Use `SecretStr` for secrets; never hardcode real secrets; keep
  `# pragma: allowlist secret` on placeholder-secret defaults.
- Resolve cross-field and placeholder values in validators or the frozen variant, never at
  read time.
- Keep `templates/configs/*.yml` and `.env.example` in sync with the model fields.
- Do not reorder the settings sources.
- Access config through the `config` singleton; do not instantiate config classes elsewhere.
- Preserve behavior and existing field names unless explicitly asked to change them.
- Do not use em-dashes in files you write or in your output.
