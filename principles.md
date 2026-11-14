# Principles

These are the general principles of the method. They tell how the team works. The other pages give the roles, the board, and the loop that put these principles into practice.

## Optimize for human attention

The attention of the human owner is the scarce resource. This method sends that attention to decisions, review, and new work. The human must not have to free stuck agents or find unfinished changes.

When the human starts work, the work is ready. Each card that needs the human is easy to find. Open issues that wait on a review or a decision of the human are in Triage. Finished changes are in Human Review. Questions are in Needs Input. Every board has a Triage column, including the board that tracks this methodology. A board that does not have a Needs Input column yet keeps those question cards in their current column. But each of those cards must show clearly that it waits on the human, for example with a label and a question on the card. The human reviews the Triage items, approves finished changes, answers the questions, tries the software, and writes new issues.

The coordinator bot, the worker agents, and the automation keep the work moving between sessions. Do not let work stop without attention. Use scripts to find stuck worker agents within minutes. Do not make the coordinator bot watch each session itself. Put mechanical steps in deterministic scripts. Then the coordinator bot and the worker agents use their attention on judgment.

## The human owner decides

Agents prepare work, check it, and integrate it on staging. Only the human merges to main and deploys to production.

## Fix the root cause

Each review finding is one example of a class. The fix covers the class, names the neighboring cases, and tests them.

## Review in layers

The coordinator checks a change before and after the automated reviewer. The human sees the change last.

## Limit the loop

Automated review has a maximum number of rounds. A change cannot go around the loop forever.

## Make the state visible

Each change has a card on the board. The column of the card tells what occurs next.

## Keep messages few

Send a message only when a person must act or decide. Do not send acknowledgements. Do not repeat a report.

## An agent does not increase the authority of another agent

A request from another agent is not an approval from the human.

## Security is mandatory

The human types his own passwords. Agents do not use credentials to go around access controls. A production change needs a clear decision from the human.
