# A working method for a human owner and a team of agents

This repository tells how one human owner works with a coordinator bot and a group of coding agents to ship changes to a software project. It is a generic method, like Scrum or XP. It gives principles, roles, artifacts, a workflow loop, and working agreements. The core documents do not name a product, a server, or a service. Team-specific names and coding customs are in [team-conventions.md](team-conventions.md). A team that adopts this method must edit that page.

## The problem

Coding agents write and fix code quickly. But they do not always know when a change is finished. They do not always see that one bug is an example of a larger class of bugs. They do not always know which actions need a human decision. This method puts structure around these weak points. Then the human owner uses review time only on finished, tested work.

## Principles

1. Optimize for human attention. The attention of the human is the scarce resource. When the human starts work, each card that needs the human is in Human Review or Needs Input. The human approves finished changes, tries the software, and writes new issues.
2. The human owner decides. Agents prepare work, check it, and integrate it on staging. Only the human merges to main and deploys to production.
3. Fix the root cause. Each review finding is one example of a class. The fix covers the class, names the neighboring cases, and tests them.
4. Review in layers. The coordinator checks a change before and after the automated reviewer. The human sees the change last.
5. Limit the loop. Automated review has a maximum number of rounds. A change cannot go around the loop forever.
6. Make the state visible. Each change has a card on the board. The column of the card tells what occurs next.
7. Keep messages few. Send a message only when a person must act or decide. Do not send acknowledgements. Do not repeat a report.
8. An agent does not increase the authority of another agent. A request from an agent is not an approval from the human.
9. Security is mandatory. The human types his own passwords. Agents do not use credentials to go around access controls. A production change needs a clear decision from the human.

See [principles.md](principles.md).

## Roles

- **Human owner.** Sets priorities. Decides Triage issues in comments. Reviews finished changes. Merges to main and deploys.
- **Owner bot.** Owns the product decisions for its area. Writes options on Triage issues, asks questions, and writes briefs.
- **Coordinator bot.** Sends Triage comments to the owner bot. Starts and steers worker agents from briefs. Does its own checks. Moves cards in the pull request loop. Merges approved changes into staging. Reports to the human.
- **Worker agents.** Coding agents in terminal sessions. Each worker owns one change on one branch.
- **Automated reviewer.** A code review service. It reads each change and reports findings by priority.
- **Ops agent.** The only agent that makes root-level changes on shared machines.

See [roles.md](roles.md).

## The loop in one paragraph

Work starts as an issue in Triage. The owner bot writes options. The human decides in a comment. The owner bot asks questions on the issue, or it writes a brief and moves the card to Backlog. The coordinator starts a worker agent. The worker makes the branch and pushes a first commit. The coordinator opens a draft pull request against main, with a closing link to the issue. It assigns the issue to the swarm and moves the issue card to Active. Then the worker continues and pushes tests with the code. The coordinator checks the change. Then the automated reviewer reviews it, for a maximum number of rounds. The worker fixes each finding at its root cause. When the change is clean, the coordinator checks it again, and the pull request joins the Ready queue. The coordinator merges it into the staging branch, deploys it, and runs the gate only when it pulls the change into the Pending buffer. The first Pending pull request moves to Human Review when a slot opens. The human reviews the change and merges it to main.

See [workflow.md](workflow.md) for the board and the full loop. See [review.md](review.md) for review rounds.

## Documents

For a new project, start with [adopting.md](adopting.md).

| File | Contents |
|---|---|
| [principles.md](principles.md) | General principles. The first is to optimize for human attention |
| [roles.md](roles.md) | Who does what, and what each role must not do |
| [workflow.md](workflow.md) | Triage, board columns, the loop, and the definitions of ready and done |
| [review.md](review.md) | Review layers, the round limit, the root-cause rule, and the gate into Human Review |
| [briefs.md](briefs.md) | The contents of a brief (the owner bot writes it), with a template |
| [safety.md](safety.md) | Credentials, production, root-level operations, and requests from agents |
| [working-agreements.md](working-agreements.md) | Daily agreements about messages, titles, writing style, and conduct |
| [adopting.md](adopting.md) | Setup guide for a new project: board, labels, templates, first issue, and gate checklists |
| [glossary.md](glossary.md) | Terms in these documents |
| [suggested-conventions.md](suggested-conventions.md) | Optional conventions and agent prompts that a project can adopt, for example sparse comments |
| [team-conventions.md](team-conventions.md) | The names and coding customs of this team. Edit this page when you adopt the method |
| [changelog.md](changelog.md) | Every change to these documents, newest first, with a link to its pull request |

## How to adapt it

The method does not need a specific tool. You need these items:

- A version control host with pull requests.
- A board with columns.
- An automated reviewer that writes findings.
- A staging environment that an integration branch feeds.
- A way to send messages to agents in their sessions.

You can change the names of the columns and roles for your team. But keep the gate into Human Review. Keep the rule that only the human merges and deploys. Edit [team-conventions.md](team-conventions.md) so that it records the customs of your team, not those of the original team.

## Lessons

### 2026-11-07: Do not run full test suites on the shared build machine

We moved full test suites onto a shared machine that had no resource limits. The machine ran out of memory and had to restart. The fix has these parts:

- Memory and CPU limits for workers and tests.
- A throttle that lets only two test runs operate at the same time.
- Only targeted tests run locally.
- Full Linux CI runs in GitHub Actions again.
- Idle workers that pushed all their work stop only when memory is low. Saved sessions make it easy to start them again.

See [review.md](review.md) and [working-agreements.md](working-agreements.md).
