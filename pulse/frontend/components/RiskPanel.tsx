import type { RiskAssessment } from "@/lib/types"
import { RISK_LEVEL, riskColor, colors } from "@/lib/theme"
import Translated from "./Translated"

interface Props { risk: RiskAssessment; lang?: "en" | "hi" }

function displayAiError(raw?: string): string | null {
  if (!raw) return null
  const lowered = raw.toLowerCase()
  if (raw.includes("429") || lowered.includes("resource_exhausted") || lowered.includes("quota") || raw.includes("quotaMetric")) {
    return "Gemini free-tier quota is used up. The demo continues on labelled mock scores. Quota often resets tomorrow."
  }
  if (raw.length > 220 || raw.includes("{'error'") || raw.trim().startsWith("{")) {
    return "Gemini is temporarily unavailable. Using labelled mock scores."
  }
  return raw
}

export default function RiskPanel({ risk, lang = "en" }: Props) {
  const c = RISK_LEVEL[risk.risk_level as keyof typeof RISK_LEVEL] || RISK_LEVEL.LOW
  const live = risk.ai_source === "gemini"
  const aiError = displayAiError(risk.ai_error)
  const quotaHit = Boolean(risk.ai_error && /429|quota|resource_exhausted/i.test(risk.ai_error))

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>{risk.district}</div>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 1 }}>
            {risk.state ? `${risk.state} · ` : ""}District Risk Assessment
          </div>
        </div>
        <span className={`badge badge-${risk.risk_level.toLowerCase()}`}>{c.label}</span>
      </div>

      <div style={{ background: c.bg, border: `1px solid ${c.border}`, borderRadius: 10, padding: "12px 16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: c.color }}>Risk Score</span>
          <span style={{ fontSize: 28, fontWeight: 800, color: c.color, letterSpacing: "-1px" }}>
            {risk.risk_score}<span style={{ fontSize: 14, fontWeight: 500, color: "var(--text-muted)" }}>/100</span>
          </span>
        </div>
        <div className="risk-bar">
          <div className="risk-bar-fill" style={{ width: `${risk.risk_score}%`, background: riskColor(risk.risk_score) }} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <div className="surface-box" style={{ padding: "10px 12px" }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Days to Surge</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>{risk.days_to_surge}</div>
        </div>
        <div className="surface-box" style={{ padding: "10px 12px" }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>At-Risk Medicines</div>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)", marginTop: 4, lineHeight: 1.4 }}>
            {(risk.key_medicines_at_risk ?? []).length > 0 ? risk.key_medicines_at_risk.join(", ") : "None"}
          </div>
        </div>
      </div>

      <div className="surface-box" style={{ padding: "10px 12px" }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 5 }}>
          Primary Signal
        </div>
        <Translated text={risk.primary_driver} lang={lang} style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }} speakSize={12} />
      </div>

      <div style={{ borderRadius: 8, padding: "10px 12px", border: `1px solid ${live ? c.border : "var(--border)"}`, background: live ? c.bg : "var(--surface-muted)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: live ? c.color : colors.textMuted }} />
          <span style={{ fontSize: 10, fontWeight: 700, color: live ? c.color : "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            {live
              ? `Gemini${risk.ai_model ? ` · ${risk.ai_model}` : ""}`
              : quotaHit
                ? "Mock fallback — Gemini quota exceeded"
                : "Mock fallback — Gemini not live"}
          </span>
        </div>
        <Translated text={risk.reasoning} lang={lang} style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6 }} speakSize={12} />
        {aiError && (
          <p style={{ fontSize: 11, color: colors.high, margin: "8px 0 0" }}>{aiError}</p>
        )}
      </div>

      <div style={{ background: "var(--accent-soft)", borderRadius: 10, padding: "12px 14px", border: "1px solid var(--accent-border)" }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: "var(--accent-dark)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 5 }}>
          Recommended Action
        </div>
        <Translated text={risk.recommended_action} lang={lang} style={{ fontSize: 12, color: "var(--text-primary)", lineHeight: 1.6 }} speakSize={12} />
      </div>
    </div>
  )
}
