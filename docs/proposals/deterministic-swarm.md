# Proposal: a deterministic swarm, with an LLM coordinator for judgment only

- **Status:** proposal. The reviewer decides which child tickets to open.
- **Plan issue:** [tangentcode/tangentswarm#23](https://github.com/tangentcode/tangentswarm/issues/23).
- **Workflow spec that the tools enforce:** [methodology#56](https://github.com/tangentcode/methodology/issues/56), the lean just-in-time Human Review flow. Where it differs from the 2026-11-12 two-slot rules, #56 replaces them. [workflow.md](../../workflow.md), [review.md](../../review.md) and [tooling.md](../../tooling.md) hold the current text.
- **State checked against:** tangentswarm `origin/main` at `809accd` (2026-11-17), and the user services on the coordinator host on the same day.

This document is a plan. It does not change the live flow, a tool, or a service.

## Goal

Run the swarm with deterministic software. Use an LLM coordinator only for judgment calls.

Before this plan, an LLM coordinator bot did many mechanical steps by hand, or woke on a timer or on every GitHub event to do them. This cost tokens, added lag, and stopped when the bot ran out of budget. One measurement: the LLM GitHub hook used 58% of all fleet usage on 2026-11-15, before the deterministic webhook replaced it.

## Decisions already made

These decisions are in the comments on tangentswarm#23 and in the tickets that came from it. They are not open.

1. **Three repositories.** (tangentswarm#23, comment 1.)
   - `tangentcode/methodology`: the text (rules and process).
   - `tangentcode/tangentswarm`: all tools. GitHub and Codex review handling is a plugin in this repository.
   - `tangentcode/tc-config` (private): the local settings for those tools. Keys stay outside every repository.
2. **`mn-workflow` and `minbot` fold into tangentswarm.** (tangentswarm#23, comment 1.)
   - Into tangentswarm, as a GitHub plugin package: the head-bound evidence module (one Codex-clean check, not three), the rules engine and runner (rules 1, 2, 4 and 5), the `gh` helper, the archive test runner, the MinBot CLI as the bot identity layer, a `swarm github tick` subcommand, and all tests from both repositories.
   - Into tc-config: the board ids, columns, actor, label, exclusions, pinned columns, per-repo test commands, the systemd units, and the MinBot install settings.
   - Delete: `agents.py` (call tangentswarm directly), and rule 3 (promote on Codex clean), because the Human Review gate owns entry to Human Review. Archive `tangentcode/mn-workflow` and `tangentcode/minbot` after cutover.
   - Cutover order: merge mn-workflow#3 and commit the live rule 3 config change; port the modules and tests with the same state-file format and once-keys; put the config and units in tc-config; run the new subcommand in dry run beside the live timer for at least one day, and compare the planned actions each pass; then switch the timer with `--live`, keep the old checkout for one week, and archive.
3. **The workflow spec is methodology#56.** (tangentswarm#23, comment 3.)
4. **One deterministic GitHub hook, no LLM in the loop.** It runs the hook rules and wakes the LLM coordinator only for exceptions. (Michal, 2026-11-15; `swarm-webhook`, live.)
5. **One events table for everything the swarm does.** (tangentswarm#32, merged as #33.)
6. **The same flow on Project 6.** There is no special flow for the tangentswarm and methodology repositories. MethBot acts as the human there. Staging steps apply only where a repository has a staging site. (Michal, 2026-11-15; tangentswarm#45.)
7. **MethBot is woken only for Project 6 `done` and `needs_input`.** Every other watchdog alert wakes swarmbot. (Michal, 2026-11-16; tangentswarm#71.)
8. **Workers never ask in the pane.** They call `needs_input`. A pane that asks is a bug, and the pane watcher reports it. (tangentswarm#51.)

## What exists today

Status words: **done** (on main and live), **on main** (merged, but not live or not used), **in progress** (open PR or issue named), **not started**.

| Part | Status | Notes |
| --- | --- | --- |
| `swarm-mcp` (tmux control MCP, HTTP) | done | Live as two services (API key, OAuth). |
| Worker MCP (`handoff`, `needs_input`, `worker_status`, `request_review`) | done | tangentswarm#53 (PR #54), #51, #71. Reports go to the events table and a spool. The `swarm-promoted` daemon acts on them outside the worker slice. `worker_status` and `request_review` are platform-only for now. |
| `swarm-agent` + `swarm-hub` (HTTP message queue) | on main, not running | The worker MCP and the spool replaced the hub as the worker-to-coordinator path. See child ticket C1. |
| Agent-done notification (#19) | done | Closed by #71. Platform: the Stop hook and `handoff` advance the card. Project 6: one POST to MethBot per head. |
| Stop hook: mark a finished PR ready, ask Codex once | done | tangentswarm#28 (closed). |
| `swarm-tick` | on main, LLM routine deleted | #20 merged. #21 and #22 closed. Its duties moved to `swarm-webhook`, `swarm-promoted` and the pane watcher (#37, #40). |
| `swarm-webhook` (deterministic GitHub hook) | done | Live. Verifies the signature, stores each delivery, classifies with a pure function, and wakes swarmbot only for listed exceptions. Has a `replay` command for missed events. |
| `swarm-promoted` (Human Review refill daemon) | done | Live. Refills Human Review in seconds. A merge webhook wakes it at once (#67, PR #68). Runs the pane watcher every minute (#40). |
| Pane watcher (replaces the LLM watchdog and stall scan) | done | #40 (PR #51). Unsent input, idle handoff, nudges, and a swarmbot wake for menus and frozen screens. |
| Shared pick order, staging fill, `-vN` cleanup | done | #35, #39, #65, #69. |
| Events table and viewers | done | #32 (PR #33); `swarm-events` TUI #34 (PRs #36, #72); agents screen #44 (PR #48); tmux status TUI #49 (PR #50). |
| Project 6 flow | in progress | Phase 1 done (#55, PR #47). Phase 2 (worker relays and launches, worker identity with the repository) is open in tangentswarm#45. |
| `mn-workflow` | live, separate repository | 5-minute timer still runs. mn-workflow#3 is open. Replacement by events: tangentswarm#31 (open). Fold-in: not started. |
| MinBot CLI | live, separate repository | `tangentcode/minbot`. Fold-in: not started. The CI claim bug is tangentswarm#30 (open). |
| Gate scripts in tangentswarm | partly done | Ported: `flow-status` (`swarm-flow-status`), park and resume (`swarm-slots`, `swarm-revive`), scoped start (`swarm-launch`), the gate lock (`swarm-lock`), gate checks 6 and 7a (`gatechecks.py`). Still outside version control, loaded from the home `bin` folder: `hr-gate`, `active-gate`, `pending-promote`, `ci-last-check`. |
| Codex review asked once per head | in progress | tangentswarm#63 (open). Several posters still share one token. |
| Hourly board sanity check | in progress | tangentswarm#43 (open). |
| Status API | in progress | tangentswarm#24, draft PR #74. |
| Low-cost worker readiness classifier (JEV) | in progress | tangentswarm#12, spec PR #73. |
| Coordinator lease | not started | |
| Web dashboard | not started | The old local `agent-dashboard` branch is 251 commits behind main and was not pushed. The TUIs above cover the read-only view for now. |
| `cloud` orchestrator | on main, unused | No change. |

## Coordinator work: status of each task

The table is the inventory from tangentswarm#23, with today's status.

| # | Task | Status | How it runs now, or what is open |
| --- | --- | --- | --- |
| 1 | Know when a worker is done, blocked or asking | done | Worker MCP `handoff` and `needs_input`; pane watcher as fallback |
| 2 | Mark a finished PR ready, move card to Auto Review | done | Stop hook and `handoff` |
| 3 | Post `@codex review` once per head | in progress | Done by the Stop hook and the webhook; one idempotent poster is tangentswarm#63 |
| 4 | Relay Codex findings to the worker | partly done | The webhook relays on the review event. The `mn-workflow` timer still does it too (tangentswarm#31) |
| 5 | Card move on Codex clean, tests, gate | partly done | Webhook `minbot` and `cascade` actions run the deterministic check `swarm-advance --minbot`. tangentswarm#30 (an LLM MinBot pass claimed CI was green) is still open. The archive test runner is not ported (C3) |
| 6 | Promote after a merge, sweep for conflicts | done | `swarm-promoted`, woken by the merge webhook |
| 7 | Resolve outdated review threads, re-request review | partly done | The MinBot check resolves addressed threads. No rule on a new head yet |
| 8 | Issue card moves | done | Webhook `card`, `merged` and `closed` actions |
| 9 | Milestone sync between PR and issue | not started | |
| 10 | Unsent prompt, menu, exited shell, stuck screen | done | Pane watcher |
| 11 | Park idle workers, resume | done | `swarm-slots`, `swarm-revive` |
| 12 | Merge to the work branch, redeploy staging | partly done | Staging fill and deploy-lag wake (#37, #65). Deploy-result events are not started |
| 13 | Staging screenshots, design checks, owner decisions | stays LLM | Judgment |
| 14 | Stall scan for new kinds of stall | in progress | Pane watcher, plus tangentswarm#43 |
| 15 | Board status reports | partly done | TUIs; status API in tangentswarm#24 |

## Roadmap: status of each child step

### Phase 0: foundation

- Gate scripts under version control, with tests: **partly done.** `hr-gate`, `active-gate`, `pending-promote` and `ci-last-check` remain. See C2.
- Merge `swarm-tick`: **done** (#20). #21 and #22 were closed.
- Swarm config file (one named swarm = repositories, board ids, columns, rules): **partly done.** `[[boards]]` entries in the private config (#47). The rules are still code. See C5.

### Phase 1: event bus (#19)

- Run `swarm-hub` as an authenticated service: **not started, maybe not needed.** See C1.
- Deploy the worker MCP and configure every new worker with it: **done** (#29, #53, #71).
- Forward each message to the coordinator: **done** for the needed cases. Exceptions wake swarmbot; Project 6 `done` and `needs_input` wake MethBot (#71).
- Worker rule: report `done`, `blocker` or `question` through the swarm MCP: **done** in the worker brief. The methodology text does not say it yet. See C9.
- Reply path through the hub: **partly done.** Answers come back on the ticket, and the resume carries them. Pane typing is still the delivery.

### Phase 2: GitHub events

- One webhook receiver: **done** (`swarm-webhook`).
- Event-driven rule engine: **partly done.** The webhook runs the rules per event. The `mn-workflow` rules still run on a timer. See C3 and C4.
- Rules for issue cards, milestone sync and outdated threads: **partly done.** Issue cards are done. See C7.
- Hourly safety-net pass and a lost-event check: **partly done.** `swarm-webhook replay` exists. The hourly pass is tangentswarm#43.
- Document which steps are rules and which are judgment: **not started.** See C9.

### Phase 3: swappable coordinator, many swarms

- Coordinator lease: **not started.** See C10.
- Queue judgment events while no coordinator holds the lease: **not started.** See C10.
- Coordinator handover procedure: **not started.** See C11.
- Several swarms from one host: **partly done.** Two boards run on one host (#47). See C5.

### Phase 4: dashboard

- Read-only dashboard: **in progress** through the status API (tangentswarm#24, PR #74).
- Coordinator switch and swarm controls: **not started.** See C12.

### Phase 5: later

- Multi-user swarms and per-user credentials: **not started.**
- Staging redeploy and deploy-result events: **partly done** (#37). See C8.

## Child tickets to split out

These tickets are not open yet. The reviewer decides which to open. Work that already has a ticket (tangentswarm#12, #24, #30, #31, #43, #45, #63) is not listed again.

| Id | Repository | Goal |
| --- | --- | --- |
| C1 | tangentswarm | Decide whether `swarm-hub` and `swarm-agent` still have a role now that the worker MCP and the spool carry reports; remove them or give them one. |
| C2 | tangentswarm | Move `hr-gate`, `active-gate`, `pending-promote` and `ci-last-check` into the repository with tests, so no tool loads code from the home `bin` folder. |
| C3 | tangentswarm | Port `mn-workflow` (evidence, rules 1, 2, 4 and 5, runner, `gh` helper, archive test runner) into a GitHub plugin with one Codex-clean check, and cut over by the plan in decision 2. |
| C4 | tangentswarm | Port the MinBot CLI into the GitHub plugin as its identity layer, with install settings in tc-config, then archive `tangentcode/minbot`. |
| C5 | tangentswarm, tc-config | One named swarm config (repositories, board, columns, rules), so a new swarm needs config only, not code. |
| C6 | tc-config | Move the board ids, the per-repo test commands and the systemd units for the swarm services into tc-config. |
| C7 | tangentswarm | Rules for milestone sync between a PR and its issue, and for outdated Codex threads on a new head. |
| C8 | tangentswarm | Deploy-result events: a staging deploy posts an event that the rules act on, in place of a poll. |
| C9 | methodology | Document which steps are rules and which are judgment, and the worker rule to report `done` and `needs_input` through the swarm MCP. |
| C10 | tangentswarm | Coordinator lease (claim, heartbeat, release, hand over) with MCP tools and a CLI; judgment events wait in the queue while no one holds it. |
| C11 | methodology | Coordinator handover procedure: what a new coordinator reads first. |
| C12 | tangentswarm | Coordinator switch and swarm controls on top of the status API. |
| C13 | tangentswarm | Multi-user swarms and per-user credentials. |

## Open questions that remain

Question 1 of tangentswarm#23 (where the tools live) is answered by decision 1. These remain open:

1. May the rule engine act as MinBot for everything the app can do, and as tangentstorm only for `@codex review` and card moves? Or should the app get the Projects permission, so only `@codex review` stays as tangentstorm?
2. Is a lease with expiry the right model for handover, or is a manual switch enough?
3. Should the dashboard be public behind a login, or on the private network only at first?
4. Should the child tickets go on Project 6, or on a new board for tangentswarm?
