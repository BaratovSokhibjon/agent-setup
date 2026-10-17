# P&P format and rules

Rules follow the original P&P agent (`bride-sh/int-agent-bride-pnp`): Hubstaff is the
outline, everything else is footnotes.

## Template (exact)

```
## YYYY-MM-DD

## DONE

**<Hubstaff project name>**
- [H:MM] <one sentence, links woven into the words they evidence>
  - <optional sub-point: follow-up filed, a number, a second outcome>

## TODO

**<Hubstaff project name>**
- <short next action, link woven in>
```

## Structure

- Section headers are the exact Hubstaff project names, bold. Projects ordered by tracked
  time, largest first.
- **Every Hubstaff task with tracked time is one `[H:MM]` bullet**, duration preserved. Never
  drop, merge into another task, or reduce an entry. Only entries under 1 minute are left out.
- GitHub, Linear, Discord, Telegram and Claude session evidence only enriches a bullet. It
  never becomes its own header, section or bullet, and never overwrites a Hubstaff entry.
- Match each piece of evidence to at most one bullet, the one whose project, repo and content
  it actually describes. Unmatched evidence stays unused; never attach it to the nearest or
  only bullet to fill space.
- Hubstaff unavailable (error, not zero): label bullets by the clearest supported project
  (never a raw repo name) and say Hubstaff was unavailable in the run notes. Never turn an
  error into "no time tracked".

## Wording

- **Completion wording** (shipped, merged, fixed, released) only with direct evidence: a merged
  PR, a commit, a closed issue, or a message confirming it.
- **Effort wording** (worked on, investigated, continued, set up) for Hubstaff-only entries.
  Time proves effort, not completion.
- Weave links into the phrase they evidence: `merged the [pinning PR](url)`, never a trailing
  "as evidenced by [commit](url)". Short repo labels are fine: `[editions-web #102](url)`.
- Be specific from the evidence: numbers (436 to 40 ms), versions, issue keys first
  (`[WK-404](url): ...`), names of people whose work was reviewed or delegated.
- Many PRs for one task: one sentence naming the outcomes, plus a sub-point if needed. Never
  one bullet per PR.
- No personal pronouns, no evaluation of the employee, no ceremony.

## TODO

- Fresh every day. Add a TODO only when today's evidence shows unfinished work, a next action
  or an open blocker: his PRs still open, issues still In Progress or In Review, promises made
  in chat, `UNANSWERED` tags asking him for something.
- A previous P&P's TODO appears only when today's evidence shows activity on it or says it is
  unfinished. Never carry one forward on its own.
- Group under the Hubstaff project the follow-up continues (never a repo name). No durations.
- A blocker states its reason and the unblock action.
- Attach a link only when it concerns that exact follow-up; never reuse a link that evidences a
  different item. Empty section when nothing is unfinished.

## Voice

Apply `write-like-sokhibjon` within these rules: plain verbs, ` - ` to join a clause, short
lines. The template and rules above win over register guidance.

## Run notes (doc tab only, never posted)

- `Tracked X:XX` and any Hubstaff entries under 1 minute left out
- `Evidence not matched: <item>` for evidence that fit no bullet
- `Previous TODOs not continued: <item>` with how many P&Ps it appeared in
- `hstaff: posted id=<id>` or `hstaff: not posted, <error>`
- `Sources missing: <source, reason>`
