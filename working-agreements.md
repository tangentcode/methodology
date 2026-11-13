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

An issue title tells the present state. Never write an issue title as a wish.

- A plain statement, such as "X does Y", is a bug report. It means that this occurs now, and we do not want it.
- A wanted change uses "should". Example: "Save As should work for every file that can be saved". Do not write "Save As works for every file that can be saved".
- Each issue has a GitHub issue type: Feature, Bug, or Task. Use Bug when the title tells about a present behavior that we do not want. Use Feature when the title tells about a wanted change. Use Task for a specific piece of work that is not a user feature and not a bug.

A pull request title completes the sentence "Merging this pull request will ...". It starts with a verb in the imperative. Example: "Make the Save As command work for every file that can be saved".

Team-specific title prefixes are in [team-conventions.md](team-conventions.md).

## Scope

- One worker, one change, one branch, one pull request. A change is a full issue or a named part of one. You can divide an issue into many pull requests. Each pull request links its issue with `Fixes` or `Part of`.
- A worker can find and show a real defect near its change. Then it fixes the defect in the same change, with a regression test. The coordinator does not ask the human whether to fix a defect that the worker showed.
- Ideas that are not related to the change become new issues in Triage. The human decides them there, in a comment or by a move to Active or to Backlog, before a worker starts.
- Items that the human parked stay parked until he says otherwise.

## Sessions and machines

- Do not close or stop worker sessions without the approval of the maintainer. The only exception is the memory rule in "Park and resume workers" below.
- Keep temporary files in the directory of the worker, not in a shared temporary directory.
- Look at the machine load before you start many workers at the same time.
- Give each worker window a name with the repository code, the pull request number, and the branch. The team rules for these names are in [team-conventions.md](team-conventions.md).

### Resource limits for workers

Each worker agent and each test run on the shared build machine starts inside its own cgroup slice. The slice has a limit for memory and CPU. The start tools apply the limit automatically. Apply the limit to the command inside the terminal pane, not to the terminal client. A limit on the client only does not apply to the process that the terminal server starts.

There is no fixed maximum number of workers. Look at the free resources before you start more workers. When you report a resource problem, give numbers: memory use and limit of the slice, swap use, available memory, CPU use, and system load. Local tests also use the two-slot throttle and the targeted-test rules in [review.md](review.md).

### Park and resume workers

Park workers only when memory is low. Memory is low when the slice is near its memory limit, or when there is no space for a new or held worker. When there are only a few workers and sufficient free resources, let all of them continue.

Stop idle workers in sequence, the worker that is idle for the longest time first. Stop when there is sufficient space. Before you stop a worker, make sure of these three conditions:

- Its worktree is clean.
- It pushed all its work.
- It is idle at an empty prompt.

Do not stop a worker that writes, tests, or waits at a permission prompt.

Before you stop a worker, record it in a registry. Keep these items: the saved session identifier, the worktree, the branch, the pull request, the last pushed head, the idle time, and the resume command. Resume is one command. It starts the saved session again in the same worktree, inside the limit. The start tool must not start a new session by mistake.

Automation resumes a parked worker when its pull request needs more work: review findings, more changes, conflicts, or a comment that needs an action. If there is no space for the worker, use this same rule to make space, and keep the worker in a queue until there is space. When you park a worker, you do not park or cancel its issue.

## Records

- Record each decision that the coordinator makes without the human: what, why, and the evidence. The human must be able to audit a run that had no supervision.
- Report times in the time zone of the human.
