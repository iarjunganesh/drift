# DRIFT brand assets

`drift-banner-dark.svg` and `drift-banner-light.svg` are the canonical
theme-aware DRIFT hero banners. They deliberately tell the same source-neutral
story: a primary release travels through a GPU compute lattice into cited
evidence, human review, and a bounded engineering check.

Use the dark/light pair in documentation through a `<picture>` element. The
Next.js frontend derives its deploy-time dark asset from this directory; do not
maintain a second committed copy under `frontend/public/`. The FastAPI service
serves the same canonical files as `/brand/dark.svg` and `/brand/light.svg` for
its Swagger documentation. Docker copies this directory into the API image.
