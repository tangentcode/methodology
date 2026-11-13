# Adopt this method on a new project

This guide is for a coordinator bot that sets up the method on a new repository and an empty board. Do the steps in sequence. Each step tells who does it.

## 1. Agree on the basics with the human owner

Before you set up anything, agree on these items with the human. Write the answers in the agent instructions file of the repository.

- [ ] The name of the main branch. Only the human merges into it.
- [ ] Whether there is a staging environment yet. If there is no staging environment, do not do the staging steps until there is one. Say so in each pull request.
- [ ] Where worker agents run. Use a shared build machine. Never use the personal computer of the human.
- [ ] Which automated reviewer you use, how to request a review, and from which account.
- [ ] The automation that moves finished work forward operates before the first worker starts. At a minimum, it runs the pre-check, marks the pull request ready, and requests review within one hour after a worker finishes a draft with passing tests. Until that automation is available, the coordinator checks each worker by hand at least one time each hour.
- [ ] Workers end each turn with one status line that a scan can read. The line tells one of these: finished and waiting for review, waiting on the human for a named item, or continuing. A worker that waits on the human for one part tells which other parts can go to review now.
- [ ] The maximum number of review rounds. It is ten, unless the human says otherwise.
- [ ] Who the ops agent is, for root-level changes.
- [ ] Who the owner bot is for this board (product decisions, Triage, and briefs).
- [ ] Which test commands are "the full suite" for each component.

Edit [team-conventions.md](team-conventions.md) so that it records the names and coding customs of this team, not those of the original team.

## 2. Set up the board

Make one board for the repository. Give it a single-select status field with these options, in this sequence:

| Column | Put a card here when | Card type |
|---|---|---|
| Inbox | The item is out of the flow for now, or it is a new ticket from a customer. Issues with the `work2` label stay here, even when they have a linked pull request | issue |
| Discuss | The issue needs careful thought or a conversation. It waits here so that simple Triage items move first | issue |
| Triage | An agent suggested plans, and the human must decide | issue |
| Backlog | The plan is approved, but it is not in the current sprint | issue |
| Active | The issue is assigned to the swarm, it does not have the `work2` label, and it has exactly one open linked pull request in a flow column (In Progress, Auto Review, Needs Input, Pending, or Human Review). The number of cards in Active equals the number of pull requests in those flow columns that belong to issues without the `work2` label | issue |
| In Progress | A worker works on the draft pull request now | draft pull request |
| Auto Review | The worker is finished, and the automated reviewer reviews the change | ready pull request |
| Needs Input | The latest comment is a question from a worker or the coordinator that a human must answer. A comment does not move the card out. The human moves it to In Progress when the question has an answer | draft pull request |
| Human Review | The pull request passed the gate (see step 6). Exactly two pull requests. One stacked pull request can go in when Human Review holds only one pull request and no independent pull request is ready | ready pull request |
| Pending | The change is ready, but it waits on another change or on a Human Review slot | ready pull request |
| Done | The human merged it to main | merged pull request |
| Canceled | The pull request is closed and not merged | closed pull request |
| Parked | The draft has real work, but we decided not to merge it yet | draft pull request |

