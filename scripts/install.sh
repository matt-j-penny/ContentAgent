#!/bin/sh
# Links each skill folder into the app's skills folder, so a git pull updates them in place.
set -e
repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="${1:-$HOME/.claude/skills}"
mkdir -p "$dest"
for dir in "$repo"/skills/*/; do
  name="$(basename "$dir")"
  target="$dest/$name"
  desired="${dir%/}"
  if [ -L "$target" ]; then
    if [ "$(readlink "$target")" != "$desired" ]; then
      echo "Skipped $name: an existing skill link points elsewhere."
      continue
    fi
  elif [ -e "$target" ]; then
    echo "Skipped $name: an existing skill is already installed."
    continue
  fi
  ln -sfn "$desired" "$target"
done
echo "ContentAgent skills linked into $dest"
