# DRIFT brand assets

`drift-banner-dark.svg` and `drift-banner-light.svg` are the canonical
theme-aware DRIFT hero banners. They deliberately tell the same source-neutral
story: a primary release travels through a GPU compute lattice into cited
evidence, human review, and a bounded engineering check.

Use the dark/light pair in documentation through a `<picture>` element. The
Next.js frontend loads the canonical files through FastAPI's `/brand/dark.svg`
and `/brand/light.svg` routes; do not copy, derive, or commit banner SVGs under
`frontend/public/`. The FastAPI service uses the same routes for its Swagger
documentation. Docker copies this directory into the API image.
