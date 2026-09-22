import { Link } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();
  const isTcgAdmin = user?.roles.includes("TCG_ADMIN");
  return (
    <div className="workspace-page">
      <header className="page-heading">
        <div><span className="eyebrow">Overview</span><h1>Good to see you, {user?.full_name.split(" ")[0]}.</h1></div>
      </header>
      <div className="summary-grid">
        <article><span>Access</span><strong>{user?.roles[0]?.replaceAll("_", " ")}</strong><p>Your active workspace role</p></article>
        <article><span>Organization</span><strong>{user?.partner_id ? "Partner" : "TCG Digital"}</strong><p>Current data scope</p></article>
        <article><span>Account</span><strong>Active</strong><p>{user?.email}</p></article>
      </div>
      <section className="content-card welcome-card">
        <div><span className="status-kicker">Phase 1A</span><h2>Partner Access & Management</h2><p>Review registrations, maintain partner profiles, and control team access from one governed workspace.</p></div>
        <Link className="button-link" to={user?.partner_id ? `/partners/${user.partner_id}` : "/partners"}>
          {isTcgAdmin ? "Manage partners" : "View company"}
        </Link>
      </section>
      <div className="quick-links"><Link to="/pricing">View pricing →</Link>{!user?.partner_id && <Link to="/products">Manage product catalog →</Link>}</div>
    </div>
  );
}
