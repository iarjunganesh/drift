# Devpost submission handoff

## Required before submitting

- [ ] Confirm **Developer Tools** as the single selected category.
- [x] Create a public repository with a license, or share the private repository
      with `testing@devpost.com` and `build-week-event@openai.com`. Verified
      via `gh repo view`: `isPrivate: false`, MIT license.
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
      - Submission audit and frontend evidence presentation:
        `019f6a46-e3eb-7de2-81b1-91515ae80043`
      - Reviewed-evidence hardening and `v0.8.0` hosted verification:
        `019f6a78-6fa2-7121-9059-85ac8ceb9904`
      - Freeze-plan audit and documentation synchronization:
        `019f7190-912d-70e3-be6d-fcc81bf8e203`
      - v0.9.0 evidence cleanup and session synchronization:
        `019f7213-be19-7e50-92ac-a48bd5ecaacb`
      - v0.9.1 evidence and screenshot synchronization:
        `019f7278-ee77-7f02-bafd-6eba8bf046d2`
      - v0.10.0 MCP thin-client implementation:
        `019f7607-aa5a-79b2-8101-4cd634495fbe`
- [x] Implement the `v0.10.0` thin-client MCP integration (`integrations/mcp/`,
      ADR-011): three stdio tools (`drift_briefing`, `drift_search`,
      `ask_drift`) over the existing public API, no credentials, nothing changed
      under `backend/`, verified end-to-end against a fixture-mode API at $0 with
      40 mocked-HTTP tests at 100% `integrations/` coverage. The VS Code MCP
      client evidence against the deployed `v0.10.0` API is captured in the
      README gallery; the bounded scrubbed MCP response archive remains the
      pending operator gate.
- [x] Record the v0.9.1 Terra grounded-chat evidence pass: eight bounded
      questions over the reviewed store, seven grounded answers, one explicit
      PyTorch decline, and the scrubbed archive plus SHA-256 manifest at
      `assets/evidence/2026-07-18-all-sources-terra.json`.
- [x] Use `019f62b9-10b7-7d82-a463-e6eb1192141c` as the primary `/feedback`
      Session ID if the Devpost form accepts only one.
- [x] Implement local claim-level evidence, separate verification, and
      review-first publication with calibration tests and a manual-run notebook.
- [x] Ran and human-reviewed four saved GPT-5.6 output examples through
      `notebooks/drift_manual_run.ipynb` against Railway PostgreSQL — Transformers
      v5.14.1, vLLM v0.25.1, NCCL v2.30.7-1, TensorRT 11.1 — cited their primary
      release URLs, and verified hosted provider-backed `/briefing`, `/search`,
      and `/chat` against the reviewed evidence on 2026-07-16 (`/chat` grounded
      via `gpt-5.6-terra` with source citations). Evidence + SHA-256 manifest
      archived to `assets/evidence/2026-07-16-all-sources-luna.json`.
- [x] Provide a judge path: hosted app is available at
      `https://dr1ftless.vercel.app` with a verified `v0.10.0` Railway API.
      On 2026-07-18, Railway `/health` and `/` reported `0.10.0`, `/docs`
      returned `200`, `/briefing?top_n=10` returned the five reviewed Tier.FINAL
      Insights (10, 11, 13, 15, 16) with no review notes, and Vercel CORS passed
      (`GET, POST`); paid `/search` and `/chat` were not re-invoked. The prior
      `v0.9.1` (same day) and `v0.8.0` (2026-07-17) verifications are retained
      as historical records. Its
      public `/briefing` and OpenAPI contract omit private human review notes.
- [x] Upload a public YouTube video under three minutes with English narration.
- [x] Replace the placeholder with the final video URL:
      `https://youtu.be/6sbIz0ZR8Hw` (see [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)).
- [x] In the video, demonstrate the product working and explain both Codex and
      GPT-5.6’s actual role. Verified frame-by-frame: Ask DRIFT grounded
      answer, the Kubernetes decline, and MCP tool call all show the product
      working; `vo_08-pipeline` narrates both Codex ("Codex shaped the
      stages, safeguards, and tests") and GPT-5.6 ("GPT-5.6 powers
      synthesis, verification, and grounded chat") by name.
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
