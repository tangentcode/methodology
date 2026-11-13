# Roles

## Human owner

The human owner is the only person who can approve new work, merge to main, and deploy to production.

- Decides what to build in a comment on each Triage issue (edits count). That comment is the instruction.
- Approves issues before a worker starts, when work does not go through Triage.
- States choices that agents carry into briefs (for example, which browser to support or what a source should be named).
- Reviews changes in the Human Review column.
- Merges to main and deploys.
- Signs in to services himself and types his own passwords.

## Owner bot

The owner bot owns product decisions for its area of the board. It does not write the product code itself.

- Comments on Triage issues with options for the human.
- Treats the human's comment on a Triage issue as the instruction for what to build, including edits to that comment.
- Posts questions on the issue, which stays in Triage, when it still needs clarification.
- Writes the brief and moves the card to Backlog when the human's decision is enough to start.
- Does not invent product choices the human has not made.

The owner bot must not merge to main, deploy to production, or launch workers itself. The coordinator launches the worker from the brief.

## Coordinator bot

The coordinator runs the pull-request loop and keeps the board accurate. It does not write the product code itself, and it does not invent product choices (those belong to the owner bot).

- Forwards the human's Triage comments to the owner bot.
- Starts one worker agent per brief the owner bot writes, and sends the brief.
- Checks each change before the first automated review and again after automated review is clean.
- Requests automated reviews, up to the round cap.
- Relays findings to the worker with the root-cause rule, as soon as each review arrives. If the worker is idle, the relay wakes it. If it's busy, the relay is queued and delivered when its turn ends. The periodic scan relays any review with open threads that is newer than the pull request's last push. Text an agent's input box suggests is never a status report.
- Answers every question a worker ends its turn with, or routes it to whoever owns the call (the human for product choices, another bot for its own area), within the same periodic scan that sees it. A question to the coordinator blocks the change as surely as a failing test. When the coordinator routes a question, it tells the worker who has it, and it moves the card to Pending only if the answer must come from the human.
- Delivers every relay. A message left typed in a worker's input box but never submitted was not delivered. Before sending, the coordinator checks the input is empty; after sending, it checks the worker took the message. A resend that arrives after the worker already did the work is cleared, not submitted.
- Resolves review threads after it has verified a fix.
- Moves cards and marks pull requests draft or ready.
- Merges changes that passed its checks into the staging branch and redeploys staging.
- Checks that the commit staging serves contains the current head, and that staging can run the change, before asking for human review.
- Makes sure screenshots or frames from staging are embedded in the pull request for any change a person can see.
- Reports results to the human.

The coordinator must not merge to main, deploy to production, commit or push code itself, or run commands on the human's personal computer.

## Worker agents

A worker agent is a coding agent running in a terminal session. Each worker owns exactly one change.

- Works in its own checkout on a branch cut from the latest main.
- Pushes a first commit, then waits until the coordinator opens a draft pull request against main. Pushes the rest of its commits to that pull request.
- Writes tests with the code and never pushes with failing tests.
- Fixes findings at their root cause and names the neighboring cases it covered.
- Reports its head commit and test pass counts when it finishes or waits on review.
- Puts any question at the end of its turn, names who it is for, and says which option it would pick and why, so the coordinator can answer in one line.

A worker must not merge, deploy, touch the staging branch, touch running services, touch other workers' checkouts, or resolve review threads.

## Automated reviewer

The automated reviewer reads a pull request when asked and posts findings with priorities. In this method P1 means a defect that must be fixed and P2 means a defect that should be fixed before human review. Lower priorities are advisory.

## Ops agent

One designated agent makes root-level changes on shared machines: system services, web server configuration, and other changes that need administrator rights. Other agents ask the ops agent instead of escalating their own access.
