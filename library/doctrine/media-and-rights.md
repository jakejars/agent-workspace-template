---
id: library-media-rights
type: doctrine
status: draft
description: The rights contract for collected work. Use when adding an image, clip, font. Not for how taste is described (see claims.md).
owner: human
updated: 2026-08-24
review_after: 2027-08-24
related:
  - type: canonical
    ref: library/INDEX.md
  - type: contrast_with
    ref: library/doctrine/claims.md
---

# Media and rights

Tracked sett content is text-only. Binary media stays external and enters by
URL through a documented seam; each linked asset has a rights row.

## Link-only is the default

Default to NOTE + `source` URL + `(remote)` rights row. If preservation is
needed, put owned or openly licensed bytes in an external store behind a seam.

## External media layout

An external specimen store may use this closed vocabulary:

| Folder | Holds | Typical |
|---|---|---|
| `images/` | raster and vector stills | png, jpg, webp, gif, svg |
| `video/` | clips, screen captures | mp4, webm, mov |
| `audio/` | sound, music, voice | mp3, wav, flac, ogg |
| `models-3d/` | meshes, scenes | glb, gltf, obj, fbx |
| `fonts/` | typeface files | ttf, otf, woff2 |
| `documents/` | PDFs and anything uncategorised | pdf, md, txt |

Unknown types use `documents/`. Names are descriptive kebab-case; variant suffixes
may be numeric, bare numeric names may not.

## The rights contract

Every specimen `NOTE.md` carries a **Contents and rights** table, one
row per file:

```markdown
## Contents and rights

| Asset | Creator | License | Source |
| --- | --- | --- | --- |
| (remote) | <creator> | CC-BY-4.0 | <url> |
| seam:library-media/images/signage-grid.png | <studio / designer> | CC-BY-4.0 | <url> |
```

- Prefer SPDX identifiers; use `All-Rights-Reserved (study quotation)` for
  private-study excerpts.
- No row, no keep.
- Unknown license means do not retain; never infer from platform terms.

## Hygiene

- Keep binary and heavy working formats outside the sett.
- Personal data requires a written reason in the NOTE.

## What an agent may do

Agents may cite, describe, link, and borrow within NOTE bounds. Never strip
attribution, guess rights, or attach specimen media to outbound material; only
sourced observations travel.
