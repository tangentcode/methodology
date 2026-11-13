# Tooling

This page describes the tools that run the workflow on the coordinator host. The rules for the loop and the Human Review gate live in [workflow.md](workflow.md) and [review.md](review.md). The text of the method lives in this repository. The tools live in the swarm tools repository. Local settings and credentials stay outside every public repository.

## Board states that the tools use

The tools run the loop and the gate in [workflow.md](workflow.md) and [review.md](review.md). They use the published board columns, with one optional queue in front of Pending.

- **Ready** is an optional queue of finished pull requests. Each one has a finished coding agent, a clean automated review, and a bot pass on the current head. A Ready pull request is not yet merged into the integration branch, not yet deployed, and not yet gated. Ready may be a board column, or only an ordered list that the tools keep. A team that follows the board setup in [adopting.md](adopting.md) does not need a Ready column.
- **Pending** is the published column for finished, gated pull requests that wait for Human Review. Some boards rename this column to Staging. The option id does not change, so no card loses its status. Commands that say "Pending" in their names act on this column under either name. This page uses the published name, Pending. Tools match columns by option id, not by name.
- **Human Review** holds exactly two pull requests.

The just-in-time target for Pending is three to five prepared pull requests. That is enough for the human to review several items while the next pull request is prepared. A prepared pull request is gated, is not blocked on another change, and can go into Human Review. Finished work that still waits on a blocker also sits in Pending, as in [Blocked work](workflow.md#blocked-work). Those blocked cards do not count toward the target. They do not stop a promotion or a pull step.

## What starts the tools

Three triggers start the tools: a GitHub event, a board-move event, and a periodic tick.

### GitHub events

An event hook on the coordinator host receives events from the forge. Those events include a pull request that opens or is marked ready, and a push to a pull request. They also include a review, a CI run that finishes, and a merge to main.

The hook starts the matching tool for that event. It does not start a full coordinator run for every event. Before it makes any API call, it skips draft pull requests. It also skips Ready pull requests that have not been pulled into Pending. It ignores repeated CI events for the same head. It uses a saved copy of the board when it can.

### The board-move trigger

A move of a project card is a signal. It can mean that Human Review dropped to one pull request, that the human rejected a change, or that a question was answered. The primary trigger is a webhook for project item events. That webhook runs the promote step at once, so a new pull request can enter Human Review in seconds. A slow poll every few minutes is only a backup, in case an event is missed.

### The periodic tick

A timer runs one pass of the tools on a regular interval. The tick is a safety net for lost events. It also does work that events do not cover. It reports stalls. It starts held launches when memory is free. It refills Pending when the buffer is short. New launches must not take memory or API quota away from the pull request that is closest to Human Review.

On each pass, the tick reports the board status. If Human Review holds fewer than two pull requests, it promotes a prepared pull request from Pending. If the prepared buffer in Pending is below its target, it starts the pull step for one Ready pull request. If a pull request has a clean automated review but no bot pass on that head, the tick records the pass. It then adds the pull request to Ready, as a column move or as an update of the ordered list.

The tick opens a draft pull request only when its worker can start, and it checks that the worker started. A draft with no live worker does not sit in In Progress.

## The pull step into Pending

Pending holds the prepared buffer and, separately, finished pull requests that still wait on a blocker. The just-in-time target is three to five prepared pull requests. Each prepared pull request is already merged into the integration branch and gated. Independent pull requests keep their own branches. The tools make a speculative stack only when no independent pull request fits, under the conditions in [Just-in-time review](workflow.md#just-in-time-review). They do only one speculative rebase at a time. A pull request that moves from Pending into Human Review must have no unmerged change other than its own. The only exception is the one permitted stacked pull request on a single Human Review base. Human Review and the prepared pull requests in Pending together are the only pull requests that are merged into the integration branch. The deploy to the staging environment is best-effort.

When the prepared buffer in Pending is below its target, one worker takes the top Ready pull request and prepares it. Ready pull requests wait in this order: milestone first, then fewest conflicts, then oldest. This preparation is the pull step. Only one pull request is prepared at a time.

1. Merge main into the pull request if that is needed. The coding agent of that pull request makes any code fixes.
2. Merge the pull request into the integration branch.
3. Deploy the staging environment again when that is possible, and verify the served commit when that is possible. This step is best-effort. A deploy that does not finish, or a staging environment that is not up to date, does not by itself fail the pull step. For a change that cannot go to the staging environment, the check that the pull request names replaces the deploy conditions. See [Pull requests that do not target main](workflow.md#pull-requests-that-do-not-target-main).
4. Confirm that CI is green on this head, and that the pull request body is complete.
5. Run the Human Review gate, including its best-effort staging rule. If the gate passes, the card goes to Pending. If the gate fails, the card goes back to In Progress with the reason, and the worker tries the next Ready pull request.

When Human Review drops to one, the first prepared pull request in Pending moves to Human Review at once. Then the pull step refills the prepared buffer. The tools do not merge, deploy, or gate any pull request other than the one that is being pulled into Pending.

## The global lock

Gate checks, promotions from Pending into Human Review, and merges into the integration branch share one global lock. Only one of these operations runs at a time. This is true for every caller: the event hook, the tick, and any helper agent.

The lock is non-blocking. If a second operation starts while the lock is held, that second operation does not wait. It stops at once and reports `busy`. It tries again on the next event or the next tick.

Gate operations skip draft pull requests. The lock does not stop the human from a merge to main.

## API budget

The tools use the bot app token first, so they draw on the bot app's own API quota. They fall back to the human account only when the app quota fails. Each fallback is written to the log.

Comments that must come from a human still go out as the human account. The usual case is a review request. The automated reviewer ignores requests from the bot app.

If the API quota is exhausted, the tools read the reset time and wait for that time. They do not fail in the middle of a run.

## Board option ids

Tools match board columns by option id, not by name. A rename of a column does not change the id, so no card loses its status. See [Board states that the tools use](#board-states-that-the-tools-use).

## The tools

### hr-gate

`hr-gate` checks the Human Review gate conditions on the current head of a pull request. The conditions are in [The gate into Human Review](review.md#the-gate-into-human-review). In apply mode it is the only path that may move a card into Human Review, or into Pending after a successful pull.

With no flag, it only checks and prints a table. `--apply N` takes the lock, checks pull request `N`, and moves the card when the conditions pass. `--sweep` checks, after a push to main, that open pull requests still merge. `--sweep --demote` also moves pull requests that no longer merge out of Human Review. `--apply` skips draft pull requests.

### pending-promote

`pending-promote` is the promote command and the pull step. The column it reads is Pending, also when a board calls that column Staging.

With no flag, or with a dry-run flag, it only shows the plan. `--apply` takes the lock and does the work. If Human Review has an open slot, it moves the first Pending card into Human Review, always through `hr-gate --apply`. If the prepared buffer in Pending is below its target, it runs the pull step for the next Ready pull request. If the human rejected a base pull request, it moves each stacked pull request back to In Progress. It also resets those branches.

### active-gate

`active-gate` checks the Active column. Each card there must be an open issue that is assigned to the swarm, and it must have an open pull request or open sub-issues. In demote mode it moves failing cards, for example a closed issue to Done. In promote mode it adds missing swarm issues that do have a pull request.

### flow-status

`flow-status` does not change the board. It prints a report of the flow rules. The report says whether Human Review holds two pull requests, and whether the prepared buffer in Pending is inside its target. It also says whether a ready-next pull request exists. The report ends in `OK` or `VIOLATED`.

### ci-last-check

`ci-last-check` asks whether every CI check on one commit has finished. It does not change anything. The event hook runs it when a CI event arrives, before it makes more API calls for that head.

### The bot app command-line tool

The bot app has a command-line tool, `minbot`. Actions that this tool writes show as the bot app, not as a person. It is a dry run unless `--apply` is given. It checks its identity before every write. Callers do not see the token.

The tool can comment, post evidence, and submit a review. It can add or remove a label, mark a pull request as a draft or as ready, and create an issue. It can list, reply to, or resolve review threads. It can also add a card to a board and set the status of a card. API reads can go through this tool so that they use the bot app quota.
