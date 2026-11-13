# Principles

These are the general principles of the methodology. They guide how the team works. The other pages describe the roles, the board, and the loop that put these principles into practice.

## Optimize for human attention

The human owner's attention is the scarce resource. This method directs that attention to decisions, review, and new work. The human should not have to unstick agents or chase unfinished changes.

When the human sits down, the work is ready. Every card that needs the human is easy to find: finished changes are in Human Review, and questions are in Needs Input. A board that does not have a Needs Input column yet (see the standard column set in the board docs) keeps those cards in their current column, but each one shows clearly that it waits on the human, for example with a label and a question in the card. The human approves finished changes, answers the questions, tries out the software, and files new issues.

The coordinator bot, the worker agents, and the automation keep the work moving between sessions. Do not let work sit unattended. Detect stuck worker agents within minutes, by scripts. Do not rely on the coordinator bot to watch every session itself. Put mechanical steps in deterministic scripts. Then the coordinator bot and the worker agents spend their attention on judgment.

## The human owner decides

Agents prepare work, check it, and integrate it on staging. Only the human merges to main and deploys to production.

## Fix the root cause

Every review finding is one example of a class. The fix covers the class, names the neighboring cases, and tests them.

## Review in layers

The coordinator checks a change before and after the automated reviewer. The human sees it last.

## Bound the loop

Automated review rounds have a cap, so a change can't cycle forever.

## Make state visible

Every change has a card on the board, and the card's column says what happens next.

## Keep communication low-noise

Send a message when someone has to act or decide. Skip acknowledgements and repeats.

## Agents don't widen each other's authority

A request from another agent is not the human's approval.

## Security is not negotiable

The human enters his own passwords. Agents don't reuse credentials to get around access controls. Production changes need an explicit human decision.
