import type {
  BacktestConfigRequest,
  BacktestOptions,
  BacktestRunDetail,
  BacktestRunSummary,
  CompanyOut,
  CompareRunsResponse,
  PrebuiltStrategy,
  UniverseStats,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") message = body.detail;
      else if (Array.isArray(body?.detail)) {
        message = body.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join("; ") || message;
      }
    } catch {}
    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// Metadata
export function getBacktestOptions(): Promise<BacktestOptions> {
  return apiFetch<BacktestOptions>("/metadata/backtest-options");
}

// Companies / universe
export function getCompanies(): Promise<CompanyOut[]> {
  return apiFetch<CompanyOut[]>("/companies");
}

export function getUniverseStats(): Promise<UniverseStats> {
  return apiFetch<UniverseStats>("/companies/stats");
}

// Backtests
export function runBacktest(config: BacktestConfigRequest): Promise<BacktestRunDetail> {
  return apiFetch<BacktestRunDetail>("/backtest/run", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export function listRuns(limit = 50): Promise<BacktestRunSummary[]> {
  return apiFetch<BacktestRunSummary[]>(`/backtest/runs?limit=${limit}`);
}

export function getRun(runId: string): Promise<BacktestRunDetail> {
  return apiFetch<BacktestRunDetail>(`/backtest/${runId}`);
}

export function deleteRun(runId: string): Promise<void> {
  return apiFetch<void>(`/backtest/${runId}`, { method: "DELETE" });
}

export function compareRuns(runIds: string[]): Promise<CompareRunsResponse> {
  return apiFetch<CompareRunsResponse>("/backtest/compare", {
    method: "POST",
    body: JSON.stringify({ run_ids: runIds }),
  });
}

export function buildExportUrl(runId: string, format: "csv" | "xlsx", table: "holdings" | "equity_curve"): string {
  return `${API_BASE_URL}/backtest/${runId}/export?format=${format}&table=${table}`;
}

// Prebuilt strategies
export function listPrebuiltStrategies(): Promise<PrebuiltStrategy[]> {
  return apiFetch<PrebuiltStrategy[]>("/strategies/prebuilt");
}

export function runPrebuiltStrategy(key: string): Promise<BacktestRunDetail> {
  return apiFetch<BacktestRunDetail>(`/strategies/prebuilt/${key}/run`, { method: "POST" });
}
