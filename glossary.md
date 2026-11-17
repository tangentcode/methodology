# Glossary

**Active.** The column for open issue cards that are assigned to the swarm. Each one does not have the `work2` label, and each one has exactly one open linked pull request in a flow column (In Progress, Auto Review, Needs Input, Ready, Staging, or Human Review). The number of cards in Active equals the number of pull requests in those flow columns that belong to issues without the `work2` label. A pull request of a `work2` issue still moves through the flow columns, but it does not count in that total. A pull request in a flow column belongs to exactly one Active issue. If one pull request fixes more than one issue, only one of those issues is in Active. An Active issue has only one pull request in a flow column at a time. If a follow-up must run at the same time as the first change, make the follow-up a separate issue. A move of an issue to this column, with no comment, is sufficient approval to start its worker.

**Automated reviewer.** A code review service. It reads a pull request and writes findings with priorities.

**Backlog.** The column for issues that have an approved plan and that no pull request has started yet. Issues set the scope. Pull requests move the work through the other columns.

**Board.** The project tracker. It has one card for each issue or pull request, in columns.

**Brief.** The written instructions of the owner bot to a worker for one change. A change is a full issue or a named part of one.

**Cheap check.** The only check when a Staging pull request moves to Human Review. The head did not change since the gate, the pull request still merges with main and with each Human Review pull request, and no person commented after the gate, except comments that the coordinator cleared. The full gate does not run again. See [Promotion from Staging](review.md#promotion-from-staging).

**Coordinator bot.** The agent that runs the pull request loop. It sends Triage comments to the owner bot, steers workers, checks changes, and moves cards.

**Discuss.** The column for issues that need careful thought or a conversation. They wait here so that simple Triage items move first. The human writes comments on the issue. The agent then writes the issue body again to agree with the answers. This continues until the issue is ready for Backlog or Active. No worker starts on a Discuss item. The coordinator does not count it as waiting on the human. Agents do not move the card forward themselves.

**Draft.** A pull request that is not ready for review. Changes in In Progress are drafts.

**Fast track.** A maintainer mark, the `fast-track` label, that moves one ticket to the front of every queue. Several tickets may carry the label at the same time, but only one of them runs through the fast track at a time. The next labeled ticket starts when the current one enters Human Review, or when the current one leaves the fast track before that, because it is canceled or the maintainer removes the label. Fast track changes the order of work. It does not change the quality bar. The ticket must pass every gate. It takes the first Staging slot, even when the pull requests behind it must be restacked. It does not stop a pull that is already running. It waits for the shared lock. It does not push a pull request out of Human Review. See [Fast track](review.md#fast-track).

**Finding.** A defect that a reviewer reports. You must fix a P1. You must fix a P2 before human review.

**Gate.** The conditions that a pull request must meet before it enters Staging. Automation and people check each condition on the current head, during the pull step, one pull request at a time. The full gate runs one time, at Staging entry. A later move from Staging to Human Review is a card move after the cheap check. After a merge to main, only the merge with main is checked again. See [Promotion from Staging](review.md#promotion-from-staging) and [After a merge to main](review.md#after-a-merge-to-main). A gate check, a promotion from Staging, and a merge into the staging branch share one lock, `~/.cache/swarm-serial.lock`, so only one of them runs at a time. The just-in-time cascade holds that lock for the whole run. A second caller queues a rerun, and the process that holds the lock drains every queued rerun before it exits. Gate operations skip draft pull requests and pull requests that are still in Ready. See [The just-in-time cascade](review.md#the-just-in-time-cascade).


**Head.** The latest commit on the branch of a pull request. Checks apply only to the current head.

**Human owner.** The person who decides Triage issues, reviews finished work, merges to main, and deploys.

**Human Review.** The column for finished pull requests that wait on the human to test them and merge them to main. It holds exactly two pull requests whenever two prepared pull requests are available, and never more than two. The next card comes from the front of Staging, as a card move after the cheap check, in seconds after a slot opens. When it holds only one pull request, the first Staging pull request can go in as a stacked pull request if it depends on that one.

**Inbox.** The column for items that are out of the flow for now, and, after launch, for new tickets from customers. Issues with the `work2` label stay here, even when they have a linked pull request.

**Independent pull request.** A pull request that merges cleanly onto main, has no unmerged commits of another Human Review pull request, and merges cleanly together with each Human Review pull request. The human can merge or reject it with no effect on the others.

**Issue title.** A short headline for an issue. A feature request title says what the thing should do, and uses "should". A plain present-tense title, such as "X does Y", is a bug report: it occurs now, and we do not want it. A title must read as a plain sentence. Keep the articles. Quote each literal word that the title discusses. A reader must be able to parse the title without reading the body.

**Issue type.** A GitHub type on each issue: Feature, Bug, or Task.

**Main.** The production branch. Only the human merges into it.

**Mockup.** A picture or sketch in a Triage issue that shows how the change should look or work. Whoever writes the issue adds it, whenever that is possible. The usual form is a heading, a PNG or a mermaid or text sketch, and a short caption that starts "Mockup, not staging." See [Triage](workflow.md#triage).

**Needs Input.** The column for draft pull requests where a human must answer a question from the worker or the coordinator.

**Neighboring cases.** Other examples of the same class of defect as a finding.

**Ops agent.** The only agent that can make root-level changes on shared machines.

**Owner bot.** The agent that owns the product decisions for an area of the board: Triage options, questions on Triage issues, and briefs.

**Pending.** The former name of the Staging column. The board option id did not change when the column was renamed. Cards kept their status. Tools must match the option id, not the name. See [Staging](#staging).

**Pull request title.** A short headline that completes the sentence "Merging this pull request will ...". It starts with a verb in the imperative.

**Ready.** The column for finished pull requests that wait to be pulled into Staging. It sits on the board between Needs Input and Staging. It is the buffer of finished work, because a merge is easier than a first implementation. The worker is done, the automated review is clean, and the post-check of the coordinator passed on the head. A MinBot pass comment names the exact head. The pull request is not merged into the staging branch, not deployed, and not gated. It is not on the staging environment. The coding agent process has exited, but its terminal session, branch, and worktree stay. Agents work Active issues until their pull requests are in Ready. See [Coding agent slots](review.md#coding-agent-slots). The active fast-track pull request waits first, when it is in Ready. Then pull requests wait by milestone, then by fewest conflicts with the current stack, then by age. See [Just-in-time Human Review flow](review.md#just-in-time-human-review-flow) and [Fast track](review.md#fast-track).

**Ready for review.** A pull request that is marked for review, not a draft. When a card moves to Auto Review, its pull request becomes ready for review.

**Root-cause rule.** Fix the cause of a finding, write a list of its neighboring cases, and test each one.

**Round.** One automated review of the current head. There is a maximum number of rounds.

**Stacked pull request.** A pull request whose head also has the changes of a base pull request that is in Human Review. Its body starts with a banner that names the base. Human Review holds a maximum of one stacked pull request. If the human rejects the base, the coordinator resets the stacked pull request to its plain branch before the human can merge it.

**Staging.** The board column, formerly named Pending, with no fixed cap. Any Ready pull request that merges cleanly, by `git merge-tree`, with main, the staging branch (`work`), and every Human Review and Staging pull request may enter. The tools cache a conflict map per head SHA. When the column drops below a floor (default 2), the cascade pulls the next clean Ready pull request. Each Staging pull request is already merged into the staging branch, deployed, verified, and gated. The expensive steps (the work merge, the redeploy, and the gate) happen only at pull time. Never rebase or rework a pull request just to fill Staging. The first Staging pull request goes into Human Review immediately when a slot opens, after only the cheap check. After a merge to main, only the merge with main is checked again. Only this column and Human Review are on the staging environment.

**Staging environment.** A test environment that the staging branch feeds. The staging branch is an integration branch. It is never merged into main. Only pull requests in the Staging column and in Human Review are merged into that branch and deployed here. Thus the commit that the staging environment serves is usually a merge that contains the head of a pull request, not the head itself.

**Swarm assignment.** An issue is assigned to the swarm when it is on the Project 4 card or has the swarm assignee. The `swarm` label is retired. Do not add it. An issue in Active must be assigned in this way. It must also have exactly one open linked pull request in a flow column, and it must not have the `work2` label.

**Triage.** The column for open issues that wait on the human to review or decide. This includes issues that have suggested plans, and proposals or new rules that wait on a decision. The human decides in a comment, or by a move of the issue to Active or to Backlog. Every board has this column, including the board that tracks this methodology. Finished pull requests that wait on the human stay in Human Review. Draft pull requests that wait on an answer stay in Needs Input.

**work2.** A label that keeps an issue in Inbox, even when the issue has a linked pull request. The pull request of a `work2` issue still moves through the flow columns in the usual way, but it does not move the issue out of Inbox and it does not count in the Active total.

**Worker agent.** A coding agent in a terminal session. It owns one change.
