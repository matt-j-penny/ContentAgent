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

## 2. Choose the data source

Content OS is the default. If its tools are available, call `get_agent_profile`. If the connection fails, explain the failure and offer to reconnect; do not silently treat a failed connection as a choice to work standalone. If Content OS is unavailable, ask whether the user wants to connect it (see the README). If they accept, help them connect and wait until it works. If they explicitly decline, use standalone mode for this conversation. Never ask them to paste an API key into chat. Respect a previous explicit choice in the same conversation; if they later connect Content OS, use it by default.

## 3. Load the right rules and context

- **Content OS:** Read [`content-os.md`](content-os.md) before any Content OS read or write. Load About You and style from `get_agent_profile`. If About You is missing, offer setup. If style is missing, writing skills offer style or a neutral voice.
- **Standalone:** Read [`standalone.md`](standalone.md), then use local profiles or the information the user supplies. Do not call Content OS tools. Follow the standalone instructions in each skill in place of its Content OS-specific reads, writes and status changes. Ask only for context necessary to the job and continue without a complete profile when possible.

## Working files

In Content OS mode, research, outlines, drafts and analysis are temporary working data in `contentagent-work/`, or in conversation if files aren't available. Persist finished outputs as the skill specifies. In standalone mode, use the durable `contentagent/` workspace described in `standalone.md`; do not label it safe to delete. Never overwrite user work without checking first.

## Optional connections

Use them when they're there, and never fail because one is missing:
- **vidIQ** (`mcp__vidiq__*` or similar): channel, keyword and outlier data. Without it, use web search and public YouTube or Instagram pages.
- **Image generation** (any image MCP or API the user has): thumbnails and carousel slides. Without it, write the concept brief only.
- **Web search**: research and fact checks.
