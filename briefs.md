# Briefs

A brief is the coordinator's written instruction to one worker agent for one issue. The worker should be able to start from the brief alone, without asking the coordinator for context.

## What a brief contains

- **Base.** The branch name, that it is cut from the latest main, and that the pull request targets main. Open a draft pull request at the first commit and link the issue.
- **Where.** The files and modules the change touches, and any nearby code the worker should not revive or touch.
- **First step.** What to read before writing code, and what decision to explain in the pull request body.
- **The issue.** The full issue text, copied in, so the brief stands alone.
- **The human's choices.** Every choice the human has stated, written in the first time. Don't leave them for a review round to discover.
- **Tests.** The cases that must be tested.
- **Acceptance.** How the human will check the result.
- **The root-cause rule.** Always included.
- **Rules.** What the worker must not do.
- **Reporting.** What to report and when.

## Template

```markdown
# Brief: <short title> (<issue reference>)

Work only in your own checkout. One pull request, targeting main.
Issue: <issue reference>. Approved by the human owner on <date>.

## Base
Use branch `<branch>`, cut from the latest main. Set the pull request base to main.
Open a draft pull request at your first commit, linking the issue.
Never merge to main and never deploy. Don't touch the staging branch,
running services, or other workers' checkouts.

## Where
- <module or directory>: <what lives there>
- Don't revive <old code or closed approach>.

Step 1, before you code: read <existing mechanism> and pick the approach
closest to the existing code. Explain the choice in the pull request body.

## Issue
<full issue text>

## The human's choices
- <choice 1>
- <choice 2>

## Tests
- <case>
- <case>

## Acceptance
<how the human will verify it, usually on staging>

## Root-cause rule (applies to every review finding)
For each finding, fix the root cause, not the instance. List the neighboring
cases of the same class in the pull request body and add tests for them
before you push. Never push with failing tests.

## Rules
- Branch from main, base main, draft pull request early.
- Don't merge, deploy, or touch the staging branch or running services.
- Don't resolve review threads.
- Keep temporary files in your own working directory, not a shared temp directory.
- <secret-handling rule, if the change touches credentials>
- Run the full suite for each component you touched and report pass counts.

## Reporting
When you finish, or are waiting on review, report the head commit and test pass counts.
```

## Relaying findings

When the coordinator relays a review finding to a worker, the message includes:

- The finding, quoted, with its file and line.
- The root-cause rule.
- Any choice the human has made that bears on the fix.

Send one complete message per round, not a stream of partial ones. Before sending, check the worker's input box. Text already sitting there is usually the agent's own suggestion, not an instruction from the human, so don't submit it.
