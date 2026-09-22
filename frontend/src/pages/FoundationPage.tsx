import type { UseQueryResult } from "@tanstack/react-query";

import type { ReadyResponse } from "../api/client";

interface FoundationPageProps {
  query: UseQueryResult<ReadyResponse, Error>;
}

const labels: Record<string, string> = {
  postgres: "PostgreSQL + pgvector",
  minio: "MinIO object storage",
};

export function FoundationPage({ query }: FoundationPageProps) {
  return (
    <section className="foundation">
      <div className="eyebrow">Phase 0 · Foundation</div>
      <h1>The foundation is ready for the partner journey.</h1>
      <p className="intro">
        A typed React client, versioned FastAPI service, durable PostgreSQL data layer, and
        private object storage—wired together for the next delivery phase.
      </p>

      <div className="status-panel" aria-live="polite">
        <div className="status-heading">
          <div>
            <span className="status-kicker">Environment</span>
            <h2>Service readiness</h2>
          </div>
          <button type="button" onClick={() => void query.refetch()} disabled={query.isFetching}>
            {query.isFetching ? "Checking…" : "Check again"}
          </button>
        </div>

        {query.isPending && <p className="notice">Contacting the backend…</p>}
        {query.isError && (
          <p className="notice notice--error">
            The API is not reachable yet. Start the backend and retry.
          </p>
        )}
        {query.data && (
          <ul className="service-list">
            {Object.entries(query.data.services).map(([name, service]) => (
              <li key={name}>
                <span className={`service-icon service-icon--${service.status}`} aria-hidden="true">
                  {service.status === "ok" ? "✓" : "!"}
                </span>
                <span>
                  <strong>{labels[name] ?? name}</strong>
                  <small>{service.status === "ok" ? "Available" : service.detail ?? "Unavailable"}</small>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="capability-grid">
        <article><span>01</span><h3>Secure access</h3><p>JWT authentication with extensible role and permission controls.</p></article>
        <article><span>02</span><h3>Traceable actions</h3><p>Correlation-aware structured logging and a persistent audit framework.</p></article>
        <article><span>03</span><h3>Repeatable setup</h3><p>Versioned migrations, idempotent seeds, and containerized infrastructure.</p></article>
      </div>
    </section>
  );
}

