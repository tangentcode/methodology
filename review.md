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

A clean review is also an event. The latest automated review of the current head can be clean, with no open P1 or P2 threads. Then the automation of the coordinator immediately starts the post-check. If the post-check passes, the pull request moves to Ready. A change that a person can see first goes through the preview check, and moves to Ready only when that check passes. See [Screenshots from a preview of the real app](#screenshots-from-a-preview-of-the-real-app). The coordinator does not start a staging merge or a gate at this point. See [The pull into Staging](#the-pull-into-staging). It does not wait for the worker, because the worker is usually already finished. The periodic scan counts a clean review with no post-check after it as a stall.

## Screenshots from a preview of the real app

This rule, from 2026-11-14, records the maintainer decision on [methodology #67](https://github.com/tangentcode/methodology/issues/67). Platform PR #476 reached Human Review with screenshots from a local Vite page that showed the component outside the app. The feature did not work in the real app.

The screenshots of a change that a person can see come from a staging-like preview of the real app. The swarm takes them, and checks that the feature works there, before the pull request enters Ready. Then the move from Staging to Human Review stays only a card move, with no wait.

- **The preview site.** Each app has a separate preview site. It runs the same build of the real app as the staging site of that app, and it mirrors the staging branch (`work`). It has its own data. It must not write to the staging database.
- **One pull request at a time.** The preview check runs in the background, upstream of Human Review, for one pull request at a time. It does not take the shared lock of the staging merge, so it never slows a pull into Staging or a promotion into Human Review.
- **The steps.** When a pull request that a person can see passes the automated review and the post-check, the swarm merges its head onto a copy of the staging branch. It deploys that copy to the preview site and confirms that the site serves it. It takes the screenshots there, and it checks that the feature works there. Then it resets the preview site back to the staging branch. The preview check never changes the staging branch, main, or the branch of the pull request.
- **The result.** If the check passes, the pull request moves to Ready, and the preview screenshots go into the pull request description for the human review. If the check fails, the card goes back to In Progress with the failed step and the last screenshot. Only pull requests that pass become Ready.
- **What does not count.** A screenshot of an isolated component page, such as a local Vite harness or a story page, is never review evidence. Local screenshots are fine during In Progress, to help the worker. They do not satisfy the gate.
- **Which head.** The preview runs on the head that enters Ready. A later merge from main or from the staging branch does not need new screenshots. A new code push sends the pull request back through the review, and then through the preview check again.
- **Until the preview site exists.** Until an app has its preview site and the swarm runs the preview check for it, the screenshots of a change in that app come from the staging site, when the pull step deploys the change. They must show the real app. An isolated component page still does not count.


## The gate into Human Review

The coordinator runs this full gate one time, when it pulls a pull request into Staging. It does not run the full gate again when it later moves the card from Staging to Human Review. That later move is a card move after a cheap check (see [Promotion from Staging](#promotion-from-staging)), and it happens as soon as a Human Review slot is open. Human Review holds exactly two pull requests whenever two prepared pull requests are available, and never more than two. One of them can be a stacked pull request (see [Stacked pull requests](workflow.md#stacked-pull-requests)). A card enters Staging only when all these conditions are true on the current head. Check them in this sequence. Record the result before you move the card.

- The pull request merges cleanly onto the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it. Or it is prepared as the one speculative rebase when no pull request in Ready fits that stack. If it is a stacked pull request, its body starts with the stacked banner. If the pull request conflicts with a Human Review pull request, do not put it in Staging. Prefer the next pull request in Ready that does not conflict.
- If the pull request is stacked, its base is open in Human Review or in Staging, or its base merged to main. A stacked pull request fails the gate when the human sent its base back or closed it. This is also true when the stacked pull request is already in Human Review or already in Staging.
- The card is a pull request. Issue cards never go in Human Review.
- The pull request is not a draft. A gate check does not start on a draft. See [The pull into Staging](#the-pull-into-staging).
- The pull request can merge into main. The gate uses the mergeable state that the forge reports. If the forge reports conflicts with the base of the pull request, this check fails. This is also true when a local merge-tree test shows no conflicts.
- No P1 or P2 findings or threads are open.
- The post-check of the coordinator passed on this head.
- A MinBot pass comment is present on this exact head. The gate does not use a `MinBot-passed` label. That label is retired.
- The Linux checks in GitHub Actions are green on this exact head.
- The change is merged into the staging branch and deployed. Staging is verified to serve the correct commit. A merge into the staging branch must not remove lines of the change. A pull request does not enter Staging until this is true.
- The pull request description tells where and how to see the change.
- Each change that a person can see, such as UI, rendered images, or generated video, has screenshots or frames in the pull request description. They come from the preview check of the real app, as [Screenshots from a preview of the real app](#screenshots-from-a-preview-of-the-real-app) tells. A screenshot of an isolated component page does not count. Existing screenshots count, also when they are from an older head. Do not take them again after a merge from main or from the staging branch. Generated media includes a side-by-side view with its reference, if there is a reference. If you are not sure whether a person can see a change, think that a person can see it.

The automation that moves cards must check each condition on this list. A condition that is written but not checked is not part of the gate.

### Checks that do not finish

A wait for a required check is not progress. A check is a stall when it did not start or did not finish in its usual run time plus a margin.

- On each scan, the coordinator looks at checks that wait in the queue and checks that run, not only failed checks. It records how long each one waited.
- When a required check is stuck, the coordinator starts a new run of the same check on the same head. It uses a manual run or the event that starts the check. It records that the old run was stuck.
- The gate reads only the newest run of each check on the current head. An older run that did not finish must not stop a newer run that passed. An older run that failed counts until a newer run passes.
- If a new run also does not start, the CI service is down. Tell the operator. Tell which cards wait on it.

If a condition fails later, for example after a new push or a late finding, the card goes back to In Progress.

When the automated review of the current head is clean, the coordinator immediately starts the post-check. If the post-check passes, the pull request moves to Ready. A change that a person can see first passes the preview check, which puts the screenshots in the pull request. Do not start a staging merge or a gate until the pull step takes this pull request. Do not take the screenshots again. Screenshots that are already in the pull request count. The pull request cannot enter Staging until the Linux checks on that head are green.

A webhook event does not run the gate for a draft pull request, or for a pull request that is in Ready and has not been pulled. The hook makes those checks before it makes any API call. It also ignores repeated CI events for the same head. If a CI event is for the pull request that is currently in the pull step, the event can continue that step. A CI event for a pull request that is already in Staging does not run the gate again. That pull request passed the gate on its head, and a new head sends the card back to In Progress. If the lock is busy, the event queues a rerun. The process that holds the lock drains that rerun before it exits.


## Human review

The human reviews the change on staging and in the pull request. Only the human merges to main and deploys to production.

A comment from the human on a pull request in Human Review, or on a card in Needs Input, does not move the card. The human can come back later and add more comments. Only a column move by the human starts the next step of the workflow:

- Human Review to In Progress means that the human rejected the change. The coordinator sends the comments to the worker.
- Needs Input to In Progress means that the human answered the questions. The coordinator sends the answers, and the worker continues the work.

Automation must act directly on these column-move events.

The attention of the human reviewer is the limit of the full system. The reviewer must never wait for work. Human Review must never be empty while work continues.

### Just-in-time Human Review flow

This rule, from 2026-11-13, replaces the 2026-11-12 two-slot and ready-next rules where they differ. Use lean, just-in-time thinking. The top priority is always to refill Human Review when an item leaves it. The human must be able to review one pull request after another, with no wait for the next card.

The rule from 2026-11-17 ([issue #64](https://github.com/tangentcode/methodology/issues/64)) makes the checks cheaper. The full checks run one time, at Staging entry. A promotion from Staging into Human Review uses only a cheap check. After a merge to main, the coordinator checks again only that each Staging pull request still merges. See [Promotion from Staging](#promotion-from-staging) and [After a merge to main](#after-a-merge-to-main).

#### Columns and limits

1. Human Review holds exactly two pull requests whenever two prepared pull requests are available, and never more than two.
   - The human reviews one pull request. Then the human moves it to Done, when it is approved and merged, or back to In Progress, when it is rejected.
   - That move is the signal that only one pull request is left. The next pull request must enter in seconds, not minutes.
   - While the human reviews the remaining pull request, a new one goes in behind it.
   - When Human Review holds exactly one pull request, and the first Staging pull request depends on it, that Staging pull request can go in as the one stacked pull request. It has a banner at the top of the body that names the Human Review pull request that it depends on. See [Stacked pull requests](workflow.md#stacked-pull-requests). If that base merges first, remove the banner. Then the pull request is a plain pull request.
2. Staging has no fixed cap. The goal is flow. This column was formerly named Pending. Any Ready pull request that merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may enter Staging. The tools cache a conflict map per head SHA. When Staging drops below a floor, the cascade pulls the next clean Ready pull request. The default floor is 2. We will compare a floor of 1 with a floor of 2 by how long pull requests take from Ready to Human Review. The expensive steps (the work merge, the redeploy, and the gate) happen only at pull time. Never rebase or rework a pull request just to fill Staging. Do not pre-merge Ready pull requests in bulk: that made every merge to main conflict with the speculative branches. Blocked pull requests can also sit in Staging, but they do not count toward the floor, and they do not stop a promotion or a pull step. A pull that is merged into the staging branch, but waits only for a worker, for example for its screenshots (condition 7a), is also blocked. It does not count toward the floor, so the cascade pulls the next clean Ready pull request See [Screenshot waits](#screenshot-waits). Only Staging and Human Review are merged into the staging branch and deployed to the staging environment. When a pull request enters Staging, its merge into the staging branch is the dry run for its merge into main. Do these merges in order, one at a time.
   - Each Staging pull request is fully prepared:
     - It is merged into the staging branch.
     - It is deployed to the staging environment, and that environment is verified to serve it.
     - The Linux checks are green on the current head.
     - The pull request body has the preview screenshots, when a person can see the change, and a section that tells where to see it.
     - All conditions of the gate pass.
   - A Staging pull request is merged into the staging branch when it is pulled, not as part of a bulk speculative stack.
   - The work merge, the redeploy, and the gate happen only at pull time, and only one pull at a time.
   - Moving the first Staging pull request to Human Review is a card move after the cheap check, so it is almost instant. It does not run the full gate again.
3. Ready is a board column between Needs Input and Staging. It is the buffer of finished pull requests. Finished work piles up here, because a merge is easier than a first implementation. Ready is also the finish line for a first-implementation coding agent. Agents work Active issues and the backlog until their pull requests are in Ready. See [Coding agent slots](#coding-agent-slots).
   - A pull request in Ready is finished. Its worker is done. The automated review of the current head is clean, or it is at the round limit or has timed out and the post-check of the coordinator has passed. No P1 or P2 findings are open. If a person can see the change, the preview check passed and its screenshots are in the pull request.
   - Thus Ready means two things on the exact head: the automated review is clean (or at its limit, as above), and a MinBot pass comment names that head. The post-check of the coordinator writes that comment. If a person can see the change, it also means a third thing: the preview check passed on that head. See [Screenshots from a preview of the real app](#screenshots-from-a-preview-of-the-real-app).
   - A pull request in Ready is not merged into the staging branch, not deployed, not gated, and not on the staging environment.
   - Pull requests in Ready wait in this order:
     1. The one active fast-track pull request, if it is in Ready. See [Fast track](#fast-track).
     2. Then pull requests with a milestone, ordered by the milestone.
     3. Then the pull requests with the fewest conflicts with the current stack.
     4. Then the oldest pull requests.
4. In Progress and Auto Review do not change. Workers build, and the automated reviewer reviews, in parallel. Only the merge, deploy, and gate step is serial.

#### Fast track

This rule, from 2026-11-13, records the maintainer decision on the fast-track proposal.

The highest priority is always to keep the flow full. Keep at least two pull requests in Human Review, when two prepared pull requests are available, and keep Staging at or above its floor, with finished pull requests piling up in Ready. Speed does not matter while the attention of the human is the constraint. Steady flow does.

Within that, high-priority tickets and a fast-track pull request fill a slot first. It may jump the queue at every step: launch, automated review, the coordinator check, the Ready queue, the pull into Staging, and the move from Staging into Human Review. Fast tracks are rare.

##### How to mark it

- The maintainer adds the `fast-track` label to the issue. The pull request inherits the label, as in [Milestones and labels](workflow.md#milestones-and-labels). The tools copy it when the pull request opens, and again when the issue is edited. A sweep backfills existing pull requests that are missing it.
- Only the maintainer adds or removes the label. Bots must not invent labels. They may copy this inherited label. They must not add a `MinBot-passed` or `swarm` label.
- Several tickets may carry the label at the same time. Only one of them runs through the fast track at a time. That ticket is the active fast-track ticket.
- The other labeled tickets wait. They start, one at a time, in the order in which they received the label. The next one becomes active when the current one enters Human Review, when the current one is canceled before it reaches Human Review, or when the maintainer removes the `fast-track` label from the current one.
- The tools remove the label when the pull request merges or is canceled. If that ticket was still the active one and it had not yet entered Human Review, the next labeled ticket becomes active.

##### What the active ticket gets

1. **Launch.** Its coding agent starts at once, before any backlog launch.
2. **Review.** The automated reviewer, the coordinator check, and the preview check take it first in their queues.
3. **Ready to Staging.** It goes to the head of the Ready queue. The next pull into Staging takes it first when Staging is below the floor. It may enter Staging when it merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request. Do not restack existing Staging pull requests just to put it first. A pull that is already running does not stop. The new pull waits for the shared lock, like every other operation.
4. **Staging to Human Review.** It takes the next free Human Review slot, ahead of the other Staging pull requests. It is promoted at once, with the same cheap check as every other pull request. It does not push a pull request out of Human Review. Human Review stays at exactly two.

##### What it may skip

Nothing. It must pass every step:

- The automated review
- The coordinator check
- CI
- The preview check, and its screenshots of the real app
- Merge into the integration branch and deploy to staging
- Screenshots and the "where to see it" section in the pull request body
- Every condition of the Human Review gate

If it fails a gate, it goes back to In Progress with its label still in place. When it is Ready again, it stays first in line if it is still the active fast-track ticket.

##### Visibility

The status output shows the fast-track card clearly, including how long it has been on fast track.

#### The pull into Staging

<a id="one-gate-or-merge-at-a-time"></a>

Only one process can merge into the staging branch, deploy staging again, run the gate, or promote a pull request from Staging at a time. This applies to every caller, including the event hook, the periodic scan, and helper agents.

These operations share one lock:

- A gate check (the conditions in [The gate into Human Review](#the-gate-into-human-review)), at Staging entry.
- A promotion of a pull request from Staging into Human Review, with its cheap check.
- A merge of a change into the staging branch.

The lock file is `~/.cache/swarm-serial.lock`. A caller that finds the lock busy queues a rerun. The process that holds the lock drains every queued rerun before it exits.

Gate operations skip draft pull requests and pull requests that are still in Ready and have not been pulled. Do not start a gate check or a promotion from Staging on a draft. Leave the card where it is.

This lock does not stop the human from a merge to main, or from a review of the cards in Human Review.

##### The just-in-time cascade

This rule, from 2026-11-14 6:32 PM ET, was updated at 6:44 PM ET and again at 7:16 PM ET on the same day. Staging has no fixed cap. The goal is flow.

One event that frees a slot, such as a pull request merged or rejected from Human Review, runs through the whole chain in one serial pass. The process holds the shared lock for the whole cascade. The same cascade runs on any event that frees a slot. The command is `~/bin/swarm-advance --cascade`.

In that one run:

1. When a Human Review slot opens, promote the first Staging pull request to Human Review at once. Use only the cheap check in [Promotion from Staging](#promotion-from-staging). The active fast-track pull request, or a high-priority pull request, goes first. If a pull request fails the cheap check, try the next one. Continue until Human Review is full or no Staging pull request passes.
2. While Staging is below the floor (default 2) and a clean Ready pull request is available, pull the next clean Ready pull request into Staging. Clean means it merges, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request. The tools cache that conflict map per head SHA. Take pull requests in the Ready order above: the active fast-track first, then milestone, then fewest conflicts, then oldest. The pull does the work merge, which refuses on a conflict or on conflict markers. Then it deploys staging again, confirms the served `.deploy-sha`, and runs `hr-gate --apply`. Those expensive steps happen only at pull time. If the work merge refuses, try the next clean pull request in Ready.
3. Any other Ready pull request that already merges cleanly in that same way may also enter Staging. There is no fixed cap. Never rebase or rework a pull request just to fill Staging.
4. The next new-work coding agent starts whenever fewer than 3 new-work agents are running and an Active issue has no pull request yet. It does not start only when Ready is short. See [Coding agent slots](#coding-agent-slots).

The pull step starts during that cascade, when Staging is below the floor and a clean Ready pull request is available. The single worker then takes the next clean pull request in Ready and does these steps:

1. If necessary, merge main into the pull request. Its worker makes any code fixes.
2. Merge the pull request into the staging branch, on top of the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it. Refuse this merge on a conflict or on conflict markers. If it refuses, try the next pull request in Ready.
3. Deploy staging again.
4. Verify that staging serves the correct commit. Confirm the served `.deploy-sha`. Also verify that the Linux checks are green and that the pull request body is complete.
5. Run the gate with `hr-gate --apply`.
   - If the gate passes, the pull request goes to Staging.
   - If the gate fails, restore the staging branch to the last admitted stack: the Human Review pull requests and the Staging pull requests only. Deploy that stack again. Then move the failed pull request back to In Progress with the reason, and try the next pull request in Ready. Do not leave a failed candidate on the staging branch, and do not merge the next candidate on top of it.
   - If the gate fails only on the screenshots (condition 7a), it is a wait, not a failure. Do not restore the stack. See [Screenshot waits](#screenshot-waits).

Do not pre-merge Ready pull requests in bulk. Every merge to main made those speculative branches conflict. We will compare a floor of 1 with a floor of 2 by how long pull requests take from Ready to Human Review.

When Human Review drops to 1, because the human moved one out, run the just-in-time cascade under the shared lock. First move the first Staging pull request that passes the cheap check to Human Review. Then, while Staging is below the floor and a clean Ready pull request is available, pull the next clean Ready pull request into Staging. Any other Ready pull request that already merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may also enter Staging. Never rebase or rework a pull request just to fill Staging. Start the next new-work coding agent if fewer than 3 new-work agents are running and an Active issue has no pull request yet. If the lock is busy, queue a rerun. The process that holds the lock drains that rerun before it exits. If Human Review has an open slot and Staging still has pull requests, fill Human Review first, up to two.

Do not merge, deploy, or gate a pull request that is still in Ready, except the follow-up evidence case in [Blocked work](workflow.md#blocked-work). Prepare only one Ready pull request at a time. Do not run the full gate again on a pull request that is already in Staging. A promotion uses the cheap check in [Promotion from Staging](#promotion-from-staging). A merge to main uses the merge check in [After a merge to main](#after-a-merge-to-main). If the head of a Staging pull request changes, the card goes back to In Progress.

- Do not pre-merge Ready pull requests in bulk, and do not make speculative rebased copies of every pull request.
- Do not merge the whole queue again after every merge to main.
- Never rebase or rework a pull request just to fill Staging.
- The expensive steps (the work merge, the redeploy, and the gate) happen only at pull time, when a clean Ready pull request enters Staging.

Conflicts: only one pull request is prepared at a time. Check it with `git merge-tree` against current main, the staging branch (`work`), and every Human Review and Staging pull request. Cache that conflict map per head SHA.

- If it conflicts, prefer the next clean pull request in Ready.
- Never rebase or rework a pull request just to fill Staging. If no Ready pull request merges cleanly, leave Staging below the floor until one does, rather than making a speculative `<branch>-vN` tip only to fill the column. Never move the branch of a card that is already in Staging or in Human Review.

If the human rejects a Human Review pull request, each Staging pull request that included the rejected work is not valid. Move those cards out of Staging, and make them again from their plain branches without the rejected work, one at a time, under the lock. If the other Human Review pull request contains the rejected work, move it out of Human Review first, in the same way. Tell the human that you removed it, and why.

Events move the work, not timers. A clean automated review moves the pull request to Ready, after the post-check passes. It does not start a merge, a deploy, or a gate. An event that frees a slot starts the just-in-time cascade. If the lock is busy, the event queues a rerun. The process that holds the lock drains that rerun before it exits. The gate uses the mergeable state that the forge reports. Check each staging merge, so that it does not remove the changes of a pull request without a report.

The reviewer always knows the state. When Human Review becomes empty, the swarm manager immediately tells the reviewer. It gives the next pull request and the time when it will be ready.

The swarm tools include a status command and a cascade command, `~/bin/swarm-advance --cascade`. The status command reports whether Human Review holds two pull requests, when two prepared pull requests are available, and whether Staging is at or above its floor (default 2). The cascade command takes the shared lock and runs the whole just-in-time cascade: it promotes the first Staging pull request into Human Review with the cheap check when a slot is open, pulls the next clean Ready pull request while Staging is below the floor, may also pull other Ready pull requests that already merge cleanly, and starts the next new-work coding agent when fewer than 3 new-work agents are running and an Active issue has no pull request yet. If the lock is busy, the command queues a rerun. The process that holds the lock drains that rerun before it exits.

##### Screenshot waits

This rule is from the incident of 2026-11-15 ([issue #82](https://github.com/tangentcode/methodology/issues/82)). Until an app has its preview site, the worker takes the screenshots of a change from staging, after the pull step deploys it. See [Screenshots from a preview of the real app](#screenshots-from-a-preview-of-the-real-app). Thus a gate that fails only on condition 7a (no screenshots) is a wait, not a failure:

- The pull stays on the staging branch, and the card stays in Ready. Do not restore the stack, and do not move the card to In Progress.
- The coordinator gives the screenshot job to the worker of the pull request. The worker edits only the body of the pull request.
- When the body has the screenshots, the gate runs again on the same head. If it passes, the pull request goes to Staging.
- The pull is blocked on a worker. It does not count toward the floor. Thus the cascade can pull the next clean Ready pull request on top of it.
- A new head ends the wait. The pull request goes back through the review.

A gate that fails on any other condition is a failure. Restore the stack, as the pull step says.

#### Promotion from Staging

This rule, from 2026-11-17, records the decision on [issue #64](https://github.com/tangentcode/methodology/issues/64). The full checks of [The gate into Human Review](#the-gate-into-human-review) run one time, when the pull request enters Staging. When a Human Review slot frees, the coordinator promotes the first Staging pull request at once. It does only a cheap check, not a full gate:

- The head is the same head that passed the gate at Staging entry.
- The pull request still merges cleanly with main and with each Human Review pull request. A local `git merge-tree` check is sufficient.
- No person commented on the pull request or reviewed it after the gate, except comments that the coordinator cleared. Comments and reviews from bots do not count.

The order is: the active fast-track pull request first, then a high-priority pull request, then the Staging order. A fast-track pull request does not push a pull request out of Human Review. The promotion takes the shared lock. It does not wait for a CI run, a redeploy, or a new read of the pull request body. Those checks passed at Staging entry, on the same head.

A pull request that fails the cheap check does not take the slot. The coordinator tries the next Staging pull request, and it continues until Human Review is full. For the pull request that failed:

- If its head changed, the card goes back to In Progress.
- If it conflicts with main, the card goes to In Progress with a merge-main relay. See [After a merge to main](#after-a-merge-to-main).
- If it conflicts only with a Human Review pull request, it waits in Staging. When that pull request merges, the merge check against main runs again.
- If a person commented after the gate, the card waits in Staging. The coordinator reads the comment and acts on it. If the comment asks for a change, the card goes back to In Progress. If the comment needs no change, for example an approval or a question that the coordinator answered, the coordinator clears it. It writes a clearance record on the pull request that names the head and the time of the last comment that it read. The cheap check then counts only person comments and reviews that are newer than that record. Clearing a comment does not run the full gate again, and the card can take the next free slot.

#### After a merge to main

This rule is also from 2026-11-17 ([issue #64](https://github.com/tangentcode/methodology/issues/64)). When main moves, the coordinator checks only one thing again for each Staging pull request: does it still merge cleanly with the new main? Use a local `git merge-tree` check, cached per main SHA and head SHA. Nothing else that a Staging pull request passed at entry depends on main. Do not run the full gate again on the Staging pull requests, and do not merge the queue again.

- A pull request that still merges cleanly stays in Staging. Do nothing to it. Send it no relay.
- A pull request that conflicts goes to In Progress. Send a merge-main relay to its worker only. The worker merges main into the branch, with a merge commit and not a rebase, and fixes the conflict. The new head then goes through the normal loop again, and the full gate runs again when it enters Staging.

#### API budget

The event hook must make these checks before it makes any API call:

- Skip draft pull requests.
- Skip pull requests that are in Ready and have not been pulled.
- Ignore repeated CI events for the same head.

The hook uses the API quota of the bot app. It falls back to the human account only when the app quota fails.

#### Coding agent slots

This rule, from 2026-11-14 8:43 PM ET, sets how coding agents start and stop.

Of the usual 5 to 8 running coding agents, 3 to 4 always do first implementations of Active issues, on independent branches. Do not stop those agents to free a slot. Finished pull requests pile up in Ready. Ready is the buffer, because a merge is easier than a first implementation.

The other 2 to 3 slots are reserved for revival of agents that must rework a change.

When a pull request reaches Ready, its coding agent is closed with `/exit`. Its tmux window, its saved session, its branch, and its worktree stay, so a reserved slot can start the agent again with feedback. Then the next Active issue starts, in a new-work slot.

The same applies to each idle agent (rule from 2026-11-15 4:40 AM ET). An agent whose pull request is in Auto Review, Needs Input, Ready, Staging, or Human Review, or that has no work, is closed with `/exit`. Close the agent, not the tmux window. Never kill the window or its processes for this. An exited agent does not take a slot and does not count toward the Claude cap. Resume it later in the same window with `claude --resume <session>` or `claude --continue`. See [Close idle agents with /exit](working-agreements.md#close-idle-agents-with-exit).

Staging pulls from Ready just in time. If the maintainer marks a pull request urgent, that pull request becomes the next Staging pull.

The next new-work coding agent starts whenever fewer than 3 new-work agents are running and an Active issue has no pull request yet. It does not start only when Ready is short.

Do not take a revival slot for new work. Do not stop a first-implementation agent to free a slot.

#### Work in progress

Keep 3 to 4 first-implementation agents running. Use the reserved slots for rework. New-work launches follow [Coding agent slots](#coding-agent-slots).
