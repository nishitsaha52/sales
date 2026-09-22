export interface DependencyStatus {
  status: "ok" | "error";
  detail: string | null;
}

export interface ReadyResponse {
  status: "ok" | "degraded";
  services: Record<string, DependencyStatus>;
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
  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
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
