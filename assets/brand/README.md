# DRIFT brand assets

`drift-banner-dark.svg` and `drift-banner-light.svg` are the canonical
theme-aware DRIFT brand banners. They share one visual language with the
architecture presentation diagram (`assets/architecture/`): the same trust-zone palette,
rounded node styling, gold human-review gate, dot-grid field, and Inter
typography. The right-side **evidence path** card distills the architecture
story to its core — an untrusted primary release crosses a human gate to become
a cited, bounded briefing — over a subtle GPU compute-lattice backdrop (traces,
vias, and a PCB edge-connector) that ties the brand to the infrastructure it
serves.

## DRIFT palette (locked)

One palette drives the banner, the presentation diagram, and the Mermaid pipeline
so they read as one system. It is anchored on what DRIFT does — turning raw
release signal into reviewed, trusted intelligence — not on any vendor's colours.

| Role | Dark | Light | Where |
| --- | --- | --- | --- |
| **Signature gradient** (teal → indigo) | `#2dd4bf` → `#818cf8` | `#0d9488` → `#4f46e5` | wordmark, eyebrows, accent rules |
| Untrusted | `#f43f5e` | `#e11d48` | zone / source dot |
| Quarantine | `#f59e0b` | `#d97706` | zone / model accent |
| Trusted | `#10b981` | `#059669` | zone / API / "reviewed" |
| Human gate | `#fbbf24` | `#b45309` | the review gate only |

The signature gradient's endpoints are the diagram's own **source-teal →
agent-indigo** node hues, so the brand mark is literally sampled from the
pipeline it describes. The semantic node colours (source, agent, store, model,
API, human, fixture) stay distinct in the diagrams because they carry meaning;
the gradient is the brand identity layered on top. Keep the values in
`build_banner.py` and `assets/architecture/build_arch.py` in sync.

## Files

| File | Purpose |
| --- | --- |
| `build_banner.py` | Source of truth; emits both banner SVGs |
| `build_banner_raster.mjs` | Rasterizes the banners to PNG via `sharp` |
| `drift-banner-dark.svg` / `-light.svg` | Canonical API-served banners |
| `drift-banner-dark.png` / `-light.png` | Convenience rasters for decks/video |

Edit `build_banner.py` (never the SVG/PNG) and regenerate both themes together:

```powershell
python build_banner.py
node build_banner_raster.mjs   # optional PNGs; needs ../../frontend deps
```

The SVG **filenames are fixed**: `backend/main.py` serves them at
`/brand/{theme}.svg` and Docker bakes this directory into the API image — do not
rename the SVG outputs. Use the dark/light pair in documentation through a
`<picture>` element. The Next.js frontend loads the canonical files through the
FastAPI routes; do not copy, derive, or commit banner SVGs under
`frontend/public/`. The FastAPI service uses the same routes for its Swagger
documentation.
