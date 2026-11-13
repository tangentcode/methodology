# Tooling

This page describes the tools that run the workflow on the coordinator host. The rules for the loop and the Human Review gate live in [workflow.md](workflow.md) and [review.md](review.md). The text of the method lives in this repository. The tools live in the swarm tools repository. Local settings and credentials stay outside every public repository.

## Board states that the tools use

The tools run the loop and the gate in [workflow.md](workflow.md) and [review.md](review.md). They use these board columns:

- **Ready** is the board column between Needs Input and Staging. It is the finish line for coding agents. Each Ready pull request has a finished coding agent and no open P1 or P2 findings. The automated review of the current head is clean, or it is at the round limit or has timed out and the post-check of the coordinator has passed. A Ready pull request is not merged into the staging branch, not deployed, and not gated. It is not on the staging environment.
- **Staging** is the board column for the prepared buffer. This column was formerly named Pending. The option id did not change, so no card lost its status. Commands that say "Pending" in their names act on this column. Tools match columns by option id, not by name.
- **Human Review** holds exactly two pull requests whenever two prepared pull requests are available, and never more than two.

The just-in-time target for Staging is three to five prepared pull requests. That is enough for the human to review several items while the next pull request is prepared. A prepared pull request is gated, is not blocked on another change, and can go into Human Review as a card move. Finished work that still waits on a blocker can also sit in Staging, as in [Blocked work](workflow.md#blocked-work). Those blocked cards do not count toward the target. They do not stop a promotion or a pull step.

Only Staging and Human Review are merged into the staging branch and deployed to the staging environment, about 7 pull requests in total.

## What starts the tools

Three triggers start the tools: a GitHub event, a board-move event, and a periodic tick.

### GitHub events

An event hook on the coordinator host receives events from the forge. Those events include a pull request that opens or is marked ready, and a push to a pull request. They also include a review, a CI run that finishes, and a merge to main.

The hook starts the matching tool for that event. It does not start a full coordinator run for every event. Before it makes any API call, it skips draft pull requests. It also skips Ready pull requests that have not been pulled into Staging. It ignores repeated CI events for the same head. It uses a saved copy of the board when it can.

### The board-move trigger

A move of a project card is a signal. It can mean that Human Review dropped to one pull request, that the human rejected a change, or that a question was answered. The primary trigger is a webhook for project item events. That webhook runs the promote step at once, so a new pull request can enter Human Review in seconds. A slow poll every few minutes is only a backup, in case an event is missed.

### The periodic tick

A timer runs one pass of the tools on a regular interval. The tick is a safety net for lost events. It also does work that events do not cover. It reports stalls. It starts held launches when memory is free. It refills Staging when the prepared buffer is short. New launches must not take memory or API quota away from the pull request that is closest to Human Review.

On each pass, the tick reports the board status. If Human Review holds fewer than two pull requests, it promotes a prepared pull request from Staging. If the prepared buffer in Staging is below its target, it starts the pull step for one Ready pull request. If a pull request is eligible for Ready but is not yet in that column, the tick records the pass and moves the card to Ready.

The tick opens a draft pull request only when its worker can start, and it checks that the worker started. A draft with no live worker does not sit in In Progress.

## The pull step into Staging

Staging holds the prepared buffer and, separately, finished pull requests that still wait on a blocker. The just-in-time target is three to five prepared pull requests. Each prepared pull request is pre-merged as a stack on main, the Human Review pull requests, and the Staging pull requests ahead of it. It is already merged into the staging branch, deployed, verified, and gated. The tools make a speculative rebase only when no pull request in Ready fits that stack, and only one at a time. Human Review and Staging together are the only pull requests that are merged into the staging branch.

When the prepared buffer in Staging is below its target, one worker takes the first Ready pull request and prepares it. Ready pull requests wait in this order: milestone first, then fewest conflicts with the current stack, then oldest. This preparation is the pull step. Only one Ready pull request is prepared at a time.

1. Merge main into the pull request if that is needed. The coding agent of that pull request makes any code fixes.
2. Merge the pull request into the staging branch, on top of the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it.
3. Deploy the staging environment again, and verify the served commit. A pull request does not enter Staging until this is true. For a change that cannot go to the staging environment, the check that the pull request names replaces the deploy conditions. See [Pull requests that do not target main](workflow.md#pull-requests-that-do-not-target-main).
4. Confirm that CI is green on this head, and that the pull request body is complete.
5. Run the Human Review gate. If the gate passes, the card goes to Staging. If the gate fails because staging lacks configuration, credentials, or a required service, the tools change the pull request to a draft. They move the card to Needs Input. The comment names what is missing and who must supply it. For other gate failures, restore the staging branch to the last admitted stack and deploy that stack again. Then the card goes back to In Progress with the reason, and the worker tries the next Ready pull request.

When Human Review drops to one, the first prepared pull request in Staging moves to Human Review at once, through `hr-gate --apply`. That step is a card move. Then the pull step refills the prepared buffer. The tools prepare only one Ready pull request at a time. They can still run the gate again on a pull request that is already in Staging, including when CI finishes, when main advances, or when they promote the card. If that later check fails, the card leaves Staging, as the gate in [review.md](review.md#the-gate-into-human-review) requires.

## The global lock

Gate checks, promotions from Staging into Human Review, and merges into the staging branch share one global lock. Only one of these operations runs at a time. This is true for every caller: the event hook, the tick, and any helper agent. See [The pull into Staging](review.md#the-pull-into-staging).

The lock is non-blocking. If a second operation starts while the lock is held, that second operation does not wait. It stops at once and reports `busy`. It tries again on the next event or the next tick.

Gate operations skip draft pull requests and pull requests that are still in Ready and have not been pulled. The lock does not stop the human from a merge to main.

## API budget

The tools use the bot app token first, so they draw on the bot app's own API quota. They fall back to the human account only when the app quota fails. Each fallback is written to the log.

Comments that must come from a human still go out as the human account. The usual case is a review request. The automated reviewer ignores requests from the bot app.

If the API quota is exhausted, the tools read the reset time and wait for that time. They do not fail in the middle of a run.

## Board option ids

Tools match board columns by option id, not by name. A rename of a column does not change the id, so no card loses its status. Staging keeps the option id that Pending had. See [Board states that the tools use](#board-states-that-the-tools-use).

## The tools

### hr-gate

`hr-gate` checks the Human Review gate conditions on the current head of a pull request. The conditions are in [The gate into Human Review](review.md#the-gate-into-human-review). In apply mode it is the only path that may move a card into Human Review, or into Staging after a successful pull.

With no flag, it only checks and prints a table. `--apply N` takes the lock, checks pull request `N`, and moves the card when the conditions pass. `--sweep` checks, after a push to main, that open pull requests still merge. `--sweep --demote` also moves pull requests that no longer merge out of Human Review or Staging. `--apply` skips draft pull requests.

### pending-promote

`pending-promote` is the promote command and the pull step. The column it reads is Staging, also when a command name still says Pending.

With no flag, or with a dry-run flag, it only shows the plan. `--apply` takes the lock and does the work. If Human Review has an open slot, it moves the first prepared Staging card into Human Review, always through `hr-gate --apply`. If the prepared buffer in Staging is below its target, it runs the pull step for the next Ready pull request. If the human rejected a base pull request, it moves each stacked pull request back to In Progress. It also resets those branches.

### active-gate

`active-gate` checks the Active column. Each card there must be an open issue that is assigned to the swarm, that does not have the `work2` label, and that has exactly one open linked pull request in a flow column. In demote mode it moves failing cards, for example a closed issue to Done, or a `work2` issue back to Inbox. In promote mode it adds missing swarm issues that do have a pull request and that do not have the `work2` label.

### flow-status

`flow-status` does not change the board. It prints a report of the flow rules. The report says whether Human Review holds two pull requests, when two prepared pull requests are available, and whether the prepared buffer in Staging is inside its target of 3 to 5. The report ends in `OK` or `VIOLATED`.

### ci-last-check

`ci-last-check` asks whether every CI check on one commit has finished. It does not change anything. The event hook runs it when a CI event arrives, before it makes more API calls for that head.

### The bot app command-line tool

The bot app has a command-line tool, `minbot`. Actions that this tool writes show as the bot app, not as a person. It is a dry run unless `--apply` is given. It checks its identity before every write. Callers do not see the token.

The tool can comment, post evidence, and submit a review. It can add or remove a label, mark a pull request as a draft or as ready, and create an issue. It can list, reply to, or resolve review threads. It can also add a card to a board and set the status of a card. API reads can go through this tool so that they use the bot app quota.
