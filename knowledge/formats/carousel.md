# Format: Instagram carousel

Read by `repurpose`. A carousel is a short, swipeable lesson. People save carousels they'll come back to and share ones that make them look smart, so build for saves and shares.

## Structure (5-10 slides)

1. **Cover (slide 1):** the hook. 4-10 words, big. A promise, a number, a contrarian take or a "stop doing X". Must make sense with no caption. A small cue to swipe (an arrow, "→").
2. **Setup (slide 2):** why it matters or the problem, in one or two short lines. Re-hook: the reason to keep swiping.
3. **Value slides (3 to N-1):** one idea per slide. A heading (3-7 words) plus at most 25 words of body, or a visual (screenshot, diagram, before/after, stat). Number them if it's a list.
4. **Payoff:** the summary, the result or the strongest point.
5. **CTA (last slide):** one action. Save this, share with someone who needs it, comment a keyword, follow for more on the topic. Match the user's offer when there's a lead magnet or DM keyword.

## Making it read well

- One idea per slide. If a slide needs more than 25 words, split it.
- Big text: nothing smaller than about 28px on a 1080-wide slide. Readable without zooming.
- Same layout on every slide (title position, margins, slide number) so swiping feels smooth. Change the visual, not the layout.
- Concrete beats abstract: real examples, real numbers, screenshots of the actual thing.
- Each slide ends with a reason to swipe (an unfinished list, a "but", a question answered on the next slide).
- The user's voice, from the style profile. Same words they'd say.

## Size and look

- 1080×1350 (4:5 portrait) takes up the most feed space; 1080×1080 also works. Same size for every slide.
- Keep important content inside a safe margin of about 80px.
- Use the user's brand colours and fonts if the style profile or About You has them; otherwise ask, or use a clean, high-contrast default (dark text on a light background, one accent colour).
- Handle or name small on every slide.

## The caption

- First line: restate the cover's promise or add the missing piece.
- 2-5 short lines of context, the user's take, or the one thing not on the slides.
- The CTA (save, share, comment keyword).
- 3-5 relevant hashtags at most, if the user uses them.

## Template (per carousel)

- **Working name**
- **Source:** the video or idea it came from
- **The one point**
- **Slides:** for each: number, heading, body text (exact words), visual
- **Caption**
- **CTA**
- **Assets needed:** screenshots, photos, generated images

## Producing the slides

- **HTML route** (needs a terminal and a browser or Playwright): write one self-contained 1080×1350 HTML file per slide with inline CSS, preview them together in one page, then screenshot each to PNG/JPG.
- **Image-generator route:** generate backgrounds or illustrations, then lay the text on in HTML or an editor. Don't trust generators to spell slide text.
- **Brief-only route:** when nothing can render, hand over the slide-by-slide brief for Canva or another editor.
