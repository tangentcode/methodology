# Team conventions

These are the conventions of our team. A team that adopts this method must edit this page for its own conventions.

## Title prefixes

The general rules for issue and pull request titles are in [working-agreements.md](working-agreements.md#issue-and-pull-request-titles).

Our team also uses short product prefixes in titles. We do not write the full product names:

| Prefix | Product |
|---|---|
| `avo:` | Minavo |
| `mn:` | Minneron |
| `mn/avo:` | Minneron and Minavo together |
| `ptw:` | Pawn Takes World |
| `swarm:` | Swarm tooling |
| `ci:` | Continuous integration |

Put the prefix at the start of the title when the work is about that product. Use `mn/avo:` when the work is about the two products. Example: a search box that should filter Recent items in Minavo and Minneron has the title `mn/avo: a search box should filter Recent items`.

## Window names

Give each tmux window of a worker the name `<code>-<PR>-<branch>`.

- `code` is a short code for the git repository, not for the product. Each window for the platform repository uses `mn`. The methodology repository uses `meth`. The swarm tooling repository uses `swarm`. Each other repository has its own short code.
- `PR` is the pull request number, not the issue number. Do not add zeros before the number. For a speculative branch with the name `<branch>-vN`, use the pull request number of the base branch.
- `branch` is the branch name, with each `/` changed to `-`.
- Keep the windows of a session sorted by name. Then the codes stay in groups, and the pull request numbers in a group stay in numeric sequence.
- Example: the platform window for pull request 372 on branch `mn-view-renders` has the name `mn-372-mn-view-renders`.

## Speculative branch names

When a worker rebases a change onto a stack, the speculative branch has the name `<branch>-vN`. `v0` is the plain original branch. The next try is `-v1`, then `-v2`, and so on. The rules for when to make and install these branches are in [workflow.md](workflow.md#just-in-time-review).

## Comments

Our team uses the sparse-comments convention in [suggested-conventions.md](suggested-conventions.md#sparse-comments-and-a-file-summary). Each file starts with a summary of one or two lines.
