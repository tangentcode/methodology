# Glossary

**Active.** The column for open issue cards that are assigned to the swarm. Each one has open sub-issues or a linked open pull request.

**Automated reviewer.** A code review service. It reads a pull request and writes findings with priorities.

**Backlog.** The column for issues that have an approved plan and that no pull request has started yet. Issues set the scope. Pull requests move the work through the other columns.

**Board.** The project tracker. It has one card for each issue or pull request, in columns.

**Brief.** The written instructions of the owner bot to a worker for one change. A change is a full issue or a named part of one.

**Coordinator bot.** The agent that runs the pull request loop. It sends Triage comments to the owner bot, steers workers, checks changes, and moves cards.

**Discuss.** The column for issues that need careful thought or a conversation. They wait here so that simple Triage items move first. The human writes comments on the issue. The agent then writes the issue body again to agree with the answers. This continues until the issue is ready for Backlog or Active. No worker starts on a Discuss item. The coordinator does not count it as waiting on the human. Agents do not move the card forward themselves.

**Draft.** A pull request that is not ready for review. Changes in In Progress are drafts.

**Finding.** A defect that a reviewer reports. You must fix a P1. You must fix a P2 before human review.

**Gate.** The conditions that a pull request must meet before it enters Pending. Automation and people check each condition on the current head, during the pull step, one pull request at a time. A later move from Pending to Human Review is only a card move. A gate check, a promotion from Pending, and a merge into the staging branch share one lock, so only one of them runs at a time. A second operation stops at once and reports `busy`. Gate operations skip draft pull requests and pull requests that are still in the Ready queue. See [The pull into Pending](review.md#the-pull-into-pending).

**Head.** The latest commit on the branch of a pull request. Checks apply only to the current head.

**Human owner.** The person who decides Triage issues, reviews finished work, merges to main, and deploys.

**Human Review.** The column for finished pull requests that wait on the human to test them and merge them to main. It holds exactly two pull requests whenever two are ready, and never more than two. The next card comes from the front of Pending, as a card move, in seconds after a slot opens. When it holds only one pull request, the first Pending pull request can go in as a stacked pull request if it depends on that one.

**Inbox.** The column for items that are out of the flow for now, and, after launch, for new tickets from customers.

**Independent pull request.** A pull request that merges cleanly onto main, has no unmerged commits of another Human Review pull request, and merges cleanly together with each Human Review pull request. The human can merge or reject it with no effect on the others.

**Issue title.** A short headline that tells the present state. A plain statement, such as "X does Y", is a bug report: it occurs now, and we do not want it. A wanted change uses "should".

**Issue type.** A GitHub type on each issue: Feature, Bug, or Task.

**Main.** The production branch. Only the human merges into it.

**Needs Input.** The column for draft pull requests where a human must answer a question from the worker or the coordinator.

**Neighboring cases.** Other examples of the same class of defect as a finding.

**Ops agent.** The only agent that can make root-level changes on shared machines.

**Owner bot.** The agent that owns the product decisions for an area of the board: Triage options, questions on Triage issues, and briefs.

**Pending.** The column for a buffer of 3 to 5 fully prepared pull requests. Each one is already merged into the staging branch, deployed, verified, gated, and pre-merged as a stack on main, the Human Review pull requests, and the Pending pull requests ahead of it. The first one goes into Human Review immediately when a slot opens. The pre-merge and the gate run only when a pull request is pulled into this buffer, one at a time.

**Pull request title.** A short headline that completes the sentence "Merging this pull request will ...". It starts with a verb in the imperative.

**Ready for review.** A pull request that is marked for review, not a draft. When a card moves to Auto Review, its pull request becomes ready for review.

**Ready queue.** The queue of finished pull requests that wait to be pulled into Pending. Each one has a clean automated review and a passing post-check on its head. It is not merged into the staging branch, not deployed, and not gated, until the pull step takes it. Pull requests wait here by milestone, then by fewest conflicts with the current stack, then by age. The exact name and the implementation, a board column or an internal sorted list, are open. See [Just-in-time Human Review flow](review.md#just-in-time-human-review-flow).

**Root-cause rule.** Fix the cause of a finding, write a list of its neighboring cases, and test each one.

**Round.** One automated review of the current head. There is a maximum number of rounds.

**Stacked pull request.** A pull request whose head also has the changes of a base pull request that is in Human Review. Its body starts with a banner that names the base. Human Review holds a maximum of one stacked pull request. If the human rejects the base, the coordinator resets the stacked pull request to its plain branch before the human can merge it.

**Staging.** A test environment that the staging branch feeds. The staging branch is an integration branch. It is never merged into main. The branch collects many changes. Thus the commit that staging serves is usually a merge that contains the head of a pull request, not the head itself.

**Swarm assignment.** The `swarm` label on an issue. An issue in Active must have this label. It must also have open sub-issues or a linked open pull request.

**Triage.** The column for open issues that have suggested plans. They wait on the human to decide.

**Worker agent.** A coding agent in a terminal session. It owns one change.
