---
name: video-breakdown
description: Break down a short-form video (Instagram Reel, TikTok, YouTube Short, or a local file) beat for beat - what is said and exactly when, what is on screen at every moment, how they line up, the hook, structure, pacing, captions, CTA and copyable editing techniques. Use when the user shares a short-form video link and asks to analyse, break down, reverse-engineer or study it, or when researcher, repurpose or analyst need a detailed breakdown of one.
---

# Video breakdown

Produces a time-accurate breakdown of one short-form video: a JSON file detailed enough that someone could rebuild the video beat for beat, plus a short summary for the user.

How it works: the video is never sent to a video model. Deepgram transcribes the audio with exact word timings, ffmpeg finds the cuts and flash transitions and pulls frames, and you look at the frames yourself and describe them. Then the two are joined on one timeline. This gets word and cut timings right to the frame and only quotes on-screen text that's really there.

Follow [`references/before-you-start.md`](references/before-you-start.md) step 1 first (the update check). Content OS is only needed to save results.

## Needs

- A terminal (Claude Code, Codex, Cursor, or any host that can run commands).
- `ffmpeg`, `ffprobe`, `yt-dlp` and `python3` installed. If one is missing, tell the user how to install it (`brew install ffmpeg yt-dlp` on a Mac) and stop.
- `DEEPGRAM_API_KEY` in the environment. If it isn't set, ask the user for their Deepgram key (deepgram.com, about $0.004 per minute of audio) and tell them how to set it. Never write the key into a file in the work folder.
- Optional: an Apify MCP or key, used to download when yt-dlp is blocked.

Everything goes in `contentagent-work/video-analysis/<VIDEO_ID>/` in the user's current folder. It's working data and safe to delete. Nothing is saved to Content OS unless the user asks (see the end).

## Step 1: Prepare (scripted)

Run the prepare script with the link or file:

```bash
python3 <this skill>/scripts/prepare.py "<url or file>" --work contentagent-work/video-analysis
```

Options: `--scene 0.15` if obvious cuts were missed, `--scene 0.35` if handheld footage gives too many; `--language es` (or `auto`) for non-English.

It downloads the video (1080p, H.264 preferred), reads its metadata, transcribes it with Deepgram nova-3, finds pauses, scene cuts, white flashes, black dips and fades, pulls a frame every second plus one just after every cut and in the middle of every transition, and makes a contact sheet. It writes `prepared.json`, which holds `meta`, `transcript` (raw text, words with timings and confidence, low-confidence words, pauses) and `frames` (each with its time and why it was taken).

If it prints `DOWNLOAD_FAILED`: if Apify is connected, use an Instagram or TikTok scraper actor to get the direct video URL, `curl -L -o <folder>/source.mp4 "<url>"`, and rerun the script on that file. Otherwise ask the user to download the video and give you the file.

If there's no audio or no speech, `has_speech` is false; build the timeline from visuals only.

## Step 2: Look at the frames

Open `contact_sheet.jpg` first for the overall shape, then view every frame in `frames/` in order.

Get more frames where you need them:
- **Motion:** around each cut, transition, or place where an element appears, take 4-6 frames 0.1s apart and compare them. Position change = slid in; size change = popped or scaled; opacity = faded; text growing = typed on.
  `python3 <this skill>/scripts/prepare.py frames <folder> 7.50 7.60 7.70 7.80`
- **Small text** (cards, UI, prompts): crop and upscale the region (`w:h:x:y` in source pixels).
  `python3 <this skill>/scripts/prepare.py crop <folder> 12.3 500:300:40:900 prompt_card`

Keep to about 60 frames for a 60-second video, more only where things change fast.

For each frame, note:
- **Layout:** full-frame talking head, split screen (top/bottom, left/right), picture-in-picture, green screen over an image, screen recording, B-roll, or a graphic card.
- **On-screen text, word for word:** captions (and their style: weight, case, colour, position, highlighted word), titles, labels, UI text. If you can't read it, write `[unreadable]`. Never guess.
- **Graphics and overlays:** stickers, icons, arrows, emojis, logos, cut-outs, paper or collage textures, progress bars, zooms, shakes.
- **Screen content:** which app or site, only if it's identifiable from what's visible, and what's shown.
- **Camera:** close-up, medium or wide, punch-in zooms, angle changes.
- **Motion:** how things enter and leave, marked `observed` (seen across dense frames) or `inferred`.
- **Never describe anyone's appearance, clothing or physical traits.** Say "speaker" or "creator".

## Step 3: Visual beats

Group consecutive frames into beats. A new beat starts at every scene cut, transition, layout change, or when an element appears or disappears. Beat boundaries use the cut and transition times from `prepared.json`, not frame times. A beat that starts on a layout change or new element rather than a cut gets a `boundary_reason`.

Write them to `<folder>/beats.json` as a list, covering 0 to the full duration with no gaps:

```json
[{"id": "v1", "start": 0.0, "end": 2.336,
  "layout": "full-frame talking head",
  "on_screen": "Everything visible, in detail (no personal appearance).",
  "on_screen_text": ["exact caption text"],
  "graphics": ["four chore emojis along the bottom third"],
  "motion": "Emojis pop in at ~0.3s.",
  "motion_confidence": "inferred",
  "transition_out": "hard cut at 2.336s",
  "frames": ["frames/f_00.50.jpg", "frames/f_01.50.jpg"]}]
```

