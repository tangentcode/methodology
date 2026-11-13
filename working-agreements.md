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

## Scope

- One worker, one change, one branch, one pull request. A change covers a whole issue or a named part of one. Splitting an issue across several pull requests is fine. Each pull request links its issue with `Fixes` or `Part of`.
- When a worker finds and demonstrates a real defect next to its change, it fixes it in the same change with a regression test. The coordinator doesn't ask the human whether to fix a demonstrated defect.
- Unrelated ideas become new issues in Triage. The human decides them there before a worker starts.
- Items the human has parked stay parked until he says otherwise.

## Sessions and machines

- Don't close or kill worker sessions without the human's say.
- Keep temporary files in the worker's own directory, not a shared temp directory.
- Check machine load before starting many workers at once.

## Records

- Log each decision the coordinator makes on its own: what, why, and the evidence. The human should be able to audit an unattended run.
- Report times in the human's time zone.
