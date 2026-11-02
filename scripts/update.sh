#!/bin/sh
# Checks for a new ContentAgent version at most once a week. Every skill runs this first.
repo="$(cd "$(dirname "$0")/.." && pwd)"
stamp="$repo/.last-update-check"

if [ -f "$stamp" ] && [ -z "$(find "$stamp" -mtime +6)" ]; then
  echo "UP_TO_DATE: last checked $(date -r "$stamp" '+%Y-%m-%d')"
  exit 0
fi

before="$(git -C "$repo" rev-parse HEAD 2>/dev/null)" || { echo "NOT_A_GIT_INSTALL: $repo"; exit 0; }
if ! err="$(git -C "$repo" pull --ff-only -q 2>&1)"; then
  echo "UPDATE_FAILED: $err"
  exit 0
fi
touch "$stamp"

after="$(git -C "$repo" rev-parse HEAD)"
if [ "$before" = "$after" ]; then
  echo "UP_TO_DATE: no new version"
else
  sh "$repo/scripts/install.sh" >/dev/null
  echo "UPDATED:"
  git -C "$repo" log --format='- %s' "$before..$after"
fi
