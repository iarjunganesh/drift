# Devpost submission handoff

## Required before submitting

- [ ] Confirm **Developer Tools** as the single selected category.
- [ ] Create a public repository with a license, or share the private repository
      with `testing@devpost.com` and `build-week-event@openai.com`.
- [x] Record all project initiative Session IDs in the README and initiative
      register:
      - Foundation: `019f61e7-1ea1-7742-9acc-99d62f39b888`
      - Publication/readiness: `019f61fc-c32e-7d92-9d2e-0bd9083d08e7`
      - Hosted deployment/README follow-up: `019f6253-ddfc-7272-8077-e34dfb3aee84`
      - Primary core-functionality session: `019f62b9-10b7-7d82-a463-e6eb1192141c`
      - Day 1/Day 2 implementation follow-up: `019f62e8-6715-70e2-a92a-fe28254f7b71`
      - Day 3/Day 4 Insight structured output: `019f6336-3690-7022-a8ef-c8c0947e240f`
      - Bounded capture/provenance and documentation cleanup:
        `019f66b4-78b8-7943-a41d-91e836d28f00`
      - Grounding guardrails and capture readiness:
        `019f6773-0e96-7363-9657-0e0531c3d594`
- [x] Use `019f62b9-10b7-7d82-a463-e6eb1192141c` as the primary `/feedback`
      Session ID if the Devpost form accepts only one.
- [x] Implement local claim-level evidence, separate verification, and
      review-first publication with calibration tests and a manual-run notebook.
- [ ] Run and human-review real, saved GPT-5.6 output examples through
      `notebooks/drift_manual_run.ipynb` against a reachable database, then cite
      their primary release URLs and verify hosted provider-backed `/search` and
      `/chat` against reviewed evidence. Railway PostgreSQL schema `0003` and
      hosted `v0.6.0` health/empty briefing/docs/banner/CORS were verified on
      2026-07-16.
- [x] Provide a judge path: hosted app is available at
      `https://dr1ftless.vercel.app` with a verified `v0.6.0` Railway API;
      reviewed live evidence remains an explicit operator gate.
- [ ] Upload a public YouTube video under three minutes with English narration.
- [ ] Replace the placeholder with the final video URL:
      `https://youtu.be/TBD` (see [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)).
- [ ] In the video, demonstrate the product working and explain both Codex and
      GPT-5.6’s actual role.
- [ ] Add the video URL, code URL, category, description, and Session ID in Devpost.

See [`docs/INITIATIVES.md`](../docs/INITIATIVES.md) for initiative scope and
the distinction between the primary core-functionality session and the earlier
foundation, publication, and hosted-demo sessions.

## Do not claim until verified

- A live feed or GPT-5.6 integration that has not completed a recorded run.
- A deployment, test account, or frontend that judges cannot access.
- Specific performance, accuracy, or cost results without captured evidence.
- A verifier pass as proof, a draft as public evidence, or a potential
  operator-risk label as a compatibility verdict.