### Fix the transcript from captions
Deepgram mishears brand names and jargon ("ChatGPT six" for "ChatGPT-6", "astro" for "ASTRA"). Check every word in `low_confidence_words`, and every brand, product and CTA keyword, against burned-in captions and on-screen text. Where the caption spells it differently, use the caption spelling in `full_text_corrected` and log it in `corrections` with the evidence. Keep the raw text too.

## Step 4: Join the timeline (scripted)

```bash
python3 <this skill>/scripts/timeline.py <folder>
```

It splits speech into phrases (at pauses of 0.15s or more, sentence ends, and beat boundaries that fall mid-sentence), attaches each phrase's words, the beats it overlaps, the on-screen text and nearest frame, adds entries for stretches with no speech, and writes `timeline.json`. It also checks the beats: full coverage, no gaps, boundaries on cuts. Fix anything it reports and rerun.

Then fill in, for every entry:
- `relationship`: how what's said relates to what's shown. One of `illustrates`, `captions_only`, `contrasts`, `reveals_after`, `independent`.
- `note`: one line on how they work together (e.g. "the word 'subtitles' lands as the subtitle track lights up").
- Where a phrase was split by a cut, say so in the note.
- For key moments, the lag between when a thing is said and when it appears (e.g. "graphic appears 0.2s before the word").

## Step 5: Structure

- **Hook (0-3s):** exact words, exact visuals, and the device (pattern interrupt, curiosity gap, bold claim, visual surprise…).
- **Sections:** hook / setup / proof / payoff / CTA, with time ranges.
- **Pacing:** cuts, average shot length and cuts per 10s are in `meta`; add where the pace changes.
- **Caption style:** words per caption card, position, font and colour, highlight behaviour, whether they sync word by word.
- **Audio:** music and its energy (from silences and pauses), sound effects at cuts if you can tell, voice pace (`words_per_minute` in `meta`).
- **CTA:** exact wording, keyword, and when it appears, spoken and on screen.
- **Editing techniques:** concrete things someone could copy ("white-flash card transition between every section", "persistent split layout: raw footage left, illustrated panel right").

## Output

Write `<folder>/<VIDEO_ID>-analysis.json`:

```json
{
  "source_url": "…",
  "method": "ffmpeg frames + scene/brightness detection, viewed by agent; Deepgram nova-3 transcript",
  "meta": "<meta from prepared.json>",
  "summary": "2-4 sentences: what the video is, the claim or story, the visual format, the CTA.",
  "transcript": {
    "source": "Deepgram nova-3",
    "full_text_raw": "…", "full_text_corrected": "…",
    "corrections": [{"raw": "astro", "corrected": "ASTRA", "evidence": "burned-in caption at 18.9s"}],
    "low_confidence_words": [], "words": []
  },
  "visual_beats": "<beats.json>",
  "synced_timeline": "<timeline.json, filled in>",
  "structure": {
    "hook": {"start": 0, "end": 3, "spoken": "…", "visual": "…", "device": "…"},
    "sections": [{"name": "hook", "start": 0, "end": 3}],
    "pacing": "…", "caption_style": "…", "audio": "…",
    "cta": {"spoken": "…", "on_screen": "…", "keyword": "…", "start": 17.0}
  },
  "editing_techniques": ["…"],
  "files": {"video": "source.mp4", "audio": "audio.wav", "deepgram_raw": "deepgram-raw.json",
            "frames_index": "frames.json", "contact_sheet": "contact_sheet.jpg"}
}
```

### Check before delivering
- The timeline covers 0 to the full duration with no gaps, and the last speech ends at the real last-word time.
- Every beat boundary is an ffmpeg cut or transition time, or has a `boundary_reason`.
- Every quoted on-screen string was read from a frame; anything unreadable says `[unreadable]`.
- Brand names and CTA keywords are corrected against captions, and each correction is logged.
- Every motion claim is marked observed or inferred.
- No descriptions of anyone's appearance.
- The JSON parses: `python3 -m json.tool <file> > /dev/null`.

Then give the user 5-10 lines: what the video is, the hook, the format, the pacing, the three most copyable techniques, and the path to the JSON.

## Long videos

Over 3 minutes, the script samples every 2 seconds instead of every second (it still takes a frame after every cut). Work through the frames and beats in chunks of about 30 seconds.

## Content OS

Read [`references/content-os.md`](references/content-os.md) before writing anything. The breakdown itself stays local. When the user asks:
- **Save it as inspiration:** `save_inspiration` with `kind` `instagram_post` or `youtube_video`, the URL, and a short `note` of what's worth copying. Content OS has no TikTok kind, so for TikToks put the link and note in the idea instead.
- **Turn it into an idea:** `create_content_idea` on the short-form board (`content_type` `Short Form`), with `inspiration_url` set to the video and a `premise` built from what made it work. Leave the user's own angle for them to add.
- **It's the user's own video:** hand the breakdown to `analyst` to compare with their other videos.
