# ContentAgent

Content-creation skills for YouTube and Instagram creators, powered by your Content OS data: a content director, researcher, outliner, script writer, style profile, packaging (titles and thumbnails), analyst and repurposing.

See [SPEC.md](SPEC.md) for how it fits together.

## Getting started

Works in any AI app on your own computer that supports skills and MCP servers, such as Claude Desktop, Claude Code, ChatGPT desktop, Codex or Cursor.

The quickest way: copy the install prompt from the **Tools** page in Content OS and paste it into your AI app. It will follow the steps below for you.

### 1. Get your Content OS API key

In Content OS, open **AI & Connections** and create an API key. It starts with `cos_` and is only shown once.

### 2. Connect Content OS

Add the Content OS MCP server, sending your key as a bearer token:

- **URL:** `https://the-content-os.com/api/mcp`
- **Header:** `Authorization: Bearer cos_…`

Claude Code:

```bash
claude mcp add --transport http content-os https://the-content-os.com/api/mcp --header "Authorization: Bearer cos_…"
```

Claude Desktop and other apps that take a JSON `mcpServers` config:

```json
"content-os": {
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://the-content-os.com/api/mcp", "--header", "Authorization: Bearer cos_…"]
}
```

### 3. Install the skills

Clone this repo to `~/.contentagent` and link the skills into your app. Installed this way, ContentAgent checks for updates once a week and pulls them itself.

```bash
git clone https://github.com/matt-j-penny/ContentAgent.git ~/.contentagent
```

```bash
sh ~/.contentagent/scripts/install.sh
```

That links every skill into `~/.claude/skills/` (Claude Code). For another app, pass its skills folder: `sh ~/.contentagent/scripts/install.sh <folder>`.

- **Claude Desktop:** zip each folder in `~/.contentagent/skills/` and upload it under Settings → Capabilities → Skills (`cd ~/.contentagent/skills && for d in */; do zip -qr "${d%/}.zip" "$d"; done`). Uploaded skills can't update themselves; re-upload after `git -C ~/.contentagent pull`.
- **Apps without skills:** point them at `~/.contentagent/AGENTS.md`.

### 4. Optional connections

- **vidIQ:** add the vidIQ MCP server and sign in with your own account. Improves research and analysis.
- **Image generation:** connect any image-generation MCP or API you already use. Needed for thumbnails and carousel images.
- **Video breakdowns:** install `ffmpeg` and `yt-dlp` (`brew install ffmpeg yt-dlp` on a Mac) and set `DEEPGRAM_API_KEY` to your own Deepgram key. Needs an app that can run commands, such as Claude Code, Codex or Cursor.

### 5. Run setup

Restart your app, then say **"run ContentAgent setup"**. It checks your connections, then asks about your business and audience and builds your style profile.

## Skills

| Skill | What it does |
|---|---|
| `setup` | Checks connections and builds your About You profile |
| `style` | Builds your style profile from your content and a short interview |
| `content-director` | Strategy, plan and board priorities; routes work to the other skills |
| `researcher` | Topic ideas, outliers, competitors and facts |
| `outliner` | Outlines a video before it's scripted |
| `script-writer` | Writes long- and short-form scripts in your voice |
| `packager` | Plans the title and thumbnail together |
| `titles` | Writes and scores titles and short-form hook text |
| `thumbnails` | Thumbnail concepts and images |
| `analyst` | How a video did against your normal, and why |
| `repurpose` | Long form into shorts, videos into carousels |
| `video-breakdown` | Beat-by-beat breakdown of a short-form video |

Every skill checks for a new ContentAgent version once a week before it starts.
