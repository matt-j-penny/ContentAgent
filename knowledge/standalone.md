# Standalone mode

Use this only after Content OS is unavailable and the user has declined the offer to connect it. When connected, `content-os.md` and the existing Content OS workflows remain authoritative. Do not copy personal Content OS data automatically. If the user later chooses to migrate, ask what to copy and never overwrite either source without checking.

## Local workspace

Use `contentagent/` in the user's current project, or a location they choose. Create folders only when needed. These are durable user files, not disposable working data. If files are unavailable, keep the same information in the conversation and explain it won't persist. Avoid inventing facts, analytics, source links or proof. Ask before replacing existing user material.

- `profile/about.md`: business, offer, audience, niche, platforms, cadence, competitors, proof and boundaries.
- `profile/style.md`: voice, tone, wording, openings, endings and writing preferences, based on user samples and feedback.
- `strategy.md`: current strategy and cadence.
- `ideas/<slug>/idea.md`: working title, platform/format, premise, pillar, status, publish date, source links and next actions. Use a unique descriptive slug; preserve existing files. Store scripts, research, outlines, storyboard, packaging, analysis and assets in that idea folder with descriptive filenames.
- `inspiration.md`: user-supplied titles, videos, thumbnail URLs and notes. Never assume the bundled examples express the user's taste.

List idea files to inspect a local plan. Update statuses or priority only as requested or as the skill would normally do; show proposed changes before reordering, archiving, replacing user text, or removing anything. In the absence of an idea, work directly from the user's material. When asked to save, show the destination and write or append without destroying existing content. If no file tools exist, return a clearly labeled copyable result.

## Reference data and data gaps

The shared Vault snapshot is `references/vault-titles.json` and `references/vault-hooks.json` (arrays); use titles and hooks as patterns, not text to copy. `references/titles.md`, `references/thumbnails.md` and `references/hooks.md` contain existing creative guidance where available. For idea tips, use those references and the skill's own instructions, or the user's guidelines. A bundled shared thumbnail URL library is not available. Use user-supplied examples or public research when accessible; do not invent URLs or treat lack of examples as a blocker.

Public video statistics, vidIQ, web search and user-provided exports or screenshots can supplement the local profile. Analytics such as impressions, CTR, retention and link clicks require actual accessible data. Explicitly identify missing data; never fabricate it. Image generation and video tools remain optional or required exactly as the individual skill describes.

## Map Content OS operations to local work

- Profile reads/writes → `profile/about.md` and `profile/style.md`.
- Ideas, boards, moves and notes → idea files and `strategy.md`; keep status and ordering legible.
- Packaging → a `packaging.md` in the idea folder, with title, thumbnail brief and local image path or URL; do not require a public URL for a local image.
- Inspiration, Vault and tips → local inspiration, bundled Vault snapshot and reference guidance.
- Storyboard sections/segments → `storyboard.md`, retaining sequence, talking points and visual direction.
- YouTube/Instagram analytics and tracked links → available connected sources or data supplied by the user; omit unsupported conclusions.

Apply the creative steps of the active skill, substituting these local inputs and outputs for Content OS calls. Never call a Content OS tool in standalone mode. Keep the connected-mode instructions unchanged when Content OS is available.
