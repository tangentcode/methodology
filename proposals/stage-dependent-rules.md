# Proposal: stage-dependent rules (greenfield and production)

> **Status: proposal. Not adopted.** This page is for review only. It does not change a rule. The live rules are in [workflow.md](../workflow.md), [review.md](../review.md), and the other core documents. Nothing on this page is built until the human owner accepts it, rejects it, or changes it. Discussion: [issue #45](https://github.com/tangentcode/methodology/issues/45).

## The question

A project has different needs at different stages of its life. Some of our rules may fit only one stage.

- **Greenfield.** A new system with no customers. The goal is to get something working and to learn fast. A defect costs little, because nobody depends on the system yet.
- **Production.** A system with real customers. A customer ticket comes in. The goal is to fix it fast and safely. A defect costs a lot, because customers see it.

Today, the method has one set of rules for all projects. This proposal asks whether some rules should apply to one stage only.

## How a project selects its stage

Suggestion: one setting for each product, in the project configuration:

```yaml
stage: greenfield   # or: production
```

- Each rule that depends on the stage says which stage it applies to. A rule that does not say a stage applies to both stages.
- The coordinator and the swarm tools read the setting. They do not guess the stage.
- Only the human owner changes the setting. A change of stage is a decision, like a merge to main.
- If the setting is missing, the tools use `production`. The stricter rules are the safe default.

The default of `production` is a suggestion of this page. The issue does not say what occurs when the setting is missing.

## Suggested sorting of the current rules

Each row names one current rule, the suggestion from the issue for each stage, and notes about the live rules today. The notes column tells where the live rules changed after the issue was written.

| # | Current rule | Greenfield suggestion | Production suggestion | Notes |
|---|---|---|---|---|
| 1 | Triage before any worker starts ([workflow.md](../workflow.md)) | Keep. Also allow a "standing yes" for small tickets in an approved area, for example cosmetic or test-only changes | Keep. Every customer ticket goes through triage and reproduction first | A standing yes needs a written list of approved areas. Who keeps that list? |
| 2 | Automated review round limit, 10 rounds ([review.md](../review.md#round-limit)) | Lower the limit, for example to 3. Then send the pull request to the second reviewer. Accept P2 findings as follow-up tickets | Keep the high limit. Block on P1 and P2 | Today a pull request with an open P2 cannot enter Ready or Staging. The greenfield suggestion changes that gate |
| 3 | Second-reviewer (MinBot) pass on the exact head ([review.md](../review.md#the-gate-into-human-review)) | Keep, because it is cheap | Keep | No change |
| 4 | Staging deploy and screenshots before Human Review ([review.md](../review.md#the-gate-into-human-review)) | Keep screenshots for UI. For tooling and test-only pull requests, allow a quick "no surface" statement | Keep. Also add a reproduction of the customer case on staging | Today, "if you are not sure whether a person can see a change, think that a person can see it." A "no surface" path must keep that default |
| 5 | Full CI green before Human Review ([review.md](../review.md#the-gate-into-human-review)) | Keep. Allow the reviewer to waive a known flaky check that has a tracking issue | Keep. No waivers | Only the human can waive. A bot must not waive a check |
| 6 | Two Human Review slots with the next pull request ready ([review.md](../review.md#just-in-time-human-review-flow)) | Keep. Throughput matters most here | Keep. Also add a hotfix lane that lets a customer fix go to the front of the queue | Today the [fast track](../review.md#fast-track) already moves one ticket to the front of every queue. See [Hotfix lane and fast track](#hotfix-lane-and-fast-track) |
| 7 | Speculative rebases (`<branch>-vN`) ([review.md](../review.md#the-gate-into-human-review)) | Use only for the next pull request | Rarely necessary. Production fixes are small and go directly onto main | The live rules already allow only one speculative rebase, and only when no Ready pull request fits the stack. This row may need no change |
| 8 | Only the human merges to main ([principles.md](../principles.md)) | Keep | Keep. Also add a release step and a rollback plan | No change to the rule. The addition is in the production-only list |
| 9 | Sparse comments and file-purpose headers ([suggested-conventions.md](../suggested-conventions.md)) | Keep | Keep | No change |
| 10 | Parked and Pending columns ([workflow.md](../workflow.md)) | Parked stays empty. Close a pull request, do not park it | Parked can hold "fix later" items that link to customer tickets | Pending is now named Staging. Staging is part of the flow, so this row is about Parked only |
| 11 | Status messages to the reviewer ([working-agreements.md](../working-agreements.md)) | Send only decisions, and a note when Human Review is empty | Also keep a status for each open customer ticket that the customer can see | A customer-visible status is a new outward-facing action. It needs its own safety rule. See [safety.md](../safety.md) |

## Suggested additions for production only

1. **Hotfix lane.** One slot that skips the Staging queue for a bug that blocks a customer. It still needs review, CI, and staging.
2. **Severity levels.** Each customer ticket has a level, for example S1 to S3. Each level has a target response time.
3. **Reproduce first.** A sandboxed agent reproduces the customer issue and attaches the evidence before a worker starts a fix.
4. **Regression test.** Each customer bug fix includes a regression test.
5. **Release notes and rollback.** Each merge to main has release notes and a rollback check.

## Suggested relaxations for greenfield only

1. Allow larger pull requests when they build a new area that nothing depends on yet.
2. Allow a feature flag or a "draft surface" to reach Human Review earlier. The surface shows a clear "not done" banner.
3. Prefer fast feedback to completeness. File follow-up tickets instead of more review rounds.

## Hotfix lane and fast track

The issue was written before the [fast track](../review.md#fast-track) rule. The two ideas overlap.

- The fast track is a `fast-track` label. Only the maintainer adds it. It moves one ticket to the front of every queue. It does not change the quality bar, and it does not push a pull request out of Human Review.
- The hotfix lane, as the issue describes it, is one extra slot for a customer-blocking bug. It also keeps the quality bar.

Two possible answers:

- **A.** The hotfix lane is the fast track. A production customer bug gets the `fast-track` label. No new slot. This is the smaller change.
- **B.** The hotfix lane is a separate, third Human Review slot that only a customer bug can use. This changes the rule that Human Review holds never more than two pull requests.

## Risks

- **Two rule sets are harder to follow.** Each worker and each tool must read the stage. A rule that a tool does not check is not part of the gate (see [review.md](../review.md#the-gate-into-human-review)). Each stage-dependent rule thus needs a tool change, not only a document change.
- **A greenfield project can get customers without a stage change.** Then the relaxed rules stay on too long. A possible guard: the coordinator asks the human about the stage when the first customer ticket arrives.
- **Relaxed gates can hide defects.** Follow-up tickets for P2 findings must not pile up. A possible guard: a limit on open follow-up tickets.

## Decision needed

The human owner decides. For each numbered row in the table, and for each production addition and greenfield relaxation, please answer one of these:

- **Both.** Keep the rule, or add it, for both stages.
- **Greenfield only.**
- **Production only.**
- **Drop.**
- **Change.** Write the change.

Also please answer these questions:

1. Do we add the `stage` setting at all, or keep one rule set for all projects?
2. If we add it, is `production` the default when the setting is missing?
3. Is the hotfix lane answer A (it is the fast track) or answer B (a separate slot)?

When the decisions are known, a follow-up pull request will change the live documents. That pull request will not change this page into rules directly. This page stays as the record of the proposal, or it is deleted if the proposal is rejected.
