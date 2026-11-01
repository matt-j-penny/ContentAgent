# ContentAgent spec

A public, installable set of content-creation skills for YouTube and Instagram creators. Each user connects their own Content OS account; vidIQ is optional but improves research and analysis.

## Where it runs

Any AI app on the user's own machine that supports skills and MCP: Claude Desktop, Claude Code, ChatGPT desktop, Codex, Cursor and similar.

- Skills use the open Agent Skills format (a folder per skill with a `SKILL.md`), so one copy works across tools.
- An `AGENTS.md` at the root points tools without skill support at the same instructions.
- Each skill must work with only the Content OS MCP connected. vidIQ and image generation are used when present and skipped when not.

## Connections

| Connection | Required | How the user connects | Used for |
|---|---|---|---|
| Content OS MCP | Yes | API key from the Content OS API page (`cos_…`), added as a bearer token to `https://the-content-os.com/api/mcp` | Profile, style, boards, ideas, scripts, analytics, links |
| vidIQ MCP | No | Sign in to their own vidIQ account | Competitor and niche data, keyword and outlier research, benchmarks |
| Image generation | No | Any image-generation MCP or API key the user already has | Thumbnails, carousel slides, repurposed assets |
| Deepgram | For `video-breakdown` | Their own API key in `DEEPGRAM_API_KEY` | Word-timed transcripts of short-form videos |
| Apify | No | Apify MCP or API key | Downloading Reels and TikToks when yt-dlp is blocked |
| Web search | No | Whatever the host tool provides | Research and fact checks |

## Data rules

- **Stored in Content OS:** About You profile, style profile, content ideas and their board position, finished scripts, packaging (titles and thumbnails).
- **Kept local and thrown away after use (ephemeral):** research notes, competitor scans, outlines, drafts and analysis working data. When the host tool has file access these go in a local `contentagent-work/` folder that is safe to delete; otherwise they stay in the conversation.
- Only the finished script is saved to a content idea. Research and outlines are never written to Content OS.

## Shared context

Every skill that reads or writes Content OS follows [`knowledge/content-os.md`](knowledge/content-os.md): the boards, what each status means and who moves ideas between them, what each idea field is for and which skill writes it, and the HTML formats the app understands.

Every skill starts by reading two records from Content OS:

1. **About You:** business, offer, audience, niche, competitors, platforms. If it's missing, run `setup` first.
2. **Style profile:** voice, tone, vocabulary, sentence rhythm, hooks they use, phrases to avoid, formatting habits. If it's missing, writing skills offer to run `style` first, or continue with a neutral voice.

## Skills

### setup
First-run onboarding.
- Checks the Content OS connection and which platforms are connected; tells the user how to add vidIQ or image generation if missing.
- Interviews the user to build the About You profile and saves it to Content OS.
- Hands off to `style`.

### content-director
Builds the content strategy and plan: what to post, when, and why, grounded in the user's business and audience. No goal-setting.
- Reads About You, the long- and short-form boards, recent performance and saved inspiration.
- Produces a strategy (content pillars, mix of long and short form, cadence) and a rolling plan.
- Creates, moves and reorders ideas on the Content OS boards directly.
- Routes work to the other skills ("research this", "outline this", "package this").

### researcher
Researches topics, competitors and niche trends.
- Topic ideas, competitor channels and accounts, outlier videos and posts, audience questions, facts and sources for a script.
- Uses vidIQ when connected; otherwise web search and public YouTube/Instagram data.
- Output is ephemeral. It can save a new idea to the board or a reference to Inspiration when the user asks.

### outliner
Turns a topic and research into a strong outline before any script is written.
- Long form: hook/intro, promise, sections with beats, payoff, CTA.
- Short form: hook, open loop, value beats, payoff, CTA.
- Asks the user for their own stories, examples and opinions to include.
- Can map the outline to Content OS storyboard sections and video segments.

