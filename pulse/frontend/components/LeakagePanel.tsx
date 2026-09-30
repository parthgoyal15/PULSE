"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { colors } from "@/lib/theme"

interface Props { district?: string }

export default function LeakagePanel({ district }: Props) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getLeakage(district).then(setData).catch(() => {}).finally(() => setLoading(false))
  }, [district])

  if (loading) return <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>Analysing stock patterns…</div>
  if (!data) return null

  const { leakage_analysis, flagged_count } = data
  const flagged = leakage_analysis.filter((r: any) => r.status === "FLAGGED")
  const normal = leakage_analysis.filter((r: any) => r.status === "NORMAL")

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Summary bar */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
        {[
          { label: "PHCs Analysed", value: leakage_analysis.length, color: colors.accentDark, bg: colors.accentSoft, border: colors.accentBorder },
          { label: "Anomalies Flagged", value: flagged_count, color: colors.critical, bg: colors.criticalSoft, border: colors.criticalBorder },
          { label: "Normal", value: leakage_analysis.length - flagged_count, color: colors.accentDark, bg: colors.lowSoft, border: colors.lowBorder },
        ].map(({ label, value, color, bg, border }) => (
          <div key={label} style={{ background: bg, border: `1px solid ${border}`, borderRadius: 10, padding: "12px 16px", textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color }}>{value}</div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      {flagged_count === 0 && (
        <div style={{ background: colors.lowSoft, border: `1px solid ${colors.lowBorder}`, borderRadius: 10, padding: 16, textAlign: "center", color: colors.accentDark, fontSize: 13 }}>
          ✓ No leakage anomalies detected across all PHCs
        </div>
      )}

      {/* Flagged PHCs */}
      {flagged.length > 0 && (
        <div>
          <div className="section-title" style={{ color: colors.critical }}>Flagged PHCs — Anomalous Dispensing Patterns</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {flagged.map((phc: any) => (
              <div key={phc.phc_id} style={{ background: colors.criticalSoft, border: `1px solid ${colors.criticalBorder}`, borderRadius: 10, padding: 14 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>{phc.phc_name}</div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>{phc.block} Block · {phc.district}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 20, fontWeight: 800, color: colors.critical }}>{phc.anomaly_score}</div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)" }}>Anomaly Score</div>
                  </div>
                </div>

                {phc.flags.map((flag: any) => (
                  <div key={flag.medicine} style={{ background: "white", borderRadius: 8, padding: "10px 12px", marginBottom: 6, border: `1px solid ${colors.criticalBorder}` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{flag.medicine}</span>
                      <span style={{ fontSize: 11, fontWeight: 700, background: flag.severity === "HIGH" ? colors.criticalSoft : colors.highSoft, color: flag.severity === "HIGH" ? "#be123c" : "#c2410c", padding: "2px 8px", borderRadius: 4 }}>
                        {flag.severity} ANOMALY
                      </span>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, fontSize: 11 }}>
                      <div className="surface-box" style={{ padding: "6px 8px" }}>
                        <div style={{ color: "var(--text-muted)" }}>Reported Dispensed</div>
                        <div style={{ fontWeight: 700, color: colors.critical, fontSize: 14, marginTop: 2 }}>{flag.reported_dispensed}</div>
                      </div>
                      <div className="surface-box" style={{ padding: "6px 8px" }}>
                        <div style={{ color: "var(--text-muted)" }}>Expected (by footfall)</div>
                        <div style={{ fontWeight: 700, color: colors.accentDark, fontSize: 14, marginTop: 2 }}>{flag.expected_consumption}</div>
                      </div>
                      <div style={{ background: colors.criticalSoft, borderRadius: 6, padding: "6px 8px" }}>
                        <div style={{ color: "var(--text-muted)" }}>Anomaly Ratio</div>
                        <div style={{ fontWeight: 800, color: colors.critical, fontSize: 14, marginTop: 2 }}>{flag.anomaly_ratio}×</div>
                      </div>
                    </div>
                  </div>
                ))}

                <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                  <button
                    disabled={phc.audit_scheduled}
                    onClick={async () => {
                      await api.scheduleAudit(phc.phc_id)
                      const next = await api.getLeakage(district)
                      setData(next)
                    }}
                    style={{ flex: 1, background: phc.audit_scheduled ? colors.lowBorder : colors.critical, color: phc.audit_scheduled ? colors.accentDark : "white", border: "none", borderRadius: 6, padding: "7px 0", fontSize: 12, fontWeight: 600, cursor: phc.audit_scheduled ? "default" : "pointer" }}
                  >
                    {phc.audit_scheduled ? "Audit scheduled" : "Schedule Physical Audit"}
                  </button>
                  <button
                    disabled={phc.officer_notified}
                    onClick={async () => {
                      await api.notifyOfficer(phc.phc_id)
                      const next = await api.getLeakage(district)
                      setData(next)
                    }}
                    style={{ flex: 1, background: "white", color: "var(--text-secondary)", border: "1px solid var(--border)", borderRadius: 6, padding: "7px 0", fontSize: 12, fontWeight: 600, cursor: phc.officer_notified ? "default" : "pointer" }}
                  >
                    {phc.officer_notified ? "Officer notified" : "Notify Block Officer"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Normal PHCs summary */}
      {normal.length > 0 && (
        <div>
          <div className="section-title">Normal PHCs</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {normal.map((phc: any) => (
              <div key={phc.phc_id} className="surface-box" style={{ padding: "8px 12px", display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 8, height: 8, background: colors.accent, borderRadius: "50%", flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>{phc.phc_name}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{phc.block} Block</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
