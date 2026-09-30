import type { CopilotReply, DelayImpact } from "@/lib/types"

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function parse<T>(res: Response, path: string): Promise<T> {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error((data as any).error || `API error ${res.status}: ${path}`)
  return data as T
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" })
  return parse<T>(res, path)
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  return parse<T>(res, path)
}

export const api = {
  getStatus: () => get<any>("/status"),

  getStates: () => get<any[]>("/states"),

  getPHCs: (district?: string, state?: string) => {
    const q = new URLSearchParams()
    if (district) q.set("district", district)
    if (state) q.set("state", state)
    const suffix = q.toString() ? `?${q}` : ""
    return get<any[]>(`/phcs${suffix}`)
  },

  getDistricts: (state?: string) =>
    get<any[]>(state ? `/districts?state=${encodeURIComponent(state)}` : "/districts"),

  getDistrictRisk: (district: string) =>
    get<any>(`/risk/${district}`),

  getTransfers: () => get<any>("/transfers"),

  getAlerts: () => get<any>("/alerts"),

  getImpact: () => get<any>("/impact"),

  translate: (text: string, target: "hi" | "en") =>
    post<{ translated: string; ai_source: string; ai_model: string | null; ai_error?: string }>("/translate", { text, target }),

  askCopilot: (question: string, opts?: { state?: string; district?: string | null; lang?: "en" | "hi" }) =>
    post<CopilotReply>("/ask", {
      question,
      state: opts?.state,
      district: opts?.district || undefined,
      lang: opts?.lang || "en",
    }),

  delayImpact: (id: string, hours = 48, lang: "en" | "hi" = "en") =>
    post<DelayImpact>(`/transfers/${encodeURIComponent(id)}/delay-impact`, { hours, lang }),

  runSentinel: (district: string, simulated = false) =>
    post<any>(`/run/sentinel?district=${district}&simulated=${simulated}`),

  runAll: (simulated = false, state?: string) => {
    const q = new URLSearchParams({ simulated: String(simulated) })
    if (state) q.set("state", state)
    return post<any>(`/run/all?${q}`)
  },

  simulateOutbreak: (state = "Maharashtra") =>
    post<any>(`/simulate/outbreak?state=${encodeURIComponent(state)}`),

  approveTransfer: (id: string) =>
    post<any>(`/transfers/${encodeURIComponent(id)}/approve`),

  escalateTransfer: (id: string) =>
    post<any>(`/transfers/${encodeURIComponent(id)}/escalate`),

  modifyTransfer: (id: string, quantity: number, reason?: string) =>
    post<any>(`/transfers/${encodeURIComponent(id)}/modify`, { quantity, reason }),

  getWeeklyReport: (district: string) =>
    get<any>(`/report/weekly/${district}`),

  getMonthlyReport: (state: string) =>
    get<any>(`/report/monthly/${state}`),

  getPostIncidentReport: (district: string) =>
    get<any>(`/report/post-incident/${district}`),

  getBacktesting: () =>
    get<any>("/backtesting"),

  getLeakage: (district?: string) =>
    get<any>(district ? `/leakage?district=${district}` : "/leakage"),

  scheduleAudit: (phcId: string) =>
    post<any>(`/leakage/${encodeURIComponent(phcId)}/audit`),

  notifyOfficer: (phcId: string) =>
    post<any>(`/leakage/${encodeURIComponent(phcId)}/notify`),
}