See [workflow.md](workflow.md#board-columns) for the full meaning of each column.

Board settings:

- [ ] Each pull request card has a Status. Use In Progress for drafts and for pull requests that still get pushes. Use Auto Review, with a review request, for all others.
- [ ] If the tracker can do it, add new issues and pull requests of the repository to the board automatically.
- [ ] When a pull request merges, move its card to Done automatically.
- [ ] When a pull request opens, give it a closing link (`Fixes`, or an equivalent). A "Part of" mention is not a closing link. Assign the issue to the swarm (the `swarm` label). Then move the issue card to Active, or keep it there if the human already moved it to Active. Keep the two cards, unless the issue has the `work2` label. The pull request card goes through the review loop. The issue card stays in Active while it has exactly one open linked pull request in a flow column. Do not put a second pull request for the same issue into a flow column while the first is still there. If a follow-up must run at the same time as the first change, make the follow-up a separate issue. Issues with the `work2` label stay in Inbox. Their pull requests still move through the review loop, but they do not count toward the Active total. The issue goes out of Active when it no longer has exactly one open linked pull request in a flow column.
- [ ] New issues go to Inbox or Triage. An issue without a pull request never goes in Auto Review, Pending, or Human Review. The only time it is in Active without a pull request is the short interval after the human moves it there and before the coordinator opens the draft pull request.

## 3. Make labels

Use few labels. These labels are sufficient to start:

| Label | Use |
|---|---|
| `approved` | The human approved the issue. Workers start only on approved issues. A move to Active also counts as approval. |
| `swarm` | The issue is assigned to the swarm. Active holds only issues with this label that do not have the `work2` label and that have exactly one open linked pull request in a flow column. |
| `work2` | The issue stays in Inbox, even when it has a linked pull request. That pull request still moves through the flow columns, but it does not count toward the Active total. |
| `parked` | The human stopped the work for now. Do not touch it until he says otherwise. |
| `blocked` | The item waits on another change or a decision. Name the blocker in a comment. |
| `ui` | The change has an effect that a person can see (UI, rendered images, or video). It needs screenshots or frames. |
| `needs-decision` | The coordinator asked the human a question and waits for the answer. |
| `follow-up` | An issue from a review finding or a neighboring case that must be a separate change. |

Review priorities (P1, P2) come from the findings of the automated reviewer. Do not also make labels for them.

## 4. Add the templates

Add an issue template to the repository:

```markdown
## Goal
<one or two sentences: what changes for the user>

## Code context and cause
<the related component, files, or modules, and why the problem occurs>

## Fix options
1. <option>
2. <option>
<two to four numbered options, with a recommendation that the maintainer can select in one comment>

## Approach
<the design that the maintainer selected>

## Choices of the human owner
- <choice>

## Out of scope
- <item that is not in this change>

## Tests
- <case>

## Acceptance
<how the human will check it, usually on staging>
```

Add a pull request template:

```markdown
Fixes <issue reference>   (or: Part of <issue reference>, when this pull request is only a part of the issue)

## What changed
<summary>

## Approach
<why this design, and which existing mechanism it uses again>

## Root-cause fixes
For each review finding: the root cause, the neighboring cases, and the tests.
- <finding>: <root cause>. Cases: <list>. Tests: <names>.

## Tests
<command>: <passed>/<total>

## Blocked on
<other change, or "nothing">

## Where to see it
<the place on staging, the steps to get there, and the staging commit that contains this head>

## Screenshot
<screenshots or frames for each item that a person can see, with a side-by-side view for generated media that has a reference, or "nothing visible changed">
```

Title rules: an issue title tells the present state. A wanted change uses "should" (example: "Save As should work for every file that can be saved"). A plain statement, such as "X does Y", is a bug report. Each issue has a GitHub issue type: Feature, Bug, or Task. A pull request title completes the sentence "Merging this pull request will ..." and starts with a verb in the imperative (example: "Make the Save As command work for every file that can be saved"). See [working-agreements.md](working-agreements.md).

Copy the brief template from [briefs.md](briefs.md) into the notes of the owner bot. Briefs do not go in the repository. The coordinator keeps a copy when it starts the worker.

Add a short agent instructions file at the root of the repository. Put these rules in it: the root-cause rule, the branch rules, and the rule that workers do not merge, deploy, or resolve review threads. Open this file as the first pull request (step 5). Then the human approves the rules in the same way as code.

## 5. Do the first issue

Use a small, real issue for the first run. Then problems with the setup show early.

1. **Human or tracker.** Puts the issue in Triage.
2. **Owner bot.** Writes options in a comment. **Human.** Decides in a comment, or by a move of the issue to Active or to Backlog. Edits to the comment also count. The coordinator sends that comment to the owner bot. A move to Active, with no comment, is sufficient approval to start the worker.
3. **Owner bot.** Writes the brief from the template, with each choice from the comment of the human, or with the default or recommended answers if the human moved the issue to Active with no comment. Moves the card to Backlog, unless the human already moved it to Active. Or it writes questions on the issue and keeps the issue in Triage, unless the human already moved it to Active.
4. **Coordinator.** Makes a checkout for the worker on the build machine. Starts the worker in its own terminal session and sends the brief. If the human moved the issue to Active, start the worker even when questions are still open.
5. **Worker.** Makes the branch from the latest main, makes a first commit, pushes the branch, and stops. The worker does not open the pull request. If it takes a default or recommended answer, it will state that default in the pull request body.
6. **Coordinator.** Opens a draft pull request from that branch against main, with a closing link. Adds the `swarm` label. Moves the issue card to Active, or keeps it there, and moves the pull request card to In Progress. After the pull request is open, the issue is never in Active without that link. A "Part of" mention is not a closing link. Then the coordinator tells the worker to continue.
7. **Worker.** Writes code and tests. Runs locally only the targeted test files, through the shared two-slot throttle, with one test worker process. Pushes, and reports the head commit and the number of tests that pass.
8. **Coordinator.** Does the pre-check (checklist A below).
9. **Coordinator.** Marks the pull request ready, moves the card to Auto Review, and requests round 1 of the automated review.
10. **Coordinator.** Reads the findings. For each P1 or P2, it changes the pull request to a draft, moves the card to In Progress, and sends the finding to the worker with the root-cause rule.
11. **Worker.** Fixes the root cause, tests the neighboring cases, updates the pull request body, pushes, and reports.
12. **Coordinator.** Makes sure of each fix on the new head (checklist B) and resolves the threads. Then it starts again from step 9 until a round is clean or the round limit is reached.
13. **Coordinator.** Does the post-check (checklist C).
14. **Coordinator.** Merges the change into the staging branch and deploys staging again. This is best-effort. Makes sure that staging can run the change. If a person can see the change, makes sure that the pull request description has screenshots or frames.
15. **Coordinator.** Checks the gate (checklist D). Human Review holds exactly two pull requests. A pull request that is independent of each Human Review pull request goes to Human Review when a slot is open. Other pull requests go to Pending. When Human Review holds only one pull request and the next finished work depends on it, one stacked pull request can go in. It has the stacked banner at the top of its body (see [Stacked pull requests](workflow.md#stacked-pull-requests)). Before a pull request goes in with a vN tip as its head, the coordinator installs that tip and does steps 12 and 13 again on it. The coordinator never installs a vN tip that is built on a pull request that the human sent back. It keeps the plain branch if that branch is clean on main, or it asks the worker for a new vN branch without the rejected work. If the gate passes, the coordinator moves the card to Human Review. It tells the human in one message: what changed, the test counts, the staging result, and the link for the review.
16. **Human.** Reviews. Then merges to main, or sends the change back with comments.

After the first issue, record each part of the setup that did not work. Fix it before you start more workers.

## 6. Gate checklists

Do these checks on the current head each time. A new push resets them.

### A. Pre-check, before the first automated review

- [ ] The human decided the issue (with a Triage comment, a move to Active, a move to Backlog, or another approval), and the issue is not parked.
- [ ] The branch starts from main, and the base of the pull request is main.
- [ ] The change does what the issue and the brief asked, and nothing more.
- [ ] The change obeys each choice in the brief.
- [ ] There are tests for the cases in the brief.
- [ ] The targeted local tests pass, and the counts agree with the report of the worker. Full Linux suites run in GitHub Actions, not on the shared build machine.
- [ ] There are no secrets, credentials, or machine-specific paths in the commits.
- [ ] The pull request can merge into main.

### B. After each fix push

- [ ] Each finding that the coordinator sent is fixed on the new head.
- [ ] The fix is for the root cause, not only for the reported line.
- [ ] The pull request body gives the neighboring cases, and each case has a test.
- [ ] The targeted tests pass locally. After the pull request is ready, the Linux suites in GitHub Actions on the current head must pass before Human Review.
- [ ] The coordinator resolves only the threads that it examined.

### C. Post-check, after the automated review is clean or at its limit

- [ ] All items in checklist A are still true.
- [ ] No P1 or P2 findings or threads are open.
- [ ] If the change touches timing, concurrency, or shared state, the related tests passed two times in sequence. Local test runs stay targeted and throttled.
- [ ] The change does not wait on another unmerged change. If it waits, move the card to Pending and stop here. There is one exception. When Human Review holds exactly one pull request and no independent pull request is ready, one stacked pull request can continue to the gate. It has a banner at the top of the body that names the Human Review pull request that it depends on.

### D. Gate into Human Review

- [ ] The pull request is independent of each pull request in Human Review. It merges cleanly onto main, it has no unmerged commits of another Human Review pull request, and it merges cleanly together with each of them. Or it is the one permitted stacked pull request: when it goes in, Human Review holds only its base, and the body starts with the stacked banner. After it is in Human Review, it can stay while its base is in Human Review, also when independent pull requests go in next to it. If none of this is true, move the card to Pending and stop here.
- [ ] If the pull request is stacked, its base is open in Human Review, or its base merged to main. If the human sent the base back or closed it, first reset the stacked pull request (see [Stacked pull requests](workflow.md#stacked-pull-requests)). Then stop here.
- [ ] If a vN tip is the head, the coordinator checked that tip against the current stack. The tip has no commits from a pull request that the human rejected (sent back, or closed without a merge). This is also true for a Pending pull request whose vN tip is built on a pull request that is not in Human Review now: make that tip again first. Checklist C and the staging checks below ran on that head. If the vN tip is old, keep the plain branch when it is clean on main.
- [ ] The pull request is not a draft.
- [ ] The pull request can merge into main.
- [ ] No P1 or P2 findings or threads are open.
- [ ] Checklist C passed on this head.
- [ ] The Linux checks in GitHub Actions are green on this exact head.
- [ ] The card is a pull request, not an issue.
- [ ] The staging deploy is best-effort. Merge the change into the staging branch and deploy staging again when you can. If you merge it, make sure that the staging merge did not remove lines of the change. Do not stop Human Review only because staging is not up to date.
- [ ] Staging can run the change, with the configuration, credentials, and services that it needs. If it cannot, do not use Pending. Change the pull request to a draft and move the card to Needs Input. Write a comment that names what is missing and who must supply it (the human, or the operator who owns the environment). When it is available, mark the pull request ready, check staging again, and do this checklist again. If the head changed, go back to In Progress.
- [ ] The pull request description tells where and how to see the change.
- [ ] Each change that a person can see, such as UI, rendered images, or video, has screenshots or frames in the pull request description. Existing screenshots count, also from an older head.

The automation that moves cards must check each item on this list.

If an item fails later, move the card back to In Progress and change the pull request to a draft.

### CI and staging setup

- Set up full Linux suites for pushes to pull requests that are ready for review, and for pushes to main. Do not run them for drafts. Cancel runs that a newer push replaces. Run Windows tests one time each week only.
- Install the shared two-slot throttle for local tests and headless browsers. Run only the test files that changed. For Vitest, use `--maxWorkers=1 --no-file-parallelism`.
- After a merge into the staging branch, check only the deployed commit, the site authentication, and a remote smoke test. Do not run full suites on the shared build machine.

## 7. Run more than one worker

- Start one worker for each brief. Each worker has its own checkout and session.
- Look at the load and memory of the build machine before you start more workers.
- Start each worker and each test command inside the cgroup slice with limits, automatically. Apply the limit to the command inside the terminal pane, not to the terminal client.
- Keep a registry of active and parked workers. For each worker, record the issue, branch, pull request, worktree, saved session, last pushed head, idle time, and the resume command.
- There is no fixed maximum number of workers. When resources are low, report the memory use and limit, swap, available memory, CPU use, and load.
- Only when memory is low, park workers that are clean, pushed all their work, and are idle at an empty prompt. Park the worker that is idle for the longest time first. When there are sufficient free resources, let workers continue. Resume saved sessions in their original worktrees, inside the limit. Resume them automatically when the pull request needs more work. See [working-agreements.md](working-agreements.md).
- When two changes touch the same files, start the second change only after the first merges. Or put the second change in Pending.
- Start each worker in the automatic-review mode of its agent. In that mode, a reviewer model approves routine actions, not a person. Use this mode together with the standing allow list below. Select a mode that reviews each action. Never select a mode that skips checks. Mode names change. Thus look at the current documentation of each agent. When this page was written, the modes were:
  - **Claude Code:** auto mode, `--permission-mode auto`.
  - **Codex CLI:** auto-review, `--sandbox workspace-write --ask-for-approval on-request` with `approvals_reviewer = "auto_review"`.
  - **Gemini CLI:** no reviewer mode. Start it with `--approval-mode auto_edit`, and write the allow list as allow rules in its policy settings.
  - **Another agent:** use its reviewer mode, if it has one. If it has no reviewer mode, start it with its allow list or policy settings. The short prompt check below finds the remaining prompts.

  Never start a worker in a mode that skips all checks. Examples are `--dangerously-skip-permissions` in Claude Code, `--yolo` in Codex, and the `yolo` approval mode in Gemini. The guardrails are the same in each mode: no pushes to main, to the staging branch, or to the branch of another worker. Nothing that destroys data, and nothing that touches secrets or credentials, without a question first. Write these rules as deny or ask rules in the agent settings. Then a reviewer model cannot approve them. Sometimes an agent cannot use its automatic mode, for example because the account or the model does not support it. Then it asks for permission at each prompt. The coordinator checks the mode when it starts each worker. It sets the mode if the agent started without it.
- Give each worker a standing allow list for the routine actions of its own change, for all agents: read-only commands, tests, dependency installs inside its own checkout, and commits and pushes to its own branch. Never allow pushes to main, to the staging branch, or to the branch of another worker. If a worker gets the same permission prompt on each change, the setup has a bug. Fix the allow list. Do not approve the prompt each time.
- Give each checkout its own dependency install, not a link into another checkout. Then, when you remove or install dependencies again, the change stays inside the directory of that worker.
- Look for workers that stopped at a permission prompt every 10 to 15 minutes. Do this separately from the slower stall scan. A prompt that waited for more than 10 minutes is a stall. The coordinator approves the prompt if the action stays inside the checkout and branch of the worker. If not, it asks the human.
