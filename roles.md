# Roles

## Human owner

The human owner is the only person who can approve new work, merge to main, and deploy to production.

- Approves issues before work starts.
- States choices that agents carry into briefs (for example, which browser to support or what a source should be named).
- Reviews changes in the Human Review column.
- Merges to main and deploys.
- Signs in to services himself and types his own passwords.

## Coordinator bot

The coordinator runs the loop and keeps the board accurate. It does not write the product code itself.

- Files issues the human approved and writes a brief for each.
- Starts one worker agent per change and sends it instructions.
- Checks each change before the first automated review and again after automated review is clean.
- Requests automated reviews, up to the round cap.
- Relays findings to the worker with the root-cause rule.
- Resolves review threads after it has verified a fix.
- Moves cards and marks pull requests draft or ready.
- Merges changes that passed its checks into the staging branch and redeploys staging.
- Checks that staging serves the current head and can run the change before asking for human review.
- Makes sure screenshots or frames from staging are embedded in the pull request for any change a person can see.
- Reports results to the human.

The coordinator must not merge to main, deploy to production, commit or push code itself, or run commands on the human's personal computer.

## Worker agents

A worker agent is a coding agent running in a terminal session. Each worker owns exactly one change.

- Works in its own checkout on a branch cut from the latest main.
- Opens a draft pull request against main as soon as it has a first commit.
- Writes tests with the code and never pushes with failing tests.
- Fixes findings at their root cause and names the neighboring cases it covered.
- Reports its head commit and test pass counts when it finishes or waits on review.

A worker must not merge, deploy, touch the staging branch, touch running services, touch other workers' checkouts, or resolve review threads.

## Automated reviewer

The automated reviewer reads a pull request when asked and posts findings with priorities. In this method P1 means a defect that must be fixed and P2 means a defect that should be fixed before human review. Lower priorities are advisory.

## Ops agent

One designated agent makes root-level changes on shared machines: system services, web server configuration, and other changes that need administrator rights. Other agents ask the ops agent instead of escalating their own access.
