import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";

export function ProtectedRoute() {
  const auth = useAuth();
  const location = useLocation();
  if (auth.isLoading) return <div className="page-loader">Loading your workspace…</div>;
  if (!auth.isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}

