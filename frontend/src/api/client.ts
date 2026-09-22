export interface DependencyStatus {
  status: "ok" | "error";
  detail: string | null;
}

export interface ReadyResponse {
  status: "ok" | "degraded";
  services: Record<string, DependencyStatus>;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  partner_id: string | null;
  roles: string[];
  permissions: string[];
}

export interface MasterDataItem {
  id: string;
  code: string;
  name: string;
}

export interface RegistrationOptions {
  partner_types: MasterDataItem[];
  partner_tiers: MasterDataItem[];
  countries: MasterDataItem[];
  partner_roles: MasterDataItem[];
}

export type PartnerStatus =
  | "PENDING_APPROVAL"
  | "ACTIVE"
  | "REJECTED"
  | "SUSPENDED"
  | "INACTIVE";

export interface Partner {
  id: string;
  code: string | null;
  company_name: string;
  legal_name: string | null;
  company_email: string;
  website: string | null;
  phone: string | null;
  address: string | null;
  primary_contact_name: string;
  primary_contact_email: string;
  primary_contact_phone: string | null;
  status: PartnerStatus;
  rejection_reason: string | null;
  approved_at: string | null;
  partner_type: MasterDataItem;
  tier: MasterDataItem | null;
  countries: MasterDataItem[];
  created_at: string;
  updated_at: string;
}

export interface PartnerList {
  items: Partner[];
  total: number;
  page: number;
  page_size: number;
}

export interface PartnerUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: string[];
  created_at: string;
}

const API_BASE_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly requestId?: string,
  ) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem("partner_portal_token");
  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { error?: { message?: string; request_id?: string } }
      | null;
    throw new ApiError(
      body?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      body?.error?.request_id,
    );
  }
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const payload = (await response.json()) as
    | { access_token: string }
    | { error?: { message?: string; request_id?: string } };
  if (!response.ok || !("access_token" in payload)) {
    const error = "error" in payload ? payload.error : undefined;
    throw new ApiError(error?.message ?? "Sign in failed", response.status, error?.request_id);
  }
  return payload.access_token;
}

export const getCurrentUser = () => apiRequest<CurrentUser>("/auth/me");
export const getRegistrationOptions = () =>
  apiRequest<RegistrationOptions>("/partners/registration-options");
export const registerPartner = (body: unknown) =>
  apiRequest<Partner>("/partners/register", { method: "POST", body: JSON.stringify(body) });
export const createPartner = (body: unknown) =>
  apiRequest<Partner>("/partners", { method: "POST", body: JSON.stringify(body) });
export const getPartners = (query = "") =>
  apiRequest<PartnerList>(`/partners${query ? `?${query}` : ""}`);
export const getPartner = (id: string) => apiRequest<Partner>(`/partners/${id}`);
export const updatePartner = (id: string, body: unknown) =>
  apiRequest<Partner>(`/partners/${id}`, { method: "PATCH", body: JSON.stringify(body) });
export const getPartnerUsers = (id: string) =>
  apiRequest<PartnerUser[]>(`/partners/${id}/users`);
export const approvePartner = (id: string, tierCode: string) =>
  apiRequest<Partner>(`/partners/${id}/approve`, {
    method: "POST",
    body: JSON.stringify({ tier_code: tierCode }),
  });
export const rejectPartner = (id: string, reason: string) =>
  apiRequest<Partner>(`/partners/${id}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
export const changePartnerStatus = (id: string, status: PartnerStatus) =>
  apiRequest<Partner>(`/partners/${id}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  });
export const createPartnerUser = (id: string, body: unknown) =>
  apiRequest<PartnerUser>(`/partners/${id}/users`, {
    method: "POST",
    body: JSON.stringify(body),
  });
export const updatePartnerUser = (partnerId: string, userId: string, body: unknown) =>
  apiRequest<PartnerUser>(`/partners/${partnerId}/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });

export function getReadiness(): Promise<ReadyResponse> {
  return fetch(`${API_BASE_URL}/api/v1/health/ready`, {
    headers: { Accept: "application/json" },
  }).then(async (response) => {
    const body = (await response.json()) as ReadyResponse;
    if (response.status === 503 && body.status === "degraded") return body;
    if (!response.ok) throw new ApiError("Could not check service readiness", response.status);
    return body;
  });
}
