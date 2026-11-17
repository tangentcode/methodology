# Proposal: prevention for the 2026-11-15 Staging refill incident

> **Status: proposal. Not adopted.** This page is for review only. The live rules are in [workflow.md](../workflow.md) and [review.md](../review.md). One small rule edit comes with this page. It only applies a rule that we have already. See [Rule edit in this pull request](#rule-edit-in-this-pull-request). Nothing else on this page is built until the human owner accepts it, rejects it, or changes it. Incident report: [issue #82](https://github.com/tangentcode/methodology/issues/82).

## The incident

On 2026-11-15, at about 7:10 PM ET, the human merged a pull request out of Human Review. Staging did not refill for many minutes, and nobody got an alert. Staging held 1 pull request. Three more (platform #524, #525, and #533) were "in flight" for about one hour.

The causes, from the report:

1. The three pull requests were merged into the staging branch (`work`) and served on staging. Each one failed hr-gate condition 7a, because its body had no screenshot. The cascade counted them as in flight. Thus fill said "Staging 1 + 3 in flight, target 2: no pull needed", and it pulled nothing.
2. The screenshot job that could unblock them did not get a worker. Each pass said "9 Claudes run or are reserved (cap 9)", but only 3 Claudes ran. The other 6 were phantom reservations from the old held-launch list, `~/var/swarm-held.json`.
3. No alert fires when Staging stays short, or when a pull request stays in flight for a long time.

The report asks four prevention questions. This page also covers cause 2, because the questions do not name it.

## What tangentswarm main does now

All references are to tangentswarm `origin/main` at `917ed0d` (2026-11-17).

| # | Item | State | Evidence |
|---|---|---|---|
| A | Phantom reservations block a worker start (cause 2) | **Solved** | [tangentswarm #46](https://github.com/tangentcode/tangentswarm/pull/46) retired the held-launch list (issue [#44](https://github.com/tangentcode/tangentswarm/issues/44), part of [#40](https://github.com/tangentcode/tangentswarm/issues/40)). `slots.claude_load` (`tangentswarm/slots.py:323`) counts only the live Claudes and the launch and start requests in the spool, "never from reservations or held lists". `launches.migrate_held` (`tangentswarm/launches.py`) moves each old row to an `unstarted` record one time, at daemon start. The file was also set to `[]` at 7:14 PM ET |
| B | A pull in flight counts toward the Staging floor with no time limit | **Not solved** | `Cascade.fill` (`tangentswarm/advance.py:564` to `568`) adds every pull in flight to `have`, and `_fill_pull` (`advance.py:583`) pulls nothing when `have >= FLOOR`. `Flow.advance` (`tangentswarm/flow.py:974` to `983`) never times out a pull that waits only on 7a. It writes `SCREENSHOTS_NEEDED`, and the pull stays open. This is on purpose: "never demoted into a column with no worker" |
| C | A screenshot job waits on the 3 rework slots | **Partly solved** | A priority path exists. `Flow.give_worker(priority=True)` (`flow.py:1072`) calls `slots.revive` with no rework-slot wait and no `MAX_CLAUDES` check. Only the live Claudes and the free memory limit it (`slots.conflict_capacity`, `slots.py:776` to `783`). Fill uses it for conflict fixes ([tangentswarm #65](https://github.com/tangentcode/tangentswarm/issues/65)). But `Flow.screenshot_job` calls `give_worker` without `priority` (`flow.py:1014`), so it waits on the rework cap (`slots.py:721`) |
| D | The screenshot (7a) before the merge into `work` | **Decided, not built** | The approved plan is the preview gate ([methodology #67](https://github.com/tangentcode/methodology/issues/67)). The design is in tangentswarm `docs/preview-gate.md`: "Status: design. ... Nothing here is built yet." Until it is built, [review.md](../review.md#screenshots-from-a-preview-of-the-real-app) says that screenshots come from staging when the pull step deploys the change. Today, `Advance.shots_on_ready` (`advance.py:404` to `419`) sends the screenshot job when a UI pull request reaches Ready |
| E | An alert when Staging stays short, or a pull stays in flight | **Not solved for this case** | The watchdog alerts when Human Review is empty and Staging holds pull requests for 10 minutes (`promote_stall`, `tangentswarm/watchdog.py:158`, and `promote_pass`, `watchdog.py:304`). `swarm-promoted` wakes swarmbot when the staging `.deploy-sha` lags `work` for 10 minutes (`DEPLOY_LAG`, `tangentswarm/promoted.py:72` and `299`, [tangentswarm #37](https://github.com/tangentcode/tangentswarm/issues/37)). The cascade prints `STALLED`, `SCREENSHOTS_NEEDED`, `NEEDS_WORKER`, and `REDEPLOY_LATE`, but these are only output lines. They do not wake anybody. In this incident, Staging was not empty and staging served each head. Thus no check fired |

The other pull requests in the brief do not change these items. [tangentswarm #66](https://github.com/tangentcode/tangentswarm/pull/66) added the shared pick order and the priority worker for a conflict skip. [#68](https://github.com/tangentcode/tangentswarm/pull/68) made the Human Review refill instant. [#70](https://github.com/tangentcode/tangentswarm/pull/70) stopped the `-vN` churn. [#78](https://github.com/tangentcode/tangentswarm/pull/78) replaced the timers with events. [#79](https://github.com/tangentcode/tangentswarm/pull/79) added the hourly sanity check, which checks board rules, not Staging flow. [methodology #96](https://github.com/tangentcode/methodology/pull/96) made the promotion from Staging a cheap check.

## Recommendations

### 1. Should a pull in flight stop counting toward the Staging target?

**Recommendation: yes, in two cases.**

- A pull in flight that waits **only** on condition 7a stops counting at once. It is blocked on a worker, not on the swarm. [review.md](../review.md#columns-and-limits) already says: "Blocked pull requests can also sit in Staging, but they do not count toward the floor." A pull in flight is on the staging branch, the same as a Staging pull request. Thus the same rule applies to it.
- A pull in flight that waits on something else (CI, or a redeploy) counts for 15 minutes from the work merge. After that, it stops counting. A normal redeploy takes 2 to 4 minutes, and `REDEPLOY_LATE` warns after 10 minutes.

The pull stays open in both cases. It is not demoted, and it keeps its place. Fill only pulls the next Ready pull request behind it. Staging has no fixed cap, so this does not break a rule.

Reason: the target exists to keep pull requests ready for Human Review. A pull that cannot finish soon does not do that.

Status: the first case only applies a rule that we have. This pull request writes it into the rules (see [Rule edit in this pull request](#rule-edit-in-this-pull-request)). The 15-minute limit is new, and needs a decision. Both need code: follow-up 1.

### 2. Should screenshot-only jobs have their own slot?

**Recommendation: no new slot. Send the screenshot job on the priority path that we have.**

Reason: a screenshot job changes only the body of the pull request, and it is short. A pull in flight waits on it, and it holds the staging branch while it waits. A conflict fix for fill is the same type of job, and it already uses the priority path (tangentswarm #65). That path still keeps the hard limits: the live Claudes and the free memory. A fourth slot type adds a new count to each capacity report, for no gain.

Status: needs code. Follow-up 2. It is one argument in `Flow.screenshot_job`, plus a test.

### 3. Can the handoff at Ready require the screenshot before the merge into `work`?

**Recommendation: not as a new gate now. The preview gate is the answer, and it is already approved.**

Reason:

- The preview gate (methodology #67) puts the screenshots and a feature check before Ready. That is what this question asks for.
- Until the preview site exists, the rule says that screenshots come from staging, at pull time. A hard 7a check before the merge into `work` would block each UI pull request whose worker needs staging for its screenshots.
- `shots_on_ready` already sends the screenshot job when a UI pull request reaches Ready. Thus many pull requests get their screenshots before fill pulls them.
- With recommendations 1 and 2, a 7a wait no longer holds the Staging target. It also gets a worker sooner.

Status: no new code for this question. Follow-up 4 tracks the build of the preview gate, if no issue tracks it yet.

### 4. Alert when Staging is below target, or a pull is in flight too long

**Recommendation: yes. Add one watchdog check.**

The check fires when one of these is true:

- A pull is in flight for more than 15 minutes from its work merge.
- Staging, counted as in recommendation 1, stays below the floor for 15 minutes while Ready holds a pull request that is not a draft.

Each finding sends one swarmbot wake (`alerts.alert`) and opens one incident report (`alerts.incident`), as the other watchdog checks do. The key is the pull request and its head for the first case, and the start time of the short period for the second case. Thus a finding that stays does not fill the board. The alert text names the gate rows that the pull waits on, the worker state (`SCREENSHOTS_NEEDED` or `NEEDS_WORKER` text), and the fix.

Reason: the alerts that we have only fire when Human Review is empty or the deploy lags. This incident had neither. The 15-minute limit is from the incident report.

Status: needs code. Follow-up 3.

## Proposed follow-up issues

These are for tangentswarm. This pull request does not open them.

1. **fill: a pull in flight that waits only on screenshots does not count toward the Staging floor.**
   In `Cascade.fill` (`advance.py:564` to `568`), count a pull in flight toward `have` only while it can finish without a worker. Use the last gate verdict of each pull: `Flow.advance` already computes it. Save the open gate rows in the pull record. A pull whose only open rows are 7a does not count. A pull with any other wait counts for `SWARM_INFLIGHT_COUNT` seconds (default 900) from its `started` time, and then does not count. The pull stays open and keeps its place. The fill line says which pulls are not counted, and why. Tests: a 7a-only pull with Staging 1 and floor 2 lets fill pull the next Ready pull request. A CI wait younger than the limit still counts. A CI wait older than the limit does not count. A fast-track pull request still goes first.

2. **Screenshot jobs use the priority worker path.**
   In `Flow.screenshot_job` (`flow.py:1014`), call `give_worker(n, text, priority=True)`. Then a screenshot job does not wait on the 3 rework slots or on `MAX_CLAUDES`. `slots.conflict_capacity` still limits it by the live Claudes and the free memory. When the job is held, the next pass tries it again, as now: the once-per-head key is marked only when the job is sent. Tests: with 3 busy rework slots, a screenshot job still resumes the parked worker. With no free memory, it is held and tried again on the next pass. `shots_on_ready` uses the same path.

3. **Watchdog: alert on a long pull in flight and on a short Staging.**
   Add a pass to `tangentswarm/watchdog.py`, next to `promote_pass`. Read the pulls in flight (`flow.load_pulls()`) and the board snapshot. Fire when a pull is in flight for more than `SWARM_INFLIGHT_ALERT` seconds (default 900), or when the counted Staging is below the floor for that long while Ready has a pull request that is not a draft. Send one `alerts.alert` and one `alerts.incident` for each key, as `promote_pass` does. Use the key `inflight:<pr>@<head>` for a pull, and `staging-short:<start time>` for a short Staging. The text names the open gate rows, the worker state, and a fix from `fix_for`. Tests: no alert before the limit; one alert after it; no second alert for the same key; a new key after the finding goes away and comes back; a dry run only prints.

4. **Build the preview gate (`docs/preview-gate.md`).**
   Open this issue only if no issue tracks the build yet. The design and the build order are in `docs/preview-gate.md`. The approval is methodology #67. The build waits on the preview hosts from the operator. When it is live, a UI pull request reaches Ready with its screenshots, and condition 7a can no longer stop a pull.

## Rule edit in this pull request

[review.md](../review.md#columns-and-limits) and [workflow.md](../workflow.md#just-in-time-review) now say that a pull that is merged into the staging branch, but waits only for a worker (for example, for its screenshots), is blocked. It does not count toward the floor. This only applies the rule about blocked pull requests that we have. It does not add the 15-minute limit. That limit waits for a decision.

## Decision needed

The human owner decides. Please answer each question:

1. Do you accept recommendation 1? A 7a-only pull does not count at once. Any other pull counts for 15 minutes. Or do you want a different limit?
2. Do you accept recommendation 2: no new slot, and screenshot jobs use the priority path?
3. For question 3, do you agree that the preview gate is the answer, with no new gate before it is built? Or do you want an interim gate? An interim gate could let fill skip a UI pull request with no screenshots and pull the next one. That breaks the strict pick order of tangentswarm #65.
4. Do you accept recommendation 4, with 15 minutes for both alerts?

When the decisions are known, the coordinator opens the accepted follow-up issues. This page stays as the record of the proposal.
