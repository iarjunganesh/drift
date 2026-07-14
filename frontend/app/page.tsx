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
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [mode, setMode] = useState("fixture");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/health`).then((response) => response.json() as Promise<{ mode?: string }>),
      fetch(`${API_URL}/briefing?top_n=3`).then((response) => response.json() as Promise<{ insight: Insight }[]>),
    ])
      .then(([health, briefing]) => {
        setMode(health.mode || "fixture");
        setInsights(briefing.map((item) => item.insight));
      })
      .catch(() => setError("The DRIFT API is not reachable. Start the backend and try again."));
  }, []);

  return (
    <main className="shell">
      <nav className="nav">
        <a className="wordmark" href="/">DRIFT</a>
        <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">API docs ↗</a>
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
        </div>
        <aside className="signal">
          <div className="signal-label">Current operating mode</div>
          <h2>{mode === "fixture" ? "Deterministic fixture briefing" : "Live grounded chat over fixture evidence"}</h2>
          <p>{error || "Every insight keeps its source, confidence, and bounded follow-up action visible."}</p>
          <div className="rail">
            <div><span>Evidence</span><strong>Primary source</strong></div>
            <div><span>Confidence</span><strong>Always visible</strong></div>
            <div><span>Action</span><strong>Bounded check</strong></div>
          </div>
        </aside>
      </section>

      <section className="section" id="briefing">
        <div className="eyebrow">Top things that matter</div>
        <h2>Today&apos;s briefing</h2>
        <p>Fixture examples are clearly labelled. Live analysis will arrive only after the feed and model pipeline is verified.</p>
        <div className="items">
          {insights.map((insight) => (
            <article className="item" key={insight.id ?? insight.title}>
              <div><strong>{insight.title}</strong><br /><small>{insight.what_to_check}</small></div>
              <span className={`pill ${insight.severity}`}>{insight.severity}</span>
            </article>
          ))}
          {!insights.length && <div className="card"><p>Loading briefing…</p></div>}
        </div>
      </section>

      <section className="section">
        <div className="eyebrow">The DRIFT contract</div>
        <h2>Useful because it stays inspectable.</h2>
        <div className="cards">
          <div className="card"><h3>What changed</h3><p>Plain-language release intelligence instead of changelog paraphrase.</p></div>
          <div className="card"><h3>Why it matters</h3><p>Reasoning tied to a production inference, training, or build workflow.</p></div>
          <div className="card"><h3>What to check</h3><p>A concrete next test, image, flag, or compatibility assumption to review.</p></div>
        </div>
      </section>

      <footer className="footer">DRIFT · fixture-first today · cited and confidence-aware by design</footer>
    </main>
  );
}
