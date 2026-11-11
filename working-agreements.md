# Working agreements

## Communication

- Send a message when someone has to act or decide. Don't send acknowledgements, and don't repeat a report.
- Lead with the result. Put details after.
- Don't chase other bots about open items. Wait for them or raise the item with the human.
- Talk to worker agents only through the sanctioned messaging tool, never by typing into their sessions by hand.
- Write the human's stated choices into the brief the first time, so he doesn't have to repeat them in review.

## Issue and pull request titles

Issue titles describe the present state. Never word an issue title as an aspiration.

- A plain statement such as "X does Y" reads as a bug report. It means this happens now, and we do not want it.
- A wanted change uses "should". Example: "Save As should work for every file that can be saved". Do not write "Save As works for every file that can be saved".
- Every issue has a GitHub issue type: Feature, Bug, or Task. Use Bug when the title states a present, unwanted behavior. Use Feature when the title states a wanted change. Use Task when the work is a specific piece of work that is not a user-facing feature or a bug.

Pull request titles complete the sentence "Merging this pull request will ...". They start with an imperative verb. Example: "Make the Save As command work for every file that can be saved".

## Scope

- One worker, one issue, one branch, one pull request.
- When a worker finds and demonstrates a real defect next to its change, it fixes it in the same change with a regression test. The coordinator doesn't ask the human whether to fix a demonstrated defect.
- Unrelated ideas become new issues in Backlog, approved by the human before work starts.
- Items the human has parked stay parked until he says otherwise.

## Sessions and machines

- Don't close or kill worker sessions without the human's say.
- Keep temporary files in the worker's own directory, not a shared temp directory.
- Check machine load before starting many workers at once.

## Records

- Log each decision the coordinator makes on its own: what, why, and the evidence. The human should be able to audit an unattended run.
- Report times in the human's time zone.
