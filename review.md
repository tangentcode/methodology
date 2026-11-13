# Review

## Layers

A change passes through four reviews, in this order:

1. **Coordinator pre-check**, before the first automated review.
2. **Automated review**, for up to a fixed number of rounds.
3. **Coordinator post-check**, after automated review is clean, before merging to staging.
4. **Human review**, after the change runs on staging and the pull request shows it.

The coordinator's checks catch problems the automated reviewer doesn't look for: a change that does more or less than the issue asked, a missing test, a brief instruction that was ignored, or a change that touches files outside its scope.

## Coordinator checks

The pre-check asks:

- Does the change match the issue and brief, and nothing more?
- Is the branch cut from main and the base set to main?
- Do tests cover the change, and do the targeted local tests pass? Check any available current-head CI results too; drafts do not run full suites.
- Did the worker report pass counts?

The post-check repeats the pre-check on the current head and adds:

- Is every P1 and P2 finding fixed and its thread resolved?
- Does the pull request body list the neighboring cases for each fix?
- Is the pull request mergeable against main?

The coordinator verifies two passing runs of the relevant tests when a change touches timing, concurrency, or shared state. Local reruns remain targeted and throttled; full suites run in Actions.

## Testing and CI

The maintainer set this policy on 2026-11-07. Earlier that day, PR CI was disabled to save Actions costs and full suites moved to the shared build box. Those suites exhausted memory and forced a reboot.

- Full suites run in GitHub Actions on Linux for pushes to ready-for-review PRs and pushes to main. Skip drafts; marking a PR ready also starts validation. A newer push cancels the older run for that PR or branch.
- Windows testing runs weekly only, not on PR pushes or manual dispatch.
- Workers run only the targeted test files they changed locally. Use one Vitest worker: `--maxWorkers=1 --no-file-parallelism`. Broad validation belongs in Actions.
- All local test and headless-browser runs use the shared slot throttle, which allows two runs at once across workers. Each run also stays inside the worker resource cap described in [working-agreements.md](working-agreements.md).
- After staging (`work`) branch merges, the shared build box runs only quick staging smoke checks: verify the deployed commit, site authentication, and a remote smoke test. It never runs full suites.
- The Human Review gate requires green Linux checks on the current PR head. An older head's results do not count.

## Round cap

Automated review is capped at a fixed number of rounds (ten works well). After the cap, workers still fix every finding the coordinator or the human raises, but the coordinator verifies those fixes itself and requests no more automated reviews. The cap stops a change from cycling indefinitely on findings of diminishing value.

A finding that arrives late, after a card has reached Human Review, still counts. The card returns to In Progress until it is fixed.

Every review request has a deadline of 30 minutes. The coordinator records when it asked and which head it asked about. An acknowledgement, such as a reaction, doesn't count as a review. If no review of that head arrives in time, the coordinator asks once more. If the second request also passes its deadline, it marks the pull request as timed out, counts the round as used, says so in its next report to the human, and goes on to its post-check.

## The root-cause rule

Every finding, from any reviewer, is handled the same way:

1. Find the root cause, not only the line the reviewer pointed at.
2. List the neighboring cases of the same class. For example, if one input path skips validation, check every input path.
3. Fix the root cause so all the cases are covered.
4. Add a test for each case.
5. Name the cases in the pull request body and in the report to the coordinator.

The coordinator includes this rule in every message that relays a finding. If a second round turns up another case of the same class, the first fix missed the root cause, and the worker should say what the real cause was.

## Threads

Workers do not resolve review threads. The coordinator resolves a thread after it has checked the fix on the current head. This keeps one party responsible for saying a finding is closed.

## Acting on a clean review

A clean review is an event too. When the latest automated review of the current head is clean and no P1 or P2 threads are open, the coordinator's automation starts the next step right away: the post-check, the staging merge, and the gate. It doesn't wait for the worker, which has usually finished already. The periodic scan treats a clean review with no post-check after it as a stall.

## The gate into human review

