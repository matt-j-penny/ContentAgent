# Interview

Use this to fill whatever the sources didn't. Run `manifest.py gaps <dir>` first and only ask about the fields it lists. Ask one or two questions at a time, one section per round. Put the suggested default first and mark it "(Recommended)". If the user says "you decide" or "default", use the default and tag the field `default`.

Every answer is tagged `asked:int-1` in `_sources`. Add the answered paths to `_locked` with `manifest.py lock`.

For visual questions, put an ASCII preview in each option's `preview` so the user can pick by looking.

---

## Round 0: Basics (always ask if empty)

1. **Name** to show on the manifest.
2. **Profiles.** Which formats do you edit for? (multi-select) YouTube long-form 16:9 · Shorts/Reels/TikTok 9:16 · LinkedIn/feed 4:5 or 1:1 · Podcast clips · Ads. Each pick becomes a `profiles.<id>` with `label`, `platform`, `aspect`, `description`.
3. **Formats.** Talking head · Tutorial / screen demo · Vlog · Faceless / voiceover · Podcast / interview.
4. **References.** Any creators whose edit you like? What should be taken from them, and what left out?
5. **One-line feel.** Offer three summaries written from what you know so far, plus Other.

## Round 1: Brand (skip if a website or brand kit gave you these)

- Colours: "Do you have brand colours?" If not, offer 3 palettes from the website/logo or the user's vibe, shown as hex in the preview.
- Fonts: heading and body. Offer 3 Google Font pairings that fit the vibe.
- Shapes: Sharp (0px) · Soft (12px) · Round (24px) · Pill.
- Texture: None · Subtle grain · Gradients · Glass.

## Round 2: Pacing

**Pace** → sets `pacing.cutsPerMin`, `maxStaticSec`, `silenceKeptMs`.

| Option | cutsPerMin long / short | maxStaticSec | silenceKeptMs |
|---|---|---|---|
| Relaxed | 6 / 14 | 8 | 300 |
| Balanced (default) | 10 / 20 | 5 | 150 |
| Fast | 16 / 28 | 3 | 80 |
| Relentless | 24 / 40 | 2 | 40 |

- **Fillers and breaths:** Remove all · Remove most, keep natural ones · Leave them.
- **Retakes:** Keep the last clean take (default) · Keep the best take · Ask me.
- **Jump cuts:** Hard jump cuts · Hide every other cut with a punch-in (default) · Smooth (morph/cross-fade).
- **Punch-ins:** None · Subtle 100/110% · Standard 100/115/130% (default) · Aggressive 100/130/160%.

## Round 3: Audio, music, SFX

- **J/L cuts:** Rarely · Into B-roll and section changes (default) · Constantly, documentary style. Lead/tail default 8 frames.
- **Loudness:** -14 LUFS (YouTube/social, default) · -16 LUFS (podcast).
- **Music:** None · Low bed under everything · Switch per section (default) · Only in intros/montages. Level under voice -24 dB default.
- **SFX density:** None · Sparse (key moments only) · Moderate (default) · Heavy.
- **SFX style:** Clean UI · Cinematic · Playful/cartoon · Retro.

## Round 4: Layouts (use previews)

**Where does the PIP sit?** Positions are in % of frame. Write the choice as a `layouts.library` region.

```
Corner (bottom-right)      Right third               Bottom centre (vertical)
+--------------------+     +--------------------+     +----------+
|                    |     |             +-----+|     | CONTENT  |
|      CONTENT       |     |   CONTENT   |     ||     |          |
|              +---+ |     |             | YOU ||     |  +----+  |
|              |YOU| |     |             |     ||     |  |YOU |  |
+--------------+---+-+     +-------------+-----++     +--+----+--+
x76 y68 w20 h28            x68 y8 w28 h84             x30 y62 w40 h30
```

