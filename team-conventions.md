# Team conventions

These are the conventions our team uses. Teams that adopt this methodology should edit this page to match their own conventions.

## Issue and pull request titles

The wording and type rules for issue and pull request titles are in [pull request #39](https://github.com/tangentcode/methodology/pull/39), which adds them to [working-agreements.md](working-agreements.md). When both pull requests are merged, those rules move to this page.

Our team also uses short product prefixes in titles, not the spelled-out product names:

| Prefix | Product |
|---|---|
| `avo:` | Minavo |
| `mn:` | Minneron |
| `mn/avo:` | Minneron and Minavo together |
| `ptw:` | Pawn Takes World |
| `swarm:` | Swarm tooling |
| `ci:` | Continuous integration |

Put the prefix at the start of the title when the work is about that product. Use `mn/avo:` when both products are involved. Example: a search box that should filter Recent items in Minavo and Minneron is titled `mn/avo: a search box should filter Recent items`.

## Window names

Name each worker's tmux window `code-PR#-branch`, where `PR#` is the pull request number and `branch` is the branch name. Example: `code-372-mn-renders`.

## Speculative branch names

When a worker rebases a change onto a stack, the speculative branch is named `<branch>-vN`. `v0` is the plain original branch. The next attempt is `-v1`, then `-v2`, and so on. The rules for when to create and install these branches are in [workflow.md](workflow.md).

## Sparse comments and a file-purpose header

[Pull request #36](https://github.com/tangentcode/methodology/pull/36) already proposes this convention on a Suggested conventions page. This page is the home for our team's conventions. When both pull requests are merged, keep the rule here.

1. Use comments sparingly. Good names and small functions explain the code. Write a comment only when the code cannot show something on its own: the reason for a choice, a constraint, or a known trap.
2. Start every file with a file-purpose header of one or two lines. The header tells what the file is for, so that a reader (a human or an agent) can quickly decide if the file is relevant.
3. Do not write comments that repeat what the code does. Do not write comments that tell the history of a change, because version control records that. Do not keep commented-out code.

Example:

```ts
/** Shared File menu commands (Save, Save As, Revert) for any open document. */
```
