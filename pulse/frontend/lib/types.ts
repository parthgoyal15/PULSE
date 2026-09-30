export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
export type Urgency = "CRITICAL" | "HIGH" | "MEDIUM"
export type AutonomyLevel = "AUTO" | "APPROVE_REQUIRED" | "ESCALATE"
export type AiSource = "gemini" | "mock" | "rule" | null

export interface PHC {
  id: string
  name: string
  district: string
  state: string
  lat: number
  lng: number
  block: string
  stock: Record<string, number>
  beds: { total: number; occupied: number }
  staff: { total: number; present: number }
  avg_daily_footfall: number
  district_risk_score?: number
  district_risk_level?: RiskLevel
}

export interface District {
  name: string
  lat: number
  lng: number
  state: string
  phc_count: number
  population: number
  risk_score: number
  risk_level: RiskLevel
  primary_driver: string
  days_to_surge: number
}

export interface RiskAssessment {
  district: string
  state?: string
  risk_score: number
  risk_level: RiskLevel
  primary_driver: string
  days_to_surge: number
  key_medicines_at_risk: string[]
  reasoning: string
  recommended_action: string
  ai_source?: AiSource
  ai_model?: string | null
  ai_error?: string
}

export interface Transfer {
  id: string
  from_district: string
  to_district: string
  from_state?: string
  to_state?: string
  medicine: string
  quantity: number
  urgency: Urgency
  deadline_days: number
  estimated_cost_inr: number
  justification: string
  autonomy_level: AutonomyLevel
  status?: string
  whatsapp_text?: string
  whatsapp_language?: string
  units_moved?: number
}

export interface Alert {
  type: string
  district?: string
  state?: string
  risk_score?: number
  risk_level?: RiskLevel
  message: string
  transfer_count?: number
  timestamp: string
  ai_source?: AiSource
}

export interface Impact {
  stockout_days_prevented: number
  patients_served: number
  units_redistributed: number
  warnings_issued: number
  leakage_flagged: number
}

export interface CopilotReply {
  question: string
  answer: string
  ai_source?: AiSource
  ai_model?: string | null
  ai_error?: string
  scope?: { state?: string | null; district?: string | null }
}

export interface DelayPhcRow {
  phc_id: string
  phc_name: string
  block?: string
  stock_now: number
  days_supply_now: number
  stock_after: number
  days_supply_after: number
  hits_zero: boolean
  uncovered_patient_visits: number
}

export interface DelayImpact {
  transfer_id: string
  hours: number
  medicine: string
  from_district: string
  to_district: string
  quantity: number
  current_urgency: string
  phcs: DelayPhcRow[]
  stockout_phcs: string[]
  stockout_count: number
  patients_at_risk: number
  recommended_urgency: string
  recommend_approve_now: boolean
  headline?: string
  cmo_brief?: string
  ai_source?: AiSource
  ai_model?: string | null
  ai_error?: string
}

export interface PulseStatus {
  gemini_live: boolean
  gemini_configured?: boolean
  quota_blocked?: boolean
  allow_mocks: boolean
  whatsapp_live: boolean
  persistence: string
  operational_states: string[]
  last_ai_error: string | null
  last_ai_source: AiSource
}
