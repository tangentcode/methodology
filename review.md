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

A clean review is also an event. The latest automated review of the current head can be clean, with no open P1 or P2 threads. Then the automation of the coordinator immediately starts the post-check. If the post-check passes, the pull request moves to Ready. The coordinator does not start a staging merge or a gate at this point. See [The pull into Staging](#the-pull-into-staging). It does not wait for the worker, because the worker is usually already finished. The periodic scan counts a clean review with no post-check after it as a stall.

## The gate into Human Review

The coordinator runs this gate when it pulls a pull request into Staging, not when it later moves the card from Staging to Human Review. That later move is only a card move, and it happens when a Human Review slot is open. Human Review holds exactly two pull requests whenever two prepared pull requests are available, and never more than two. One of them can be a stacked pull request (see [Stacked pull requests](workflow.md#stacked-pull-requests)). A card enters Staging only when all these conditions are true on the current head. Check them in this sequence. Record the result before you move the card.

- The pull request merges cleanly onto the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it. Or it is prepared as the one speculative rebase when no pull request in Ready fits that stack. If it is a stacked pull request, its body starts with the stacked banner. If the pull request conflicts with a Human Review pull request, do not put it in Staging. Prefer the next pull request in Ready that does not conflict.
- If the pull request is stacked, its base is open in Human Review or in Staging, or its base merged to main. A stacked pull request fails the gate when the human sent its base back or closed it. This is also true when the stacked pull request is already in Human Review or already in Staging.
- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft.
- The pull request can merge into main. The gate uses the mergeable state that the forge reports. If the forge reports conflicts with the base of the pull request, this check fails. This is also true when a local merge-tree test shows no conflicts.
- No P1 or P2 findings or threads are open.
- The post-check of the coordinator passed on this head.
- The Linux checks in GitHub Actions are green on this exact head.
- The change is merged into the staging branch and deployed. Staging is verified to serve the correct commit. A merge into the staging branch must not remove lines of the change. A pull request does not enter Staging until this is true.
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

When the automated review of the current head is clean, the coordinator immediately starts the post-check. If the post-check passes, the pull request moves to Ready. Do not start a staging merge or a gate until the pull step takes this pull request. Do not take the screenshots again. Screenshots that are already in the pull request count. The pull request cannot enter Staging until the Linux checks on that head are green.

A webhook event does not run the gate for a draft pull request, or for a pull request that is in Ready and has not been pulled. The hook makes those checks before it makes any API call. It also ignores repeated CI events for the same head. If a CI event is for the pull request that is currently in the pull step, the event can continue that step when the lock is free. If the lock is busy, the event reports `busy` and does not wait.

## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.

A comment from the human on a pull request in Human Review, or on a card in Needs Input, does not move the card. The human can come back later and add more comments. Only a column move by the human starts the next step of the workflow:

- Human Review to In Progress means that the human rejected the change. The coordinator sends the comments to the worker.
- Needs Input to In Progress means that the human answered the questions. The coordinator sends the answers, and the worker continues the work.

Automation must act directly on these column-move events.

The attention of the human reviewer is the limit of the full system. The reviewer must never wait for work. Human Review must never be empty while work continues.

### Just-in-time Human Review flow

This rule, from 2026-11-13, replaces the 2026-11-12 two-slot and ready-next rules where they differ. Use lean, just-in-time thinking. The top priority is always to refill Human Review when an item leaves it. The human must be able to review one pull request after another, with no wait for the next card.

#### Columns and limits

1. Human Review holds exactly two pull requests whenever two prepared pull requests are available, and never more than two.
   - The human reviews one pull request. Then the human moves it to Done, when it is approved and merged, or back to In Progress, when it is rejected.
   - That move is the signal that only one pull request is left. The next pull request must enter in seconds, not minutes.
   - While the human reviews the remaining pull request, a new one goes in behind it.
   - When Human Review holds exactly one pull request, and the first Staging pull request depends on it, that Staging pull request can go in as the one stacked pull request. It has a banner at the top of the body that names the Human Review pull request that it depends on. See [Stacked pull requests](workflow.md#stacked-pull-requests). If that base merges first, remove the banner. Then the pull request is a plain pull request.
2. Staging is a buffer of 3 to 5 pull requests. This column was formerly named Pending. Keep it small. It must be large enough that the human can review 4 or 5 items while the next pull request is prepared, even if about 3 pull requests in Ready fail the gate in a row. Only Staging and Human Review are merged into the staging branch and deployed to the staging environment, about 7 pull requests in total. When a pull request enters Staging, its merge into the staging branch is the dry run for its merge into main. Do these merges in order, one at a time.
   - Each Staging pull request is fully prepared:
     - It is merged into the staging branch.
     - It is deployed to the staging environment, and that environment is verified to serve it.
     - The Linux checks are green on the current head.
     - The pull request body has screenshots, when a person can see the change, and a section that tells where to see it.
     - All conditions of the gate pass.
   - Each Staging pull request is pre-merged as a speculative stack. It sits on top of main, plus the Human Review pull requests that we expect the human to merge, plus the Staging pull requests ahead of it. Because of this, it has no merge conflicts to fix later.
   - The pre-merge and the gate checks happen only for a pull request that is being pulled into Staging, and only one at a time.
   - Moving the first Staging pull request to Human Review is only a card move, so it is almost instant.
3. Ready is a board column between Needs Input and Staging. It holds finished pull requests that wait to be pulled into Staging. Ready is the finish line for coding agents. Agents work the backlog until their pull requests are in Ready.
   - A pull request in Ready is finished. Its worker is done, the automated review is clean, and the post-check of the coordinator passed on the head commit.
   - A pull request in Ready is not merged into the staging branch, not deployed, not gated, and not on the staging environment.
   - Pull requests in Ready wait in this order:
     1. Pull requests with a milestone first, ordered by the milestone.
     2. Then the pull requests with the fewest conflicts with the current stack.
     3. Then the oldest pull requests.
4. In Progress and Auto Review do not change. Workers build, and the automated reviewer reviews, in parallel. Only the merge, deploy, and gate step is serial.

#### The pull into Staging

Only one process can merge into the staging branch, deploy staging again, run the gate, or promote a pull request from Staging at a time. This applies to every caller, including the event hook, the periodic scan, and helper agents.

These operations share one lock. If a second operation starts while the lock is held, that second operation does not wait. It stops at once and reports `busy`. It tries again later, on the next event or the next periodic scan.

The pull step starts when Staging has fewer pull requests than its target size, for example because one pull request just moved to Human Review. The single worker then takes the first pull request in Ready and does these steps:

1. If necessary, merge main into the pull request. Its worker makes any code fixes.
2. Merge the pull request into the staging branch, on top of the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it.
3. Deploy staging again.
4. Verify that staging serves the correct commit, that the Linux checks are green, and that the pull request body is complete.
5. Run the gate.
   - If the gate passes, the pull request goes to Staging.
   - If the gate fails, restore the staging branch to the last admitted stack: the Human Review pull requests and the Staging pull requests only. Deploy that stack again. Then move the failed pull request back to In Progress with the reason, and try the next pull request in Ready. Do not leave a failed candidate on the staging branch, and do not merge the next candidate on top of it.

Expect one or two failures before a pull request fits. That is why the buffer exists.

When Human Review drops to 1, because the human moved one out, move the first Staging pull request to Human Review at once. This promotion takes the shared lock. If the lock is busy, the promotion stops at once, reports `busy`, and tries again later. Then start the pull step to refill Staging. If Human Review has an open slot and Staging still has pull requests, fill Human Review first, up to two.

Do not merge, deploy, or gate any pull request other than the one that is being pulled into Staging, except the follow-up evidence case in [Blocked work](workflow.md#blocked-work). Pull requests in Ready get no merges, gates, or checks after they move to Ready.

- Do not make speculative rebased copies of every pull request.
- Do not merge the whole queue again after every merge to main.
- The staging environment gets one pull request at a time, just before that pull request enters the Staging column.

Conflicts: only one pull request is prepared at a time, so prepare it against current main plus the two Human Review pull requests and the Staging pull requests ahead of it.

- If it conflicts with a Human Review pull request, prefer the next pull request in Ready that does not.
- Make a speculative rebase only if no pull request in Ready fits, and make only one at a time. If you do that rebase, use a `<branch>-vN` tip. Install that tip as the head before the pull request enters Staging, and run the tests, the post-check, and the gate on that head. Never move the branch of a card that is already in Staging or in Human Review.

If the human rejects a Human Review pull request, each Staging pull request that included the rejected work is not valid. Move those cards out of Staging, and make them again from their plain branches without the rejected work, one at a time, under the lock. If the other Human Review pull request contains the rejected work, move it out of Human Review first, in the same way. Tell the human that you removed it, and why.

Events move the work, not timers. A clean automated review moves the pull request to Ready, after the post-check passes. It does not start a merge, a deploy, or a gate. The pull step starts only when Staging is below its target size and the lock is free. The gate uses the mergeable state that the forge reports. Check each staging merge, so that it does not remove the changes of a pull request without a report.

The reviewer always knows the state. When Human Review becomes empty, the swarm manager immediately tells the reviewer. It gives the next pull request and the time when it will be ready.

The swarm tools include a status command and a promote command. The status command reports whether Human Review holds two pull requests, when two prepared pull requests are available, and whether Staging holds 3 to 5 fully prepared pull requests. The promote command moves the first Staging pull request into Human Review when a slot is open, then starts the pull step to refill Staging. The promote command also takes the shared lock. If the lock is busy, it stops at once and reports `busy`.

#### API budget

The event hook must make these checks before it makes any API call:

- Skip draft pull requests.
- Skip pull requests that are in Ready and have not been pulled.
- Ignore repeated CI events for the same head.

The hook uses the API quota of the bot app. It falls back to the human account only when the app quota fails.

#### Work in progress

New workers must not take memory or API quota away from the pull request that is closest to Human Review.
