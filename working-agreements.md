# Working agreements

## Messages

- Send a message only when a person must act or decide. Do not send acknowledgements. Do not repeat a report.
- Give the result first. Put the details after it.
- Do not ask other bots again and again about open items. Wait for them, or tell the human about the item.
- Speak to worker agents only through the approved message tool. Never type into their sessions by hand.
- Write the choices of the human into the brief the first time. Then the human does not have to say them again in review.

## Writing style

Use this style in all chats, issues, pull request descriptions, commit messages, briefs, and documents:

- Follow ASD-STE100 (Simplified Technical English).
- Use simple, clear, direct English. Use short sentences. Use one instruction in each sentence.
- Use ASCII characters only. Do not use emojis, Unicode symbols, smart quotes, or long dashes. Use a straight quote (' or ") and a hyphen (-).

## Issue and pull request titles

A feature request title says what the thing should do. Example: "PTW mouse back button should undo the last annotation while dictating".

A plain present-tense title is a bug report: a complaint about current behavior. Example: "PTW mouse back button undoes the last annotation while dictating" means that this occurs now, and we do not want it.

Do not write a feature request as a present-tense statement. That reads as a bug report.

- A wanted change uses "should". Example: "Save As should work for every file that can be saved". Do not write "Save As works for every file that can be saved".
- Each issue has a GitHub issue type: Feature, Bug, or Task. Use Bug when the title tells about a present behavior that we do not want. Use Feature when the title tells about a wanted change. Use Task for a specific piece of work that is not a user feature and not a bug.

The pull request that implements a feature is titled as an imperative. It completes the sentence "Merging this pull request will ...". Example: "Make the back button undo the last annotation while dictating".

A title must read as a plain sentence. Keep the articles ("a", "an", "the"). When the title talks about a literal word, put that word in quotation marks. Example: a feature-request title uses the word "should".

Do not drop words to make a headline. Do not stack words that can be a noun or a verb, such as list, move, title, issue, feature, gate, sweep, stage, review, mark, check, track, cut, record, or save. A reader must be able to parse the title without reading the body.

Examples:

- Hard to parse: "List search should use one shared filter component". Clear: "Search boxes on list pages should use one shared filter component".
- Hard to parse: "ptw: mark a move right or wrong (! / ?) with check/X icon and coin/buzzer sound". Clear: "ptw: the board should let the user mark a move as right or wrong, with a check or X icon and a coin or buzzer sound".
- Hard to parse: "Track bottom/side panel open state in URL hash ($D:...)". Clear: "The URL hash should remember whether the bottom and side panels are open".
- Hard to parse: "Move media storage to Cloudflare R2 with browser caching". Clear: "Media files should be stored on Cloudflare R2 and cached in the browser".

Keep titles short, but not at the cost of a clear parse.

Team-specific title prefixes are in [team-conventions.md](team-conventions.md).

## Scope

- One worker, one change, one branch, one pull request. A change is a full issue or a named part of one. You can divide an issue into many pull requests. Each pull request links its issue with `Fixes` or `Part of`. Only one of those pull requests is in a flow column at a time. If a follow-up must run at the same time as the first change, for example to supply evidence, make the follow-up a separate issue.
- A worker can find and show a real defect near its change. Then it fixes the defect in the same change, with a regression test. The coordinator does not ask the human whether to fix a defect that the worker showed.
- Ideas that are not related to the change become new issues in Triage. The human decides them there, in a comment or by a move to Active or to Backlog, before a worker starts.
- Items that the human parked stay parked until he says otherwise.

## Sessions and machines

- Do not close or stop worker sessions without the approval of the maintainer. The only exception is an idle agent: close it with `/exit`, as "Close idle agents with /exit" below tells. Never kill a worker window or its processes.
- Keep temporary files in the directory of the worker, not in a shared temporary directory.
- Look at the machine load before you start many workers at the same time.
- Give each worker window a name with the repository code, the pull request number, and the branch. The team rules for these names are in [team-conventions.md](team-conventions.md).

### Resource limits for workers

Each worker agent and each test run on the shared build machine starts inside its own cgroup slice. The slice has a limit for memory and CPU. The start tools apply the limit automatically. Apply the limit to the command inside the terminal pane, not to the terminal client. A limit on the client only does not apply to the process that the terminal server starts.

There is no fixed maximum number of workers. Look at the free resources before you start more workers. When you report a resource problem, give numbers: memory use and limit of the slice, swap use, available memory, CPU use, and system load. Local tests also use the two-slot throttle and the targeted-test rules in [review.md](review.md).

### Close idle agents with /exit

This rule is from the maintainer, 2026-11-15 4:40 AM ET: "Idle agents should be closed with /exit ... We can always resume them. (Close the agent not the tmux window)". It replaces the earlier rule that stopped idle workers only when memory was low.

- An agent is idle when its pull request is in Auto Review, Needs Input, Ready, Staging, or Human Review, or when it has no work. Close an idle agent with `/exit`. Do not wait until memory is low. The Needs Input case is from the maintainer, 2026-11-15 6:45 PM ET (tangentswarm #40, item 4): the question is on the ticket, and the answer resumes the agent.
- Close the agent, not the tmux window. The window, its shell, the worktree, and the branch stay.
- Never kill the window, its shell, or its processes to close an idle agent. Send only `/exit`.
- An exited agent does not count toward the Claude cap. Only a live agent process counts.
- Resume the agent later in the same window: `claude --resume <session>`, or `claude --continue` when the session identifier is not known.

We also call this step "park". A parked worker is an agent that exited with `/exit` and that has its window, its saved session, and its worktree.

Send `/exit` only when these three conditions are true:

- Its worktree is clean.
- It pushed all its work.
- It is idle at an empty prompt.

There is one exception. An agent whose card is in Needs Input can have uncommitted work when it is closed. Its worktree and its files stay, and the resume starts the agent in that worktree.

An agent that writes, tests, or waits at a permission prompt is not idle. Do not close it.

Before you close an agent, record it in a registry. Keep these items: the saved session identifier, the window, the worktree, the branch, the pull request, the last pushed head, the idle time, and the resume command. Resume is one command. It starts the saved session again in the same window and worktree, inside the limit. The start tool must not start a new session by mistake.

Automation resumes a parked worker when its pull request needs more work: review findings, more changes, conflicts, or a comment that needs an action. If the Claude cap is full or memory is low, the resume waits in a queue until there is space. When you park a worker, you do not park or cancel its issue.

## Records

- Record each decision that the coordinator makes without the human: what, why, and the evidence. The human must be able to audit a run that had no supervision.
- Report times in the time zone of the human.
