# ContentAgent

Content-creation skills for YouTube and Instagram creators, powered by your Content OS data: a content director, researcher, outliner, script writer, style profile, packaging (titles and thumbnails), analyst and repurposing.

Still being built. See [SPEC.md](SPEC.md) for the plan.

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

Each folder in `skills/` is one skill. Add them to your app's skills:

- **Claude Code:** clone this repo and copy the folders in `skills/` into `~/.claude/skills/`.
- **Claude Desktop:** zip each skill folder and upload it under Settings → Capabilities → Skills.
- **Other apps:** put the folders wherever your app loads skills from, or point it at `AGENTS.md`.

### 4. Optional connections

- **vidIQ:** add the vidIQ MCP server and sign in with your own account. Improves research and analysis.
- **Image generation:** connect any image-generation MCP or API you already use. Needed for thumbnails and carousel images.

### 5. Run setup

Restart your app, then say **"run ContentAgent setup"**. It checks your connections, then asks about your business and audience and builds your style profile.
