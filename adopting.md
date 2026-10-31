# Adopting this on a new project

This guide is for a coordinator bot setting up the method on a new repository and an empty board. Work through it in order. Each step names who does it.

## 1. Agree the basics with the human owner

Before setting anything up, confirm these with the human and write the answers into the repository's agent instructions file:

- [ ] The name of the main branch, and that only the human merges into it.
- [ ] Whether there is a staging environment yet. If not, skip staging steps until there is one, and say so in each pull request.
- [ ] Where worker agents run (a shared build machine, never the human's personal computer).
- [ ] Which automated reviewer is used, how a review is requested, and from which account.
- [ ] The round cap (ten unless the human says otherwise).
- [ ] Who the ops agent is for root-level changes.
- [ ] Which test commands count as "the full suite" for each component.

## 2. Set up the board

Create one board for the repository with a single-select status field and these options, in this order:

| Column | Put a card here when | The pull request is |
|---|---|---|
| Backlog | The issue is proposed or approved but no worker has started | not yet open |
| In Progress | A worker is writing code or fixing findings | a draft |
| Auto Review | The coordinator's pre-check passed and the automated reviewer is reviewing | ready |
| Pending | The change is otherwise ready but waits on another change or a decision | ready or draft |
| Human Review | The pull request passed the gate (see step 6). Pull requests only | ready |
| Done | The human merged it to main | merged |

Board settings:

- [ ] Add new issues and pull requests in the repository to the board automatically, if the tracker supports it.
- [ ] Move a card to Done automatically when its pull request merges.
- [ ] When a pull request links an issue, remove the issue card from the board. The pull request card carries the work, so the board counts it once and Human Review holds only pull requests.

## 3. Create labels

Keep labels few. These are enough to start:

| Label | Use |
|---|---|
| `approved` | The human approved the issue. Workers start only on approved issues. |
| `parked` | The human paused it. Leave it alone until he says otherwise. |
| `blocked` | Waiting on another change or decision. Name the blocker in a comment. |
| `ui` | Changes something a person can see (UI, rendered images or video), so it needs screenshots or frames from staging. |
| `needs-decision` | The coordinator asked the human a question and is waiting. |
| `follow-up` | Filed from a review finding or neighboring case that belongs in its own change. |

Review priorities (P1, P2) come from the automated reviewer's findings. Don't duplicate them as labels.

## 4. Add the templates

Add an issue template to the repository:

```markdown
## Goal
<one or two sentences: what changes for the user>

## Approach
<the design, closest to existing code; name the files or modules>

## Choices the human owner made
- <choice>

## Out of scope
- <thing not in this change>

## Tests
- <case>

## Acceptance
<how the human will check it, usually on staging>
```

Add a pull request template:

```markdown
Fixes <issue reference>

## What changed
<summary>

## Approach
<why this design; what existing mechanism it reuses>

## Root-cause fixes
For each review finding: the root cause, the neighboring cases, and the tests.
- <finding>: <root cause>. Cases: <list>. Tests: <names>.

## Tests
<command>: <passed>/<total>

## Blocked on
<other change, or "nothing">

## Where to see it
<the staging place to look, the steps to get there, and the commit staging is serving>

## Screenshot
<current staging screenshots or frames for anything a person can see, with a side-by-side for generated media that has a reference, or "nothing visible changed">
```

Copy the brief template from [briefs.md](briefs.md) into the coordinator's own notes. Briefs don't go in the repository.

Add a short agent instructions file at the repository root with the root-cause rule, the branch rules, and the rule that workers don't merge, deploy, or resolve review threads. Open it as the first pull request (step 5), so the human approves the rules the same way as code.

## 5. Run the first issue

Use a small, real issue for the first run, so problems with the setup show up early.

1. **Human.** Approves the issue. The coordinator adds the `approved` label and puts the card in Backlog.
2. **Coordinator.** Writes the brief from the template, including every choice the human stated.
3. **Coordinator.** Creates a checkout for the worker on the build machine, starts the worker in its own terminal session, and sends the brief. Moves the card to In Progress.
4. **Worker.** Cuts the branch from the latest main, makes a first commit, and opens a draft pull request against main that links the issue.
5. **Worker.** Writes code and tests, runs the full suite, pushes, and reports the head commit and pass counts.
6. **Coordinator.** Runs the pre-check (checklist A below).
7. **Coordinator.** Marks the pull request ready, moves the card to Auto Review, and requests round 1 of automated review.
8. **Coordinator.** Reads the findings. For each P1 or P2, converts the pull request to a draft, moves the card to In Progress, and relays the finding to the worker with the root-cause rule.
9. **Worker.** Fixes the root cause, tests the neighboring cases, updates the pull request body, pushes, and reports.
10. **Coordinator.** Verifies each fix on the new head (checklist B), resolves the threads, and repeats from step 7 until a round comes back clean or the cap is reached.
11. **Coordinator.** Runs the post-check (checklist C).
12. **Coordinator.** Merges the change into the staging branch, redeploys staging, and checks that staging serves the current head and can run the change. If the change is visible, makes sure current screenshots or frames from staging are embedded in the pull request description.
13. **Coordinator.** Checks the gate (checklist D). If it passes, moves the card to Human Review and tells the human in one message: what changed, the test counts, the staging result, and the link to review.
14. **Human.** Reviews, then merges to main or sends it back with comments.

After the first issue, note anything in the setup that didn't work and fix it before starting more workers.

## 6. Gate checklists

Run these on the current head every time. A new push resets them.

### A. Pre-check, before the first automated review

- [ ] The issue is approved and not parked.
- [ ] The branch is cut from main and the pull request base is main.
- [ ] The change does what the issue and brief asked, and nothing else.
- [ ] Every choice in the brief is followed.
- [ ] Tests exist for the cases in the brief.
- [ ] The full suite passes when the coordinator runs it, and matches the worker's reported counts.
- [ ] No secrets, credentials, or machine-specific paths are committed.
- [ ] The pull request is mergeable against main.

### B. After each fix push

- [ ] Each relayed finding is fixed on the new head.
- [ ] The fix addresses the root cause, not only the reported line.
- [ ] The neighboring cases are listed in the pull request body and each has a test.
- [ ] The full suite passes.
- [ ] The coordinator resolves only the threads it has verified.

### C. Post-check, after automated review is clean or capped

- [ ] Everything in checklist A still holds.
- [ ] No P1 or P2 findings or threads are open.
- [ ] The tests pass twice in a row if the change touches timing, concurrency, or shared state.
- [ ] The change is not blocked on another unmerged change. If it is, move the card to Pending and stop here.

### D. Gate into Human Review

- [ ] The pull request is not a draft.
- [ ] It is mergeable against main.
- [ ] No P1 or P2 findings or threads are open.
- [ ] Checklist C passed on this head.
- [ ] The card is a pull request, not an issue.
- [ ] The change is merged into the staging branch, staging is redeployed, and staging is serving this head.
- [ ] Staging can run the change, with the configuration, credentials and services it needs. If it can't, move the card to Pending and ask the human.
- [ ] The pull request description says where and how to see the change.
- [ ] Any change a person can see, such as UI, rendered images or video, has current staging screenshots or frames embedded in the pull request description.

Any automation that moves cards must check every item on this list.

If any item fails later, move the card back to In Progress and convert the pull request to a draft.

## 7. Running more than one worker

- Start one worker per approved issue, each in its own checkout and session.
- Check the build machine's load and memory before starting more.
- Keep a list of active workers: issue, branch, session, last reported head.
- When two changes touch the same files, start the second only after the first merges, or put the second in Pending.
