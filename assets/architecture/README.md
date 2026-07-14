# Architecture assets — source of truth

This directory contains the visual architecture used by the README, the
architecture deep dive, slides, and the three-minute demo video.

## Files

| File | Purpose |
| --- | --- |
| `architecture-diagram.mmd` | Canonical Mermaid source; edit this first |
| `architecture-diagram-light.svg` | Scalable light-theme render for README/docs |
| `architecture-diagram-dark.svg` | Scalable dark-theme render for README/docs |
| `architecture-diagram-light.png` | Light-theme raster for slides/video |
| `architecture-diagram-dark.png` | Dark-theme raster for slides/video |
| `architecture-diagram-*.config.json` | Mermaid theme and typography configuration |

The Mermaid source is the authority. Do not hand-edit an SVG or PNG to change
the architecture; update the MMD and regenerate all four renders together.

## Diagram design rules

- Keep the primary system pipeline horizontal and shallow: Engineer → API →
  fixture/live path → Scout → Synthesizer → Insight → Briefing.
- Use subgraphs for live-only behavior so the fixture path remains visually
  obvious.
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
npx --yes -p @mermaid-js/mermaid-cli mmdc -i architecture-diagram.mmd -o architecture-diagram-dark.svg -b "#0b1020" -c architecture-diagram-dark.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i architecture-diagram.mmd -o architecture-diagram-light.svg -b "#f5f7fb" -c architecture-diagram-light.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i architecture-diagram.mmd -o architecture-diagram-dark.png -b "#0b1020" -c architecture-diagram-dark.config.json --scale 3
npx --yes -p @mermaid-js/mermaid-cli mmdc -i architecture-diagram.mmd -o architecture-diagram-light.png -b "#f5f7fb" -c architecture-diagram-light.config.json --scale 3
```

No paid design, image-generation, or hosting service is required. The SVGs
scale without pixelation; the PNGs are convenience exports for decks and video.

## Where the assets are used

- [Project README](../../README.md) — hero architecture visual and clickable
  light/dark renders;
- [Architecture deep dive](../../docs/ARCHITECTURE.md) — visual-first system
  contract;
- [Demo script](../../submission/DEMO_SCRIPT.md) — architecture shot at
  approximately 2:00; and
- `submission/` evidence — future screenshots and recordings.
