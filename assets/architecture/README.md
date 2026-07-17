# Architecture assets — source of truth

This directory contains the visual architecture used by the README, the
architecture deep dive, slides, and the three-minute demo video.

## Files

### Detailed pipeline diagram (Mermaid — system of record)

| File | Purpose |
| --- | --- |
| `arch-pipeline.mmd` | Canonical Mermaid source; edit this first |
| `arch-pipeline-light.svg` | Scalable light-theme render for README/docs |
| `arch-pipeline-dark.svg` | Scalable dark-theme render for README/docs |
| `arch-pipeline-light.png` | Light-theme raster for slides/video |
| `arch-pipeline-dark.png` | Dark-theme raster for slides/video |
| `arch-pipeline-*.config.json` | Mermaid theme and typography configuration |

The Mermaid source is the authority for the pipeline. Do not hand-edit an SVG
or PNG to change the architecture; update the MMD and regenerate all four
renders together.

### Presentation diagram (hand-authored — first-look visual)

| File | Purpose |
| --- | --- |
| `build_arch.py` | Source of truth for the presentation diagram; emits both SVGs |
| `build_arch_raster.mjs` | Rasterizes the presentation SVGs to high-DPI PNG via `sharp` |
| `arch-light.svg` | Light-theme presentation diagram for README top / slides / video |
| `arch-dark.svg` | Dark-theme presentation diagram for README top / slides / video |
| `arch-light.png` | Light-theme presentation raster |
| `arch-dark.png` | Dark-theme presentation raster |

The presentation diagram (`arch-*`) dramatizes the same six typed stages as a
first-look **trust boundary** story: untrusted feeds → quarantined machine
drafts → the human review gate → trusted, published briefing. It is a companion,
not a replacement: edit `build_arch.py` (never the SVG/PNG) and regenerate both
themes together. It shares its visual language — trust-zone colours, node
styling, and the gold review gate — with the `assets/brand/` banner.

The presentation diagram keeps the "engineer also reviews" back-edge; the
Mermaid diagram deliberately omits it. That single edge (`Engineer → review
gate`) closes a cycle through `gate → store → Briefing → API → Engineer`, which
breaks Mermaid's left-to-right ranking and scrambles the zone order. The
hand-laid presentation diagram can show it safely; the auto-laid Mermaid stays
acyclic so the three trust zones read cleanly left to right.

## Diagram design rules

- Keep the primary system pipeline horizontal and shallow: Engineer → API →
  fixture/live path → Scout → Synthesizer → claim extraction → verifier →
  review gate → Briefing.
- Group the live stages into the three trust-zone subgraphs — untrusted input,
  quarantine, trusted/published — so the human review gate reads as the only
  bridge and the fixture path stays visually obvious.
- Keep the Mermaid graph acyclic: no edge may point back into an earlier stage
  (e.g. `Engineer → review gate`), because a cycle breaks left-to-right ranking
  and scrambles the zones. Show loop-closing edges only in the hand-laid
  presentation diagram.
- Keep model and persistence dependencies as dashed side paths rather than
  creating a second competing pipeline.
- Use `<br/>` labels for readable node wrapping; avoid paragraphs inside nodes.
- If a supporting flow is more than five nodes deep, use `flowchart TB` in the
  document rather than widening the main asset.
- Keep the colors semantically stable: source, agent, data, model, API, user,
  and note.

## Regenerate the renders

From this directory, use the free and open-source Mermaid CLI:

```powershell
npx --yes -p @mermaid-js/mermaid-cli mmdc -i arch-pipeline.mmd -o arch-pipeline-dark.svg -b "#0b1020" -c arch-pipeline-dark.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i arch-pipeline.mmd -o arch-pipeline-light.svg -b "#f5f7fb" -c arch-pipeline-light.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i arch-pipeline.mmd -o arch-pipeline-dark.png -b "#0b1020" -c arch-pipeline-dark.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i arch-pipeline.mmd -o arch-pipeline-light.png -b "#f5f7fb" -c arch-pipeline-light.config.json --scale 3
```

Then regenerate the presentation diagram (both themes, then the PNG rasters). The rasterizer
reuses the `sharp` install under `frontend/`, so run `npm --prefix ../../frontend ci`
first if `node_modules` is absent:

```powershell
python build_arch.py
node build_arch_raster.mjs
```

No paid design, image-generation, or hosting service is required. The SVGs
scale without pixelation; the PNGs are convenience exports for decks and video.

## Where the assets are used

- [Project README](../../README.md) — presentation architecture visual and clickable
  light/dark renders;
- [Architecture deep dive](../../docs/ARCHITECTURE.md) — visual-first system
  contract;
- [Demo script](../../submission/DEMO_SCRIPT.md) — architecture shot at
  approximately 2:00; and
- `submission/` evidence — future screenshots and recordings.
