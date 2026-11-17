# Proposal: idle Claudes must not hold the Claude cap or the rework slots

> **Status: proposal. Not adopted.** This page is for review only. The live rules are in [working-agreements.md](../working-agreements.md#close-idle-agents-with-exit), [workflow.md](../workflow.md), and [review.md](../review.md). Nothing on this page is built until the human owner accepts it, rejects it, or changes it. Discussion: [issue #83](https://github.com/tangentcode/methodology/issues/83).

- **Incident:** [#83](https://github.com/tangentcode/methodology/issues/83), 2026-11-15 7:16 PM ET. Idle platform Claudes held the Claude cap and the 3 rework slots. Three screenshot jobs waited until 7:43 PM ET. It came after [#82](https://github.com/tangentcode/methodology/issues/82) on the same evening.
- **State checked against:** tangentswarm `origin/main` at `917ed0d` (2026-11-17), and the state files of the live services on the coordinator host on the same day. The line numbers on this page are at `917ed0d`.
- **Standing rule:** idle agents are closed with `/exit`, and their tmux windows stay ([Close idle agents with /exit](../working-agreements.md#close-idle-agents-with-exit), methodology #99).

## Summary

The incident asked 8 questions. Three are solved on tangentswarm main. Two are solved in part. Three need code.

| # | Question | State on main | Recommendation |
|---|---|---|---|
| 1 | Do idle workers count against the caps? | No change since the incident | Keep the count. Close idle workers instead |
| 2 | Does park cover idle workers before Ready? | **Solved** by the pane watcher (PR #51), except one case | Keep. Close the gap with follow-up A |
| 3 | Drop a rework record when its Claude stops with no push? | **Open** | Yes, through follow-up A |
| 4 | Do older-commit Codex threads count when the head is clean? | **Solved** (PR #26) | No change |
| 5 | Park before fill? | **Solved in part** (PR #26): only held Ready handoffs are tried again | Do not reorder. Follow-up B |
| 6 | A timer while a job is held? | **Open** | No timer. A freed slot is the event. Follow-up B |
| 7 | How to detect a missed Stop hook? | **Solved** by the pane watcher (PR #51) | No change |
| 8 | Wake when a job stays held? | **Solved in part**: the wake URL is installed. A held screenshot job does not wake | Yes, after 15 minutes. Follow-up C |

## What tangentswarm main does now

These facts are the base for the answers.

- **The pane watcher runs.** PR #51 (merged 2026-11-15 9:01 PM ET, after the incident) added `tangentswarm/panewatch.py`. It captures each worker pane once a minute. `decide()` (`panewatch.py:124-151`) acts on an idle worker:
  - card in Needs Input: `/exit` (line 137);
  - card past In Progress, PR closed, or no PR: `/exit` (lines 144 and 151);
  - card in In Progress or a draft, worktree clean, and the local head is the PR head: the Stop hook missed it, so the watcher queues the handoff and opens an incident (line 150, and lines 358-389);
  - uncommitted or unpushed work: one nudge.

  The watcher is live: `~/.local/state/swarm-flow/panes.json` is written each minute.
- **The counts did not change.** `slots.live_claudes()` (`slots.py:304`) still counts every live platform Claude, busy or idle. `slots._revive()` still counts every live Claude in a rework worktree (`slots.py:720`). Both use only live processes, so a Claude closed with `/exit` frees its slot at once.
- **The Stop hook runs once for each branch head.** `stophook._run()` returns at once when it already saw `branch@head` (`stophook.py:300`).
- **The cascade order.** `Cascade._run()` (`advance.py:845-848`) runs fill, park, and then `retry_held()`. `retry_held()` (`flow.py:1042`) tries again only the held Ready handoffs (a merge-main relay), at most every 300 s (`HELD_RETRY`).

## Answers

### 1. Do idle workers count against MAX_CLAUDES and the rework cap?

**Recommendation: yes, keep the count. Make sure no idle worker stays alive.**

Reasons:

- An idle Claude process still uses memory on the shared host. The caps protect memory. A count of only busy Claudes would let the host start more processes than it can hold when the idle ones wake up.
- Michal's rule for tangentswarm #44 (2026-11-15 7:17 PM ET) is: capacity comes from live state only. A live process is live state. A status field that says "idle" is a guess about the next minute.
- The standing rule already says what to do with an idle agent: close it with `/exit`. Then it does not count, because both counts read only live processes. The window and the saved session stay for `swarm-revive`.

So the fix for this question is in questions 2 and 3: close every idle worker fast. No change to the count.

### 2. Should park also cover idle workers in In Progress, Needs Input, or Auto Review?

**Already solved on main, except one case. Recommendation: keep it, and close the gap with follow-up A.**

The pane watcher (PR #51) does this now, once a minute (see [What tangentswarm main does now](#what-tangentswarm-main-does-now)). For the three Claudes of the incident:

| PR | Card | Idle since | What the watcher does now |
|---|---|---|---|
| #541 | Needs Input | 4:40 AM ET | `/exit` within a minute (`panewatch.py:137`) |
| #546 | In Progress, head pushed, handoff missed | 12:08 PM ET | Queues the handoff and opens an incident (`panewatch.py:150`). The card goes to Auto Review. The next minute, `/exit` (`panewatch.py:151`) |
| #538 | In Progress, revived, no new push | 11:02 AM ET | Queues the handoff, but the Stop hook already saw this head (`stophook.py:300`), so it does nothing. **The Claude stays idle.** This is the gap |

The rule text says that an agent is idle "when its pull request is in Ready, Staging, or Human Review, or when it has no work". The watcher also closes agents in Needs Input and Auto Review. Michal decided the Needs Input case on tangentswarm #40 (item 4, 2026-11-15 6:45 PM ET). This pull request adds both columns to the rule text (see [Rule edits in this pull request](#rule-edits-in-this-pull-request)).

### 3. Should a rework record be dropped when its Claude stops without a push?

**Recommendation: yes. Free the slot and move the card out of In Progress. Follow-up A.**

A revived Claude that stops with no new push did one of these things:

- It found that the feedback needs no change (the #538 case).
- It disagrees with a finding.
- It is stuck.

In each case, a live Claude in In Progress waits for nothing. It must not hold a rework slot and a cap slot. Two parts:

- If Codex is clean on the head, the handoff runs again: the card goes to Auto Review, and the MinBot check runs. Then the watcher closes the Claude.
- If Codex findings are still open on the head, a person must decide. The card goes to Needs Input with the worker's last message as the question. Then the watcher closes the Claude (as in question 2).

Today neither part runs, because the Stop hook marks each head once (`stophook.py:300`). A revive does not clear that mark.

Also, a Claude closed by the watcher keeps its rework record in `slots.json`. Only `park_ready()` removes it (`slots.py:612`). The record does not hold a slot, because the slot count reads only live Claudes. But it is stale data. Follow-up A removes it.

### 4. Do Codex threads on an older commit count when Codex is clean on the current head?

**Already solved on main. Recommendation: no change.**

- `advance.codex_decision()` (`advance.py:121-146`) returns `clean` first when `codex_clean()` is true. `codex_clean()` counts only open threads on the head, or threads with an unknown commit (`advance.py:117`). A thread from an older head does not count.
- swarm-webhook sends "Codex found issues on your head" only when `codex_decision()` returns `findings` (`webhook.py:496-499`).
- The MinBot pass resolves the older threads (`advance.addressed_threads()`, `advance.py:156`). The Stop hook uses the same rule (`tick.codex_status()`, `tick.py:271-275`).
- Commit `e6bd8f3` (PR #26, 2026-11-15 2:38 PM ET) added this. The #538 relay was at 11:02 AM ET, before that commit.

A related bug is still open: tangentswarm #75 (PR #81). A Codex summary that is still running can count as clean. That is a different bug. It does not change this answer.

### 5. Should the cascade park before it fills?

**Solved in part. Recommendation: do not change the order. Try held jobs again after park. Follow-up B.**

- Fill must come first. Fill does the one board read of the pass, and its pulls and moves change the columns that park reads.
- Main already tries again after park, but only for one kind of job. `retry_held()` runs after `park()` (`advance.py:848`, commit `a9be989`, PR #26). It covers only held Ready handoffs (merge-main relays) and waits 300 s between tries.
- A screenshot job is not held. When `screenshot_job()` finds no worker, it writes only a `SCREENSHOTS_NEEDED` note (`flow.py:1019`). Nothing tries it again in the same pass. This is the 7:24 PM ET case of the incident.

Follow-up B makes every held job a saved hold, and tries all holds again after park when park freed a slot.

### 6. Should a pass also run on a timer while a job is held?

**Recommendation: no timer. Run a pass when a slot frees.**

- Michal moved the swarm from timers to events (tangentswarm #31, PR #78). A timer would bring back passes that do nothing.
- A held job waits for a slot. A slot frees only when a Claude process ends: a park, a `/exit` from the watcher, or a Claude that ends by itself. The watcher sees each of these within a minute. That is the event.
- When a slot frees and a hold exists, queue one cascade pass. Then the held job starts within about a minute, not at the next GitHub event (18 minutes in the incident).

A second gap: when swarm-webhook cannot relay Codex or CI findings, it only wakes swarmbot (`webhook.py:440-442`). It saves nothing, so no later pass tries the relay again. In the incident, swarmbot ran `swarm-revive 546` by hand. Follow-up B saves this relay as a hold too.

### 7. How can a missed Stop hook be detected?

**Already solved on main. Recommendation: no change.**

The pane watcher (PR #51) detects the #546 case. It acts when a worker is idle at its prompt, its worktree is clean, its local head is the PR head, and the card is in In Progress or the PR is a draft (`panewatch.py:147-150`). It queues the handoff through the spool and opens one incident for each head (`panewatch.py:385-388`). The incident gives the evidence to find why the hook did not run. The cause for #546 is still not known.

The gap of question 3 is not a missed hook. The hook ran on that head before, and the revive did not push a new head.

### 8. Should a held job raise the exception wake after a limit?

**Solved in part. Recommendation: yes, one wake after 15 minutes. Follow-up C.**

- The wake URL is installed now. `~/.config/tangentswarm/swarmbot-wake-url` exists, and `webhook.log` shows `wake-sent` with status 200 on 2026-11-17.
- A held webhook relay wakes swarmbot at once (`webhook.py:442`). With follow-up B, the relay is tried again by itself, so a wake at once is too early.
- A held screenshot job does not wake anybody. It writes only a note (`flow.py:980-981` and `flow.py:1019`).

With follow-ups A and B, a hold that stays for 15 minutes means that a slot is held by a Claude that the watcher did not close. That is a bug, so swarmbot must diagnose it. Send one wake for each PR and head, with the hold reason and the PRs that hold the slots, with their columns and idle times.

## Proposed follow-up issues

Michal opens these, or tells swarmbot to open them. This pull request does not open them. All three are in tangentcode/tangentswarm.

### A. A revived worker that stops without a push leaves In Progress

A Claude that `swarm-revive` started can stop with no new push: the feedback needed no change, the worker disagrees with a finding, or it is stuck. Today the Stop hook does nothing, because it already handled that branch head (`stophook.py:300`). The pane watcher queues the handoff, and the hook again does nothing (`panewatch.py:150`). The Claude stays idle in In Progress and holds a rework slot and a cap slot (incident methodology #83, platform #538, 8.5 hours). Fix: (1) when `slots._revive()` records a rework, it clears the Stop hook mark for the branch head, so the next Stop checks the head again; (2) in the Stop hook, when Codex is clean on the head, the handoff runs as usual (Auto Review, MinBot check); (3) when Codex findings are open on the head, Codex already reviewed the head, and the worker was revived for them, the card goes to Needs Input with the worker's last message on the ticket, not "left to mn-workflow"; (4) when the watcher sends `/exit` to a worker, it removes that PR's rework record from `slots.json`, the same as `park_ready()` does. Tests: a revive on an already-handled clean head ends in Auto Review; a revive for findings with no push ends in Needs Input; then the watcher closes the Claude; the rework record is gone after a watcher `/exit`.

### B. Held jobs are saved and start when a slot frees

Two kinds of jobs that find no free slot are lost today. A screenshot job writes only a `SCREENSHOTS_NEEDED` note (`flow.py:1019`). A Codex or CI relay from swarm-webhook only wakes swarmbot (`webhook.py:442`). Only the held Ready handoffs are tried again, after park and at most every 300 s (`flow.py:1042`). In the incident, slots freed at 7:24 PM ET, and the next pass came at 7:42 PM ET. Fix: (1) the screenshot job and the webhook relay save a hold (PR, head, reason, relay text) the same way that a held handoff does now; (2) `retry_held()` tries every hold whose PR head did not change, in any column, and gives the screenshot job and the relay to the worker in the same way as the first try; (3) in the cascade, when `park()` parked at least one Claude, `retry_held()` runs at once for that pass, without the 300 s wait; (4) when the pane watcher sends `/exit`, or sees a worker Claude end, and a hold exists, it queues one cascade pass. No new timer. Tests: a screenshot job refused in fill starts after park in the same pass; a held webhook relay starts on the next pass after a slot frees; a hold for an older head is dropped; a watcher `/exit` with a hold queues one pass.

### C. A job held for 15 minutes wakes swarmbot once

With A and B, a job that stays held for 15 minutes means that something holds a slot that the tools did not free. Fix: (1) when a hold from B is older than `SWARM_HELD_WAKE` (default 900 s), send one exception wake for each PR and head (key `held:<pr>@<head>`), with the hold reason, and for each Claude that holds a rework or cap slot: its PR, its column, and its idle time from the watcher; (2) swarm-webhook stops its immediate wake for a held relay, because B now tries it again (keep the immediate wake for other relay failures); (3) one incident ticket for each such wake, with the methodology #81 sections. Tests: no wake before 900 s; one wake after it; no second wake for the same head; a new head gives a new wake.

## Rule edits in this pull request

The pane watcher already closes idle agents in Needs Input and Auto Review. Michal decided the Needs Input case on tangentswarm #40 (item 4). The rule text listed only Ready, Staging, and Human Review. This pull request adds Needs Input and Auto Review to the definition of an idle agent in [working-agreements.md](../working-agreements.md#close-idle-agents-with-exit), [glossary.md](../glossary.md), [review.md](../review.md), [roles.md](../roles.md), and [adopting.md](../adopting.md). It also says that an agent in Needs Input can have uncommitted work when it is closed. Its worktree and its files stay, and the resume starts the agent in that worktree.

## Decision needed

The human owner decides. For each item, please answer **accept**, **reject**, or **change** (write the change):

1. Question 1: keep counting idle workers against both caps.
2. Follow-up A.
3. Follow-up B, with no new timer.
4. Follow-up C, with a 15-minute limit.

When the decisions are known, the accepted follow-ups become tangentswarm issues. This page stays as the record of the proposal, or it is deleted if the proposal is rejected.
