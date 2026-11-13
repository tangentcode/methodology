# Suggested conventions

A project can adopt these conventions. They are not part of the core method. Each entry gives the rule, an example, and a short prompt that an agent can follow to apply the rule.

## Sparse comments and a file summary

### Rule

1. Use few comments. Good names and small functions explain the code. Write a comment only when the code cannot show something itself: the reason for a choice, a constraint, or a known trap.
2. Start each file with a summary of one or two lines. The summary tells what the file is for. Then a reader (a human or an agent) can quickly decide if the file is related to the task.
3. Do not write comments that repeat what the code does. Do not write comments that tell the history of a change, because version control records that history. Do not keep code that is commented out.

### Example

```ts
/** Shared File menu commands (Save, Save As, Revert) for any open document. */
```

### Prompt for an agent

> Apply the sparse-comments convention to this file. Make sure that the file starts with a summary of one or two lines that tells what the file is for. Remove comments that only repeat what the code does, comments that tell the history of a change, and code that is commented out. Keep comments that give a reason, a constraint, or a known trap. Do not change the behavior of the code.

### How to adopt it

Put the rule in the instructions file that the agents of the project read before they work. Then workers follow the rule, and reviewers can check it.
