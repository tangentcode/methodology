---
name: Incident report
about: Record one failure of the swarm - what happened, why, the fix, and the prevention (see workflow.md, Incident reports)
title: "Incident YYYY-MM-DD H:MM PM ET: <what happened>"
labels: []
assignees: []
---

Incident report (methodology #81). Opened by <automation or agent>, <date> <time> ET. Diagnosed by <swarmbot>, <date> <time> ET. Related: <issues and pull requests>.

## What happened
<the facts, with the times: the cards, pull requests, agents, and log lines that show the failure>

## Why
1. <the root cause, with the code, file, and line when you can>
2. <each contributing cause>

<what you examined and found not true; or "Not known" and what is still to examine>

## Fix
- <time>: <what was done, by whom, and how you made sure that it worked>
- Still open: <the part of the fix that is not done, or "nothing">

## Prevention
- <how to stop the same class of failure, with the follow-up issue that does it>
- <each choice for Michal, as a question>
