---
name: style
description: Builds and maintains the user's style profile (voice, tone, vocabulary, sentence rhythm, hooks they use, phrases to avoid, formatting habits) from their existing scripts, YouTube transcripts and Instagram captions plus a short interview, and saves it to Content OS. Use when the user asks to build, update or check their style or voice profile, says something like "I never say 'guys'" or "that doesn't sound like me", or when a writing skill finds the style profile missing.
---

# Style

The style profile is what makes every script, title and caption sound like the user and not like an AI. It's built from evidence (what they actually say) and confirmed by them.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Style can run without an About You profile, but it's better with one.

## Quick edits

If the user just wants to change one thing ("I never say 'guys'", "less formal"), read the profile with `get_agent_profile`, make the edit in the right section, show the changed lines, and save with `update_agent_profile {style}`. Done; skip the rest.

## Step 1: Gather samples

Aim for 8-15 samples of the user talking or writing in their own voice, mixed across formats. Best first:

1. **Their finished scripts** in Content OS: `list_content_ideas` on both boards, and read `script_idea` for ideas in `Planning Filming` or later. These are closest to what ContentAgent will write.
2. **YouTube transcripts** of their recent, best-performing videos (`list_youtube_videos` for IDs and views). Get transcripts with whatever's available: a transcript MCP, `yt-dlp --write-auto-subs --skip-download`, or ask the user to paste a few.
3. **Short-form transcripts**: their recent Shorts or Reels. `video-breakdown` gets a word-accurate transcript if a terminal and Deepgram are available.
4. **Instagram captions**: from their profile page or an Instagram tool if connected.
5. **Anything they paste**: emails, newsletters, posts.

Weight videos that performed well more heavily; that's the voice that works. Auto-captions mishear names and jargon, so judge rhythm and phrasing, not spelling. Keep samples in `contentagent-work/style/`.

If there's nothing to analyse (a new creator), skip to the interview and say the profile will improve once they've published a few videos.

## Step 2: Analyse

Measure, don't guess. For spoken samples, separately for long and short form:

- **Sentence length:** typical words per sentence, how much it varies, how short the shortest punches are.
- **Openers:** how videos start. Quote 3-5 real first lines.
- **Signature phrases:** words and phrases they repeat (with counts). Their transitions ("so", "now", "here's the thing").
- **Vocabulary:** plain or technical, slang, swearing, British or American spelling, words they never use.
- **Person and address:** "you" vs "we" vs "I", how they refer to the audience.
- **Tone:** e.g. dry, hype, calm teacher, blunt, playful. Pick 3 adjectives and back each with a quote.
- **Humour:** if any, what kind.
- **Structure habits:** lists, stories, demos, how they close, how they do CTAs.
- **Captions and on-screen text:** case, emoji use, length, hashtags.

## Step 3: Interview

Show a short summary of what you found, then ask 4-6 questions to confirm and fill gaps:
- "Does this sound like you? What's off?"
- Words or phrases they hate, or that sound fake in their mouth.
- Creators whose style they admire, and what specifically.
- How they want to come across (and how they don't).
- Anything they say off camera that should be in their content but isn't.

## Step 4: Write the profile

Markdown. Every rule should be specific enough that a writer could check a script against it. Quote real lines as examples.

```markdown
# Style profile

## Voice in one line
…

## Tone
- Adjective: what it means for them, with a real quote

## Sentence rhythm
- Long form: …
- Short form: …

## Words and phrases they use
- "…" (how and when)

## Never use
- "…" (why)

## How they open
- Long form: … (examples)
- Short form: … (examples)

## How they close and do CTAs
…

## Structure habits
…

## On-screen text and captions
…

## Spelling and formatting
…

## Notes
- Things the user told us directly (dated)
```

Show it, apply corrections, save with `update_agent_profile {style}`. Pass only `style`; omitting `about` keeps the About You profile.

## Step 5: Test it

Rewrite one paragraph from a sample, in the new profile, without looking back at the original, and show both. Ask if the rewrite sounds like them. If not, fix the profile, not just the paragraph.

Then suggest `content-director` if there's no plan yet.
