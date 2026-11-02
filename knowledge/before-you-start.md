# Before you start

Every ContentAgent skill does these steps first, once per conversation. If another ContentAgent skill already did them in this conversation, skip to the skill.

## 1. Check for updates

ContentAgent is installed as a git clone in `~/.contentagent`, with each skill linked into the app's skills folder. If you can run commands, run:

```bash
sh ~/.contentagent/scripts/update.sh
```

It only goes online when the last check was more than a week ago, so it's quick. Then act on the first word it prints:

| Output | Do |
|---|---|
| `UP_TO_DATE` | Carry on. Say nothing. |
| `UPDATED` | Tell the user in one line that ContentAgent updated, with the change list it printed. Re-read this skill's `SKILL.md` (it may have changed), then carry on. New skills appear after the app restarts. |
| `UPDATE_FAILED` | Tell the user in one line that the update check failed and why, then carry on with the installed version. If it's local changes blocking the pull, suggest `git -C ~/.contentagent stash` or a fresh install. |
| `NOT_A_GIT_INSTALL` | ContentAgent was copied in rather than cloned, so it can't update itself. Tell the user once, and point them at the install steps in the README (clone to `~/.contentagent`, then run `scripts/install.sh`). Carry on. |
| No such file | Same as `NOT_A_GIT_INSTALL`. |

If you can't run commands (a chat app with no terminal), skip this step.

## 2. Check Content OS is connected

Call `get_agent_profile`. If the Content OS tools aren't available, stop and tell the user to connect the Content OS MCP server (README, step 2), or to run `setup`.

## 3. Read the rules

Read [`content-os.md`](content-os.md) before reading or writing anything in Content OS.

## 4. Load the user

From `get_agent_profile`:
- **About You** missing or nearly empty: say so and offer to run `setup` first. Only `setup`, `style` and `video-breakdown` may carry on without it.
- **Style profile** missing: writing skills (script-writer, titles, repurpose) offer to run `style` first, or carry on in a plain, neutral voice if the user prefers.

## Working files

Research, outlines, drafts and analysis are working data. When you can write files, keep them in `contentagent-work/` in the user's current folder (it's safe to delete). Otherwise keep them in the conversation. Only what each skill says gets saved to Content OS.

## Optional connections

Use them when they're there, and never fail because one is missing:
- **vidIQ** (`mcp__vidiq__*` or similar): channel, keyword and outlier data. Without it, use web search and public YouTube or Instagram pages.
- **Image generation** (any image MCP or API the user has): thumbnails and carousel slides. Without it, write the concept brief only.
- **Web search**: research and fact checks.
