"use client";

import { useState } from "react";

type ChatAnswer = {
  answer: string;
  source_citations: string[];
  model_used: string;
  grounded_insight_ids: number[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SUGGESTIONS = [
  "What should I check for vLLM?",
  "What changed in NCCL collectives?",
  "Does TensorRT 11.1 affect my CUDA version?",
];

type Status = "idle" | "loading" | "answered" | "empty" | "error";

export default function AskDrift() {
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<ChatAnswer | null>(null);

  async function ask(pending: string) {
    const trimmed = pending.trim();
    if (trimmed.length < 2 || status === "loading") return;

    setStatus("loading");
    setResult(null);
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (response.status === 404) {
        setStatus("empty");
        return;
      }
      if (!response.ok) {
        throw new Error(`The DRIFT API returned ${response.status}.`);
      }

      const answer = (await response.json()) as ChatAnswer;
      setResult(answer);
      setStatus("answered");
    } catch {
      setStatus("error");
    }
  }

  return (
    <section className="section" id="ask">
      <div className="eyebrow">Grounded chat</div>
      <h2>Ask DRIFT</h2>
      <p>
        Ask about a release and get an answer grounded only in retrieved DRIFT
        evidence, returned with its source citations. In live mode the answer is
        generated over human-reviewed, verifier-passed Insights; in fixture mode
        it is composed from the labelled example records.
      </p>

      <form
        className="ask-form"
        onSubmit={(event) => {
          event.preventDefault();
          void ask(question);
        }}
      >
        <label className="visually-hidden" htmlFor="ask-input">
          Ask a question about a release
        </label>
        <input
          id="ask-input"
          className="ask-input"
          type="text"
          value={question}
          placeholder="What should I check for vLLM?"
          onChange={(event) => setQuestion(event.target.value)}
          autoComplete="off"
        />
        <button
          className="button primary"
          type="submit"
          disabled={status === "loading" || question.trim().length < 2}
        >
          {status === "loading" ? "Asking…" : "Ask"}
        </button>
      </form>

      <div className="ask-suggestions" aria-label="Example questions">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            className="ask-chip"
            onClick={() => {
              setQuestion(suggestion);
              void ask(suggestion);
            }}
          >
            {suggestion}
          </button>
        ))}
      </div>

      {status === "loading" && (
        <div className="card ask-answer">
          <p>Retrieving cited evidence…</p>
        </div>
      )}

      {status === "empty" && (
        <div className="card ask-answer">
          <h3>No matching insights</h3>
          <p>
            No reviewed DRIFT insight matched that question. Try a specific
            library or release, such as vLLM, NCCL, TensorRT, or Transformers.
          </p>
        </div>
      )}

      {status === "error" && (
        <div className="card ask-answer">
          <h3>The DRIFT API is not reachable</h3>
          <p>Start the backend and ask again.</p>
        </div>
      )}

      {status === "answered" && result && (
        <div className="card ask-answer">
          <div className="ask-answer-label">Grounded answer</div>
          <p className="ask-answer-body">{result.answer}</p>
          {result.source_citations.length > 0 && (
            <div className="citations" aria-label="Answer sources">
              {result.source_citations.map((citation) => (
                <a key={citation} href={citation} target="_blank" rel="noreferrer">
                  Source ↗
                </a>
              ))}
            </div>
          )}
          <div className="ask-meta">
            <span>Model {result.model_used}</span>
            {result.grounded_insight_ids.length > 0 && (
              <span>Grounded in insight {result.grounded_insight_ids.join(", ")}</span>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
