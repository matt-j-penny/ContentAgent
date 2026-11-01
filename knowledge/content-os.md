# Working with Content OS

Every ContentAgent skill reads this before it touches Content OS. It explains what lives where, what each status means, which fields a skill may write, and how to write them so they show up properly in the app.

All access goes through the Content OS MCP tools (`list_content_ideas`, `update_content_idea`, `move_content_idea`, …). If a tool is missing, `content_os_request` can call any endpoint in the Content OS API directly.

## The two boards

Content ideas sit on two Kanban boards with the same columns:

| Board | `board` value | Holds `content_type` |
|---|---|---|
| Long form | `long` | `YT Long Form`, `Email` |
| Short form | `short` | `Short Form` |

- `list_content_ideas {board}` returns one board. Read both when planning.
- The board follows `content_type`. Changing an idea's `content_type` to or from `Short Form` moves it to the other board, at the bottom of the same column.
- Instagram content is `Short Form`. A YouTube Short is also `Short Form`.

## Statuses (columns)

In order. Each idea is in exactly one.

| Status | Means | The idea should have | Who moves it here |
|---|---|---|---|
| `Idea` | A captured idea, not being worked on yet | `name`, ideally a one-line `premise` | content-director, researcher, repurpose, or the user |
| `Researching` | Topic, competitors and facts are being gathered | `premise` | researcher, when it starts on the idea |
| `Scripting` | Outline and script are being written | A clear `premise` | outliner or script-writer, when they start |
| `Planning Filming` | Script is done; shots, B-roll and proof are being planned | `script_idea` | script-writer, once the user approves the saved script |
| `To Record` | Ready to film | Script, packaging chosen | The user (a skill only when asked) |
| `To Edit` | Filmed, waiting on the edit | | The user |
| `To Publish` | Edited, waiting to go out | Packaging, `publish_date` | The user |
| `Published` | Live | `youtube_video_id` for YouTube long form | The user, or a skill when asked and the video is found |
| `Graveyard` | Dropped. Kept for reference and for reviving later | | The user, or content-director with the user's OK |

Rules:
- Skills only move ideas forward through `Idea → Researching → Scripting → Planning Filming` on their own. Recording, editing and publishing happen in the real world, so only move into `To Record` or later when the user says so.
- Never move an idea backwards without asking.
- Use `Graveyard` for ideas that are dead. Never `delete_content_idea` unless the user explicitly asks to delete it.
- Moving needs the idea's current status as `expected_status`. Read the idea first (`list_content_ideas`). If the move fails with a conflict, someone else moved it: re-read and ask before trying again.
- Omit `anchor_id` to drop the idea at the bottom of the column. Pass `anchor_id` (and `after: true` to go below it) to place it next to another card, which is how content-director sets priority within a column: higher up means sooner.
- A column can be sorted by `publish_date` instead (`set_column_date_sort`). In a date-sorted column, manual order doesn't matter; set `publish_date` instead.
- Don't change `status` through `update_content_idea`; always use `move_content_idea`.

## Content idea fields

What each field is for, how it appears in the app, and which skill writes it. Rich-text fields are HTML (see "Writing HTML" below).

