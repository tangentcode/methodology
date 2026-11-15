# Tooling

This page describes the tools that run the workflow on the coordinator host. The rules for the loop and the Human Review gate live in [workflow.md](workflow.md) and [review.md](review.md). The text of the method lives in this repository. The tools live in the swarm tools repository. Local settings and credentials stay outside every public repository.

## Board states that the tools use

The tools run the loop and the gate in [workflow.md](workflow.md) and [review.md](review.md). They use these board columns:

- **Ready** is the board column between Needs Input and Staging. It is the finish line for coding agents. Each Ready pull request has a finished coding agent and no open P1 or P2 findings. The automated review of the current head is clean, or it is at the round limit or has timed out and the post-check of the coordinator has passed. A Ready pull request is not merged into the staging branch, not deployed, and not gated. It is not on the staging environment.
- **Staging** is the board column with no fixed cap. Any Ready pull request that merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may enter. When the column drops below a floor (default 2), the cascade pulls the next clean Ready pull request. This column was formerly named Pending. The option id did not change, so no card lost its status. Commands that say "Pending" in their names act on this column. Tools match columns by option id, not by name.
- **Human Review** holds exactly two pull requests whenever two prepared pull requests are available, and never more than two.

Staging has no fixed cap. The goal is flow. A Staging pull request is gated, is not blocked on another change, and can go into Human Review as a card move. Any Ready pull request that merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may enter Staging. The tools cache a conflict map per head SHA. When Staging drops below a floor (default 2), the cascade pulls the next clean Ready pull request. The expensive steps (the work merge, the redeploy, and the gate) happen only at pull time. Never rebase or rework a pull request just to fill Staging. Finished work that still waits on a blocker can also sit in Staging, as in [Blocked work](workflow.md#blocked-work). Those blocked cards do not count toward the floor. They do not stop a promotion or a pull step.

Only Staging and Human Review are merged into the staging branch and deployed to the staging environment.

## What starts the tools

Three triggers start the tools: a GitHub event, a board-move event, and a periodic tick.

### GitHub events

An event hook on the coordinator host receives events from the forge. Those events include a pull request that opens or is marked ready, and a push to a pull request. They also include a review, a CI run that finishes, and a merge to main.

The hook starts the matching tool for that event. It does not start a full coordinator run for every event. Before it makes any API call, it skips draft pull requests. It also skips Ready pull requests that have not been pulled into Staging. It ignores repeated CI events for the same head. It uses a saved copy of the board when it can.

### The board-move trigger

A move of a project card is a signal. It can mean that Human Review dropped to one pull request, that the human rejected a change, or that a question was answered. The primary trigger is a webhook for project item events. That webhook runs `~/bin/swarm-advance --cascade` at once, so a new pull request can enter Human Review in seconds, and the rest of the chain can refill in the same run. A slow poll every few minutes is only a backup, in case an event is missed.

### The periodic tick

A timer runs one pass of the tools on a regular interval. The tick is a safety net for lost events. It also does work that events do not cover. It reports stalls. It starts held launches when memory is free. It pulls the next clean Ready pull request into Staging when Staging is below the floor. New launches must not take memory or API quota away from the pull request that is closest to Human Review.

On each pass, the tick reports the board status. If a Human Review slot is open or Staging is below the floor, it runs `~/bin/swarm-advance --cascade`, which promotes the first Staging pull request when a Human Review slot is open, pulls the next clean Ready pull request while Staging is below the floor, may also pull other Ready pull requests that already merge cleanly, and signals for the next coding agent when Ready has fewer than 6 pull requests. If a pull request is eligible for Ready but is not yet in that column, the tick records the pass and moves the card to Ready.

The tick opens a draft pull request only when its worker can start, and it checks that the worker started. A draft with no live worker does not sit in In Progress.

## The pull step into Staging

Staging has no fixed cap, and, separately, it may hold finished pull requests that still wait on a blocker. Any Ready pull request that merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may enter Staging. The tools cache a conflict map per head SHA. Never rebase or rework a pull request just to fill Staging. A Staging pull request is already merged into the staging branch, deployed, verified, and gated. Human Review and Staging together are the only pull requests that are merged into the staging branch.

When Staging is below the floor (default 2), one worker takes the next clean Ready pull request and prepares it. Ready pull requests wait in this order: the one active fast-track pull request first, if it is in Ready, then milestone, then fewest conflicts with the current stack, then oldest. See [Fast track](review.md#fast-track). This preparation is the pull step. The expensive steps happen only at pull time. Only one Ready pull request is prepared at a time.

1. Merge main into the pull request if that is needed. The coding agent of that pull request makes any code fixes.
2. Merge the pull request into the staging branch, on top of the current stack: main, the Human Review pull requests, and the Staging pull requests ahead of it. Refuse this merge on a conflict or on conflict markers. If it refuses, try the next pull request in Ready.
3. Deploy the staging environment again, and confirm the served `.deploy-sha`. A pull request does not enter Staging until this is true. For a change that cannot go to the staging environment, the check that the pull request names replaces the deploy conditions. See [Pull requests that do not target main](workflow.md#pull-requests-that-do-not-target-main).
4. Confirm that CI is green on this head, and that the pull request body is complete.
5. Run the Human Review gate with `hr-gate --apply`. If the gate passes, the card goes to Staging. If the gate fails because staging lacks configuration, credentials, or a required service, the tools change the pull request to a draft. They move the card to Needs Input. The comment names what is missing and who must supply it. For other gate failures, restore the staging branch to the last admitted stack and deploy that stack again. Then the card goes back to In Progress with the reason, and the worker tries the next Ready pull request.

When Human Review drops to one, `~/bin/swarm-advance --cascade` runs the whole just-in-time cascade under the shared lock. The first Staging pull request moves to Human Review at once, through `hr-gate --apply`. That step is a card move. Then, while Staging is below the floor, the pull step brings in the next clean Ready pull request. Any other Ready pull request that already merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may also enter Staging. Never rebase or rework a pull request just to fill Staging. If Ready then has fewer than 6 pull requests, the tools tell the swarm manager to start the next coding agent, and to keep about 2 agents working. The tools prepare only one Ready pull request at a time. They can still run the gate again on a pull request that is already in Staging, including when CI finishes, when main advances, or when they promote the card. If that later check fails, the card leaves Staging, as the gate in [review.md](review.md#the-gate-into-human-review) requires.

## The global lock

Gate checks, promotions from Staging into Human Review, and merges into the staging branch share one global lock. Only one of these operations runs at a time. This is true for every caller: the event hook, the tick, and any helper agent. See [The pull into Staging](review.md#the-pull-into-staging).

The lock file is `~/.cache/swarm-serial.lock`. The just-in-time cascade holds this lock for the whole run. A caller that finds the lock busy queues a rerun. The process that holds the lock drains every queued rerun before it exits.

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

### swarm-advance

`~/bin/swarm-advance --cascade` is the just-in-time cascade command. It takes the shared lock and, in one serial run, promotes the first Staging pull request into Human Review when a slot is open, pulls the next clean Ready pull request while Staging is below the floor (default 2), may also pull other Ready pull requests that already merge cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request, and signals the swarm manager to start the next coding agent when Ready has fewer than 6. The expensive steps happen only at pull time. It never rebases or reworks a pull request just to fill Staging. If the lock is busy, it queues a rerun. The process that holds the lock drains that rerun before it exits. See [The just-in-time cascade](review.md#the-just-in-time-cascade). This command is being built in [tangentswarm #26](https://github.com/tangentcode/tangentswarm/pull/26).

### pending-promote

`pending-promote` is the older promote command and the pull step. The column it reads is Staging, also when a command name still says Pending. Prefer `~/bin/swarm-advance --cascade` for an event that frees a slot.

With no flag, or with a dry-run flag, it only shows the plan. `--apply` takes the lock and does the work. If Human Review has an open slot, it moves the first Staging card into Human Review, always through `hr-gate --apply`. If Staging is below the floor, it runs the pull step for the next clean Ready pull request. Any other Ready pull request that already merges cleanly may also enter Staging. If the human rejected a base pull request, it moves each stacked pull request back to In Progress. It also resets those branches.

### active-gate

`active-gate` checks the Active column. Each card there must be an open issue that is assigned to the swarm, that does not have the `work2` label, and that has exactly one open linked pull request in a flow column. In demote mode it moves failing cards, for example a closed issue to Done, or a `work2` issue back to Inbox. In promote mode it adds missing swarm issues that do have a pull request and that do not have the `work2` label.

### flow-status

`flow-status` does not change the board. It prints a report of the flow rules. The report says whether Human Review holds two pull requests, when two prepared pull requests are available, and whether Staging is at or above its floor (default 2). It also shows the active fast-track card, if there is one, and how long that card has been on fast track. The report ends in `OK` or `VIOLATED`.

### ci-last-check

`ci-last-check` asks whether every CI check on one commit has finished. It does not change anything. The event hook runs it when a CI event arrives, before it makes more API calls for that head.

### The bot app command-line tool

The bot app has a command-line tool, `minbot`. Actions that this tool writes show as the bot app, not as a person. It is a dry run unless `--apply` is given. It checks its identity before every write. Callers do not see the token.

The tool can comment, post evidence, and submit a review. It can add or remove a label, mark a pull request as a draft or as ready, and create an issue. It can list, reply to, or resolve review threads. It can also add a card to a board and set the status of a card. API reads can go through this tool so that they use the bot app quota.
