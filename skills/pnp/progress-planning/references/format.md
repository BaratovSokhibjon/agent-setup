# P&P format and quality bar

## Template (exact)

```
## YYYY-MM-DD

## Done

**<Hubstaff project name>**
- [H:MM] <outcome> - <links>
  - <optional sub-point: follow-up filed, number, second outcome>

## To Do

**<Hubstaff project name>**
- <next step> - <link or "discuss in <link>">
```

- Headers are always `## Done` and `## To Do`. Project headers are the Hubstaff project
  name exactly (`INT: WakilAI`, `INT: Infra - Administration`), bold, one blank line before.
- Every item line starts `- [H:MM] `. Projects are ordered by tracked time, items within a
  project by time, largest first.
- Links are markdown: `[WK-404](url)`, `[editions-web #102](url)`; Discord and Telegram links
  as `[thread](url)` or `[message](url)`. Never a bare "discuss in" with nothing after it.

## Keep or drop

- **Keep** a Hubstaff task when at least one piece of evidence (PR, commit, issue, Discord or
  Telegram message) matches it. Its time is the task's Hubstaff time.
- **Drop** a task with no evidence. List it in the run notes with its time so the user can
  see what was left out. Do not invent an outcome from the task name alone.
- **Merge** tasks on one subject into one line and add their times (for example "fix
  inference failures" and "debug inference request failures").
- **Fold** many small PRs into one outcome line with a sub-point; never one line per PR.
- Tasks under 3 minutes with evidence fold into the closest related item of the same
  project; without evidence they are dropped silently.
- Evidence with no tracked time (a Discord decision, a review) can be a sub-point of a related
  item, never its own timed line.

## Writing the Done line (the bar: Dilshod's P&Ps)

1. **Outcome first.** Say what now works, shipped, or was decided: "pin conversations and
   projects shipped", "ATMOS confirmed the error is on their side". Not "worked on",
   "go through", "try testing".
2. **Issue key first when there is one:** `[WK-404](url): ...`.
3. **Concrete details from the evidence:** numbers (436 to 40 ms), versions, counts, names of
   the people whose work he reviewed or delegated ("reviewed Abduvaliy's failover PR").
4. **Follow-ups as sub-points:** `- follow-up filed: [WK-412](url) ...`.
5. One line, two at most. Group small maintenance into one line ("Console polish: ...").

## Writing the To Do

1. Start from the previous P&P's To Dos. Drop the ones today's Done completes.
2. Add his PRs still open at the end of the day, issues he owns that moved to In Progress or
   In Review, and promises he made in Discord or Telegram ("I'll check tomorrow").
3. Each item is one verifiable next step with its link. Three to six items.
4. An item carried over 3 or more entries gets flagged in the run notes as stale (not in the
   posted report).

## Voice

Apply `write-like-sokhibjon` within the template: plain verbs, ` - ` to join a clause, short
lines, no ceremony. The template and links above take priority over register rules.

## Example (quality reference)

```
**INT: LumioHubAI - Smart Office**
- [1:33] [LSO-268](https://linear.app/...): auto-OUT live on all 3 branches (backend 0.7.16, AI 0.8.21, frontend 1.10.26), door cameras marked as entrance
- [0:38] [LSO-310](https://linear.app/...): People / Dashboard 3-37x faster on prod (backend 0.7.15)
  - follow-up filed: [LSO-318](https://linear.app/...) per-row queries and missing indexes
```
