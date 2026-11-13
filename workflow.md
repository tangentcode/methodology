# Workflow

## Artifacts

- **Issue.** States one goal, the approach, and acceptance criteria. Work starts as an issue in Triage. The human decides what to build in a comment on that issue.
- **Brief.** The owner bot's instructions to one worker for one change: a whole issue, or a named part of one. See [briefs.md](briefs.md).
- **Pull request.** One per worker's change, branched from main and targeting main. It starts as a draft. An issue usually becomes one pull request, but a large issue can be split into several, each with its own worker and branch and each naming the part of the issue it covers. A partial pull request references the issue without a closing keyword, for example `Part of #N`. Only the pull request that completes the issue's acceptance criteria uses a closing keyword such as `Fixes #N`, so merging a partial change doesn't close the issue early.
- **Board.** One card per issue or pull request. The column says what happens next.
- **Staging branch.** An integration branch that collects changes for testing on the staging environment. It is never merged into main.

## Board columns

| Column | Meaning | Who moves the card in | Holds |
|---|---|---|---|
| Triage | New work waiting for the owner bot to propose options and the human to decide | Human, coordinator, or tracker | Issues only |
| Backlog | Issues that define scope and that no pull request has picked up yet | Owner bot, coordinator, or human | Issues only |
| Needs Input | The owner bot has questions for the human on the issue | Owner bot | Issues only |
| In Progress | A worker is writing or fixing code. The pull request is a draft | Coordinator | Pull requests only |
| Auto Review | Ready for review. The pull request is marked ready and the automated reviewer is running | Coordinator | Pull requests only |
| Pending | Otherwise ready, but blocked on another change or an outside decision | Coordinator | Pull requests only |
| Human Review | Passed the gate. Waiting on the human | Coordinator, through the gate | Pull requests only |
| Done | Merged to main | Human, or the board on merge | Pull requests |

Moving a card to Auto Review also means marking the pull request ready. Moving it back to In Progress means converting it to a draft.

### Issues and pull requests on the board

Every pull request card must have a Status. Set a new card to In Progress if the pull request is a draft or is still being pushed. Otherwise, set it to Auto Review and request a review. Never leave its Status blank.

An issue with no pull request lives only in Triage, Backlog, or Needs Input. Issues never sit in Auto Review, Pending, or Human Review.

Once a pull request links the issue on the host (`Fixes #N`, or `Part of #N` when one issue spans several pull requests), remove the issue card. The pull request card carries the work from then on. The link must actually appear on the host, not only in free text. Many open issues with no pull request is a failure: an agreed issue should promptly get a pull request.

```mermaid
flowchart LR
    T[Triage] -->|owner bot has questions| NI[Needs Input]
    T -->|brief written| B[Backlog]
    NI -->|human answers| T
    B -->|draft pull request opened, issue card removed| IP
    IP -->|coordinator pre-check passes| AR[Auto Review]
    AR -->|P1 or P2 finding| IP
    AR -->|blocked on another change| P[Pending]
    P -->|blocker cleared| AR
    AR -->|clean, post-check passes, deployed and verified on staging, screenshots in PR| HR[Human Review]
    HR -->|human requests changes| IP
    HR -->|late finding| IP
    HR -->|human merges to main| D[Done]
```

### Moving cards without losing a step

Entering Auto Review is one action: move the card, mark the pull request ready, request an automated review of the current head, and record the head that was sent for review. A card in Auto Review with no review request or review on its current head is a stall. A change that has reached the round cap doesn't go back to Auto Review. The coordinator verifies the new head itself (step 7) and goes on to its post-check.

When the automation holds off a step because the worker is still busy, it records the deferral, with the pull request, head and time. It rechecks within 15 minutes, and on every periodic scan after that, until the worker is idle or a newer push replaces the deferral. Then it does the deferred step on the current head. The periodic scan also looks at In Progress cards, not only Auto Review. An idle worker whose head is newer than its last review goes through the pre-check and into Auto Review. If the change has reached the round cap, it goes to the coordinator's own verification instead.