### script-writer
Writes the script from an approved outline, in the user's style.
- Long-form and short-form modes. Builds on the existing `shortform-script` and `youtube-intro` skills and the `script-check` agent.
- Asks the user questions where the outline needs their input instead of inventing it.
- Saves the finished script to the content idea in Content OS.

### style
Builds and maintains the user's style profile.
- Analyses their existing content (YouTube transcripts, Instagram captions, past scripts) and drafts a profile.
- Runs a short interview to fill gaps and confirm it.
- Saves to Content OS; can be updated any time ("I never say 'guys'").

### packager
Plans the title and thumbnail together, since they have to work as a pair.
- Reads the idea or script, generates several packaging concepts (title plus thumbnail idea), and ranks them.
- Calls `titles` and `thumbnails` for each concept and saves the chosen options to the idea's packaging in Content OS.

### titles
Writes and scores titles.
- Uses a knowledge file on what makes a good title (curiosity, clarity, specificity, length, title/thumbnail complementarity, niche patterns from vidIQ outliers).
- YouTube titles and Instagram on-screen hooks/captions.

### thumbnails
Designs thumbnail concepts and, if image generation is connected, produces them.
- Uses a knowledge file on what makes a good thumbnail (one focal point, faces and emotion, contrast, minimal text, readable at small size, not repeating the title).
- Outputs a concept brief, and an image when a generator is available. Saves to packaging.

### analyst
Explains how a video is performing and why.
- Compares a video to the user's other videos published in a similar time window: views, view velocity, CTR, impressions, retention and average view percentage, watch time, subscribers gained, and tracked-link clicks.
- Looks for the likely cause (packaging vs. retention vs. topic vs. timing) and suggests fixes.
- Instagram: per-post views, reach, saves, shares and comments where available.

### video-breakdown
Breaks down one short-form video (Reel, TikTok, Short or local file) beat for beat. Built and tested.
- Deepgram nova-3 for word-timed transcript; ffmpeg for scene cuts, flash/fade transitions and frames; the agent views the frames itself. No video model.
- Scripts do the mechanical parts (`prepare.py`: download, transcript, cuts, frames; `timeline.py`: join speech to visual beats and check coverage). The agent describes frames, groups beats, corrects the transcript from captions and writes the structure.
- Output is a local JSON breakdown plus a short summary. Needs a terminal, ffmpeg, yt-dlp and a Deepgram key.
- Used by `researcher` (study outliers), `repurpose` (copy a format) and `analyst` (the user's own shorts).

### repurpose
Turns one piece of content into others.
- Long form into shorts, shorts into carousels (more formats later).
- Each output format has a template describing what a good one looks like.
- Can produce assets: carousel slides and images through any connected image generator.
- New pieces can be added to the short-form board.

## Knowledge files

Shared references the skills read, written once and kept in the repo:

- `knowledge/content-os.md`: how to work with Content OS ideas, statuses, fields and attached records. Written.
- `knowledge/titles.md`: what makes a good title.
- `knowledge/thumbnails.md`: what makes a good thumbnail.
- `knowledge/hooks.md`: hook patterns for long and short form.
- `knowledge/formats/`: one template per repurposing format (short, carousel, …).

These need researching and writing before the skills that use them.

## Build order

1. `setup` and the Content OS changes it depends on (About You, style profile).
2. `style`.
3. `content-director`.
4. `researcher` → `outliner` → `script-writer`.
5. Knowledge files, then `packager`, `titles`, `thumbnails`.
6. `analyst` (after the analytics additions in Content OS).
7. `repurpose`.

## Open questions

- Check each target app's connector settings accepts an `Authorization: Bearer cos_…` header. Desktop apps that run local MCP servers can always use `mcp-remote` or the stdio server; some web connector dialogs only offer OAuth.
- Skills are installed one folder at a time, so they can't see `knowledge/` in the repo. Either the install step copies `knowledge/` alongside them, or a build step copies the knowledge files each skill needs into its folder (`skills/<name>/references/`).
- Which skills from the existing personal set (`shortform-script`, `youtube-intro`, `script-check`, `carousel`) move into this repo as-is?
