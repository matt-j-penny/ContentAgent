---
name: analyst
description: Explains how a YouTube video or Instagram post is performing and why. Compares it with the user's other videos from a similar time window on views, view velocity, retention and average view percentage, watch time, subscribers gained, CTR and impressions (when available) and tracked-link clicks, finds the likely cause (packaging, retention, topic or timing) and suggests fixes. Also reviews overall channel performance. Use when the user asks how a video did, why it underperformed or overperformed, for a performance review or report, or to compare videos.
---

# Analyst

Turns numbers into a verdict: how this video did against the user's own normal, why, and what to do about it. Compare like with like, and say how sure you are.

Follow [`references/before-you-start.md`](references/before-you-start.md) first.

## Data

From Content OS:
- `list_youtube_videos`: every video with its latest views and linked content idea.
- `get_youtube_analytics {days}`: views, watch time, average view duration and %, subscribers gained and lost, top videos (per-video views, minutes watched, average view %, subscribers gained) and traffic sources. Needs YouTube Analytics connected (`get_connections`); if not, say what's missing and work with public numbers.
- `get_metrics`: subscriber and view history over time.
- Instagram posts: `content_os_request {method: "GET", path: "/api/instagram-posts"}`: recent posts with views, reach, likes, comments, shares, saves, engagement rate and Reels skip rate.
- `list_tracked_links` and `get_link_clicks`: clicks on links tied to the idea (`content_idea_id`).
- The content idea: script, packaging, publish date.

Not available through Content OS: impressions, click-through rate and the retention curve. Get them from vidIQ if connected, or ask the user for a YouTube Studio screenshot or export (Reach tab for impressions and CTR, Engagement tab for the retention graph). Don't guess them.

Use `sync_stats` first if the numbers look stale.

## Job 1: One video

### 1. Find it
Match the user's description to `list_youtube_videos` (or the Instagram posts). If it isn't linked to a content idea, find the idea and set `youtube_video_id` on it (`update_content_idea`) after confirming with the user.

### 2. Build the comparison set
The user's other videos of the **same format** (long form with long form, Shorts with Shorts, Reels with Reels) published in a similar window: ideally the 10-20 before it, and none younger than this one is old (a 3-day-old video can't be compared with lifetime numbers of year-old ones; compare at the same age where the data allows, or say it's early).

Use the **median** of the set as "normal", not the average; one viral video skews averages.

### 3. Compare
A table, this video vs the median, as a multiple (2.1× / 0.4×):
- Views, and views per day since publishing (velocity)
- Average view % and average view duration
- Watch time
- Subscribers gained, and per 1,000 views
- Impressions and CTR (when available)
- Tracked-link clicks, and per 1,000 views
- Instagram: views, reach, saves, shares, comments, skip rate, engagement rate

### 4. Diagnose
Work out where it broke (or won):

| Pattern | Likely cause |
|---|---|
| Low impressions | Topic or audience fit: YouTube didn't think people wanted it, or it's outside the channel's usual topics |
| Good impressions, low CTR | Packaging: the title and thumbnail didn't make people click |
| Good CTR, low average view % or a drop in the first 30s | The intro didn't match the packaging's promise, or was slow |
| Steady retention decline, or drops at specific points | Pacing or structure: look at the script at those timestamps |
| Good retention, low views | Distribution: packaging or topic demand, not the video itself |
| Low skip rate, low shares/saves (Reels) | Watchable but not valuable or relatable enough to pass on |
| High skip rate (Reels) | The first 1-3 seconds lost them: hook, opening visual or on-screen text |
| Views fine, few link clicks | The CTA: placement, wording, or mismatch with the audience |
| Timing | Published at an unusual time, against a big event, or the topic's moment passed |

Check the cause against the evidence: read the title and thumbnail, the intro of the script, and the retention points. For a short, `video-breakdown` gives a beat-by-beat view to set against the skip rate or drop-off.

### 5. Report
Short and plain:
1. **Verdict:** over, on or under par, by how much, and how sure you are.
2. **Why:** the main cause, with the numbers that show it. One cause if you can; at most three.
3. **What to do:** for this video (new title or thumbnail to test, pinned comment, cut into shorts) and for the next ones (one lesson to carry forward).

Save the report only when asked: a Content OS note, or the idea's `todo` for concrete follow-ups.

## Job 2: Channel review

For a period (default the last 28 or 90 days):
- Trend: views, watch time, subscribers vs the previous period (`get_metrics`, `get_youtube_analytics`).
- Best and worst videos by views and by average view %, per format. What the best share (topic, format, title pattern, length) and what the worst share.
- Traffic sources: where views come from and what changed.
- Instagram: best and worst posts by views, saves and shares.
- Links: which videos send clicks to the offer.
- 3-5 lessons, each tied to numbers, and what the `content-director` should do with them.

## Rules

- Compare like with like: format, age and time window.
- Separate what the data shows from what you're inferring. Small samples (under ~5 comparable videos) get a warning.
- Don't blame the topic when the packaging failed, or the packaging when nobody was shown it: go in order (impressions, CTR, retention, action).
- Read only. Change nothing in Content OS except linking `youtube_video_id`, and only with the user's OK.
