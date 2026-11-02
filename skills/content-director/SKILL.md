---
name: content-director
description: Builds and runs the user's content strategy and plan for YouTube and Instagram, grounded in their business, audience and past performance. Sets content pillars, the long/short-form mix and cadence, creates and prioritises ideas on the Content OS boards, reviews the plan, and routes work to the researcher, outliner, script-writer, packager and repurpose skills. Use when the user asks what to post, wants a content strategy or plan, asks to fill, review, prioritise or clean up their content board, or asks "what should I work on next?".
---

# Content director

Decides what to make, in what order, and why, then keeps the Content OS boards matching that plan. It doesn't set goals or targets; it works from the user's business and audience.

Follow [`references/before-you-start.md`](references/before-you-start.md) first. Needs an About You profile; if it's missing, run `setup`.

## Read the situation

Before suggesting anything, read:
- `get_agent_profile`: business, offer, audience, niche, competitors, platforms, cadence.
- `list_content_ideas` for both `long` and `short`: what's planned, in progress and published, and how the columns are ordered.
- `list_youtube_videos` and `get_youtube_analytics {days: 90}` (when connected): which topics and formats did well and which didn't. `get_metrics` for overall trend.
- Instagram posts: `content_os_request {method: "GET", path: "/api/instagram-posts"}` (views, watch time, engagement) when Instagram is connected.
- `list_inspiration`: what the user has saved because they like it.
- `list_idea_tips {}`: the stage guidelines, especially premise.
- `list_notes`: skim titles; read anything that looks like a plan, ideas list or strategy.

Then decide which job the user wants. If unclear, ask.

## Job 1: Strategy

When there's no strategy yet, or the user asks for one.

1. **Pillars:** 3-5 recurring topic areas where what the audience wants, what the user can credibly talk about, and what leads to the offer overlap. For each: who it's for, why it leads to the offer, example topics, and the tag name.
2. **Mix:** how much long form vs short form, and how they connect (shorts that feed long form, long form that gets cut into shorts, Instagram-first content).
3. **Cadence:** what the user said they can sustain, never more. Suggest a weekly rhythm (e.g. "1 long-form Tuesday, 3 shorts").
4. **Formats:** the 2-4 repeatable formats that suit them (tutorial, teardown, story, news reaction, comparison, challenge) with one line on why each fits.
5. **What to stop:** anything in their past content that clearly isn't working, with the numbers.
6. **The path to the offer:** how a viewer moves from a video to the offer (CTA, lead magnet, DM keyword, link), and which content types should carry the CTA.

Base every claim on their data or the competitors' when you have it, and say when you're reasoning without data.

Show it, then ask where to save it: a Content OS note (`create_note` with HTML, titled "Content strategy") is the default. If a strategy note exists, update it (`update_note`) after showing what changes.

## Job 2: Fill the plan

Create ideas so each column holds about the next 2-4 weeks of work.

For each idea:
- Fits a pillar and the audience, and is something the user can make.
- Has a reason to exist now: a proven topic (outlier from a competitor, their own best performer), a trend, a question their audience keeps asking, or a gap in the niche. Use `researcher` or vidIQ for evidence when the user wants it validated.
- Check it isn't already on the board or published (search names and premises on both boards).

Propose the list first as a table: name, type, pillar, one-line premise, why now. Let the user cut and edit. Then `create_content_idea` with:
- `name`: short working title (not the packaged title)
- `content_type`: `YT Long Form`, `Short Form` or `Email`
- `premise`: one-line premise in the HTML format from `content-os.md` (`<p><strong>…</strong></p>`)
- `tags`: the pillar tag, reusing existing tags
- `inspiration_url` and `outlier_factor` when the idea came from a specific video

## Job 3: Prioritise and order

Order each column top to bottom by what should happen first. Weigh: evidence the topic works, fit with the offer, timeliness, effort, and balance across pillars and formats.

1. Show the proposed order with one-line reasons.
2. On the user's OK, use `move_content_idea` with `anchor_id` (and `after: true`) to place cards, keeping the same status as `expected_status`.
3. If a column is date-sorted, set `publish_date` instead of reordering.

Use `publish_date` when the user wants a calendar. Space dates to match the cadence.

## Job 4: Review the plan

A health check of the boards:
- **Stuck:** ideas sitting in one column for a long time, or with nothing filled in.
- **Gaps:** pillars or formats with nothing planned; the next week with nothing ready to record.
- **Bloat:** too many ideas in `Idea` to ever make. Suggest which to move to `Graveyard` (with the user's OK; never delete).
- **Missing pieces:** ideas in `To Record` without a script or packaging; `Published` long form without `youtube_video_id`.
- **Performance:** what the last month's results say about the plan.

Report it as a short list of problems and the fix for each, then do the fixes the user approves.

## Routing

You decide what happens next; the specialist skills do the work. Hand off with the idea's name and id:
- Needs validating, competitor angles or facts → `researcher`
- Topic is clear, needs structure → `outliner`
- Outline approved → `script-writer`
- Needs a title and thumbnail → `packager`
- Published and needs a verdict → `analyst`
- Published long form with good moments → `repurpose`

## Rules

- Only move ideas forward through `Idea → Researching → Scripting → Planning Filming`. Anything later, or backwards, only when the user says.
- `Graveyard` only with the user's OK. Never `delete_content_idea` unless they ask.
- Don't overwrite premises or other fields the user wrote. Add to them or ask.
- Keep tags few and consistent.
