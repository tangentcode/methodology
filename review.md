# Review

## Layers

A change goes through four reviews, in this sequence:

1. **Coordinator pre-check**, before the first automated review.
2. **Automated review**, for a maximum number of rounds.
3. **Coordinator post-check**, after the automated review is clean and before the merge to staging.
4. **Human review**, after the change runs on staging and the pull request shows it.

The checks of the coordinator find problems that the automated reviewer does not look for. Examples: a change that does more or less than the issue asked, a missing test, an instruction in the brief that the worker did not obey, or a change to files outside its scope.

## Coordinator checks

The pre-check asks these questions:

- Does the change agree with the issue and the brief, and do nothing more?
- Does the branch start from main, and is the base main?
- Do tests cover the change? Do the targeted local tests pass? Also look at the CI results for the current head, if they are available. Drafts do not run full suites.
- Did the worker report the number of tests that pass?

The post-check does the pre-check again on the current head. It also asks:

- Is each P1 and P2 finding fixed, and is its thread resolved?
- Does the pull request body give the neighboring cases for each fix?
- Can the pull request merge into main?

When a change touches timing, concurrency, or shared state, the coordinator makes sure that the related tests passed two times. Local test runs stay targeted and throttled. Full suites run in GitHub Actions.

## Tests and CI

The maintainer set this policy on 2026-11-07. Before that, on the same day, pull request CI was off to decrease the Actions costs, and full suites ran on the shared build machine. Those suites used all the memory, and the machine had to restart.

- Full suites run in GitHub Actions on Linux. They run for each push to a pull request that is ready for review, and for each push to main. They do not run for drafts. When you mark a pull request as ready, validation also starts. A newer push cancels the older run for that pull request or branch.
- Windows tests run one time each week only. They do not run for pull request pushes or for manual starts.
- Workers run locally only the targeted test files that they changed. Use one test worker process. For example, with Vitest: `--maxWorkers=1 --no-file-parallelism`. Broad validation runs in Actions.
- All local test runs and headless browser runs use the shared slot throttle. The throttle lets two runs operate at the same time across all workers. Each run also stays inside the worker resource limit in [working-agreements.md](working-agreements.md).
- After a merge into the staging branch, the shared build machine runs only quick staging smoke checks. It makes sure of the deployed commit and the site authentication, and it runs a remote smoke test. It never runs full suites.
- The Human Review gate needs green Linux checks on the current head of the pull request. The results of an older head do not count.

## Round limit

Automated review has a maximum number of rounds. Ten rounds is a good limit. After the limit, workers continue to fix each finding from the coordinator or the human. But the coordinator makes sure of those fixes itself and does not request more automated reviews. The limit stops a change from going around the loop forever on findings of less and less value.

A finding that arrives late, after a card is in Human Review, also counts. The card goes back to In Progress until the fix is done.

Each review request has a time limit of 30 minutes. The coordinator records when it asked, and for which head. An acknowledgement, such as a reaction, is not a review. If no review of that head arrives in time, the coordinator asks one more time. If the second request also passes its time limit, the coordinator marks the pull request as timed out. It counts the round as used, tells the human in its next report, and starts its post-check.

## The root-cause rule

Use the same procedure for each finding, from all reviewers:

1. Find the root cause, not only the line that the reviewer shows.
2. Write a list of the neighboring cases of the same class. For example, if one input path does not validate, examine each input path.
3. Fix the root cause, so that the fix covers all the cases.
4. Add a test for each case.
5. Give the cases in the pull request body and in the report to the coordinator.

The coordinator puts this rule in each message that sends a finding. If a second round finds one more case of the same class, the first fix did not find the root cause. Then the worker must tell what the real cause was.

## Threads

Workers do not resolve review threads. The coordinator resolves a thread after it checks the fix on the current head. Thus only one party says that a finding is closed.

## Act on a clean review

A clean review is also an event. The latest automated review of the current head can be clean, with no open P1 or P2 threads. Then the automation of the coordinator immediately starts the next step: the post-check, the staging merge, and the gate. It does not wait for the worker, because the worker is usually already finished. The periodic scan counts a clean review with no post-check after it as a stall.

## The gate into Human Review

