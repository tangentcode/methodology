# Working agreements

## Communication

- Send a message when someone has to act or decide. Don't send acknowledgements, and don't repeat a report.
- Lead with the result. Put details after.
- Don't chase other bots about open items. Wait for them or raise the item with the human.
- Talk to worker agents only through the sanctioned messaging tool, never by typing into their sessions by hand.
- Write the human's stated choices into the brief the first time, so he doesn't have to repeat them in review.

## Scope

- One worker, one issue, one branch, one pull request.
- When a worker finds and demonstrates a real defect next to its change, it fixes it in the same change with a regression test. The coordinator doesn't ask the human whether to fix a demonstrated defect.
- Unrelated ideas become new issues in Backlog, approved by the human before work starts.
- Items the human has parked stay parked until he says otherwise.

## Sessions and machines

- Don't close or kill worker sessions without the maintainer's approval, except for the memory-pressure parking policy below.
- Keep temporary files in the worker's own directory, not a shared temp directory.
- Check machine load before starting many workers at once.

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
