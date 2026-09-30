import { useEffect, useState } from "react"
import type { DelayImpact, Transfer } from "@/lib/types"
import { RISK_LEVEL, colors } from "@/lib/theme"
import { api } from "@/lib/api"
import Translated from "./Translated"
import SpeakButton from "./SpeakButton"

interface Props {
  transfer: Transfer
  lang?: "en" | "hi"
  onApprove?: (id: string) => void
  onEscalate?: (id: string) => void
  onModify?: (id: string) => void
}

const urgencyStyle: Record<string, { color: string; bg: string; border: string }> = {
  CRITICAL: { color: RISK_LEVEL.CRITICAL.color, bg: RISK_LEVEL.CRITICAL.bg, border: RISK_LEVEL.CRITICAL.border },
  HIGH:     { color: RISK_LEVEL.HIGH.color, bg: RISK_LEVEL.HIGH.bg, border: RISK_LEVEL.HIGH.border },
  MEDIUM:   { color: "#b45309", bg: RISK_LEVEL.MEDIUM.bg, border: RISK_LEVEL.MEDIUM.border },
}

const autoText: Record<string, string> = {
  AUTO:             "Suggested auto-execute under 100 units — still requires dashboard confirm in this demo",
  APPROVE_REQUIRED: "Waiting for CMO approve — persists in SQLite after you confirm",
  ESCALATE:         "Requires explicit approval or escalate to state secretary",
}

function splitWhatsappText(raw?: string): { local: string; english: string } {
  if (!raw) return { local: "", english: "" }
  const marker = raw.search(/\n\s*\n\s*EN:/i)
  if (marker === -1) return { local: raw.trim(), english: "" }
  const local = raw.slice(0, marker).trim()
  const english = raw.slice(marker).replace(/^\s*\n+\s*EN:\s*/i, "").trim()
  return { local, english }
}

export default function TransferCard({ transfer, lang = "en", onApprove, onEscalate, onModify }: Props) {
  const s = urgencyStyle[transfer.urgency] || urgencyStyle.MEDIUM
  const cmoLanguage = transfer.whatsapp_language === "or" ? "Odia" : transfer.whatsapp_language === "mr" ? "Marathi" : transfer.whatsapp_language === "hi" ? "Hindi" : null
  const { english: whatsappEnglish } = splitWhatsappText(transfer.whatsapp_text)

  if (transfer.status === "approved") {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 14px", background: colors.lowSoft, border: `1px solid ${colors.lowBorder}`, borderRadius: 12 }}>
        <div style={{ fontSize: 13 }}>
          <span style={{ fontWeight: 600 }}>{(transfer.units_moved ?? transfer.quantity).toLocaleString()} {transfer.medicine}</span>
          <span style={{ color: "var(--text-secondary)" }}> · {transfer.from_district} → {transfer.to_district} · Stock moved</span>
        </div>
      </div>
    )
  }

  if (transfer.status === "escalated") {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 14px", background: colors.highSoft, border: `1px solid ${colors.highBorder}`, borderRadius: 12 }}>
        <div style={{ fontSize: 13 }}>
          <span style={{ fontWeight: 600 }}>{transfer.quantity.toLocaleString()} {transfer.medicine}</span>
          <span style={{ color: "var(--text-secondary)" }}> · Escalated to state secretary · {transfer.from_district} → {transfer.to_district}</span>
        </div>
      </div>
    )
  }

  return (
    <div style={{ border: `1px solid ${s.border}`, borderRadius: 14, background: s.bg, overflow: "hidden" }}>
      <div style={{ background: s.color, padding: "6px 14px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "white", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          {transfer.urgency}
        </span>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.85)" }}>
          Deadline: {transfer.deadline_days}d
        </span>
      </div>

      <div style={{ padding: "12px 14px", display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>{transfer.medicine}</span>
          <span style={{ fontSize: 14, fontWeight: 700, color: s.color }}>{transfer.quantity.toLocaleString()} units</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8, background: "white", borderRadius: 6, padding: "7px 10px", border: "1px solid var(--border)" }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>{transfer.from_district}</span>
          <span style={{ color: "var(--text-muted)", fontSize: 14 }}>→</span>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>{transfer.to_district}</span>
          <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-secondary)", fontWeight: 500 }}>₹{transfer.estimated_cost_inr.toLocaleString()}</span>
        </div>

        {transfer.from_state && transfer.to_state && (
          <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
            {transfer.from_state === transfer.to_state
              ? `Intra-state · ${transfer.to_state}`
              : `Inter-state · ${transfer.from_state} → ${transfer.to_state}`}
          </div>
        )}

        <Translated text={transfer.justification} lang={lang} style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 }} speakSize={12} />

        {whatsappEnglish && (
          <div style={{
            background: "white", padding: "8px 10px",
            borderRadius: 6, border: "1px solid var(--border)",
          }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 5 }}>
              WhatsApp preview
            </div>
            <Translated
              text={whatsappEnglish}
              lang={lang}
              speakSize={11}
              style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5, whiteSpace: "pre-wrap" }}
            />
          </div>
        )}

        <div style={{ fontSize: 11, color: "var(--text-secondary)", background: "white", padding: "5px 8px", borderRadius: 5, border: "1px solid var(--border)" }}>
          {autoText[transfer.autonomy_level] || autoText.APPROVE_REQUIRED}
          {cmoLanguage ? ` · Actual WhatsApp send is in ${cmoLanguage}` : ""}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          {onApprove && <button className="btn btn-approve" onClick={() => onApprove(transfer.id)}>Approve</button>}
          {onModify && <button className="btn btn-outline" onClick={() => onModify(transfer.id)}>Modify</button>}
          {onEscalate && <button className="btn btn-outline" onClick={() => onEscalate(transfer.id)}>Escalate</button>}
        </div>

        <DelayImpactBlock transferId={transfer.id} lang={lang} />
      </div>
    </div>
  )
}

