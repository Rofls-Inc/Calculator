import { useEffect, useState } from "react";

import { getHealth } from "./api/client.js";


function App() {
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    let active = true;

    getHealth()
      .then(() => active && setBackendStatus("online"))
      .catch(() => active && setBackendStatus("offline"));

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="page-shell">
      <section className="project-card">
        <span className="eyebrow">Software Engineering · Sprint 0</span>
        <h1>Calculator service</h1>
        <p className="lead">
          The project skeleton is ready. The team can now implement expression
          evaluation, SQLite history, and the calculator interface independently.
        </p>

        <div className={`status status--${backendStatus}`}>
          <span className="status__dot" aria-hidden="true" />
          Backend: {backendStatus}
        </div>

        <div className="work-grid">
          <article>
            <h2>Calculate</h2>
            <p>POST /api/v1/calculate</p>
          </article>
          <article>
            <h2>History</h2>
            <p>GET /api/v1/history</p>
          </article>
          <article>
            <h2>Health</h2>
            <p>GET /api/v1/health</p>
          </article>
        </div>
      </section>
    </main>
  );
}


export default App;
