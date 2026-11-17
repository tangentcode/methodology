# Proposal: one flow for every board

> **Status: proposal. Not adopted.** This page is for review only. Nothing on this page is built until Michal accepts it, rejects it, or changes it. Discussion: [tangentswarm #107](https://github.com/tangentcode/tangentswarm/issues/107).

- **Request:** Michal, 2026-11-17 8:52 AM ET: the swarm server should be one process that works the same on any board.
- **Code checked:** tangentswarm `origin/main` at `2cec62e` (2026-11-17). File and function names on this page are at that commit.
- **Work in flight:** tangentswarm [#98](https://github.com/tangentcode/tangentswarm/issues/98) (PR #108), [#101](https://github.com/tangentcode/tangentswarm/issues/101) (PR #109) and [#105](https://github.com/tangentcode/tangentswarm/issues/105) (PR #110) are being built now. This plan treats them as current code. It does not wait for them. Each step below says where their code goes.

## Summary

The server was built for the platform board (Project 4). The methodology board (Project 6) came later. Where a platform rule did not fit, we added a second copy of the code for Project 6. So each new feature is built two times.

Half of the fix is already there. `tangentswarm/board.py` has a `Board` class, and the private config file already has a `[[boards]]` list with each board's number, repos, columns and a `staging` flag. But most of the code does not use it. About 20 files still say "the repo is `tangentcode/platform`" in a constant, and the webhook asks `platform()` 15 times.

The plan:

1. Add the missing settings to each board's entry in the config file.
2. Change the code, one area at a time, to read the board's settings and not ask "is this platform?".
3. When both boards run on the shared code for an area, delete the Project 6 copy of that area.

Each step is a small PR. Each step keeps both boards working. No step needs a big cut-over.

## What the boards do differently today

These are the real differences between the two boards. Each one becomes a setting. Nothing else should differ.

| Difference | Platform (Project 4) | Methodology (Project 6) |
|---|---|---|
| Repos | `tangentcode/platform` | `tangentcode/tangentswarm`, `tangentcode/methodology` |
| Staging step | Yes: Ready -> Staging -> Human Review. The PR head must be served on the staging sites | No: Ready -> Human Review |
| Who merges | Michal, from Human Review | The server, when the worker says done (`p6merge`) |
| Window name | `<code>-<PR>-<slug>`, for example `mn-` | `swarm-<PR>-<slug>`, `meth-<PR>-<slug>` (one code for each repo) |
| Worktree name | `~/ver/platform.<slug>` | `~/ver/tangentswarm.<slug>`, `~/ver/methodology.<slug>` |
| Worker limits | 3 new, 4 while Ready is short, 3 rework | About 4 live workers, no rework slots |
| Human Review size | 2 (`flow.HR_TARGET`) | 2 (`boardflow.HR_TARGET`, a second constant) |
| Who gets the exceptions | swarmbot (wake URL) | MethBot |
| How the worker ends | Stop hook marks the PR ready and asks Codex | `handoff` reports done. The server verifies and merges |
| Labels and milestones sync | Yes (`swarm-label-sync`) | No |
| MinBot check | Through `mn-workflow` and `hr-gate` in `~/bin` | `boardflow.minbot_repo` in this repo |

Some of these differences are real choices (staging, who merges). Some exist only because the code was written two times (two `HR_TARGET` constants, two ways to count live workers). The second kind goes away. It does not become a setting.

## Every place the code checks for platform or Project 6

Grouped by area. "Platform only" means the code works on Project 4 and silently does nothing on Project 6.

### Board reading

- `board.py`: `DEFAULT` is the platform board. `BOARDS[1:]` are "the others". The default repo is `tangentcode/platform` when the config has none.
- `boardcache.py`: a 60-second snapshot of the board, for platform only (`REPO`). Project 6 is read fresh each time by `boards.open_prs`.
- `promoted.py`: reads the platform board by itself (`read_board`). `BOARD_EVERY` queues the promote pass only for boards with no staging.
- `status_api.py`: `b is board.DEFAULT` picks the fast-track ticket and the snapshot path. `b.staging` picks the columns and the Human Review size.
- `sanity.py`: `board.DEFAULT.number` turns on the deferred rule. `BOARDS[1:]` read the other boards. The launch records are "platform numbers only".

### Moving cards (the flow)

- `advance.py`: `REPO` is platform. `--repo` and `--promote-board` exist only for "a board without staging".
- `boardflow.py`: the whole file is the no-staging copy of the MinBot check and of promote, with its own `HR_TARGET`.
- `flow.py`: `REPO` is platform. `HR_TARGET` is the platform Human Review size. Label edits use the platform repo.
- `flowstatus.py`: reads only open platform PRs.
- `gatechecks.py`, `gitpush.py`: the staging checks and the push from the hr-gate scratch repo. Platform only, and right to be so: they belong to the staging step, not to the board.
- `labels.py`: label and milestone sync. Platform only.

### Starting workers

- `launcher.py`: `REPO` and `GIT` are platform. The window is `mn-<PR>-<slug>`.
- `launches.py`: checks for a second Claude in `~/ver/platform.<branch>`.
- `brief.py`: `REPO` is platform unless `SWARM_BRIEF_REPO` is set.
- `slots.py`: the slot counts (`NEW_SLOTS`, `REWORK_SLOTS`) are platform numbers. `live_claudes()` counts only `~/ver/platform.*`. `P6_PREFIX`, `p6_worker()` and `tell_p6()` are the Project 6 copies.
- `p6merge.py`: `LIVE_TARGET`, `live_workers()` and the Backlog pull are the Project 6 copy of slot counting and starting. `WINDOW_CODE` maps each Project 6 repo to its window code.
- tangentswarm #98 (PR #108, being built) adds a Project 6 launcher. That is a second copy of `launcher.py`.

### Worker sessions

- `stophook.py`: runs only in `~/ver/platform.<slug>`. Project 6 uses `handoff` instead.
- `worker_mcp.py`: `p6_pr()`, `p6_only()`, `p6_done()` and `p6_needs_input()` are the Project 6 copies. `worker_status` and `request_review` refuse in a Project 6 worktree.
- `panewatch.py`: watches only `~/ver/platform.<slug>` panes.
- `tick.py`: `PLATFORM_GIT` and `REPO`. It classifies only platform worktrees.
- `watchdog.py`: `REPO`, `PLATFORM_GIT`, and a Codex query with the platform repo name written in it.
- `codexrounds.py`: `REPO` is platform. A row with no repo is a platform row.
- `mcp_server.py`, `registry.py`: name the plain checkout `platform` in examples. Small.

### Webhook and alerts

- `webhook.py`: `platform()` is `repo == 'tangentcode/platform'`. It is asked in 15 places: the card read, the MinBot check, the relay to a worker, the root-cause text, which wakes to skip, the promote step, the active gate, the label sync, the launch records. `ROOT_CAUSE_P6`, `P6_NO_WAKE`, `p6_merge_ready()`, `do_p6merge()` and `do_p6cleanup()` are the Project 6 copies. tangentswarm #105 (PR #110, being built) adds two more copies: the rejection relay and the answer relay.
- `events.py`: `platform = repo == REPO`. Only platform events queue a MinBot check from here.
- `events_view.py`: `PLATFORM` hides the repo name for platform rows.
- `alerts.py`: `METHBOT_REPOS` is the Project 6 repo list, written a second time. MethBot is woken only for those repos.
- `needsinput.py`: `REPO` is platform.
- `p6merge.py`: the whole server-side merge. It is Project 6 only because platform merges by hand.

### Outside this repo

- `~/bin/hr-gate`, `~/bin/swarm-start-scoped` and `mn-workflow` know only platform. This plan does not move them. Where the shared code needs their job on another board, it calls the code in this repo (as `boardflow` does now for the MinBot check).

## The per-board settings

All settings go in the board's entry in the private config file (`~/.config/tangentswarm/config.toml`). No new file. The config already holds the board number, ids, columns, repos and the staging flag. This adds the rest.

Today the platform board is under `[project]` and the others are under `[[boards]]`. The first step makes every board a `[[boards]]` entry, and keeps reading `[project]` as the first board for as long as the live config has it.

```toml
[[boards]]
name = "platform"
number = 4
id = "PVT_example"
status_field = "PVTSSF_example"
repos = ["tangentcode/platform"]

# Window and worktree names. One code for each repo.
window_codes = { "tangentcode/platform" = "mn" }
# Worktree: ~/ver/<repo name>.<slug>. The same rule for every board.

# Staging. Absent or empty: Ready goes to Human Review directly.
staging_sites = { work = "work.example.test", minavo = "minavo.example.test" }

# Who merges after Human Review: "human" (Michal) or "server" (merge on the worker's done).
merge = "human"

# How the worker ends: "stop-hook" (mark ready, ask Codex) or "done" (verify and merge).
handoff = "stop-hook"

# Who gets the exceptions the server cannot handle.
coordinator = "swarmbot"

# Sync labels and milestones on this board's PRs.
label_sync = true

[boards.limits]
new_workers = 3           # new-work Claudes to keep running
new_workers_short = 4     # ... while Ready is short
rework_workers = 3        # Claudes that fix a PR that went back to In Progress
human_review = 2          # PRs that may wait in Human Review

[boards.options]
"Inbox" = "opt-inbox"
# ... the column ids, as now


[[boards]]
name = "methodology"
number = 6
id = "PVT_example6"
status_field = "PVTSSF_example6"
repos = ["tangentcode/tangentswarm", "tangentcode/methodology"]
window_codes = { "tangentcode/tangentswarm" = "swarm", "tangentcode/methodology" = "meth" }
staging_sites = {}
merge = "server"
handoff = "done"
coordinator = "methbot"
label_sync = false

[boards.limits]
new_workers = 4
new_workers_short = 4
rework_workers = 0
human_review = 2

[boards.options]
"Inbox" = "opt6-inbox"
# ...
```

Rules for the settings:

- **Host-wide limits stay host-wide.** `MAX_CLAUDES` (10) and the RAM floor protect the one machine. They are not per board. The board limits are shares inside them.
- **Environment overrides stay.** `SWARM_NEW_SLOTS` and the others keep working, so a live service does not change when the config is read in a new way. Each one overrides the matching setting of the platform board only, as today. They can go later.
- **A repo is on one board only.** `board.for_repo(repo)` then gives every setting from a repo name. Code that has only a PR and a repo never needs to know which board it is on.
- **The window code is per repo, not per board.** Project 6 has two repos with two codes.
- **`staging_sites` replaces both `staging = true` and the `[staging]` table.** A board has a staging step if and only if it has staging sites.

## How the code changes

One rule for every change: code reads the setting from `board.for_repo(repo)` (or the board it already holds). No code compares a repo to `tangentcode/platform`, and no code compares a board to `board.DEFAULT`.

Some code is right to exist for one board only, because it does a step that only one board has. The staging checks (`gatechecks.py`, `gitpush.py`) and the server merge (`p6merge.py`) are examples. They stay. But the code that calls them asks the board's setting ("does this board have staging sites?", "does this board merge on done?"), and the file names lose `p6`.

## Migration, step by step

Each step is one small PR. Each step has tests on both boards. The order puts the cheap, safe steps first. Steps 4 to 9 do not depend on each other and can go in any order after step 3.

1. **Settings, read only.** Add the new keys to `Board` and to `config.example.toml`. Read `[project]` as the first board if it is there. Every setting has a default that matches what the code does today, so the live config needs no edit and nothing changes. Tests: each board gets the expected settings from the example file, and from a config with only `[project]`.
2. **A two-board test fixture.** One test helper that runs a test on the platform board and on the methodology board, with fake GitHub reads. Later steps use it. This is how "tests run the full flow on both boards" gets done.
3. **Replace the repo constants.** The about 20 `REPO = 'tangentcode/platform'` lines become `board.for_repo()` calls or a board passed in. `alerts.METHBOT_REPOS` and `p6merge.REPOS` become the methodology board's `repos`. No behavior change. This step is wide but each change is one line, so it can be split into two or three PRs by file.
4. **One promote step.** `boardflow.promote` and the staging cascade both read `limits.human_review`. Delete `boardflow.HR_TARGET`. The promote step picks "Ready -> Staging" or "Ready -> Human Review" from `staging_sites`.
5. **One MinBot check.** The webhook and `events.py` queue the same check for every repo. The check runs the repo-local checks for all boards, and the staging checks only when the board has staging sites. `webhook.platform()` stops being asked for the MinBot check.
6. **One worker lookup and relay.** `slots.p6_worker()` and `tell_p6()` become the one way to find the live worker of a PR on any board, from the window code and the worktree name. The Codex relay, the rejection relay and the answer relay (from #105) all use it. `ROOT_CAUSE_P6` and `ROOT_CAUSE` become one text. `P6_NO_WAKE` (Codex findings with no live worker are only logged) becomes the rule for a board with no rework workers. A board with rework workers revives a Claude, as platform does now.
7. **One way to count and start workers.** `slots.live_claudes()` and `p6merge.live_workers()` become one count, by board, from the worktree names. The platform launcher and the Project 6 launcher (from #98) become one launcher that takes the board's window code, repo and brief. The Backlog pull after a merge and the cascade fill both call it, each with the board's `limits`.
8. **One worker end.** The Stop hook and `handoff` read the board's `handoff` setting. The worker MCP serves `worker_status` and `request_review` on every board. `worker_mcp.p6_only()` goes away. `p6merge.py` is renamed to `servermerge.py` and runs when `merge = "server"`.
9. **One watch.** `panewatch.py`, `tick.py` and `watchdog.py` look at the worktrees of every board's repos, not only `~/ver/platform.*`. The wake target comes from the board's `coordinator`. `sanity.py` checks every board the same way.
10. **Clean up.** Delete what no longer has a caller: `board.DEFAULT`, `webhook.platform()`, the `p6_*` names, `P6_PREFIX`, `WINDOW_CODE`. Change the live config to the new form (`[[boards]]` only). This is the last step on purpose: until here, the old config form works.

After step 10, `git grep -n -E "tangentcode/platform|board.DEFAULT|p6"` in `tangentswarm/` finds only comments and tests.

## How #98, #101 and #105 fold in

- **#98, the Project 6 launcher (PR #108).** Build it as approved. Step 7 merges it with `launcher.py`. Its window names (`swarm-`, `meth-`) are the `window_codes` setting. Its target of about 4 workers is `limits.new_workers`.
- **#101, drop parking (PR #109).** This removes `held.json` and `retry_held`. It is not a platform vs Project 6 split. But it changes the fill step that step 7 touches. Step 7 is built on top of it: a conflicting PR waits in In Progress on any board.
- **#105, the rejection and answer relays (PR #110).** Build it as approved. Step 6 merges its lookup with the Codex relay lookup, so the three relays use one function on every board.

If one of these merges after the step that would fold it in, that step's PR gets a small follow-up. The order does not block any of them.

## Proposed tickets

These go to **Project 6 Triage**, not Backlog. Nobody starts them until Michal answers this proposal. Nothing is launched by this PR.

| # | Title | Depends on |
|---|---|---|
| A | Per-board settings: read the new keys, with today's behavior as the default | - |
| B | Test helper that runs a test on both boards | A |
| C | Replace the hard-coded platform repo with the board's settings | A |
| D | One promote step for boards with and without staging | B, C |
| E | One MinBot check for every repo | B, C |
| F | One worker lookup and relay for every board (folds in #105) | B, C |
| G | One worker count and one launcher for every board (folds in #98, after #101) | B, C |
| H | One worker end: Stop hook or done, by board setting | B, C |
| I | Pane watcher, tick and watchdog on every board's worktrees | B, C |
| J | Delete the Project 6 copies and move the live config to the new form | D to I |

## Questions for Michal

1. **Who merges.** Platform merges by hand from Human Review. Project 6 merges on the server when the worker is done. Is that a real difference to keep as a setting, or should one board move to the other's way?
2. **Rework on Project 6.** Project 6 has no rework slots today. Should it get some (`rework_workers`), or stay at 0?
3. **Label sync on Project 6.** Should `swarm-label-sync` run on the tangentswarm and methodology repos too?
4. **The live config.** Step 10 edits the private config file on the coordinator host. Who makes that edit: a worker, or you?