A push past the head the coordinator checked sends a Human Review card back to In Progress. The coordinator's post-check names the commit it checked, so a stale pass is easy to spot.

## Triage

New issues and gripes enter Triage. Each issue must include code context for the relevant component, explain why the problem happens, and give two to four numbered fix options with a recommendation. A symptom and expected behavior alone are not enough. The maintainer should be able to choose with one comment.

Work starts as an issue in Triage. The owner bot comments on the issue with options. The human decides in a comment; that comment is the instruction for what to build, and edits to it count too. The coordinator forwards the human's comment to the owner bot.

The owner bot then either:

1. Moves the card to Needs Input and posts its questions on the issue, or
2. Writes a brief and moves the card to Backlog. The coordinator launches a coding worker from that brief. The worker branches from main with the pull request base set to main.

Parked items stay parked until the human says otherwise. Product choices belong to the owner bot; the coordinator does not invent them.

## The loop

1. An issue lands in Triage. The owner bot proposes options. The human decides in a comment.
2. The owner bot writes a brief (or asks for clarification in Needs Input first). The coordinator starts a worker. The issue card stays in Backlog.
3. The worker cuts a branch from main, opens a draft pull request early, and pushes code with tests. Once the draft pull request exists, the coordinator removes the issue card and puts the pull request card in In Progress.
4. The coordinator runs its pre-review check (see [review.md](review.md)).
5. The coordinator marks the pull request ready, moves the card to Auto Review, and requests an automated review.
6. For each P1 or P2 finding, the coordinator converts the pull request to a draft, moves the card to In Progress, and relays the finding to the worker with the root-cause rule. The worker fixes and pushes. The coordinator verifies the fix, resolves the thread, and returns to step 5.
7. After the round cap, the worker still fixes findings, but the coordinator verifies them itself and requests no more automated reviews.
8. When no P1 or P2 findings remain, the coordinator runs its post-review check.
9. The coordinator merges the change into the staging branch, redeploys staging, and checks that the commit staging serves contains the current head and that staging can run the change.
10. For any change a person can see, current screenshots or frames from staging go into the pull request description. The description also says where and how to see the change.
11. The coordinator checks the full gate in [review.md](review.md). Only if it passes does the card move to Human Review.
12. The human reviews. He merges to main, or sends the change back with comments, which returns it to step 6.

### Pull requests that don't target main

The human may approve a change that targets another long-lived branch, such as a deploy-tooling branch. It follows the same loop and skips only the steps that can't apply. For a change that can't go to staging, the gate's deploy conditions are replaced by the check its pull request names, such as the tooling's own test suite, run and recorded on the current head. "Mergeable against main" becomes "mergeable against its base". A skipped step never means the loop stops. After a clean automated review, the coordinator still runs its post-check and the gate, and moves the card to Human Review.

Every pull request card gets a status in the same action that adds it to the board. The periodic scan picks up any open pull request whose card has no status, and any whose latest automated review of the current head is clean but has no coordinator post-check after it.

## Definition of ready

An issue is ready for a worker when:

- The human has decided what to build in a Triage comment (or otherwise approved the issue).
- It states the goal, the approach, and what is out of scope.
- It has acceptance criteria someone can check.
- The human's stated choices are written into it.
- It does not depend on unmerged work, or the dependency is named and the issue waits in Backlog until that work merges.

## Definition of done

A change is done when:

- The human has merged it to main.
- Its tests ran green on the final head, with pass counts reported.
- Every review finding is fixed at its root cause, with neighboring cases tested.
- It ran on a staging deploy that contained its final head, with screenshots or frames in the pull request if it changed anything a person can see.
- No review threads are open.

## Worker liveness

A card in In Progress must have a live worker that is doing the work. A shell window or a saved session is not a live worker.

