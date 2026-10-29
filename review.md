# Review

## Layers

A change passes through four reviews, in this order:

1. **Coordinator pre-check**, before the first automated review.
2. **Automated review**, for up to a fixed number of rounds.
3. **Coordinator post-check**, after automated review is clean, before merging to staging.
4. **Human review**, after the change runs on staging.

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

A card moves to Human Review only when all of these hold on the current head:

- The pull request is not a draft.
- It is mergeable against main.
- No P1 or P2 findings or threads are open.
- The coordinator's post-check passed.
- The change is merged into the staging branch and staging is redeployed.
- A change with a visible UI difference has a staging screenshot attached.

If any condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.