| Field | App label | Type | What goes in it | Written by |
|---|---|---|---|---|
| `name` | Title | text | Working title of the idea. Short and descriptive; not the final packaged title | Anyone creating the idea |
| `content_type` | Type | `YT Long Form` / `Short Form` / `Email` | The format. Decides the board | Creator of the idea |
| `premise` | Premise: "Core Premise / Hook" | HTML | The core idea and why people should care: one or two sentences up top, then the angle, the promise to the viewer, and key talking points as toggles | content-director, researcher, outliner |
| `script_idea` | Script Idea | HTML | The finished script, and nothing else | script-writer only |
| `todo` | To Do | HTML checklist | Open tasks for this idea (get a guest, record B-roll of X) | Any skill, adding items only |
| `ai_research` | AI Research | HTML | Research findings. Only write here when the user asks to save research; by default research stays local | researcher, when asked |
| `body_text` | Proof → Notes | HTML | Notes about proof and sources | researcher, when asked |
| `thumbnail_ideas` | Packaging → Notes | HTML | Loose thumbnail and title brainstorming that isn't a finished option yet | packager, thumbnails |
| `editing_idea` | Editing Idea (hidden tab) | HTML | Visual style, pacing, transitions | Leave alone for now |
| `publish_date` | Publish date | `YYYY-MM-DD` | Planned or actual publish date | content-director, or the user |
| `tags` | Tags | string[] | Content pillar and topic tags. content-director decides the set; keep it small and reuse existing tags | content-director |
| `inspiration_url` | Inspiration | URL | The video or post that sparked the idea | researcher, content-director |
| `outlier_factor` | Outlier | number | How far the inspiration video outperformed its channel (e.g. `4.2` = 4.2× the channel's typical views) | researcher, from vidIQ or comparison |
| `featured_images` | | string[] | Image URLs shown on the card | Leave alone |
| `youtube_video_id` | Linked YouTube video | text | The published video's ID. Links stats to the idea. Find it with `list_youtube_videos` | analyst, or when moving to `Published` |

`create_content_idea` needs `name` and `content_type`; `status` defaults to `Idea`. New ideas always land at the bottom of their column.

### Before writing a field

1. Read the idea first. `update_content_idea` replaces the whole field, it doesn't append.
2. If the field is empty, write it.
3. If it already has the user's content, don't overwrite it. Show what you'd change and ask, or add to it (for `todo`, append new items to the existing list).
4. `script_idea` especially: if a script already exists, ask whether to replace it, or save the new one below a heading like `<h2>Draft 2</h2>`.

## Records attached to an idea

These are separate tools, each keyed by `content_idea_id`.

### Packaging (`list_packaging`, `add_packaging`, `update_packaging`, `delete_packaging`)
The app's Packaging tab. Each option is one title paired with one thumbnail, shown as a YouTube preview.
- `title`: the exact title as it would appear on YouTube.
- `description`: the thumbnail concept in a sentence or two (what's in it, the text on it, the emotion).
- `image_url`: the thumbnail image, when one has been generated or uploaded.
- `order_index`: lower is better. Put the recommended option first.
- The first option with an image is used as the card's preview on the board.
- Finished options go here; rough brainstorming goes in `thumbnail_ideas`.

### Proof (`list_proof`, `add_proof`, …)
Screenshots and sources that back up claims in the video (results, stats, testimonials). `image_url` plus an optional `caption` saying what it proves. Add proof the user supplies or asks you to save; don't invent it.

### Checklist (`get_idea_checklist`, `set_idea_checklist_item`)
Every idea gets the same production checklist from a template the user controls (`list_checklist_items`). Tick items when a skill has actually done that step. Don't change the template unless asked.

### Storyboard sections and video segments
Hidden in the app for now. An outline can be mapped onto them when the user asks:
- **Sections** (`create_storyboard_section`): the outline's main parts, in order.
- **Segments** (`create_video_segment`): the beats within a section. `section_id` links a beat to its section; `talking_points` is what's said (HTML), `screen_direction` is what's shown (HTML), `visual_type` is one of `talking_head`, `screen_share`, `b_roll`, `graphic`, `demo`; `script_selection_text` is the exact script text the beat covers, which highlights it in the Script tab; `status` is `planning` or `completed`.

### Tracked links (`create_tracked_link`)
Short links with click counts. Pass `content_idea_id` so the analyst can tie clicks to the video.

## Writing HTML

Rich-text fields use the app's editor. Plain HTML works: `<p>`, `<h1>`–`<h3>`, `<strong>`, `<em>`, `<ul>`/`<ol>`/`<li>`, `<blockquote>`, `<a href>`. No `<style>`, scripts, classes, or Markdown: Markdown shows up as literal `#` and `*`.

The app also understands these blocks:

**Toggle** (premise talking points, collapsible; can nest):
```html
<div data-toggle-section="" data-open="false">
  <div data-toggle-title>Talking point</div>
  <div data-toggle-body><p>Details, story, example…</p></div>
</div>
```

**Planning callout** (premise; a box with a tick):
```html
<div data-planning-callout="" data-checked="false"><p>Decide which case study to use</p></div>
```

**Edit direction** (script; tells the editor what to show, kept apart from spoken lines):
```html
<div data-edit-direction-callout=""><p>Cut to screen recording of the dashboard</p></div>
```

**Checklist** (`todo`):
```html
<ul data-type="taskList">
  <li data-type="taskItem" data-checked="false"><p>Record B-roll of the desk setup</p></li>
</ul>
```

### Script format (`script_idea`)
- Spoken lines as `<p>`, one thought per paragraph, written exactly as the user would say it.
- Long form: `<h2>` per section (Hook, Intro, each main section, Payoff, CTA).
- Short form: one block, with the hook as the first paragraph in `<strong>`.
- Visual and edit notes in edit-direction callouts, never mixed into spoken lines.
- No stage directions in brackets inside spoken lines.

### Premise format (`premise`)
```html
<p><strong>One-sentence premise: who it's for and what they'll get.</strong></p>
<p>Why now / why this angle: one or two sentences.</p>
<div data-toggle-section="" data-open="false">
  <div data-toggle-title>Talking point 1</div>
  <div data-toggle-body><p>…</p></div>
</div>
```

## The usual flow

1. **content-director** creates ideas in `Idea` with a name, type, one-line premise and tags, and orders the column by priority.
2. **researcher** moves an idea to `Researching`, works locally, then tightens the `premise` and sets `inspiration_url` and `outlier_factor`. Research stays local unless the user asks to save it to `ai_research`.
3. **outliner** moves it to `Scripting` and writes the outline locally (or into premise toggles if the user wants it in the app).
4. **script-writer** writes the script, saves it to `script_idea`, and once the user approves it moves the idea to `Planning Filming`.
5. **packager / titles / thumbnails** add packaging options at any point after the premise is clear.
6. The user records, edits and publishes, moving the card themselves.
7. **analyst** links `youtube_video_id` once it's live and reports on performance.
8. **repurpose** creates new `Short Form` ideas from a published long-form one, each with its own premise and, when written, its script.

## Other data skills read

- `get_agent_profile`: About You and style profile. Read before planning or writing anything.
- `list_inspiration`: saved videos, posts, titles and thumbnails the user likes. Useful for ideas, titles and thumbnails.
- `list_vault_titles`: proven YouTube titles. `X` and `Y` are placeholders. Read before writing titles and use them as patterns, never copy one word for word.
- `list_vault_hooks`: proven short-form hooks with their source. `[topic]`-style brackets are placeholders. Read before writing short-form hooks and use them as patterns.
- The Vault is shared by every Content OS user and read-only. The user's own taste is in `list_inspiration`; when the two disagree, follow the user's.
- `list_youtube_videos`, `get_youtube_analytics`, `get_metrics`: performance data.
- `list_notes` / `get_note`: the user's own notes pages. Read when relevant; write only when asked.
