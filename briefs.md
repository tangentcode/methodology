# Briefs

A brief is the written instruction of the owner bot to one worker agent for one change. A change is a full issue or a named part of one. The coordinator starts the worker and sends the brief. The worker must be able to start from the brief only, without a request for more context.

## The contents of a brief

- **Base.** The branch name. The branch starts from the latest main, and the pull request targets main. The worker makes and pushes a first commit, and then stops. The coordinator opens the draft pull request, with a closing link to the issue, before the worker continues.
- **Where.** The files and modules that the change touches. Also any nearby code that the worker must not use again or change.
- **First step.** What to read before the worker writes code, and which decision to explain in the pull request body.
- **The issue.** The full text of the issue, copied into the brief. Then the brief is complete without other documents.
- **The choices of the human.** Each choice from the Triage comment of the human, and from all later answers. Write them in the first time. Do not let a review round find them.
- **Tests.** The cases that the worker must test.
- **Acceptance.** How the human will check the result.
- **The root-cause rule.** Always include it.
- **Rules.** What the worker must not do.
- **Reports.** What to report, and when.

## Template

```markdown
# Brief: <short title> (<issue reference>)

Work only in your own checkout. Make one pull request that targets main.
Issue: <issue reference>. The human owner approved it on <date>.
Pull request title: an imperative phrase that completes "Merging this pull request will ...".

## Base
Use branch `<branch>`. Start it from the latest main. Set the pull request base to main.
Make a first commit, push the branch, report it, and stop. Do not open
the pull request. The coordinator opens a draft pull request for this
branch, with a closing link to the issue, and tells you to continue.
Then push all your other commits to that pull request.
Never merge to main. Never deploy. Do not change the staging branch,
running services, or the checkouts of other workers.

## Where
- <module or directory>: <what is in it>
- Do not use <old code or closed approach> again.

Step 1, before you write code: read <existing mechanism>. Select the approach
that is nearest to the existing code. Explain the choice in the pull request body.

## Issue
<full issue text>

## The choices of the human
- <choice 1>
- <choice 2>

## Tests
- <case>
- <case>

## Acceptance
<how the human will check it, usually on staging>

## Root-cause rule (for each review finding)
For each finding, fix the root cause, not only the one example. In the pull
request body, write a list of the neighboring cases of the same class. Add
tests for them before you push. Never push when tests fail.

## Rules
- Start the branch from main. The base is main. Push a first commit and wait for the draft pull request from the coordinator.
- Do not merge or deploy. Do not change the staging branch or running services.
- Do not resolve review threads.
- Keep temporary files in your own working directory, not in a shared temporary directory.
- <rule for secrets, if the change touches credentials>
- Write issues, pull request bodies, commit messages, and replies in ASD-STE100 style, in ASCII only (see working-agreements.md, Writing style).
- Run only the targeted tests for the files that you changed. Report the number of tests that pass.

## Reports
When you are finished, or when you wait on review, report the head commit and the number of tests that pass.
```

## How to send findings

When the coordinator sends a review finding to a worker, the message includes:

- The finding, as a quote, with its file and line.
- The root-cause rule.
- Each choice of the human that has an effect on the fix.

Send one complete message for each round. Do not send many partial messages. Before you send, look at the input box of the worker. Text that is already there is usually a suggestion from the agent, not an instruction from the human. Do not submit it.
