#!/usr/bin/env python3
"""Fill the change list in changelog.md from main's history.

One entry per first-parent commit on the branch, newest first: a merged pull
request links to the PR, and a commit pushed straight to the branch links to
the commit. Uses only git, so it needs no token, but the checkout must have
full history (fetch-depth: 0 in Actions).

Usage: scripts/changelog.py [changelog.md] [ref]
The file keeps its hand-written text; only the lines between the two marker
comments are replaced.
"""
import os
import re
import subprocess
import sys

START = "<!-- changelog:start -->"
END = "<!-- changelog:end -->"

# Characters that Liquid, kramdown or HTML would treat as markup. A PR title
# is untrusted text, so each of these becomes a numeric entity and the title
# renders exactly as written.
SPECIAL = set('&<>{}[]()*_`\\|$~#!:"\'%^=+-.')


def escape(text):
    return "".join(f"&#{ord(c)};" if c in SPECIAL else c for c in text)


def first_parent_log(ref):
    # Merge dates in UTC, whatever zone the merge was made in.
    fmt = "%H%x1f%cd%x1f%s%x1f%b%x1e"
    out = subprocess.run(
        ["git", "log", "--first-parent", "--date=format-local:%Y-%m-%d",
         f"--format={fmt}", ref],
        check=True, capture_output=True, text=True,
        env={**os.environ, "TZ": "UTC"},
    ).stdout
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if rec:
            yield rec.split("\x1f")


MERGE = re.compile(r"^Merge pull request #(\d+) from \S+$")
SQUASH = re.compile(r"^(.*) \(#(\d+)\)$")


def entry(repo, sha, date, subject, body):
    m = MERGE.match(subject)
    if m:
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        title, num = (lines[0] if lines else subject), m.group(1)
    else:
        m = SQUASH.match(subject)
        title, num = (m.group(1), m.group(2)) if m else (subject, None)
    if num:
        url = f"https://github.com/{repo}/pull/{num}"
        return f"- {date}: [{escape(title)}]({url}) (#{num})"
    url = f"https://github.com/{repo}/commit/{sha}"
    return f"- {date}: [{escape(title)}]({url}) (commit `{sha[:7]}`)"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "changelog.md"
    ref = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    repo = os.environ.get("GITHUB_REPOSITORY", "tangentcode/methodology")
    text = open(path, encoding="utf-8").read()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        sys.exit(f"{path}: expected one {START} line followed by one {END} line")
    head, rest = text.split(START)
    _, tail = rest.split(END)
    entries = [entry(repo, *rec) for rec in first_parent_log(ref)]
    if not entries:
        sys.exit(f"no commits found on {ref}")
    body = "\n".join(entries)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{head}{START}\n{body}\n{END}{tail}")


if __name__ == "__main__":
    main()
