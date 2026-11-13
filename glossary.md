# Glossary

**Active.** The column for open issue cards that are assigned to the swarm and have open sub-issues or a linked open pull request.

**Automated reviewer.** A code-review service that reads a pull request and posts prioritized findings.

**Backlog.** The column for issues that no pull request has picked up yet. Issues define scope. Pull requests carry the work through the other columns.

**Board.** The project tracker with one card per issue or pull request, arranged in columns.

**Brief.** The owner bot's written instructions to a worker for one change: a whole issue, or a named part of one.

**Coordinator bot.** The agent that runs the pull-request loop, forwards Triage comments to the owner bot, steers workers, checks changes, and moves cards.

**Draft.** A pull request that is not ready for review. Changes in In Progress are drafts.

**Finding.** A defect a reviewer reports. P1 must be fixed. P2 should be fixed before human review.

**Gate.** The set of conditions a pull request must meet before its card moves to Human Review. Each condition is checked on the current head, by automation as well as by people.

**Head.** The latest commit on a pull request's branch. Checks apply to the current head only.

**Human owner.** The person who decides Triage issues, reviews finished work, merges to main, and deploys.

**Main.** The production branch. Only the human merges into it.

**Needs Input.** The column for draft pull requests where a human must answer a question from the worker or the coordinator.

**Owner bot.** The agent that owns product decisions for an area of the board: Triage options, questions on Triage issues, and briefs.

**Neighboring cases.** Other instances of the same class of defect as a finding.

**Ops agent.** The one agent allowed to make root-level changes on shared machines.

**Human Review.** The column for finished pull requests that wait on the human to test and merge to main. It holds any number of independent pull requests. When it holds only one pull request, it can also hold one stacked pull request built on that one.

**Independent pull request.** A pull request that merges cleanly onto main, contains no unmerged commits of another Human Review pull request, and merges cleanly together with each Human Review pull request. The human can merge or reject it without an effect on the others.

**Pending.** The column for a short, ordered buffer of finished pull requests that are ready to merge and that do not conflict with the current Human Review pull requests or with each other. The buffer is rebased ahead of time, kept small, and refilled after each Human Review decision.

**Stacked pull request.** A pull request whose head also contains the changes of a base pull request that is in Human Review. Its body starts with a banner that names the base. Human Review holds at most one, and only when the base is the only other pull request there. If the base is rejected, the coordinator resets it to its plain branch before the human can merge it.

**Ready.** A pull request marked for review. Moving a card to Auto Review marks it ready.

**Root-cause rule.** Fix the cause of a finding, list its neighboring cases, and test each one.

**Round.** One automated review of the current head. Rounds have a cap.

**Swarm assignment.** The `swarm` label on an issue. An issue in Active must carry it, and must also have open sub-issues or a linked open pull request.

**Triage.** The first board column. New issues wait here for the owner bot to propose options and the human to decide.

**Staging.** A test environment fed by the staging branch, an integration branch that is never merged into main. Because the branch collects many changes, the commit staging serves is usually a merge that contains a pull request's head, not the head itself.

**Worker agent.** A coding agent in a terminal session that owns one change.
