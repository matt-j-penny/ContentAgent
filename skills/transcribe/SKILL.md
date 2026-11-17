---
name: transcribe
description: "Transcribe a video or audio file with word-level timestamps — not just a plain transcript. Use when the user asks to transcribe footage, needs a transcript to find precise moments in audio/video, or when another workflow (cutting, captioning, finding a quote) needs to know exactly when each word was spoken. Tries Deepgram by default; other word-timed providers only on request, and refuses to settle for a transcription source that only returns sentence-level or no timestamps."
metadata:
  version: 1.0.0
  last_updated: 2026-09-08
---

# Transcribe

You produce one artifact: a transcript where every word carries its own start/end timestamp. This skill doesn't cut, caption, or edit anything — it's the input other workflows (rough-cut, caption generation, quote-finding) build on, so getting the timestamps right matters more than the prose of the transcript itself.

Follow [references/before-you-start.md](references/before-you-start.md) for Content OS or standalone mode. Use the creator's local video manifest when available; it is a local editing rulebook, not a Content OS record. Never overwrite source media.

## Before Starting

Gather or confirm:
1. Path to the source file — video or audio, either works.
2. What the transcript is for, if it's not obvious — this affects nothing about *how* you transcribe, but confirms word-level timestamps are actually needed (they always are for this skill; if the user only wants readable prose with no timing need, a plain transcript is faster and this skill is overkill).
3. Transcription preference: Deepgram by default; use another word-timed provider only when explicitly requested.

## Why word-level, not sentence-level

A sentence- or paragraph-level timestamp only tells you roughly where something was said — useless for finding an exact cut point, syncing a caption to a specific word, or locating a quote to the frame. Word-level timestamps are what make a transcript *usable* as data rather than just readable text. Never accept a transcription source or API mode that only returns coarser-than-word timing.

## Workflow

### 1. Extract audio, if given a video

```bash
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

Transcribe the audio directly if one is already provided — no need to go through video.

### 2. Transcribe, in preference order

**Deepgram (default, try first):**

```bash
curl -s -X POST \
  "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true&paragraphs=true&utterances=true&words=true" \
  -H "Authorization: Token ${DEEPGRAM_API_KEY}" \
  -H "Content-Type: audio/mpeg" \
  --data-binary @audio.mp3 \
  -o transcript.json
```

`words=true` is what produces the per-word array — without it Deepgram only returns the flat transcript string. The response's word-level data lives at `results.channels[0].alternatives[0].words[]`, each entry shaped `{word, start, end, confidence, punctuated_word}`. Sentence-level data (useful for reading the transcript back, not for cut points) is at `results.channels[0].alternatives[0].paragraphs.paragraphs[].sentences[]`.

If Deepgram is unavailable, explain what is missing. Use a different word-timed provider only when the user explicitly requests it; verify its timestamp format before proceeding.

### 3. Verify before handing off

Before treating the transcript as done, confirm:
- The word array actually has per-word `start`/`end` values, not just a segment-level range repeated across words (a bug in some Whisper wrapper configs).
- Timestamps are in seconds relative to the file that was actually transcribed — if a video's audio was extracted first, timestamps are relative to that extracted audio, not the original video's timeline (usually the same thing, but check if the extraction had a `-ss` offset).
- Confidence/quality looks reasonable — spot-check a few words against the audio if anything downstream depends on precision (e.g. a rough cut).

### 4. Hand off

Return (or save) the word-level array itself, not just the transcript text — whatever consumes this (a cut list, a caption track, a search) needs the timestamps, not the prose.

## Common Mistakes

1. **Using a transcription mode/endpoint that only returns sentence- or paragraph-level timing** — check the response actually has a per-word array before moving on.
2. **Falling back to Whisper or ElevenLabs first "because it's faster/cheaper"** — the default order (Deepgram by default; alternatives only when explicitly requested) exists for a reason; ask before using an alternative.
3. **Losing track of the timeline the timestamps are relative to** — especially after any audio extraction step with an offset.
4. **Discarding the word-level array and keeping only the flat transcript string** — that throws away the one thing this skill exists to produce.
5. **Not verifying `words=true` (or the equivalent) was actually set** — some transcription requests silently succeed with only prose returned if the timestamp flag was omitted.

## Task-Specific Questions

1. Use Deepgram, or has the user explicitly requested another word-timed transcription source?
2. Does the downstream use need the transcript saved to a file, or just returned inline for immediate use in this task?
3. Is the source already audio-only, or does it need extracting from a video first?
