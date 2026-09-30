"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { colors } from "@/lib/theme"

export default function BacktestingPanel() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getBacktesting().then(setData).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>Loading backtesting data…</div>
  if (!data) return null

  const out = data.outcome_summary
  const timeline = data.weekly_timeline || []
  const signals = data.signals_comparison?.sources || []

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      {/* Hero outcome */}
      <div style={{ background: "linear-gradient(135deg, #3d8a82, #2f7a72)", borderRadius: 14, padding: 24, color: "white" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "rgba(255,255,255,0.75)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
          Historical Validation · 2019 Maharashtra Dengue Outbreak
        </div>
        <div style={{ fontSize: 18, fontWeight: 700, color: "white", marginBottom: 16 }}>
          PULSE would have prevented the Raigad stock-out entirely
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          {[
            { label: "Advance Warning", value: `${out.pulse_advance_warning_days} days`, sub: "before actual stock-out", color: "#5eead4" },
            { label: "Patients Affected", value: "0", sub: `vs ${out.patients_affected_actual?.toLocaleString()} without PULSE`, color: "#7dd3fc" },
            { label: "Pre-positioning Cost", value: `₹${(out.pre_positioning_cost_inr/100000).toFixed(1)}L`, sub: `saved ₹${(out.cost_of_inaction_inr/100000).toFixed(0)}L in hospitalisation`, color: "#fdba74" },
            { label: "Return on Investment", value: out.roi, sub: "cost of action vs inaction", color: "#c4b5fd" },
          ].map(({ label, value, sub, color }) => (
            <div key={label} style={{ background: "rgba(255,255,255,0.14)", borderRadius: 10, padding: "12px 14px", border: "1px solid rgba(255,255,255,0.22)" }}>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.72)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 24, fontWeight: 800, color, letterSpacing: "-0.5px" }}>{value}</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.78)", marginTop: 2 }}>{sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Signal detection comparison */}
      <div className="card" style={{ padding: 20 }}>
        <div className="section-title">Signal Detection Timeline — How Early Each Source Warned</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {signals.map((s: any, i: number) => {
            const isTraditional = s.signal.includes("Traditional")
            const barPct = Math.min(100, (s.days_before_stockout / 30) * 100)
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 220, fontSize: 12, color: isTraditional ? colors.critical : "var(--text-secondary)", fontWeight: isTraditional ? 600 : 400, flexShrink: 0 }}>
                  {s.signal}
                </div>
                <div style={{ flex: 1, background: "var(--surface-muted)", borderRadius: 4, height: 8, position: "relative" }}>
                  <div style={{
                    width: `${barPct}%`, height: 8, borderRadius: 4,
                    background: isTraditional ? colors.critical : colors.accent,
                    transition: "width 1s",
                  }} />
                </div>
                <div style={{ width: 80, textAlign: "right", fontSize: 12, fontWeight: 600, color: isTraditional ? colors.critical : colors.accentDark, flexShrink: 0 }}>
                  {s.days_before_stockout === 0 ? "Too late" : `${s.days_before_stockout}d early`}
                </div>
              </div>
            )
          })}
        </div>
        <div style={{ marginTop: 12, padding: "8px 12px", background: colors.lowSoft, borderRadius: 8, border: `1px solid ${colors.lowBorder}`, fontSize: 12, color: colors.accentDark }}>
          PULSE fused all signals and generated the first alert <strong>21 days</strong> before the traditional system detected the crisis.
        </div>
      </div>

      {/* Week-by-week timeline */}
      <div className="card" style={{ padding: 20 }}>
        <div className="section-title">Week-by-Week Comparison — What Happened vs What PULSE Would Have Done</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {timeline.map((week: any, i: number) => (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "140px 60px 1fr 1fr",
              gap: 12, padding: "10px 12px", borderRadius: 8,
              background: week.ors_stock_days === 0 ? colors.criticalSoft : i % 2 === 0 ? "var(--surface-muted)" : "white",
              border: week.ors_stock_days === 0 ? `1px solid ${colors.criticalBorder}` : "1px solid transparent",
              alignItems: "flex-start",
            }}>
              <div>
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>{week.week}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 4 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: week.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 10, fontWeight: 600, color: week.color }}>{week.pulse_risk_level}</span>
                </div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 18, fontWeight: 800, color: week.color }}>{week.pulse_risk_score}</div>
                <div style={{ fontSize: 9, color: "var(--text-muted)" }}>RISK</div>
              </div>
              <div style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5 }}>
                <span style={{ fontWeight: 600, color: "var(--text-muted)", fontSize: 10, textTransform: "uppercase" }}>Actual: </span>
                {week.actual_event}
              </div>
              <div style={{ fontSize: 11, lineHeight: 1.5 }}>
                <span style={{ fontWeight: 600, color: colors.accentDark, fontSize: 10, textTransform: "uppercase" }}>PULSE: </span>
                <span style={{ color: week.pulse_action.startsWith("✅") ? colors.accentDark : week.pulse_action.startsWith("🔴") ? colors.critical : "var(--text-secondary)" }}>
                  {week.pulse_action}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
