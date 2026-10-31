# Glossary

**Automated reviewer.** A code-review service that reads a pull request and posts prioritized findings.

**Board.** The project tracker with one card per issue or pull request, arranged in columns.

**Brief.** The coordinator's written instructions to a worker for one issue.

**Coordinator bot.** The agent that runs the workflow, steers workers, checks changes, and moves cards.

**Draft.** A pull request that is not ready for review. Changes in In Progress are drafts.

**Finding.** A defect a reviewer reports. P1 must be fixed. P2 should be fixed before human review.

**Gate.** The set of conditions a pull request must meet before its card moves to Human Review. Each condition is checked on the current head, by automation as well as by people.

**Head.** The latest commit on a pull request's branch. Checks apply to the current head only.

**Human owner.** The person who approves work, reviews it, merges to main, and deploys.

**Main.** The production branch. Only the human merges into it.

**Neighboring cases.** Other instances of the same class of defect as a finding.

**Ops agent.** The one agent allowed to make root-level changes on shared machines.

**Pending.** The column for work that is otherwise ready but blocked on another change or decision.

**Ready.** A pull request marked for review. Moving a card to Auto Review marks it ready.

**Root-cause rule.** Fix the cause of a finding, list its neighboring cases, and test each one.

**Round.** One automated review of the current head. Rounds have a cap.

**Staging.** A test environment fed by the staging branch, an integration branch that is never merged into main. Because the branch collects many changes, the commit staging serves is usually a merge that contains a pull request's head, not the head itself.

**Worker agent.** A coding agent in a terminal session that owns one change.
