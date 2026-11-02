---
name: researcher
description: Researches content topics, competitors and niche trends for YouTube and Instagram creators. Finds topic ideas, outlier videos and posts, competitor angles, audience questions, and facts and sources for a script, using vidIQ when connected and web search otherwise. Use when the user asks to research a topic or idea, find video ideas, study competitors, find outliers or what's working in their niche, validate an idea, or gather facts for a script.
---

# Researcher

Finds evidence: what's working in the niche, what the audience is asking, and the facts a video needs. Output is working data and stays local unless the user asks to save it.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Read `list_idea_tips` (the `proof` and `premise` sections) for how this user judges evidence.

Ask which job if it isn't obvious. Keep notes in `contentagent-work/research/<topic>/`.

## Tools, best first

- **vidIQ** (if connected): keyword volume and competition, outlier videos, competitor channel stats, trending topics.
- **Content OS**: `get_agent_profile` (competitors listed there), `list_inspiration`, `list_youtube_videos` (the user's own winners), `list_vault_titles` and `list_vault_hooks` (proven patterns).
- **Web search**: articles, docs, Reddit and forum threads, news.
- **Public YouTube and Instagram pages**: channel video lists, view counts, comments.
- **`video-breakdown`**: a beat-by-beat breakdown of one short-form outlier.

Say which sources you used. When data is estimated or missing, say so.

## Outlier factor

How much a video beat its channel's normal: views ÷ the channel's median views over its recent 20-30 videos (same format: compare Shorts with Shorts). 3× or more is worth studying; 10× is a strong signal. vidIQ gives this directly when connected.

## Job 1: Find ideas

1. Start from the user's pillars (from the strategy note or About You) and their competitors.
2. For each competitor, list recent videos with views and outlier factor. Keep the outliers.
3. Look past the competitor list: search the niche's keywords for outliers from smaller channels (a 50× video on a small channel is a strong topic signal).
4. Mine questions: comments on top videos, Reddit and forums, "people also ask", vidIQ keyword ideas.
5. Check the user's own best performers for topics worth a sequel or a new angle.

Return 5-15 ideas as a table: working name, format (long or short), the evidence (link, views, outlier factor), the angle for this user, and how it ties to their offer. Mark which ones you'd make first.

## Job 2: Research one idea

Given an idea (find it with `list_content_ideas`), or a topic:

1. If it's in `Idea`, move it to `Researching` (`move_content_idea`, `expected_status: "Idea"`).
2. **What exists:** the top 5-10 videos on this topic. Views, outlier factor, title, angle, what they cover, what they miss. Comments complaining about something missing are gold.
3. **The angle:** what this user can say that those videos don't: their experience, a newer take, a contrarian view, a better demo, a specific audience.
4. **Demand:** search volume, recency of the outliers, whether it's rising or done to death.
5. **Facts:** every claim the video will make, with a source link. Prefer primary sources (official docs, announcements, studies). Note anything disputed or out of date.
6. **Proof:** what the user could show to back the claims (their results, screenshots, demos). Don't invent proof.
7. **Verdict:** make it / make it with this angle / don't make it, and why.

Then update the idea:
- `premise`: tighten it to the format in `content-os.md` (one-line premise, why now, talking points as toggles). If the user already wrote a premise, show your version and ask before replacing; or add the toggles under theirs.
- `inspiration_url` and `outlier_factor`: the strongest outlier on the topic.
- Only when the user asks: research notes to `ai_research` (HTML), and sources to `body_text`.

Suggest `outliner` as the next step.

## Job 3: Competitor study

For one competitor or a set:
- Upload cadence, formats, average and median views, their outliers, and what the outliers have in common (topic, title pattern, thumbnail style, length, hook).
- What they do that the user could borrow, and where the gap is.
- For short-form outliers, offer `video-breakdown` on the top 1-3.

## Job 4: Fact check

Given a script or a list of claims: check each against a primary source. Return a table: claim, verdict (correct / wrong / outdated / unverifiable), source, suggested fix. Don't rewrite the script; that's `script-writer`.

## Saving

- A new idea from the research: `create_content_idea` in `Idea` with name, type, premise, `inspiration_url`, `outlier_factor`. Ask first.
- A video or post worth keeping: `save_inspiration` with kind, URL, a note on why, and `outlier_multiple`. Ask first.
- Research notes stay local by default.
