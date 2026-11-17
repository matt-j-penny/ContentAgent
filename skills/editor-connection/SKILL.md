---
name: editor-connection
description: Discover and use available video-editor integrations for a content project. Use when the user wants to edit in an installed or connected video editor, or asks which editor connection is available.
---

# Video editor connections

Follow [references/before-you-start.md](references/before-you-start.md) to choose Content OS or standalone mode. Determine the editor and project the user means. Read the relevant video-manifest profile when available; use it to guide supported editing decisions, never as evidence that an editor is connected.

## Discover the actual connection

- **CapCut:** `capcut-editor`, when installed on macOS, can validate a keep-list and create a new single-source rough-cut draft. That integration does not yet edit existing drafts or export.
- **Matt's Recordly:** `screen-recording` can use its optional installed CLI after checking the live app's capabilities. Do not assume other Recordly builds have the same CLI.
- **Premiere Pro, DaVinci Resolve, Palmier Pro, Final Cut Pro or another editor:** inspect the current host's available connector, MCP tools or documented CLI. Use only operations that are actually exposed and work for the current app and project. A tool catalog, app installation, project file, or the name of an MCP server alone is not proof of a live connection. Do not assume equivalent operations exist across editors.

When multiple projects or running instances match, identify the intended one before changing it. If no compatible integration exists, explain what is missing and offer a supported file-based output or an edit plan. Do not silently switch editors or claim that all major editors are connected.

## Work in the chosen editor

Read the existing project state before changing it. Preserve source media and the user's existing edits; follow the editor's documented save and undo behavior. For rough cuts, `rough-cut` prepares a validated keep-list. For B-roll, music and sound effects, use `b-roll` or `audio-design` for planning and only place tracks through an actual connected editor when it supports them. Confirm changes and export only when the user requests the relevant action, then inspect the resulting timeline or output. If an editor tool fails, report what succeeded and what remains instead of assuming the timeline changed.
