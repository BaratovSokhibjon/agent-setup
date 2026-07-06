# agent-setup

This is my agent configs that I primarily use for development.

## Install the skills

Install everything:

```bash
npx skills add BaratovSokhibjon/agent-setup
```

Install a specific skill by its `name`:

```bash
npx skills add BaratovSokhibjon/agent-setup --skill python-refactor
npx skills add BaratovSokhibjon/agent-setup --skill go-review
```

List everything available first:

```bash
npx skills add BaratovSokhibjon/agent-setup --list
```

## Available skills

Skills are organized in a catalog layout (`skills/<category>/<name>/SKILL.md`). The
category folder is only for organization; the `name` in each skill's frontmatter is what
you pass to `--skill`.

| Skill (`name`) | Category | Purpose |
| --- | --- | --- |
| `commit` | (root) | Group changes by concern and create clean Conventional Commits. |
| `init-project` | (root) | List humblebeeai templates, pick the one matching the project, and adapt it (falls back to base-template). |
| `review` | generic | Language-agnostic code review; writes a structured report. |
| `refactor` | generic | Language-agnostic behavior-preserving cleanup from the diff. |
| `api-key-support` | generic | Add/extend API key creation, verification, and lifecycle; escalates if the codebase lacks key support. |
| `python-review` | python | Review Python against the Google Python Style Guide. |
| `python-refactor` | python | Refactor Python to the Google Python Style Guide. |
| `configify` | python | Add or modify config sections using the layered pydantic-settings convention (mutable/frozen, env prefixes, YAML). |
| `javascript-review` | javascript | Review JavaScript against the Google JavaScript Style Guide. |
| `javascript-refactor` | javascript | Refactor JavaScript to the Google JavaScript Style Guide. |
| `typescript-review` | typescript | Review TypeScript against the Google TypeScript Style Guide. |
| `typescript-refactor` | typescript | Refactor TypeScript to the Google TypeScript Style Guide. |
| `go-review` | go | Review Go against the Google Go Style Guide and Effective Go. |
| `go-refactor` | go | Refactor Go to the Google Go Style Guide and Effective Go. |

The `review` skills write a report to `/tmp/<dirname>/code-review.md`, which the matching
`refactor` skill reads to prioritize its fixes. Pick the language variant that matches the
dominant language of your diff; fall back to the generic `review`/`refactor` otherwise.
</content>