Human Review holds exactly two pull requests. One of them can be a stacked pull request (see [Stacked pull requests](workflow.md#stacked-pull-requests)). A card moves to Human Review only when all these conditions are true on the current head. Check them in this sequence. Record the result before you move the card.

- The pull request is independent of each pull request in Human Review. Or it is the one permitted stacked pull request, and its body starts with the stacked banner. A stacked pull request can go in only when its base is the only pull request in Human Review. After it is in, it can stay while its base is in Human Review, also when independent pull requests go in next to it. If the pull request is not independent and not the permitted stacked pull request, the card goes to Pending.
- If the pull request is stacked, its base is open in Human Review, or its base merged to main. A stacked pull request fails the gate when the human sent its base back or closed it. This is also true when the stacked pull request is already in Human Review.
- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft.
- The pull request can merge into main. The gate uses the mergeable state that the forge reports. If the forge reports conflicts with the base of the pull request, this check fails. This is also true when a local merge-tree test shows no conflicts.
- No P1 or P2 findings or threads are open.
- The post-check of the coordinator passed on this head.
- The Linux checks in GitHub Actions are green on this exact head.
- The staging deploy is best-effort. Merge the change into the staging branch and deploy staging again when you can. Do not stop Human Review when the body does not name the served commit, when a check of the served tree for removed lines would fail, or when staging is not up to date after a merge from main or from the staging branch. After such a merge, a clean merge and a quick unit-test run of the test files that the pull request touched are sufficient.
- The pull request description tells where and how to see the change.
- Each change that a person can see, such as UI, rendered images, or generated video, has screenshots or frames in the pull request description. Existing screenshots count, also when they are from an older head. Do not take them again after a merge from main or from the staging branch. Generated media includes a side-by-side view with its reference, if there is a reference. If you are not sure whether a person can see a change, think that a person can see it.

The automation that moves cards must check each condition on this list. A condition that is written but not checked is not part of the gate.

### Checks that do not finish

A wait for a required check is not progress. A check is a stall when it did not start or did not finish in its usual run time plus a margin.

- On each scan, the coordinator looks at checks that wait in the queue and checks that run, not only failed checks. It records how long each one waited.
- When a required check is stuck, the coordinator starts a new run of the same check on the same head. It uses a manual run or the event that starts the check. It records that the old run was stuck.
- The gate reads only the newest run of each check on the current head. An older run that did not finish must not stop a newer run that passed. An older run that failed counts until a newer run passes.
- If a new run also does not start, the CI service is down. Tell the operator. Tell which cards wait on it.

If a condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

When the automated review of the current head is clean, the coordinator immediately starts the post-check, a best-effort staging merge and deploy, and the gate check. It does this also when CI on that head still runs. CI can finish at the same time. Do not take the screenshots again. Screenshots that are already in the pull request count. But the card cannot go into Human Review until the Linux checks on that head are green.

When CI finishes for a pull request head that is in Auto Review or Pending, a webhook event runs the gate again. An event starts this, not a timer.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.

A comment from the human on a pull request in Human Review, or on a card in Needs Input, does not move the card. The human can come back later and add more comments. Only a column move by the human starts the next step of the workflow:

- Human Review to In Progress means that the human rejected the change. The coordinator sends the comments to the worker.
- Needs Input to In Progress means that the human answered the questions. The coordinator sends the answers, and the worker continues the work.

Automation must act directly on these column-move events.

The attention of the human reviewer is the limit of the full system. The reviewer must never wait for work. Human Review must never be empty while work continues.

### Two slots and one ready-next pull request

1. Human Review holds exactly two pull requests. Plan for the best result, where the reviewer merges the two. When Human Review holds exactly one pull request and no independent pull request is ready, one stacked pull request can go in. It has a banner at the top of the body that names the Human Review pull request that it depends on. If that base merges first, remove the banner. Then the pull request is a plain pull request.
2. Pending is a queue sorted by conflict count. Pull requests that have no conflicts (with main, with the Human Review pull requests, and with each other) are first. Fully independent pull requests wait in Pending without a rebase.
3. A merge immediately pulls the next pull request. When the reviewer merges a Human Review pull request, it goes out of Human Review. The first pull request in the Pending queue goes in immediately. Then Human Review holds two again. The pull request that goes in must have no unmerged change other than its own changes. The only exception is the other Human Review pull request, when the new pull request is the one stacked pull request with a banner in item 1. A speculative tip that has a change that is not merged and not in Human Review stays in Pending until that change merges. The reviewer immediately starts on the other Human Review pull request.
4. The ready-next rule. While Human Review holds two pull requests and work continues, at least one pull request is fully gated. It can go into Human Review when the two merge. "Fully gated" means: a clean automated review, the pass of the second reviewer, and green CI on the exact head that will go in. It also needs screenshots in the pull request (existing screenshots count, also from an older head) and a best-effort staging deploy. Select a pull request with no conflicts. Only when there is no such pull request, rebase one pull request onto main and the two Human Review pull requests (a `-vN` branch), and gate it there. Do only one speculative rebase at a time.
5. A rejection makes a new speculative tip. If the reviewer rejects a Human Review pull request, make the speculative tip again without the rejected pull request. Start from its plain `-v0` branch. Do this while the reviewer reviews the other pull request. The other Human Review pull request can be the stacked pull request with a banner from item 1. Then it contains the rejected change, and a merge of it would also merge that change. Remove it from Human Review immediately: move it back to Pending, make it again from its plain branch without the rejected change, and gate it again before it can go back. Tell the reviewer that you removed it, and why.
6. Events move the work, not timers. A clean automated review and a CI-finished event each immediately start the next gate step, also when CI still runs at review time. The gate uses the mergeable state that the forge reports. Check each staging merge, so that it does not remove the changes of a pull request without a report.
7. The reviewer always knows the state. When Human Review becomes empty, the swarm manager immediately tells the reviewer. It gives the next pull request and the time when it will be ready.

The swarm tools include a status command and a promote command. The status command reports whether the ready-next rule is true (OK or VIOLATED) and shows the sorted queue. The promote command keeps two pull requests in Human Review and keeps one pull request ready next.
