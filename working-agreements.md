# Working agreements

## Communication

- Send a message when someone has to act or decide. Don't send acknowledgements, and don't repeat a report.
- Lead with the result. Put details after.
- Don't chase other bots about open items. Wait for them or raise the item with the human.
- Talk to worker agents only through the sanctioned messaging tool, never by typing into their sessions by hand.
- Write the human's stated choices into the brief the first time, so he doesn't have to repeat them in review.

## Writing style

Use this style in all chats, issues, pull request descriptions, commit messages, and briefs:

- Follow ASD-STE100 (Simplified Technical English).
- Use simple, clear, direct English. Use short sentences. Use one instruction in each sentence.
- Use ASCII characters only. Do not use emojis, Unicode symbols, smart quotes, or long dashes. Use a straight quote (' or ") and a hyphen (-).

## Issue and pull request titles

Issue titles describe the present state. Never word an issue title as an aspiration.

- A plain statement such as "X does Y" reads as a bug report. It means this happens now, and we do not want it.
- A wanted change uses "should". Example: "Save As should work for every file that can be saved". Do not write "Save As works for every file that can be saved".
- Every issue has a GitHub issue type: Feature, Bug, or Task. Use Bug when the title states a present, unwanted behavior. Use Feature when the title states a wanted change. Use Task when the work is a specific piece of work that is not a user-facing feature or a bug.

Pull request titles complete the sentence "Merging this pull request will ...". They start with an imperative verb. Example: "Make the Save As command work for every file that can be saved".

## Scope

- One worker, one change, one branch, one pull request. A change covers a whole issue or a named part of one. Splitting an issue across several pull requests is fine. Each pull request links its issue with `Fixes` or `Part of`.
- When a worker finds and demonstrates a real defect next to its change, it fixes it in the same change with a regression test. The coordinator doesn't ask the human whether to fix a demonstrated defect.
- Unrelated ideas become new issues in Triage. The human decides them there before a worker starts.
- Items the human has parked stay parked until he says otherwise.

## Sessions and machines

- Don't close or kill worker sessions without the maintainer's approval, except for the memory-pressure parking policy below.
- Keep temporary files in the worker's own directory, not a shared temp directory.
- Check machine load before starting many workers at once.
- Name each worker's tmux window `<code>-<PR>-<branch>`.
  - `code` is a short code for the git repository, not the product. Every window for the platform repository uses `mn`. The methodology repository uses `meth`. Other repositories each have their own short code; the swarm tooling repository uses `swarm`.
  - `PR` is the pull request number, not the issue number. Do not pad the number with zeros. For a speculative branch named `<branch>-vN`, use the pull request number of the base branch.
  - `branch` is the branch name with each `/` replaced by `-`.
  - Keep the windows in a session sorted by name, so that codes stay in groups and, inside a group, pull request numbers stay in numeric order.
  - Example: a platform window for pull request 372 on branch `mn-view-renders` is named `mn-372-mn-view-renders`.

### Worker resource limits

Every worker agent and every test run on the shared build box starts inside a dedicated memory- and CPU-capped cgroup slice. Launcher tooling applies the cap automatically. Wrap the command inside the terminal pane, not the terminal client: wrapping only the client does not cap the process the terminal server starts.

There is no fixed worker-count limit. Check headroom before launching more. Report resource trouble with numbers: slice memory use and limit, swap use, available memory, CPU use, and system load. Local tests also use the two-slot throttle and targeted-test rules in [review.md](review.md).

### Parking and resuming workers

Park workers only under memory pressure: when the slice is near its memory limit, or when a new or held worker cannot fit. With only a few workers and enough headroom, leave them all running.

Exit eligible idle workers longest-idle first, stopping as soon as there is room. Before exiting one, verify all three conditions: its worktree is clean, all its work is pushed, and it is idle at an empty prompt. Do not stop a worker still writing, testing, or waiting at a permission prompt.

Record a parked worker in a registry before exiting it. Keep its saved session identifier, worktree, branch, PR, last pushed head, idle time, and resume command. Resuming is one command that relaunches the saved session in the same worktree, inside the cap; the launcher must not start a fresh session by mistake.

Automation resumes a parked worker when its PR needs more work: review findings, rework, conflicts, or a comment requiring action. If it cannot fit, free room using this same policy and keep it queued until there is headroom. Parking a worker does not park or cancel its issue.

## Records

- Log each decision the coordinator makes on its own: what, why, and the evidence. The human should be able to audit an unattended run.
- Report times in the human's time zone.
