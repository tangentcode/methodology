#!/usr/bin/env bash
# Write changelog.md: one line per merged pull request, newest first,
# each linking to its PR. Runs in the Pages workflow before the Jekyll
# build, so the page is always current. Needs gh and GH_TOKEN.
set -euo pipefail
repo="${GITHUB_REPOSITORY:-tangentcode/methodology}"
out="${1:-changelog.md}"
{
  echo "# Changelog"
  echo
  echo "Every change to this methodology lands as a merged pull request. Newest first."
  echo "The full history is in the [commit log](https://github.com/$repo/commits/main)."
  echo
  gh pr list -R "$repo" --state merged --base main --limit 1000 \
    --json number,title,url,mergedAt \
    --jq 'sort_by(.mergedAt) | reverse | .[] |
      "- \(.mergedAt[0:10]): [\(.title)](\(.url)) (#\(.number))"'
} > "$out"
