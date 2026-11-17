# Analysing sources

Every source gets an id (`nle-1`, `vid-1`, `ref-1`, `web-1`, `int-1`), an entry in `meta.sources`, and a folder at `<dir>/sources/<id>/` for its raw output. Every value you write gets `_sources["<path>"] = "<measured|observed|asked|default>:<id>"`. For profile values use `profiles.<profile>.<path>` as the key.

- **measured**: a number read from project data or ffmpeg/Deepgram
- **observed**: seen in frames or the Gemini breakdown
- **asked**: the user said so
- **default**: nobody said, you chose

## Which profile does a source feed?

Use its aspect and length: 9:16 → short-form profile; 16:9 and longer than ~3 min → long-form profile; 1:1 / 4:5 → feed profile. A value shared by every profile goes in `base`. A value that differs goes in that profile only. With one source, put everything in `base` and create its profile with just the label/platform/aspect.

---

## A. NLE projects (most accurate)

| Tool | How to read it |
|---|---|
| CapCut | `nle.py "<draft folder>" --out sources/nle-N`. Drafts live in `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/` (Mac) or `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\` (Windows). List the folder and let the user pick. |
| Premiere Pro | Ask the user to run File > Export > Final Cut Pro XML, then `nle.py <file.xml>`. `.prproj` is not read directly. |
| DaVinci Resolve | Preferred: the davinci-resolve MCP, live. Use `timeline` to list tracks and items, `timeline_item` to read each item's start/end and properties (ZoomX, Pan, Tilt, CropLeft...), `timeline_item_fusion` for titles, and `timeline_markers`. Build the same numbers `nle.py` reports. Fallback: File > Export > Timeline > FCPXML, then `nle.py`. |
| Final Cut Pro | File > Export XML → `nle.py <file.fcpxml>` |
| Palmier Pro | `nle.py "<name>.palmier" --out sources/nle-N --dialogue`. Projects live in `~/Documents/Palmier Pro/`. Read directly: exact layout boxes per webcam/screen state (`palmier.framing`), move durations, media-bin folders (Broll/SFX/Music/Graphics), caption styles and animation presets, colour effect values, nested sequences. `--dialogue` rebuilds the kept speech so `measure.py dialogue.mp3` can measure pauses, WPM and fillers. Pick finished edits: rough cuts show no overlays/SFX. |
| Anything else | If it exports FCPXML, FCP7 XML or EDL, use that. Otherwise render the video and treat it as a Mode B source (you lose exact numbers, say so). |

Also grab a few frames from the rendered video if one exists, or from the graphics files themselves (flatten alpha onto grey: transparent overlays turn black otherwise), (`measure.py --no-transcribe`) for the evidence section and to classify overlays.

**nle.json → manifest**

| nle.json | manifest |
|---|---|
| `mainTrack.cutsPerMin` | `pacing.cutsPerMin` |
| `visualChanges.medianGapSec`, `maxGapSec` | `pacing.maxStaticSec` (round up the typical max) |
| `mainTrack.scales` (e.g. 100%, 115%, 130%) | `pacing.punchIn.levels` |
| `keyframes.KFTypeScale*` | animated zooms → `camera.postMoves` |
| `jlCuts` | `audio.jCut` / `audio.lCut` (`leadFrames` = `medianOffsetFrames`) |
| `audio.dialogVolumeDb`, `musicVolumeDb` | `music.underVoiceDb` = music minus dialog |
| `audio.sfxPerMin`, `sfxNames` | `sfx.density`, `sfx.mapping` (match SFX times to what's on screen) |
| `overlays.pipPositions` | `layouts.library` regions: `w = h = scale×100` (same-aspect source), `x = cx − w/2`, `y = cy − h/2`. Check against a frame. |
| `palmier.framing` (Palmier) | exact `layouts.library` regions per state: `x{l}-{r} y{t}-{b}` are % of frame. Count = how often that state is used |
| `tracks.syncedSources` | a second source cut in lockstep (screen recording): `camera.screenRecording` |
| `overlays.fullFrame*` | B-roll or full-screen graphics, decide from `fullFrameNames` and frames → `broll.density` or `motionGraphics.frequency` |
| `captions` | `captions.*` (style from `wordsPerItem`, colours, fonts, `verticalPositions`) |
| `text` | `motionGraphics.frequency`, `brand.typography`, `brand.colors` |
| `transitions` | `transitions.approved`, `defaultCutPct` |
| `effects` | `effects.*`, `color.*` (CapCut adjustment effects like contrast/saturation) |

## B. The creator's own videos

1. `measure.py <file-or-url> --out sources/vid-N` gives cuts, shot lengths, loudness, silence, WPM, fillers, word gaps and frames. Uses Deepgram nova-2.
2. Run the `youtube-editing-style` skill on the same source for the visual read: layouts, B-roll rules, captions, graphics, transitions, SFX, colour. Pass `--focus "layouts and PIP positions, layout switching, caption style, motion graphic style and placement, SFX mapping, J/L cuts"`. For long videos, analyse the first 4 min plus a middle section, and say which parts were watched.
3. Look at the frames yourself (Read the jpgs) to confirm layout positions and graphic placement. Add 6–12 telling frames to `evidence.frames` with a note each.
4. Template bank: run `mograph-snatcher` on URL sources (or pick graphics from frames) and add each recreated template to `templates/` + `templates[]` with `origin: "vid-N"`. Ask before doing this if there are more than ~8 graphics, since it's slow.

**stats.json → manifest**

| stats.json | manifest |
|---|---|
| `cuts.perMin` | `pacing.cutsPerMin` (scene detection undercounts same-framing jump cuts, so cross-check with the Gemini read) |
| `cuts.shotSec.p90` | `pacing.maxStaticSec` |
| `speech.gapMs.p90` | `pacing.silenceKeptMs` |
| `speech.fillersPerMin` | ≈0 → fillers removed |
| `speech.longPauses` | where they let moments breathe |
| `audio.integratedLufs`, `truePeakDb` | `audio.dialogue` |
| `aspect`, `duration` | which profile |

## C. Someone else's videos (reference)

Same pipeline as B, with `type: "reference"`. Then:
- **Never** take their brand: colours, fonts, logo, texture.
- After analysis, show the user a short list of what you found (pace, PIP style, captions, motion style, SFX, transitions...) as a multi-select: "Which of these do you want to adopt?" Only the picked items go into the manifest, tagged `observed:ref-N`. Record the picks in `meta.sources[].adopted`.
- Graphics from references go in the bank re-styled to the user's brand tokens, with `origin: "ref-N"`.

## D. From scratch (website, assets, interview)

1. **Website:** open it (built-in browser or a scrape tool) and pull colours (backgrounds, buttons, links, headings), font families and weights, corner radius, shadows, and the logo. This is the same method as the `create-design-md` skill, Step 1. If the user already has a DESIGN.md or `content-os/brand-kit.md`, read that instead. Tag `measured:web-1`.
2. **Other assets** (logo, brand kit, thumbnails, a channel URL): pull colours/fonts from them. A channel URL can also become a Mode B source.
3. Run the interview (`references/interview.md`) for everything still empty.
4. The starter templates copied by `init` already use the brand tokens once `render` writes `_brand.css`. Check they look right in the page.

## Conflicts

Priority, high to low: the user's answers > NLE projects > own videos > adopted reference items > defaults. Never change a path listed in `_locked`. When two sources disagree by a lot (e.g. 8 vs 20 cuts/min), it's usually two profiles, so check aspect/length before averaging. If it really is a conflict, ask.