- When a worker finishes, parks or exits, the same action moves its card. A finished draft goes through the pre-check, is marked ready and moves to Auto Review. A card that waits on a human decision moves to Pending: the coordinator adds the `needs-decision` label and names the open question as the blocker. A card that waits on another change also moves to Pending and names that change. An issue card with no pull request yet goes back to Backlog with the question in a comment.
- A worker that ends its turn with a question about the next step is not finished. The coordinator answers or routes the question in the same scan, and does not leave the card in In Progress.
- A resume that fails is a board event. The coordinator reads the resume result. If no worker started, the coordinator starts one or moves the card out of In Progress.
- Each scan compares In Progress cards with live workers. A card with no live worker, or with an idle worker and no new push, is a stall. The scan fixes it in that run.

## Blocked work

A change that is otherwise ready but waits on another change goes to Pending, not Auto Review or Human Review. Its pull request body names each blocker on its own line in a fixed form such as `Blocked by #N`, so automation can read it. Notes in a worker's session don't count. An issue that no pull request has picked up yet stays in Backlog even when it waits on other work, and it uses the same `Blocked by #N` lines in its body.

Each time a pull request merges, the coordinator's automation looks for Pending cards that list it or the issue it closes. When all of a card's blockers have merged, the coordinator rebases or merges main into the branch, moves the card out of Pending, tells the worker to resume, and continues the loop. When a Backlog issue's blockers have all merged, the coordinator reports that it is unblocked and ready for a worker. The periodic scan treats a Pending card whose blockers have all merged as a stall, not as a wait, and reports any Backlog issue whose blockers have all merged.

A block must point one way. Sometimes a change can't show its evidence on its own. For example, it adds code that nothing on screen uses yet, so the screenshot has to come from the follow-up change that uses it. Then the follow-up must not wait for the first change to merge, because the first change can't reach Human Review without that evidence. That is a circular wait, and both changes sit idle. Instead:

- The follow-up starts at once. Its branch is cut from main, with the first change's branch merged into it. Its pull request targets main and names the first change as its blocker.
- The follow-up's staging evidence goes into both pull request descriptions, so the first change can pass the gate.
- On each scan, the coordinator checks that every Pending card's blocker can move forward without that card. If the blocker can't, the coordinator breaks the cycle this way right away.

### Blocked on the staging environment

Sometimes a change is finished and reviewed, but staging itself is broken in a way the worker can't see into. For example, every file write returns a server error while reads and other requests work, and the worker can't read the server's logs. The worker can't take the required screenshots, so the change can't pass the gate.

- The worker stops, cleans up anything it created on staging, and ends its turn with a status line that says it's blocked on staging. The line names the symptom, the request that fails, and what the worker ruled out.
- The coordinator treats that line as a handoff, not as a finished turn. In the same pass, it sends the symptom to whoever operates staging (the operator role, or the human if no one else can read the server logs). The card moves to Pending, and the pull request body names the staging fault as the blocker.
- When the operator says the fault is fixed, the coordinator checks the failing request itself, then tells the worker to finish the screenshots. The card goes back into the loop at step 10.
- A scan that finds a worker blocked on staging, with no message to the operator yet, counts it as a stall.

A broken staging environment also blocks every other change that needs screenshots there. So the coordinator reports it once, names each change that is waiting on it, and resumes all of them when it's fixed.

## Deploy automation target

As of 2026-11-07, the target is to replace Actions SSH redeploy jobs with a signed GitHub push webhook. This is in progress, not a claim that the listener is live.

A small listener on the shared build box verifies `X-Hub-Signature-256` using a secret kept out of git. It accepts pushes to main and work, returns 202 immediately, and queues the existing redeploy targets under the host-wide redeploy lock. It logs each run. Main pushes redeploy production targets after the maintainer merges; work pushes redeploy staging targets. Bots still never merge to main or deploy production themselves.

This removes Actions minutes for redeploy jobs, not for testing. The rollout must document where to read deploy logs and how to redeliver a push, then verify a ping and a redelivered push against the served commit.
