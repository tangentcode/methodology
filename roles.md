# Roles

## Human owner

The human owner is the only person who can approve new work, merge to main, and deploy to production.

- Decides what to build in a comment on each Triage issue, or by a move of the issue to Active or to Backlog. Edits to that comment also count. A comment is the instruction. A move to Active, with no comment, is sufficient approval to start the worker.
- Approves an issue before a worker starts, when the work does not go through Triage.
- Gives choices that agents put into briefs. For example: which browser to support, or the name of a source.
- Reviews changes in the Human Review column.
- Merges to main and deploys.
- Signs in to services himself and types his own passwords.

## Owner bot

The owner bot owns the product decisions for its area of the board. It does not write the product code.

- Writes options for the human in comments on Triage issues.
- Uses the comment of the human on a Triage issue as the instruction for what to build. Edits to that comment also count. A move of the issue to Active, with no comment, is also an approval.
- Writes questions on the issue when it needs more information. The issue stays in Triage, unless the human already moved it to Active.
- Writes the brief and moves the card to Backlog when the decision of the human is sufficient to start, unless the human already moved the issue to Active.
- Does not make product choices that the human did not make. If the human moved the issue to Active while questions are still open, the worker takes the default or recommended answer. It states that default in the pull request body. The card does not go to Needs Input for those questions.

The owner bot must not merge to main, deploy to production, or start workers. The coordinator starts the worker from the brief.

## Coordinator bot

The coordinator runs the pull request loop and keeps the board correct. It does not write the product code. It does not make product choices. Product choices belong to the owner bot.

- Sends the Triage comments of the human to the owner bot.
- Starts one worker agent for each brief that the owner bot writes, and sends the brief to the worker. Also starts a worker when the human moves an issue to Active.
- Checks each change before the first automated review. Checks it again after the automated review is clean.
- Requests automated reviews, up to the maximum number of rounds.
- Sends each finding to the worker with the root-cause rule, immediately when the review arrives. If the worker is idle, the message starts it. If the worker is busy, the message waits in a queue until the turn of the worker ends. The periodic scan sends each review that has open threads and that is newer than the last push to the pull request. Text that an agent suggests in its input box is never a status report.
- Answers each question at the end of a worker turn in the same periodic scan that finds it. Or it sends the question to the correct owner: the human for product choices, or another bot for the area of that bot. A question to the coordinator stops the change as much as a failed test does. When the coordinator sends a question to an owner, it tells the worker who has the question. It moves the card to Needs Input only if the answer must come from the human.
- Makes sure that each message arrives. A message that is typed in the input box of a worker but not submitted did not arrive. Before it sends, the coordinator makes sure that the input box is empty. After it sends, it makes sure that the worker accepted the message. If the worker already did the work before a second copy arrives, the coordinator clears that copy and does not submit it.
- Resolves review threads after it makes sure that the fix is correct.
- Moves cards. Marks pull requests as draft or ready.
- Merges a change into the staging branch, and deploys staging again, only when it pulls that pull request into Staging. It does this for one pull request at a time.
- Makes sure that staging serves the correct commit before the pull request enters Staging. A staging merge must not remove lines of the change. For a change that cannot go to staging, the check that its pull request names replaces the deploy conditions.
- Runs only one gate check, Staging promotion, or staging merge at a time. These operations share one lock. If the lock is busy, the second operation stops at once and reports `busy`. It tries again later. Gate operations skip draft pull requests and pull requests that are still in Ready. See [The pull into Staging](review.md#the-pull-into-staging).

- Makes sure that each change that a person can see has screenshots or frames in the pull request. Existing screenshots count. Do not take them again after a merge from main or from the staging branch.
- Reports results to the human.
- Treats Ready as the finish line for coding agents. Agents work the backlog until their pull requests are in Ready.
- Keeps exactly two pull requests in Human Review whenever two prepared pull requests are available. Keeps a buffer of 3 to 5 fully prepared pull requests in Staging. Only Staging and Human Review are merged into the staging branch and deployed to the staging environment, about 7 pull requests in total. Pulls the next finished pull request from Ready only when Staging is below that target, one at a time. When a pull request enters Staging, its merge into the staging branch is the dry run for its merge into main. Do these merges in order.
- If Human Review becomes empty while work continues, tells the reviewer immediately. Gives the next pull request and the time when it will be ready.
- Acts when the human moves a card from Human Review or from Needs Input to In Progress. A comment from the human does not move the card.

The coordinator must not merge to main, deploy to production, commit or push code, or run commands on the personal computer of the human. There is one exception, because it is not new code. Before a card goes into Staging, the coordinator (or its gate tools) can move a pull request branch to a tip that a worker pushed and tested. It can also move the branch back to a saved plain tip. It must not move the branch of a card that is already in Staging or in Human Review. See [Just-in-time review](workflow.md#just-in-time-review).

## Worker agents

A worker agent is a coding agent in a terminal session. Each worker owns exactly one change.

- Works in its own checkout, on a branch from the latest main.
- Pushes a first commit. Then it waits until the coordinator opens a draft pull request against main. It pushes all its other commits to that pull request.
- Writes tests with the code. Never pushes when tests fail.
- Fixes each finding at its root cause. Names the neighboring cases that the fix covers.
- Reports its head commit and the number of tests that pass, when it is finished or waits on review.
- Puts each question at the end of its turn. Tells who the question is for. Tells which option it recommends and why. Then the coordinator can answer in one line.

A worker must not merge, deploy, change the staging branch, change running services, change the checkouts of other workers, or resolve review threads.

## Automated reviewer

The automated reviewer reads a pull request when the coordinator asks. It writes findings with a priority. In this method, P1 is a defect that you must fix. P2 is a defect that you must fix before human review. Lower priorities are advice only.

## Ops agent

One agent makes root-level changes on shared machines. Examples are system services, web server configuration, and other changes that need administrator rights. Other agents ask the ops agent. They do not increase their own access.
