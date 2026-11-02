#!/bin/sh
# Links each skill folder into the app's skills folder, so a git pull updates them in place.
set -e
repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="${1:-$HOME/.claude/skills}"
mkdir -p "$dest"
for dir in "$repo"/skills/*/; do
  name="$(basename "$dir")"
  if [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ]; then
    echo "Skipped $name: $dest/$name is a copy, not a link. Delete it and rerun to keep it up to date."
    continue
  fi
  ln -sfn "${dir%/}" "$dest/$name"
done
echo "ContentAgent skills linked into $dest"
