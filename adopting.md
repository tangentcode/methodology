# Adopting this on a new project

This guide is for a coordinator bot setting up the method on a new repository and an empty board. Work through it in order. Each step names who does it.

## 1. Agree the basics with the human owner

Before setting anything up, confirm these with the human and write the answers into the repository's agent instructions file:

- [ ] The name of the main branch, and that only the human merges into it.
- [ ] Whether there is a staging environment yet. If not, skip staging steps until there is one, and say so in each pull request.
- [ ] Where worker agents run (a shared build machine, never the human's personal computer).
- [ ] Which automated reviewer is used, how a review is requested, and from which account.
- [ ] The automation that moves finished work forward is running before the first worker starts. At minimum, within an hour of a worker finishing a draft with passing tests, it runs the pre-check, marks the pull request ready and requests review. Until that automation exists, the coordinator checks every worker by hand at least once an hour.
- [ ] Workers end every turn with one status line a scan can read: done and waiting for review, waiting on the human for a named thing, or continuing. A worker that is waiting on the human for one part says which other parts can go to review now.
- [ ] The round cap (ten unless the human says otherwise).
- [ ] Who the ops agent is for root-level changes.
- [ ] Who the owner bot is for this board (product decisions, Triage, briefs).
- [ ] Which test commands count as "the full suite" for each component.

Edit [team-conventions.md](team-conventions.md) so it records this team's naming and coding customs, not the ones written for the original team.

## 2. Set up the board

Create one board for the repository with a single-select status field and these options, in this order:

| Column | Put a card here when | Card type |
|---|---|---|
| Inbox | The item is kept out of the flow for now, or is a new customer ticket | issue |
| Discuss | The issue needs careful thought or a conversation. Set aside so simple triage items flow first | issue |
| Triage | An agent has suggested plans and the human must decide | issue |
| Backlog | The plan is approved but not in the current sprint | issue |
| Active | The issue is assigned to the swarm and has sub-issues or a linked open pull request | issue |
| In Progress | A worker is working on the draft pull request now | draft pull request |
| Auto Review | The worker signed off and the automated reviewer is reviewing | ready pull request |
| Needs Input | The latest comment is a worker or coordinator question that a human must answer | draft pull request |
| Human Review | The pull request passed the gate (see step 6). Any number of independent pull requests, plus at most one stacked pull request when only its base is there | ready pull request |
| Pending | The change is otherwise ready but waits on another change or a decision | ready pull request |
| Done | The human merged it to main | merged pull request |
| Canceled | The pull request was closed without merging | closed pull request |
| Parked | The draft has real work but we decided not to merge it yet | draft pull request |

See [workflow.md](workflow.md#board-columns) for the full meaning of each column.

Board settings:

- [ ] Every pull request card has a Status: In Progress for drafts or ongoing pushes; otherwise Auto Review with a review requested.
- [ ] Add new issues and pull requests in the repository to the board automatically, if the tracker supports it.
- [ ] Move a card to Done automatically when its pull request merges.
- [ ] When a pull request is opened, give it a closing link (Fixes, or an equivalent). A "Part of" mention is not a link. Assign the issue to the swarm (the `swarm` label), then move the issue card to Active. Keep both cards. The pull request card carries the review loop. The issue card stays in Active while any linked pull request is open or any sub-issue is open. It leaves Active only when both are gone.
- [ ] New issues land in Triage. Issues with no pull request never go in Auto Review, Pending, or Human Review.

## 3. Create labels

Keep labels few. These are enough to start:

| Label | Use |
|---|---|
| `approved` | The human approved the issue. Workers start only on approved issues. |
| `swarm` | Assigned to the swarm. Active holds only issues with this label, plus open sub-issues or a linked open pull request. |
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

## Code context and cause
<relevant component, files or modules, and why the problem happens>

## Fix options
1. <option>
2. <option>
<two to four numbered options, with a recommendation the maintainer can choose in one comment>

## Approach
<the design chosen by the maintainer>

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
Fixes <issue reference>   (or: Part of <issue reference>, when this pull request covers only part of the issue)

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
<the staging place to look, the steps to get there, and the staging commit being served, which contains this head>

## Screenshot
<current staging screenshots or frames for anything a person can see, with a side-by-side for generated media that has a reference, or "nothing visible changed">
```

Title rules: an issue title describes the present state. A wanted change uses "should" (example: "Save As should work for every file that can be saved"). A plain statement such as "X does Y" reads as a bug report. Every issue gets a GitHub issue type: Feature, Bug, or Task. A pull request title completes the sentence "Merging this pull request will ..." and starts with an imperative verb (example: "Make the Save As command work for every file that can be saved"). See [working-agreements.md](working-agreements.md).

Copy the brief template from [briefs.md](briefs.md) into the owner bot's notes. Briefs don't go in the repository. The coordinator keeps a copy when it launches the worker.

Add a short agent instructions file at the repository root with the root-cause rule, the branch rules, and the rule that workers don't merge, deploy, or resolve review threads. Open it as the first pull request (step 5), so the human approves the rules the same way as code.

## 5. Run the first issue

Use a small, real issue for the first run, so problems with the setup show up early.

1. **Human or tracker.** Puts the issue in Triage.
2. **Owner bot.** Comments with options. **Human.** Decides in a comment (edits count). The coordinator forwards that comment to the owner bot.
3. **Owner bot.** Writes the brief from the template, including every choice from the human's comment, and moves the card to Backlog (or posts questions on the issue and leaves it in Triage).
4. **Coordinator.** Creates a checkout for the worker on the build machine, starts the worker in its own terminal session, and sends the brief.
5. **Worker.** Cuts the branch from the latest main, makes a first commit, pushes the branch, and stops. The worker does not open the pull request.
6. **Coordinator, then worker.** The coordinator opens a draft pull request from that branch against main, with a closing link, adds the `swarm` label, moves the issue card to Active, and moves the pull request card to In Progress. The issue never sits in Active without that link. A "Part of" mention is not a link. Then the coordinator tells the worker to continue. The worker writes code and tests, runs the full suite, pushes, and reports the head commit and pass counts.
7. **Worker.** Writes code and tests, runs only the targeted test files locally through the shared two-slot throttle with one Vitest worker, pushes, and reports the head commit and pass counts.
8. **Coordinator.** Runs the pre-check (checklist A below).
9. **Coordinator.** Marks the pull request ready, moves the card to Auto Review, and requests round 1 of automated review.
10. **Coordinator.** Reads the findings. For each P1 or P2, converts the pull request to a draft, moves the card to In Progress, and relays the finding to the worker with the root-cause rule.
11. **Worker.** Fixes the root cause, tests the neighboring cases, updates the pull request body, pushes, and reports.
12. **Coordinator.** Verifies each fix on the new head (checklist B), resolves the threads, and repeats from step 8 until a round comes back clean or the cap is reached.
13. **Coordinator.** Runs the post-check (checklist C).
14. **Coordinator.** Merges the change into the staging branch, redeploys staging, and checks that the commit staging serves contains the current head and that staging can run the change. If the change is visible, makes sure current screenshots or frames from staging are embedded in the pull request description.
15. **Coordinator.** Checks the gate (checklist D). A pull request that is independent of every pull request in Human Review goes to Human Review. If it is not independent, it goes to Pending when it is clean on the current stack. When Human Review holds only one pull request and the next finished work depends on it, one stacked pull request can enter, with the stacked banner at the top of its body (see [Stacked pull requests](workflow.md#stacked-pull-requests)). Before a pull request enters with a vN tip as its head, the coordinator installs that tip and repeats steps 11 and 12 on it. A vN tip built on a pull request that was sent back is never installed: the coordinator keeps the plain branch if that is clean on main, or asks the worker for a new vN branch without the rejected work. If the gate passes, moves the card to Human Review and tells the human in one message: what changed, the test counts, the staging result, and the link to review.
16. **Human.** Reviews, then merges to main or sends it back with comments.

After the first issue, note anything in the setup that didn't work and fix it before starting more workers.

## 6. Gate checklists

Run these on the current head every time. A new push resets them.

### A. Pre-check, before the first automated review

- [ ] The human has decided the issue (Triage comment or approval) and it is not parked.
- [ ] The branch is cut from main and the pull request base is main.
- [ ] The change does what the issue and brief asked, and nothing else.
- [ ] Every choice in the brief is followed.
- [ ] Tests exist for the cases in the brief.
- [ ] Targeted local tests pass and match the worker's reported counts; full Linux suites run in GitHub Actions, not on the shared build box.
- [ ] No secrets, credentials, or machine-specific paths are committed.
- [ ] The pull request is mergeable against main.

### B. After each fix push

- [ ] Each relayed finding is fixed on the new head.
- [ ] The fix addresses the root cause, not only the reported line.
- [ ] The neighboring cases are listed in the pull request body and each has a test.
- [ ] Targeted tests pass locally. After the PR is marked ready, require current-head Linux suites in GitHub Actions before Human Review.
- [ ] The coordinator resolves only the threads it has verified.

### C. Post-check, after automated review is clean or capped

- [ ] Everything in checklist A still holds.
- [ ] No P1 or P2 findings or threads are open.
- [ ] The relevant tests pass twice in a row if the change touches timing, concurrency, or shared state; local reruns stay targeted and throttled.
- [ ] The change is not blocked on another unmerged change. If it is, move the card to Pending and stop here. One exception: a stacked pull request whose base is the only pull request in Human Review passes this item (see [Stacked pull requests](workflow.md#stacked-pull-requests)).

### D. Gate into Human Review

- [ ] The pull request is independent of every pull request in Human Review: it merges cleanly onto main, it contains no unmerged commits of another Human Review pull request, and it merges cleanly together with each of them. Or it is the one permitted stacked pull request: when it enters, Human Review holds only its base, and the body starts with the stacked banner. After it is in Human Review, it stays eligible while its base is in Human Review, even if independent pull requests enter next to it. If neither is true, move the card to Pending and stop here.
- [ ] If the pull request is stacked, its base is still open in Human Review, or it merged to main. If the base was sent back or closed, reset the stacked pull request first (see [Stacked pull requests](workflow.md#stacked-pull-requests)) and stop here.
- [ ] If a vN tip is installed as the head, that tip was checked against the current stack and contains no commits from a pull request that was rejected (sent back or closed unmerged). This also applies to a Pending pull request whose vN tip was built on a pull request that is no longer in Human Review: rebuild that tip first. Checklist C and the staging checks below ran on that head. If the vN tip is stale, the plain branch is kept when it is clean on main.
- [ ] The pull request is not a draft.
- [ ] GitHub Actions Linux checks are green on its current head.
- [ ] It is mergeable against main.
- [ ] No P1 or P2 findings or threads are open.
- [ ] Checklist C passed on this head.
- [ ] The card is a pull request, not an issue.
- [ ] The change is merged into the staging branch, staging is redeployed, and the commit staging serves contains this head.
- [ ] Staging can run the change, with the configuration, credentials and services it needs. If it can't, do not use Pending. Convert the pull request to a draft, move the card to Needs Input, and post a comment that names what is missing and who must provide it (the human, or the operator who owns the environment). When it is in place, mark the pull request ready, check staging again, and run this checklist again. If the head changed, go back to In Progress.
- [ ] The pull request description says where and how to see the change.
- [ ] Any change a person can see, such as UI, rendered images or video, has current staging screenshots or frames embedded in the pull request description.

Any automation that moves cards must check every item on this list.

If any item fails later, move the card back to In Progress and convert the pull request to a draft.

### CI and staging setup

- Configure Linux full suites for ready-for-review PR pushes (skip drafts and run on ready-for-review) and main pushes. Cancel superseded runs. Run Windows weekly only.
- Install the shared two-slot throttle for local tests and headless browsers. Target exact changed test files; use `--maxWorkers=1 --no-file-parallelism` for Vitest.
- Keep post-work-merge checks to the deployed commit, site auth, and a remote smoke test. Do not run full suites on the shared build box.

## 7. Running more than one worker

- Start one worker per brief, each in its own checkout and session.
- Check the build machine's load and memory before starting more.
- Launch every worker and test command inside the capped cgroup slice automatically, wrapping the command inside the terminal pane rather than the terminal client.
- Keep a registry of active and parked workers, with issue, branch, PR, worktree, saved session, last pushed head, idle time, and a one-command resume.
- There is no fixed worker-count limit. Report memory use and limit, swap, available memory, CPU use, and load when resources are tight.
- Under memory pressure only, park clean, fully pushed workers idle at empty prompts, longest-idle first. Leave workers running when there is headroom. Resume saved sessions in their original worktrees inside the cap, automatically when PR feedback requires more work. See [working-agreements.md](working-agreements.md).
- When two changes touch the same files, start the second only after the first merges, or put the second in Pending.
- Start every worker in its agent's automatic-review mode by default, where a reviewer model approves routine actions instead of a person. Use it together with the standing allow list below. Pick a mode that reviews each action, never one that skips checks. Mode names change, so check each agent's current documentation. At the time of writing:
  - **Claude Code:** auto mode, `--permission-mode auto`.
  - **Codex CLI:** auto-review, `--sandbox workspace-write --ask-for-approval on-request` with `approvals_reviewer = "auto_review"`.
  - **Gemini CLI:** no reviewer mode. Start it with `--approval-mode auto_edit` and write the allow list as allow rules in its policy settings.
  - **Any other agent:** use its reviewer mode if it has one. If it has none, start it with its allow-list or policy settings, and rely on the short prompt check below to catch what's left.

  Never start a worker in a mode that skips all checks, such as Claude Code's `--dangerously-skip-permissions`, Codex's `--yolo` or Gemini's `yolo` approval mode. The guardrails are the same in every mode: no pushes to main, the staging branch or another worker's branch, and nothing destructive or touching secrets or credentials without asking first. Write those as deny or ask rules in the agent's settings, so a reviewer model can't approve them. If an agent can't enter its automatic mode, for example because the account or model doesn't support it, it falls back to prompting. The coordinator checks the mode when it starts each worker and switches it on if the agent started without it.
- Give every worker, whatever agent it runs, a standing allow list for the routine actions of its own change: read-only commands, running tests, installing dependencies inside its own checkout, and committing and pushing its own branch. Never allow pushes to main, the staging branch or another worker's branch. If a worker hits the same permission prompt on every change, that's a setup bug. Fix the allow list instead of approving the prompt each time.
- Give each checkout its own dependency install, not a link into another checkout, so removing or reinstalling dependencies stays inside the worker's own directory.
- Check for workers stopped on a permission prompt every 10 to 15 minutes, separately from the slower stall scan. A prompt that has waited more than 10 minutes counts as a stall. The coordinator approves it if the action stays inside the worker's own checkout and branch, and asks the human otherwise.
