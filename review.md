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
- Do the tests exist, and do they pass when the coordinator runs them?
- Did the worker report pass counts?

The post-check repeats the pre-check on the current head and adds:

- Is every P1 and P2 finding fixed and its thread resolved?
- Does the pull request body list the neighboring cases for each fix?
- Is the pull request mergeable against main?

The coordinator runs the tests twice when a change touches timing, concurrency, or shared state.

## Round cap

Automated review is capped at a fixed number of rounds (ten works well). After the cap, workers still fix every finding the coordinator or the human raises, but the coordinator verifies those fixes itself and requests no more automated reviews. The cap stops a change from cycling indefinitely on findings of diminishing value.

A finding that arrives late, after a card has reached Human Review, still counts. The card returns to In Progress until it is fixed.

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

## The gate into human review

A card moves to Human Review only when all of these hold on the current head. Check them in this order and record the result before moving the card:

- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft.
- It is mergeable against main. The gate trusts the forge's own mergeable state. If the forge reports conflicts with the pull request base, this check fails, even if a local merge-tree looks clean.
- No P1 or P2 findings or threads are open.
- The coordinator's post-check passed on this head.
- The Linux checks in GitHub Actions are green on this exact head.
- The change is deployed where the human will review it, and the deploy is verified. The change is merged into the staging branch and staging was redeployed. The commit staging is actually serving contains the pull request's current head. Staging is an integration branch, so that commit is usually a merge rather than the head itself. Record the commit staging is serving. The staged environment must also be able to run the change, with any configuration, credentials or services it needs. If staging can't run it, the card goes to Pending with a question for the human, not to Human Review.
- A staging merge is also checked for dropped changes. It is not enough that the served commit is a descendant of the pull request head. The pull request's own changes must actually be present in the tree that staging serves.
- The pull request description says where and how to see the change.
- Any change a person can see, such as UI, rendered images or generated video, has current screenshots or frames from staging embedded in the pull request description. Generated media includes a side-by-side with its reference when there is one. If there's any doubt about whether a change is visible, treat it as visible.

Whatever automation moves cards has to check every condition on this list. A condition that's written down but not checked isn't part of the gate.

If any condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

When automated review comes back clean on the current head, the coordinator starts the post-check, the staging merge, the staging deploy, the screenshots, and the gate check at once, even if CI on that head is still running. CI can finish in parallel. The card still cannot enter Human Review until the Linux checks on that head are green.

When CI completes for a pull request head that is in Auto Review or Pending, a webhook event re-runs the gate. This is event-driven, not a timer.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.

The human reviewer's attention is the constraint of the whole system. The reviewer must never wait for work. Human Review must never be empty while work is in progress.

### Two slots and one ready-next pull request

1. Human Review holds exactly two pull requests. Plan for the happy path, where the reviewer merges both.
2. Pending is a queue sorted by conflict count. Pull requests that conflict with nothing (main, the Human Review pull requests, and each other) come first. Fully independent pull requests wait in Pending with no rebase.
3. A merge pulls the next pull request at once. When the reviewer merges a Human Review pull request, it leaves Human Review. The head of the Pending queue enters immediately, so Human Review holds two again. The reviewer moves on to the other Human Review pull request at once.
4. The ready-next invariant. While Human Review holds two pull requests and any work is in progress, at least one pull request is fully gated and can enter Human Review once both merge. "Fully gated" means: clean automated review, the second-reviewer pass, green CI, deployed to staging, and screenshots, all on the exact head that will enter. Prefer a pull request that has no conflicts. Only when none exists, speculatively rebase one pull request onto main plus both Human Review pull requests (a `-vN` branch) and gate it there. Do only one speculative rebase at a time.
5. A rejection rebuilds the speculative tip. If the reviewer rejects a Human Review pull request, rebuild the speculative tip without the rejected pull request (start from its `-v0` plain branch), while the reviewer reviews the other pull request.
6. Events drive the flow, not timers. A clean automated review and a CI-completion event each run the next gate step at once, even when CI is still running at review time. The gate uses the forge's own mergeable state. A staging merge is checked so that it does not silently drop a pull request's changes.
7. The reviewer always knows the state. When Human Review becomes empty, the swarm manager tells the reviewer at once that it noticed, and names the next pull request and its ETA.

`flow-status` reports whether the invariant holds (OK or VIOLATED) and shows the sorted queue. `pending-promote` keeps Human Review at two pull requests and keeps one pull request ready next.