- **PIP shape:** Rectangle · Rounded (default) · Circle · Background cut out (no frame).
- **PIP border/shadow:** None · Soft shadow (default) · Thin border · Brand-colour border.
- **Split screen:** Never · 50/50 for comparisons (default) · 1/3 face + 2/3 content.
- **Vertical demos:** Stacked content top, face bottom (default) · Full-screen content + small PIP · Green-screen face over content.

```
Stacked 50/50          Stacked 60/40          Green screen
+----------+           +----------+           +----------+
| CONTENT  |           | CONTENT  |           | CONTENT  |
|          |           |          |           |          |
+----------+           |          |           |    __    |
|   YOU    |           +----------+           |   (YOU)  |
|          |           |   YOU    |           |   /  \   |
+----------+           +----------+           +----------+
```

- **What triggers a layout change?** (multi-select) Showing something on screen · A list · A comparison · New section · Every N seconds for variety.
- **How do layouts change?** Hard cut · Animated: face shrinks into the PIP (default, 400 ms) · Slide/push · Whip.
- **Min/max time in one layout:** default 3 s / 20 s (long-form), 2 s / 8 s (short).

## Round 5: Video structure

- **Segment types** the videos use (multi-select): Intro · Explain (talking) · Demo (screen) · Story · List · Comparison · Interview · Outro/CTA.
- For each chosen segment: which layout from Round 4, and roughly how much B-roll (none/some/most).
- **Typical order:** offer two or three sequences built from their segments.
- **Section dividers:** None · Chapter card (default) · Text pop + whoosh · Layout change only.
- **Intro/outro:** Straight in, no sting (default) · Short branded sting · End card N seconds.

## Round 6: Captions (per profile)

```
Word by word            Phrase (2-4 words)       Full line subtitle

    THIS IS             THIS IS HOW              This is how you edit for
                                                  the algorithm
   [active word         [active word             (no highlight)
    in accent]           in accent]
```

- **Style:** Word by word · Phrase with active word highlight (default for short) · Full subtitles · Off (default for long-form).
- **Position:** Lower third · Centre · Above the PIP. Shorts must stay inside the safe zones.
- **Case:** UPPERCASE · Sentence case.
- **Emphasis:** Accent colour on keywords (default) · Scale up · Emoji · None.
- **Behind the subject:** Yes · No (default).

## Round 7: Motion graphics

- **Overall style:** Minimal & clean (default) · Bold & kinetic · Playful · Techy/UI · Cinematic.
- **Motion feel** → `motionGraphics.motion`:

| Option | easing | inMs | outMs | overshoot | staggerMs |
|---|---|---|---|---|---|
| Snappy | cubic-bezier(.2,.9,.1,1) | 250 | 180 | none | 40 |
| Smooth (default) | cubic-bezier(.2,.8,.2,1) | 400 | 250 | slight | 70 |
| Bouncy | cubic-bezier(.34,1.56,.64,1) | 450 | 250 | strong | 80 |
| Cinematic | cubic-bezier(.65,0,.35,1) | 700 | 500 | none | 120 |

- **How often:** Only for key moments (~1/min) · Regular (~4/min, default) · Constant (something new every few seconds).
- **What triggers one?** (multi-select) Numbers/stats · Names/titles · Lists · Tools/products · Key terms · Quotes · Processes/steps.
- **Where do they go?** Beside the speaker on the open side (default) · Full screen · Over the content area · Behind the speaker.
- **How should they be built?** HyperFrames (HTML) · Remotion · Native NLE titles · Whatever fits.
- **Anything you never want?** Free text.

## Round 8: Transitions, effects, colour

- **Transitions:** Hard cuts only · Hard cuts + occasional whip/zoom between sections (default) · Lots of stylised transitions.
- **Effects allowed** (multi-select): Speed ramps · Freeze frames · Shake · Glitch · Blur/focus · Light leaks.
- **Look:** Clean & neutral · Warm (default) · Cool/techy · Cinematic contrast · High-saturation pop.

## Round 9: How the AI works

- **Decide alone vs ask:** Do everything, flag doubts with markers (default) · Ask before removing content · Ask about everything creative.
- **New templates:** Make them freely and add to the bank · Ask first (default).
