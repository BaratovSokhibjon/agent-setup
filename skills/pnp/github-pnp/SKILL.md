---
name: github-pnp
description: >-
  Fetch a person's GitHub activity for a work date across every org they work in: PRs they
  opened or merged, commits, and reviews, as compact evidence lines for a Progress & Planning
  report. Works inside cloud sessions that only reach attached repos by building the repo set
  first and attaching each repo read-only. Use when progress-planning needs code evidence.
metadata:
  keywords:
    - github
    - pull requests
    - commits
    - p&p
    - progress and planning
---

# github-pnp

Return what shipped or moved in code during the window, nothing else. Rule: no em-dashes in
output.

## Fixed values

- Login: `BaratovSokhibjon`
- Seed repos: `wakil-ai/editions-web`, `wakil-ai/editions-api`, `wakil-ai/editions-gateway`,
  `wakil-ai/rest-api-ai`, `wakil-ai/planning`, `wakil-ai/authentik`, `wakil-ai/nginx-config`,
  `wakil-ai/stack-editions`
- Window W: work date D in UZT = `D-1T19:00:00Z` to `DT19:00:00Z`

## Repo set (search and user endpoints are blocked in cloud sessions)

1. Repo set = seed repos + `REPOS` from `linear-pnp` + any `github.com/<owner>/<repo>` in the
   day's Discord or Telegram messages, Hubstaff task summaries, or the previous P&P.
2. For each repo not attached yet: `add_repo(owner, repo, access: "read")`. Do not clone. A
   refusal goes into the output as `NO_ACCESS | <owner/repo>`.

## Calls per repo

```bash
gh api "repos/$R/pulls?state=all&sort=updated&direction=desc&per_page=50" --jq \
  '.[] | select(.updated_at >= "'$WS'") | select(.user.login == "BaratovSokhibjon")
   | [.number, .state, (.merged_at // ""), .title, .html_url] | @tsv'
gh api "repos/$R/commits?author=BaratovSokhibjon&since=$WS&until=$WE&per_page=100" --jq \
  '.[] | [.sha[0:7], .commit.author.date, (.commit.message | split("\n")[0]), .html_url] | @tsv'
```

- Keep a PR when it was opened or merged inside W (an update alone is not enough).
- PRs are the main signal: squash merges hide his commits, and PR titles carry the substance
  (what changed, numbers, issue keys, design sheet rows).
- Reviews of others' PRs, only when a Hubstaff task or Linear issue points at that PR:
  `gh api repos/$R/pulls/<n>/reviews --jq '.[] | select(.user.login=="BaratovSokhibjon") | [.state, .submitted_at] | @tsv'`
- Run repos in one shell loop; stop paging when a page has nothing inside W.

## Output

```
<owner/repo>#<n> | merged|opened|reviewed | <UTC time> | <title> | <url>
<owner/repo>@<sha> | commit | <UTC time> | <subject> | <url>   (only commits not in a listed PR)
```

Then `OPEN | <owner/repo>#<n> | <title>` for his PRs still open at the end of W (To Do
candidates).
