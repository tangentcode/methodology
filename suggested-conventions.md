# Suggested conventions

These are conventions that a project can adopt. They are not part of the core method. Each entry gives the rule, an example, and a short prompt that an agent can follow to apply it.

## Sparse comments and a file summary

### Rule

1. Use comments sparingly. Good names and small functions explain the code. Write a comment only when the code cannot show something on its own: the reason for a choice, a constraint, or a known trap.
2. Start every file with a summary of one or two lines. The summary tells what the file is for, so that a reader (a human or an agent) can quickly decide if the file is relevant.
3. Do not write comments that repeat what the code does. Do not write comments that tell the history of a change, because version control records that. Do not keep commented-out code.

### Example

```ts
/** Shared File menu commands (Save, Save As, Revert) for any open document. */
```

### Prompt for an agent

> Apply the sparse-comments convention to this file. Make sure that the file starts with a one- or two-line summary of what the file is for. Remove comments that only repeat what the code does, comments that tell the history of a change, and commented-out code. Keep comments that give a reason, a constraint, or a known trap. Do not change the behavior of the code.

### Adopting it

Put the rule in the instructions file that the project's agents read before they work, so that workers follow it and reviewers can check it.
