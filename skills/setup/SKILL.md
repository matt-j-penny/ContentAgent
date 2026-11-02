---
name: setup
description: First-run onboarding for ContentAgent. Checks the Content OS connection and optional connections (vidIQ, image generation, Deepgram), interviews the user about their business, offer, audience, niche and competitors, saves their About You profile to Content OS, then hands off to style. Use when the user says "run ContentAgent setup", "set up ContentAgent", "onboard me", wants to update their business or audience details, or when another ContentAgent skill finds the About You profile missing.
---

# Setup

Gets a new user ready: connections checked, About You profile saved. Takes about ten minutes of the user's time. Ends by handing off to `style`.

Follow [`references/before-you-start.md`](references/before-you-start.md) steps 1-3 first. This skill is the one that creates the About You profile, so don't stop if it's missing.

## Step 1: Connections

Check each and report them as one short list (connected / not connected / how to fix):

1. **Content OS MCP.** If its tools aren't available, stop here and walk the user through the README's step 2: create an API key on the **AI & Connections** page (starts with `cos_`), then add the server with the key as a bearer token. For Claude Code that's:
   ```bash
   claude mcp add --transport http content-os https://the-content-os.com/api/mcp --header "Authorization: Bearer cos_…"
   ```
   Never ask the user to paste the key into the chat; tell them to put it in the command or config themselves. They need to restart the app afterwards.
2. **Platforms in Content OS.** `get_connections`. YouTube and Instagram are optional but the analyst and director work much better with them. If one's missing, tell them it's connected in Content OS under **AI & Connections** (YouTube needs a Data API key and handle; YouTube Analytics needs a one-time Google sign-in; Instagram goes through Zernio). Don't connect them yourself unless the user gives you the key in a command they run.
3. **vidIQ** (optional): is a vidIQ MCP available? If not, say it improves research and analysis, and that they add the vidIQ MCP server and sign in with their own account.
4. **Image generation** (optional): is any image-generation tool available? If not, say thumbnails and carousels will be briefs only until they connect one.
5. **Video breakdowns** (optional, needs a terminal): `ffmpeg`, `yt-dlp`, `python3` installed, `DEEPGRAM_API_KEY` set. Check with `command -v` and `[ -n "$DEEPGRAM_API_KEY" ]`; never print the key.
6. **Updates:** if `~/.contentagent/.git` doesn't exist, ContentAgent was copied in and won't update itself. Recommend the git install from the README.

Missing optional connections don't block setup. Carry on.

## Step 2: About You interview

Call `get_agent_profile`. If an About You profile exists, show a short summary and ask what's changed instead of starting over.

Otherwise interview the user. Ask one or two questions at a time, in plain language, and follow up on vague answers ("everyone" is not an audience). Before asking, look for answers yourself: their YouTube channel and recent videos (`list_youtube_videos`), `get_metrics`, their website if they mention one. Then confirm what you found rather than asking from scratch.

Cover:
1. **Business:** what they do, and how content makes them money (product, service, community, sponsorship, affiliate, job).
2. **Offer:** what they sell, price range, and where content sends people (link, DM keyword, lead magnet).
3. **Audience:** who they want watching. Role or situation, skill level, what they're struggling with, what they want. One main audience, plus any secondary.
4. **Niche:** the topic area and the angle that makes them different from others in it.
5. **Platforms:** which of YouTube long form, YouTube Shorts and Instagram they post on, and how often they realistically can.
6. **Competitors and peers:** 3-8 channels or accounts their audience also watches. Handles or links.
7. **Proof and credibility:** results, numbers, experience they can talk about honestly.
8. **Boundaries:** topics they won't cover, claims they can't make, anything brand-sensitive.

Stop once you have enough to plan content. Don't ask about goals or targets; ContentAgent doesn't set them.

## Step 3: Save

Write the profile as markdown, using the user's own words where they're good:

```markdown
# About You

## Business
…
## Offer
- What: …
- Price: …
- Where content sends people: …
## Audience
- Main: …
- They struggle with: …
- They want: …
- Secondary: …
## Niche and angle
…
## Platforms and cadence
| Platform | Posting | Realistic cadence |
|---|---|---|
## Competitors and peers
- @handle (platform): why they're relevant
## Proof
- …
## Boundaries
- …
```

Show it to the user, apply their corrections, then `update_agent_profile {about}`. Only pass `about`; leaving `style` out keeps the stored style profile.

## Step 4: Hand off

Tell the user what's set up and what's missing in two or three lines, then:
- No style profile yet: "Next I'll build your style profile from your existing videos and a few questions." Run `style`.
- Style profile exists: suggest `content-director` to build a plan.
