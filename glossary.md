# Glossary

**Active.** The column for open issue cards that are assigned to the swarm. Each one does not have the `work2` label, and each one has exactly one open linked pull request in a flow column (In Progress, Auto Review, Needs Input, Pending, or Human Review). The number of cards in Active equals the number of pull requests in those flow columns. To keep that equality true, a pull request of a `work2` issue does not go into a flow column, and an issue has only one pull request in a flow column at a time. A move of an issue to this column, with no comment, is sufficient approval to start its worker.

**Automated reviewer.** A code review service. It reads a pull request and writes findings with priorities.

**Backlog.** The column for issues that have an approved plan and that no pull request has started yet. Issues set the scope. Pull requests move the work through the other columns.

**Board.** The project tracker. It has one card for each issue or pull request, in columns.

**Brief.** The written instructions of the owner bot to a worker for one change. A change is a full issue or a named part of one.

**Coordinator bot.** The agent that runs the pull request loop. It sends Triage comments to the owner bot, steers workers, checks changes, and moves cards.

**Discuss.** The column for issues that need careful thought or a conversation. They wait here so that simple Triage items move first. The human writes comments on the issue. The agent then writes the issue body again to agree with the answers. This continues until the issue is ready for Backlog or Active. No worker starts on a Discuss item. The coordinator does not count it as waiting on the human. Agents do not move the card forward themselves.

**Draft.** A pull request that is not ready for review. Changes in In Progress are drafts.

**Finding.** A defect that a reviewer reports. You must fix a P1. You must fix a P2 before human review.

**Gate.** The conditions that a pull request must meet before its card moves to Human Review. Automation and people check each condition on the current head.

**Head.** The latest commit on the branch of a pull request. Checks apply only to the current head.

**Human owner.** The person who decides Triage issues, reviews finished work, merges to main, and deploys.

**Human Review.** The column for finished pull requests that wait on the human to test them and merge them to main. It holds exactly two pull requests. When it holds only one pull request and no independent pull request is ready, one stacked pull request on that one can go in.

**Inbox.** The column for items that are out of the flow for now, and, after launch, for new tickets from customers. Issues with the `work2` label stay here, even when they have a linked pull request.

**Independent pull request.** A pull request that merges cleanly onto main, has no unmerged commits of another Human Review pull request, and merges cleanly together with each Human Review pull request. The human can merge or reject it with no effect on the others.

**Issue title.** A short headline that tells the present state. A plain statement, such as "X does Y", is a bug report: it occurs now, and we do not want it. A wanted change uses "should".

**Issue type.** A GitHub type on each issue: Feature, Bug, or Task.

**Main.** The production branch. Only the human merges into it.

**Needs Input.** The column for draft pull requests where a human must answer a question from the worker or the coordinator.

**Neighboring cases.** Other examples of the same class of defect as a finding.

**Ops agent.** The only agent that can make root-level changes on shared machines.

**Owner bot.** The agent that owns the product decisions for an area of the board: Triage options, questions on Triage issues, and briefs.

**Pending.** The column for finished pull requests that wait. A pull request waits here when it depends on another unmerged pull request, or when no Human Review slot is open. It is a queue sorted by conflict count. One fully gated pull request is ready next.

**Pull request title.** A short headline that completes the sentence "Merging this pull request will ...". It starts with a verb in the imperative.

**Ready.** A pull request that is marked for review. When a card moves to Auto Review, its pull request becomes ready.

**Root-cause rule.** Fix the cause of a finding, write a list of its neighboring cases, and test each one.

**Round.** One automated review of the current head. There is a maximum number of rounds.

**Stacked pull request.** A pull request whose head also has the changes of a base pull request that is in Human Review. Its body starts with a banner that names the base. Human Review holds a maximum of one stacked pull request. If the human rejects the base, the coordinator resets the stacked pull request to its plain branch before the human can merge it.

**Staging.** A test environment that the staging branch feeds. The staging branch is an integration branch. It is never merged into main. The branch collects many changes. Thus the commit that staging serves is usually a merge that contains the head of a pull request, not the head itself.

**Swarm assignment.** The `swarm` label on an issue. An issue in Active must have this label. It must also have exactly one open linked pull request in a flow column, and it must not have the `work2` label.

**Triage.** The column for open issues that have suggested plans. They wait on the human to decide, in a comment or by a move of the issue to Active or to Backlog.

**work2.** A label that keeps an issue in Inbox, even when the issue has a linked pull request. The pull request of a `work2` issue does not go into a flow column. A `work2` issue does not go into Active, and it does not count in the Active total.

**Worker agent.** A coding agent in a terminal session. It owns one change.
