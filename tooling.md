# Tooling

This page describes the tools that run the workflow on the coordinator host. The rules live in [workflow.md](workflow.md) and [review.md](review.md). The tools enforce those rules. The text of the method lives in this repository. The tools live in the swarm tools repository. Local settings and credentials stay outside every public repository.

## What starts the tools

Three triggers start the tools: a GitHub event, a board-move event, and a periodic tick.

### GitHub events

An event hook on the coordinator host receives events from the forge. Those events include a pull request that opens or is marked ready, and a push to a pull request. They also include a review, a CI run that finishes, and a merge to main.

The hook starts the matching tool for that event. It does not start a full coordinator run for every event. Before it makes any API call, it skips draft pull requests. It also skips Ready pull requests that have not been pulled into the Staging column. It ignores repeated CI events for the same head. It uses a saved copy of the board when it can.

### The board-move trigger

A move of a project card is a signal. It can mean that Human Review dropped to one pull request, that the human rejected a change, or that a question was answered. The primary trigger is a webhook for project item events. That webhook runs the promote step at once, so a new pull request can enter Human Review in seconds. A slow poll every few minutes is only a backup, in case an event is missed.

### The periodic tick

A timer runs one pass of the tools on a regular interval. The tick is a safety net for lost events. It also does work that events do not cover. It reports stalls. It starts held launches when memory is free. It refills the Staging column when the buffer is short. New launches must not take memory or API quota away from the pull request that is closest to Human Review.

On each pass, the tick reports the board status. If Human Review holds fewer than two pull requests, it promotes from the Staging column. If the Staging column holds fewer than its target, it starts the pull step for one Ready pull request. If a pull request has a clean automated review but no bot pass on that head, the tick records the pass. It then moves the card to Ready.

The tick opens a draft pull request only when its worker can start, and it checks that the worker started. A draft with no live worker does not sit in In Progress.

## The pull step into the Staging column

Ready is the finish line for coding agents. A Ready pull request has a finished coding agent, a clean automated review, and a bot pass on the current head. It is not merged into the integration branch. It is not deployed to the staging environment. It is not gated.

The Staging column is a buffer of three to five pull requests. Each of those pull requests is already merged into the integration branch, deployed to the staging environment, and gated. It is stacked on main, on the Human Review pull requests, and on the Staging pull requests ahead of it. Human Review and the Staging column together are the only pull requests that are merged into the integration branch and deployed to the staging environment. That is about seven pull requests in total.

When the Staging column has fewer pull requests than its target, one worker takes the top Ready pull request and prepares it. Ready pull requests wait in this order: milestone first, then fewest conflicts, then oldest. This preparation is the pull step. Only one pull request is prepared at a time.

1. Merge main into the pull request if that is needed. The coding agent of that pull request makes any code fixes.
2. Merge the pull request into the integration branch.
3. Deploy the staging environment again, and verify that it serves the correct commit.
4. Confirm that CI is green on this head, and that the pull request body is complete.
5. Run the Human Review gate. If the gate passes, the card goes to the Staging column. If the gate fails, the card goes back to In Progress with the reason, and the worker tries the next Ready pull request.

When Human Review drops to one, the first Staging card moves to Human Review at once. Then the pull step refills the Staging column. The tools do not merge, deploy, or gate any pull request other than the one that is being pulled into the Staging column.

## The global lock

Gate checks, promotions from the Staging column into Human Review, and merges into the integration branch share one global lock. Only one of these operations runs at a time. This is true for every caller: the event hook, the tick, and any helper agent.

The lock is non-blocking. If a second operation starts while the lock is held, that second operation does not wait. It stops at once and reports `busy`. It tries again on the next event or the next tick.

Gate operations skip draft pull requests. The lock does not stop the human from a merge to main.

## API budget

The tools use the bot app token first, so they draw on the bot app's own API quota. They fall back to the human account only when the app quota fails. Each fallback is written to the log.

Comments that must come from a human still go out as the human account. The usual case is a review request. The automated reviewer ignores requests from the bot app.

If the API quota is exhausted, the tools read the reset time and wait for that time. They do not fail in the middle of a run.

## Board option ids

Tools match board columns by option id, not by name. A rename of a column does not change the id, so no card loses its status. The column that was named Pending is now named Staging. It is the same option. Commands that still say "Pending" in their names act on that same column.

## The tools

### hr-gate

`hr-gate` checks the Human Review gate conditions on the current head of a pull request. The conditions are in [The gate into Human Review](review.md#the-gate-into-human-review). In apply mode it is the only path that may move a card into Human Review, or into the Staging column after a successful pull.

With no flag, it only checks and prints a table. `--apply N` takes the lock, checks pull request `N`, and moves the card when the conditions pass. `--sweep` checks, after a push to main, that open pull requests still merge. `--sweep --demote` also moves pull requests that no longer merge out of Human Review. `--apply` skips draft pull requests.

### pending-promote

`pending-promote` is the promote command and the pull step. The command name still says Pending. The column it reads is the Staging column.

With no flag, or with a dry-run flag, it only shows the plan. `--apply` takes the lock and does the work. If Human Review has an open slot, it moves the first Staging card into Human Review, always through `hr-gate --apply`. If the Staging column is below its target, it runs the pull step for the next Ready pull request. If the human rejected a base pull request, it moves each stacked pull request back to In Progress. It also resets those branches.

### active-gate

`active-gate` checks the Active column. Each card there must be an open issue that is assigned to the swarm, and it must have an open pull request or open sub-issues. In demote mode it moves failing cards, for example a closed issue to Done. In promote mode it adds missing swarm issues that do have a pull request.

### flow-status

`flow-status` does not change the board. It prints a report of the flow rules. The report says whether Human Review holds two pull requests, whether the Staging column is inside its buffer, and whether a ready-next pull request exists. The report ends in `OK` or `VIOLATED`.

### ci-last-check

`ci-last-check` asks whether every CI check on one commit has finished. It does not change anything. The event hook runs it when a CI event arrives, before it makes more API calls for that head.

### The bot app command-line tool

The bot app has a command-line tool, `minbot`. Actions that this tool writes show as the bot app, not as a person. It is a dry run unless `--apply` is given. It checks its identity before every write. Callers do not see the token.

The tool can comment, post evidence, and submit a review. It can add or remove a label, mark a pull request as a draft or as ready, and create an issue. It can list, reply to, or resolve review threads. It can also add a card to a board and set the status of a card. API reads can go through this tool so that they use the bot app quota.
