import { useQuery } from "@tanstack/react-query";
import { Navigate, Route, Routes } from "react-router-dom";

import { getReadiness } from "../api/client";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { AppLayout } from "../layouts/AppLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { FoundationPage } from "../pages/FoundationPage";
import { LoginPage } from "../pages/LoginPage";
import { PartnerDetailPage } from "../pages/PartnerDetailPage";
import { PartnerUsersPage } from "../pages/PartnerUsersPage";
import { PartnersPage } from "../pages/PartnersPage";
import { RegisterPage } from "../pages/RegisterPage";

function AppShell() {
  const readiness = useQuery({
    queryKey: ["readiness"],
    queryFn: getReadiness,
    retry: 1,
    refetchInterval: 30_000,
  });

  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/partners" element={<PartnersPage />} />
        <Route path="/partners/new" element={<RegisterPage admin />} />
        <Route path="/partners/:partnerId" element={<PartnerDetailPage />} />
        <Route path="/partners/:partnerId/users" element={<PartnerUsersPage />} />
        <Route path="/system" element={<FoundationPage query={readiness} />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>;
}

export default AppShell;