function DelayImpactBlock({ transferId, lang }: { transferId: string; lang: "en" | "hi" }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<DelayImpact | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setData(null)
    setOpen(false)
    setError(null)
  }, [lang, transferId])

  const run = async () => {
    if (data) { setOpen(v => !v); return }
    setLoading(true)
    setError(null)
    setOpen(true)
    try {
      const res = await api.delayImpact(transferId, 48, lang)
      setData(res)
    } catch (err: any) {
      setError(err?.message || "Delay analysis failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={run}
        disabled={loading}
        className="btn btn-outline"
        style={{ width: "100%", fontWeight: 700, color: "var(--accent-dark)", borderColor: "var(--accent-border)", background: "var(--accent-soft)" }}
      >
        {loading ? "Projecting 48h stock…" : data && open ? "Hide 48h delay" : "If delayed 48h"}
      </button>

      {open && (
        <div style={{
          marginTop: 8, background: "white", border: "1px solid var(--border)",
          borderRadius: 8, padding: "10px 11px", display: "flex", flexDirection: "column", gap: 8,
        }}>
          {error && <div style={{ fontSize: 12, color: "var(--critical)" }}>{error}</div>}
          {data && (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "flex-start" }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)", lineHeight: 1.4 }}>
                  {data.headline}
                </div>
                <span style={{
                  fontSize: 10, fontWeight: 700, whiteSpace: "nowrap",
                  color: data.ai_source === "gemini" ? "var(--accent-dark)" : "var(--text-muted)",
                }}>
                  {data.ai_source === "gemini" ? "Gemini" : "Mock"}
                </span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
                {[
                  { label: "PHCs at zero", value: String(data.stockout_count) },
                  { label: "Visits uncovered", value: String(data.patients_at_risk) },
                  { label: "Urgency if delayed", value: data.recommended_urgency },
                ].map(cell => (
                  <div key={cell.label} className="surface-box" style={{ padding: "6px 8px", textAlign: "center" }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: data.stockout_count ? colors.critical : colors.accentDark }}>{cell.value}</div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)", marginTop: 2 }}>{cell.label}</div>
                  </div>
                ))}
              </div>
              {data.cmo_brief && (
                <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <p style={{ flex: 1, margin: 0, fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    {data.cmo_brief}
                  </p>
                  <SpeakButton text={data.cmo_brief} lang={lang} size={11} />
                </div>
              )}
              {data.phcs?.length > 0 && (
                <div style={{ fontSize: 11, color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: 4 }}>
                  {data.phcs.map(p => (
                    <div key={p.phc_id} style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <span style={{ fontWeight: p.hits_zero ? 700 : 500, color: p.hits_zero ? colors.critical : "var(--text-secondary)" }}>
                        {p.phc_name}
                      </span>
                      <span>
                        {p.days_supply_now}d → {p.days_supply_after}d
                        {p.hits_zero ? " · zero" : ""}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {data.recommend_approve_now && (
                <div style={{ fontSize: 11, fontWeight: 700, color: colors.critical }}>
                  Recommend approve now — waiting burns remaining cover.
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
