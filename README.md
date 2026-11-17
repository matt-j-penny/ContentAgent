# ContentAgent

Content-creation skills for YouTube and Instagram creators, using Content OS by default, with a standalone local mode: a content director, researcher, outliner, script writer, style profile, packaging (titles and thumbnails), analyst and repurposing.

See [SPEC.md](SPEC.md) for how it fits together.

## Getting started

Works in any AI app on your own computer that supports skills and MCP servers, such as Claude Desktop, Claude Code, ChatGPT desktop, Codex or Cursor.

The quickest way: copy the install prompt from the **Tools** page in Content OS and paste it into your AI app. It will follow the steps below for you.

### 1. Choose how to work

Content OS is the default. To connect it, follow steps 2 and 3 below. If you prefer not to connect, install the skills in step 4, run setup, and decline the connection when asked. Standalone mode saves your profiles and work in a local `contentagent/` folder (or your chosen location). In apps without file access, work stays in the conversation.

### 2. Get your Content OS API key

In Content OS, open **AI & Connections** and create an API key. It starts with `cos_` and is only shown once.

### 3. Connect Content OS

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

### 4. Install the skills

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

### 5. Optional connections

- **vidIQ:** add the vidIQ MCP server and sign in with your own account. Improves research and analysis.
- **Image generation:** connect any image-generation MCP or API you already use. Needed for thumbnails and carousel images.
- **Video breakdowns:** install `ffmpeg` and `yt-dlp` (`brew install ffmpeg yt-dlp` on a Mac) and set `DEEPGRAM_API_KEY` to your own Deepgram key. Needs an app that can run commands, such as Claude Code, Codex or Cursor.

### 6. Run setup

Restart your app, then say **"run ContentAgent setup"**. It checks your connections, then asks about your business and audience and builds your style profile.

## Skills

| Skill | What it does |
|---|---|
| `setup` | Checks connections and builds your About You profile |
| `style` | Builds your style profile from your content and a short interview |
| `content-director` | Strategy, plan and board priorities; routes work to the other skills |
| `researcher` | Topic ideas, outliers, competitors and facts |
| `yt-video-research` | Research a video topic using competitors, transcripts and comments |
| `instagram-research` | Research and rank public Instagram competitor posts |
| `outliner` | Workshops a video idea and outlines it before scripting |
| `script-writer` | Writes long- and short-form scripts in your voice |
| `packager` | Plans the title and thumbnail together |
| `titles` | Writes and scores titles and short-form hook text |
| `thumbnails` | Thumbnail concepts and images |
| `analyst` | How a video did against your normal, and why |
| `repurpose` | Long form into shorts, videos into carousels |
| `carousel-generator` | Create reusable carousel designs and optional video slides |
| `video-breakdown` | Beat-by-beat breakdown of a short-form video |
| `video-manifest` | Capture an editing style from project files, video and interviews |
| `youtube-editing-style` | Analyse the editing style of a long-form or short video |
| `transcribe` | Produce word-timed transcripts for editing |
| `rough-cut` | Plan and make a transcript-based rough cut |
| `capcut-editor` | Create a new editable CapCut rough-cut draft on macOS |
| `audio-design` | Mix supplied music and timed sound effects under video |
| `b-roll` | Plan and insert supplied video cutaways over existing footage |
| `short-clip` | Reframe a selected interval as a vertical clip |
| `face-tracking` | Find face positions for a face-following crop |
| `gaze-analysis` | Propose camera/screen layouts from corroborated cues |
| `programmatic-short` | Assemble a vertical image-and-narration video |
| `3d-video` | Render an editable 3D object turntable in Blender |
| `motion-reference` | Analyse and recreate motion graphics with available tools |
| `screen-recording` | Plan, capture or edit a screen-share with available tools |
| `ai-media` | Generate visual assets with an available image or video provider |
| `editor-connection` | Discover and use available video-editor connections |

Every skill checks for a new ContentAgent version once a week before it starts.

Standalone mode includes a snapshot of the shared title and short-form hook Vault. Thumbnail examples may be supplied by the user or researched; a shared thumbnail URL library is not included. Analytics require an available source or user-supplied data.

Carousel rendering needs Node.js, Playwright and its Chromium browser; video slides also need ffmpeg. Image generation is optional. See the carousel-generator skill for installation and usage.

Video-manifest and editing workflows use local files. Video analysis and rough cutting need ffmpeg; video transcription uses Deepgram by default. The manifest can be used without a video or API key through an interview. See each skill for supported inputs and dependencies.

The CapCut integration creates new single-source drafts only. It requires macOS and CapCut; close CapCut before draft creation. Its draft format has not yet been verified against every CapCut version.

Video creation dependencies vary by skill. Local clips, B-roll, audio mixes and image-based shorts need ffmpeg; 3D turntables need Blender. Motion-reference capture needs Pillow and ffmpeg. Screen recording, AI generation and third-party editors require compatible tools to be available in the host. The CapCut bridge currently creates new drafts only and has not been live-tested against every version.

Face tracking uses OpenCV and the bundled YuNet model. Camera/screen analysis optionally uses MediaPipe and a separately supplied Face Landmarker model; head orientation alone cannot reliably establish eye gaze.
