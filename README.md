# A working methodology for a human owner and a team of agents

This repository describes how one human owner works with a coordinator bot and a group of coding agents to ship changes to a software project. It is written as a generic method, in the spirit of Scrum or XP. It names principles, roles, artifacts, a workflow loop, and working agreements. It does not name any particular product, server, or service.

## The problem it solves

Coding agents can write and fix code quickly. They are less reliable at judging when a change is finished, at noticing that one bug is an example of a wider class, and at knowing which actions need a human decision. This method puts structure around those weak points so the human owner spends review time on finished, tested work.

## Principles

1. Optimize for human attention. The human's attention is the scarce resource. When the human sits down, every card that needs them is in Human Review or Needs Input. They approve finished changes, try out the software, and file new issues.
2. The human owner decides. Agents prepare work, check it, and integrate it on staging. Only the human merges to main and deploys to production.
3. Fix the root cause. Every review finding is treated as one example of a class. The fix covers the class, names the neighboring cases, and tests them.
4. Review in layers. The coordinator checks a change before and after the automated reviewer, and the human sees it last.
5. Bound the loop. Automated review rounds have a cap, so a change can't cycle forever.
6. Make state visible. Every change has a card on the board, and the card's column says what happens next.
7. Keep communication low-noise. Send a message when someone has to act or decide. Skip acknowledgements and repeats.
8. Agents don't widen each other's authority. A request from another agent is not the human's approval.
9. Security is not negotiable. The human enters his own passwords, agents don't reuse credentials to get around access controls, and production changes need an explicit human decision.

See [principles.md](principles.md).

## Roles

- **Human owner.** Sets priorities, approves new work, reviews finished changes, merges to main, and deploys.
- **Coordinator bot.** Writes briefs, starts and steers worker agents, runs its own checks, moves cards, merges approved changes into staging, and reports to the human.
- **Worker agents.** Coding agents in terminal sessions. Each one owns one change on one branch.
- **Automated reviewer.** A code-review service that reads each change and reports findings by priority.
- **Ops agent.** The only agent that makes root-level changes on shared machines.

See [roles.md](roles.md).

## The loop in one paragraph

The human approves an issue. The coordinator writes a brief and starts a worker agent. The worker opens a draft pull request against main early and pushes tests with the code. The coordinator checks the change, then the automated reviewer reviews it, for at most a fixed number of rounds. The worker fixes each finding at its root cause. When the change is clean, the coordinator checks it again, merges it into the staging branch, and redeploys staging. If the change passes the gate into human review, the card moves to Human Review. The human reviews it and merges it to main.

See [workflow.md](workflow.md) for the board and the full loop, and [review.md](review.md) for review rounds.

## Documents

Starting a new project? Begin with [adopting.md](adopting.md).


| File | Contents |
|---|---|
| [principles.md](principles.md) | General principles, starting with optimizing for human attention |
| [roles.md](roles.md) | Who does what, and what each role must not do |
| [workflow.md](workflow.md) | Board columns, the loop, definitions of ready and done |
| [review.md](review.md) | Review layers, round cap, the root-cause rule, the gate into human review |
| [briefs.md](briefs.md) | What a brief contains, with a template |
| [safety.md](safety.md) | Credentials, production, root-level operations, agent requests |
| [working-agreements.md](working-agreements.md) | Day-to-day agreements about communication and conduct |
| [adopting.md](adopting.md) | Setup guide for a new project: board, labels, templates, first issue, gate checklists |
| [glossary.md](glossary.md) | Terms used in these documents |

## Adapting it

Nothing here depends on a specific tool. You need a version-control host with pull requests, a board with columns, an automated reviewer that posts findings, a staging environment fed by an integration branch, and a way to send messages to agents in their sessions. Rename the columns and roles to fit your team, but keep the gate into human review and the rule that only the human merges and deploys.
