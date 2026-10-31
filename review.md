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

## Acting on a clean review

A clean review is an event too. When the latest automated review of the current head is clean and no P1 or P2 threads are open, the coordinator's automation starts the next step right away: the post-check, the staging merge, and the gate. It doesn't wait for the worker, which has usually finished already. The periodic scan treats a clean review with no post-check after it as a stall.

## The gate into human review

A card moves to Human Review only when all of these hold on the current head. Check them in this order and record the result before moving the card:

- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft.
- It is mergeable against main.
- No P1 or P2 findings or threads are open.
- The coordinator's post-check passed on this head.
- The change is deployed where the human will review it, and the deploy is verified. The change is merged into the staging branch and staging was redeployed. The commit staging is actually serving contains the pull request's current head. Staging is an integration branch, so that commit is usually a merge rather than the head itself. Record the commit staging is serving. The staged environment must also be able to run the change, with any configuration, credentials or services it needs. If staging can't run it, the card goes to Pending with a question for the human, not to Human Review.
- The pull request description says where and how to see the change.
- Any change a person can see, such as UI, rendered images or generated video, has current screenshots or frames from staging embedded in the pull request description. Generated media includes a side-by-side with its reference when there is one. If there's any doubt about whether a change is visible, treat it as visible.

Whatever automation moves cards has to check every condition on this list. A condition that's written down but not checked isn't part of the gate.

If any condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.
