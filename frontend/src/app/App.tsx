import { useQuery } from "@tanstack/react-query";
import { Link, Route, Routes } from "react-router-dom";

import { getReadiness } from "../api/client";
import { FoundationPage } from "../pages/FoundationPage";

function AppShell() {
  const readiness = useQuery({
    queryKey: ["readiness"],
    queryFn: getReadiness,
    retry: 1,
    refetchInterval: 30_000,
  });

  const state = readiness.isSuccess ? "connected" : readiness.isError ? "offline" : "checking";

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link className="brand" to="/">
          <span className="brand-mark" aria-hidden="true">T</span>
          <span>
            <strong>TCG Digital</strong>
            <small>Partner Portal</small>
          </span>
        </Link>
        <span className={`connection connection--${state}`}>
          <span className="connection-dot" aria-hidden="true" />
          API {state}
        </span>
      </header>
      <main>
        <Routes>
          <Route path="*" element={<FoundationPage query={readiness} />} />
        </Routes>
      </main>
    </div>
  );
}

export default AppShell;

