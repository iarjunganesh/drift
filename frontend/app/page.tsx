"use client";

import { useEffect, useState } from "react";

type Insight = {
  id: number | null;
  title: string;
  summary: string;
  why_it_matters: string;
  what_to_check: string;
  severity: "cosmetic" | "minor" | "breaking" | "security";
  confidence: number;
  source_citations: string[];
  model_used: string;
  claims?: {
    text: string;
    kind: "direct_fact" | "inference" | "recommended_check";
    evidence: { excerpt: string; source_url: string; start_char: number; end_char: number }[];
  }[];
  upstream_release_type?: "major" | "minor" | "patch" | "pre_release" | "unknown";
  operator_risks?: string[];
  applicability_conditions?: string[];
  publication_status?: "draft" | "reviewed";
  verification_status?: "passed" | "legacy_unverified";
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [mode, setMode] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadBriefing() {
      try {
        const [healthResponse, briefingResponse] = await Promise.all([
          fetch(`${API_URL}/health`),
          fetch(`${API_URL}/briefing?top_n=3`),
        ]);
        if (!healthResponse.ok || !briefingResponse.ok) {
          throw new Error("The DRIFT API returned an unsuccessful response.");
        }

        const [health, briefing] = await Promise.all([
          healthResponse.json() as Promise<{ mode?: string }>,
          briefingResponse.json() as Promise<{ insight: Insight }[]>,
        ]);
        if (!isMounted) return;

        setMode(health.mode || "fixture");
        setInsights(briefing.map((item) => item.insight));
        setError("");
      } catch {
        if (!isMounted) return;

        setInsights([]);
        setError("The DRIFT API is not reachable. Start the backend and try again.");
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    void loadBriefing();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="shell">
      <nav className="nav">
        <a className="brand-lockup" href="/" aria-label="DRIFT home">
          <span className="wordmark">DRIFT</span>
          <span className="product-line">Release intelligence</span>
        </a>
        <div className="nav-links">
          <a href="#briefing">Briefing</a>
          <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">API docs ↗</a>
        </div>
      </nav>

      <section className="hero">
        <div>
          <div className="eyebrow">Release intelligence for AI infrastructure</div>
          <h1>Know what changed before it becomes your incident.</h1>
          <p>
            DRIFT turns framework, runtime, compiler, and distributed-training releases
            into a cited answer: what changed, why it matters, and what to check next.
          </p>
          <div className="actions">
            <a className="button primary" href="#briefing">View today&apos;s briefing</a>
            <a className="button" href={`${API_URL}/docs`} target="_blank" rel="noreferrer">Explore the API</a>
          </div>
          <div className="proof-line" aria-label="DRIFT evidence process">
            <span>Primary releases</span><i>→</i><span>Cited claims</span><i>→</i><span>Human-reviewed checks</span>
          </div>
        </div>
        <aside className="signal">
          <picture className="signal-brand">
            <source media="(prefers-color-scheme: dark)" srcSet={`${API_URL}/brand/dark.svg`} />
            <source media="(prefers-color-scheme: light)" srcSet={`${API_URL}/brand/light.svg`} />
            <img
              src={`${API_URL}/brand/light.svg`}
              alt="DRIFT evidence path: a primary release flows through a GPU compute lattice into cited evidence, human review, and a bounded engineering check"
            />
          </picture>
          <div className="signal-label">Current operating mode</div>
          <h2>
            {mode === "fixture"
              ? "Deterministic fixture briefing"
              : mode === "live"
                ? "Human-reviewed, claim-grounded live evidence"
                : "Checking published evidence"}
          </h2>
          <p>{error || "Every insight keeps its source span, claim type, confidence, and bounded follow-up action visible."}</p>
          <div className="rail">
            <div><span>Evidence</span><strong>Primary source</strong></div>
            <div><span>Publication</span><strong>Human review gate</strong></div>
            <div><span>Confidence</span><strong>Always visible</strong></div>
            <div><span>Action</span><strong>Bounded check</strong></div>
          </div>
        </aside>
      </section>

      <section className="section" id="briefing">
        <div className="eyebrow">Top things that matter</div>
        <h2>Today&apos;s briefing</h2>
        <p>
          Fixture examples are clearly labelled. In live mode, only verifier-passed,
          human-reviewed records are public; facts, interpretations, and checks stay distinct.
        </p>
        <div className="items">
          {insights.map((insight) => (
            <article className="item" key={insight.id ?? insight.title}>
              <div className="item-body">
                <div className="item-heading">
                  <strong>{insight.title}</strong>
                  <span className="audit-label">
                    {insight.model_used === "fixture-curated" ? "Fixture example" : "Reviewed live evidence"}
                  </span>
                </div>
                <p>{insight.summary}</p>
                <p><strong>Why it matters:</strong> {insight.why_it_matters}</p>
                <p><strong>What to check:</strong> {insight.what_to_check}</p>
                <div className="evidence-row">
                  <span>Confidence {Math.round(insight.confidence * 100)}%</span>
                  <span>Model {insight.model_used}</span>
                  {insight.upstream_release_type && <span>Upstream release: {insight.upstream_release_type}</span>}
                  {insight.operator_risks?.length ? <span>Potential risks: {insight.operator_risks.join(", ")}</span> : null}
                </div>
                {insight.claims?.length ? (
                  <details className="claims">
                    <summary>Inspect claim evidence</summary>
                    {insight.claims.map((claim, index) => (
                      <div className="claim" key={`${claim.kind}-${index}`}>
                        <strong>{claim.kind.replace("_", " ")}</strong>
                        <span>{claim.text}</span>
                        {claim.evidence.map((evidence) => (
                          <a key={`${evidence.source_url}-${evidence.start_char}`} href={evidence.source_url} target="_blank" rel="noreferrer">
                            “{evidence.excerpt}” ↗
                          </a>
                        ))}
                      </div>
                    ))}
                  </details>
                ) : null}
                <div className="citations" aria-label={`Sources for ${insight.title}`}>
                  {insight.source_citations.map((citation) => (
                    <a key={citation} href={citation} target="_blank" rel="noreferrer">
                      Source ↗
                    </a>
                  ))}
                </div>
              </div>
              <span className={`pill ${insight.severity}`}>{insight.severity}</span>
            </article>
          ))}
          {isLoading && <div className="card status-card"><p>Loading briefing…</p></div>}
          {!isLoading && error && <div className="card status-card"><p>{error}</p></div>}
          {!isLoading && !error && !insights.length && (
            <div className="card status-card">
              <h3>No reviewed insights published yet</h3>
              <p>
                When a reviewer publishes a verifier-passed capture, this briefing will show
                cited changes, why they matter, a bounded check, and inspectable claim evidence.
              </p>
            </div>
          )}
        </div>
      </section>

      <section className="section">
        <div className="eyebrow">The DRIFT contract</div>
        <h2>Useful because it stays inspectable.</h2>
        <div className="cards">
          <div className="card"><h3>Primary facts</h3><p>Each live factual claim retains an exact, frozen source excerpt and offset.</p></div>
          <div className="card"><h3>Labelled interpretation</h3><p>Potential operator risk is distinct from what the upstream source directly states.</p></div>
          <div className="card"><h3>Review before publication</h3><p>Verifier-passed drafts stay private until a human records their review.</p></div>
        </div>
      </section>

      <footer className="footer">DRIFT · fixture-first today · review-gated, claim-grounded live evidence</footer>
    </main>
  );
}