Human Review holds exactly two pull requests. One of them may be a stacked pull request (see [Stacked pull requests](workflow.md#stacked-pull-requests)). A card moves to Human Review only when all of these hold on the current head. Check them in this order and record the result before moving the card:

- The pull request is independent of every pull request in Human Review. Or it is the one permitted stacked pull request, and its body starts with the stacked banner. To enter, its base must be the only pull request in Human Review. After it entered, it stays eligible while its base is in Human Review, even when independent pull requests enter next to it. If neither is true, the card goes to Pending instead.
- If the pull request is stacked, its base is still open in Human Review, or it merged to main. A stacked pull request whose base was sent back or closed fails the gate, even if it is already in Human Review.
- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft.
- It is mergeable against main. The gate trusts the forge's own mergeable state. If the forge reports conflicts with the pull request base, this check fails, even if a local merge-tree looks clean.
- No P1 or P2 findings or threads are open.
- The coordinator's post-check passed on this head.
- The Linux checks in GitHub Actions are green on this exact head.
- Staging deploy is best-effort. Merge the change into the staging branch and redeploy when you can, but do not block Human Review if the body does not name the served commit, if a served-tree check for dropped lines would fail, or if staging is still catching up after a merge from main or work. After such a merge, a clean merge plus a quick unit-test run of the pull request's touched test files is enough.
- The pull request description says where and how to see the change.
- Any change a person can see, such as UI, rendered images or generated video, has screenshots or frames embedded in the pull request description. Existing screenshots count, even if they were taken on an older head; do not retake them after a merge from main or work. Generated media includes a side-by-side with its reference when there is one. If there's any doubt about whether a change is visible, treat it as visible.

Whatever automation moves cards has to check every condition on this list. A condition that's written down but not checked isn't part of the gate.

### Checks that do not finish

Waiting for a required check is not progress. A check that has not started or finished within its usual run time, plus a margin, is a stall:

- The coordinator checks queued and running checks on every scan, not only failed ones. Note how long each one has waited.
- When a required check is stuck, the coordinator starts a new run of the same check on the same head, by a manual run or by the event that starts the check. It records that the old run was stuck.
- The gate reads only the newest run of each check on the current head. An older run that never finished must not block a newer run that passed. An older run that failed still counts until a newer run passes.
- If a new run does not start either, the CI service is down. Tell the operator, and say which cards wait on it.

If any condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

When automated review comes back clean on the current head, the coordinator starts the post-check, a best-effort staging merge and deploy, and the gate check at once, even if CI on that head is still running. CI can finish in parallel. Do not retake screenshots; existing shots already in the pull request count. The card still cannot enter Human Review until the Linux checks on that head are green.

When CI completes for a pull request head that is in Auto Review or Pending, a webhook event re-runs the gate. This is event-driven, not a timer.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.

A human comment on a pull request in Human Review, or on a card in Needs Input, does not move the card. The human may come back later and add more comments. Only an explicit column move by the human starts the next workflow step. Human Review to In Progress means the human rejected the change: the coordinator relays the comments to the worker. Needs Input to In Progress means the human answered the questions: the coordinator relays the answers and the worker continues the work. Automation must react to these column-move events directly.

The human reviewer's attention is the constraint of the whole system. The reviewer must never wait for work. Human Review must never be empty while work is in progress.

### Two slots and one ready-next pull request

1. Human Review holds exactly two pull requests. Plan for the happy path, where the reviewer merges both. When Human Review holds exactly one pull request and no independent pull request is ready, one stacked pull request may enter, with a banner at the top of the body naming the Human Review pull request it depends on. If that base merges first, drop the banner and treat the pull request as plain.
2. Pending is a queue sorted by conflict count. Pull requests that conflict with nothing (main, the Human Review pull requests, and each other) come first. Fully independent pull requests wait in Pending with no rebase.
3. A merge pulls the next pull request at once. When the reviewer merges a Human Review pull request, it leaves Human Review. The head of the Pending queue enters immediately, so Human Review holds two again. The entering pull request may contain no unmerged change other than its own, except for the remaining Human Review pull request when it enters as the one bannered stacked pull request in item 1. A speculative tip that still contains a change that is not merged and is not in Human Review stays in Pending until that change merges. The reviewer moves on to the other Human Review pull request at once.
4. The ready-next invariant. While Human Review holds two pull requests and any work is in progress, at least one pull request is fully gated and can enter Human Review once both merge. "Fully gated" means: clean automated review, the second-reviewer pass, and green CI on the exact head that will enter, with screenshots present in the pull request (existing shots count even from an older head) and a best-effort staging deploy. Prefer a pull request that has no conflicts. Only when none exists, speculatively rebase one pull request onto main plus both Human Review pull requests (a `-vN` branch) and gate it there. Do only one speculative rebase at a time.
5. A rejection rebuilds the speculative tip. If the reviewer rejects a Human Review pull request, rebuild the speculative tip without the rejected pull request (start from its `-v0` plain branch), while the reviewer reviews the other pull request. If the other Human Review pull request is the bannered stacked pull request from item 1, it contains the rejected change, and merging it would merge that change too. Withdraw it from Human Review at once: move it back to Pending, rebuild it from its plain branch without the rejected change, and re-gate it before it can return. Tell the reviewer that it was withdrawn and why.
6. Events drive the flow, not timers. A clean automated review and a CI-completion event each run the next gate step at once, even when CI is still running at review time. The gate uses the forge's own mergeable state. A staging merge is checked so that it does not silently drop a pull request's changes.
7. The reviewer always knows the state. When Human Review becomes empty, the swarm manager tells the reviewer at once that it noticed, and names the next pull request and its ETA.

`flow-status` reports whether the invariant holds (OK or VIOLATED) and shows the sorted queue. `pending-promote` keeps Human Review at two pull requests and keeps one pull request ready next.
