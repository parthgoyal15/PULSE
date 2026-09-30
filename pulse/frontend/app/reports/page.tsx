"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { api } from "@/lib/api"
import WhatsAppPreview from "@/components/WhatsAppPreview"
import BacktestingPanel from "@/components/BacktestingPanel"
import LeakagePanel from "@/components/LeakagePanel"
import PulseLogo from "@/components/PulseLogo"

type Tab = "weekly" | "monthly" | "postincident" | "backtesting" | "leakage" | "whatsapp"

const DISTRICTS = [
  "Raigad", "Pune", "Nashik", "Thane",
  "Puri", "Cuttack", "Khordha", "Balasore",
  "Barmer", "Jodhpur", "Jaipur", "Udaipur",
]
const STATES = ["Maharashtra", "Odisha", "Rajasthan"]

export default function ReportsPage() {
  const [tab, setTab] = useState<Tab>("weekly")
  const [selectedDistrict, setSelectedDistrict] = useState("Raigad")
  const [selectedState, setSelectedState] = useState("Maharashtra")
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchReport = async () => {
    setLoading(true)
    setReport(null)
    try {
      if (tab === "weekly") {
        const data = await api.getWeeklyReport(selectedDistrict)
        setReport(data)
      } else if (tab === "monthly") {
        const data = await api.getMonthlyReport(selectedState)
        setReport(data)
      } else if (tab === "postincident") {
        const data = await api.getPostIncidentReport(selectedDistrict)
        setReport(data)
      }
    } catch {
      setReport({ error: true })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (tab === "weekly" || tab === "monthly" || tab === "postincident") {
      fetchReport()
    }
  }, [tab, selectedDistrict, selectedState])

  const TABS: { id: Tab; label: string; icon: string }[] = [
    { id: "weekly", label: "Weekly Brief", icon: "📋" },
    { id: "monthly", label: "Monthly Overview", icon: "📊" },
    { id: "postincident", label: "Post-Incident", icon: "🔍" },
    { id: "backtesting", label: "Backtesting", icon: "📈" },
    { id: "leakage", label: "Leakage Detection", icon: "🔎" },
    { id: "whatsapp", label: "WhatsApp Demo", icon: "💬" },
  ]

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      {/* Header */}
      <div className="app-chrome" style={{
        borderBottom: "1px solid var(--nav-line)",
        padding: "20px 28px",
      }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", display: "flex", alignItems: "center" }}>
          <Link href="/" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none", marginRight: 32 }}>
            <PulseLogo size={40} />
            <span style={{ fontSize: 15, fontWeight: 700, color: "var(--nav-text)", letterSpacing: "0.08em" }}>PULSE</span>
          </Link>

          {/* Breadcrumb */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--text-secondary)" }}>
            <Link href="/" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Dashboard</Link>
            <span>/</span>
            <span style={{ color: "var(--nav-text)", fontWeight: 600 }}>Reports & Intelligence</span>
          </div>
        </div>
      </div>

      {/* Page body */}
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "24px 24px" }}>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: "var(--text-primary)", margin: 0, letterSpacing: "-0.4px" }}>Reports & Intelligence</h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: "4px 0 0" }}>Weekly briefs, outbreak analysis, leakage detection, and historical validation</p>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4, marginBottom: 24, overflowX: "auto", paddingBottom: 2 }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "8px 16px", borderRadius: 8, fontSize: 13, fontWeight: 600,
              cursor: "pointer", border: "none", whiteSpace: "nowrap",
              background: tab === t.id ? "var(--accent)" : "white",
              color: tab === t.id ? "white" : "var(--text-secondary)",
              boxShadow: tab === t.id ? "0 2px 8px rgba(18,181,167,0.32)" : "0 1px 3px rgba(5,22,28,0.06)",
              transition: "all 0.15s",
            }}>
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: (tab === "backtesting" || tab === "leakage" || tab === "whatsapp") ? "1fr" : "280px 1fr", gap: 20 }}>

          {/* Sidebar — only for report types */}
          {(tab === "weekly" || tab === "monthly" || tab === "postincident") && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {(tab === "weekly" || tab === "postincident") && (
                <div className="card" style={{ padding: 16 }}>
                  <div className="section-title">Select District</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {DISTRICTS.map(d => (
                      <button key={d} onClick={() => setSelectedDistrict(d)} style={{
                        padding: "8px 12px", borderRadius: 8, textAlign: "left", fontSize: 13,
                        fontWeight: selectedDistrict === d ? 700 : 400,
                        background: selectedDistrict === d ? "var(--accent-soft)" : "transparent",
                        color: selectedDistrict === d ? "var(--accent-dark)" : "var(--text-secondary)",
                        border: selectedDistrict === d ? "1px solid var(--accent-border)" : "1px solid transparent",
                        cursor: "pointer",
                      }}>
                        {d}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {tab === "monthly" && (
                <div className="card" style={{ padding: 16 }}>
                  <div className="section-title">Select State</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {STATES.map(s => (
                      <button key={s} onClick={() => setSelectedState(s)} style={{
                        padding: "8px 12px", borderRadius: 8, textAlign: "left", fontSize: 13,
                        fontWeight: selectedState === s ? 700 : 400,
                        background: selectedState === s ? "var(--accent-soft)" : "transparent",
                        color: selectedState === s ? "var(--accent-dark)" : "var(--text-secondary)",
                        border: selectedState === s ? "1px solid var(--accent-border)" : "1px solid transparent",
                        cursor: "pointer",
                      }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* About card */}
              <div className="card" style={{ padding: 16 }}>
                <div className="section-title">About this report</div>
                <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
                  {tab === "weekly" && "AI-generated weekly brief covering risk trends, top transfers, and recommended actions for district CMOs."}
                  {tab === "monthly" && "State-level monthly overview aggregating all district signals, leakage incidents, and outcome metrics."}
                  {tab === "postincident" && "Root-cause analysis generated after a supply disruption — what happened, why, and prevention protocol."}
                </div>
              </div>
            </div>
          )}

          {/* Main content */}
          <div>
            {/* Report panels */}
            {(tab === "weekly" || tab === "monthly" || tab === "postincident") && (
              <div className="card" style={{ padding: 24 }}>
                {loading && (
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, padding: 40 }}>
                    <div style={{ width: 36, height: 36, border: "3px solid var(--border)", borderTopColor: "var(--accent)", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                    <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
                      {loading ? "Generating report…" : ""}
                    </div>
                  </div>
                )}

                {!loading && report?.error && (
                  <div style={{ padding: 20, background: "var(--critical-soft)", border: "1px solid var(--critical-border)", borderRadius: 10, color: "#be123c", fontSize: 13, textAlign: "center" }}>
                    Failed to fetch report. Make sure the backend is running.
                  </div>
                )}

                {!loading && report && !report.error && (
                  <div>
                    {/* Report header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, paddingBottom: 16, borderBottom: "1px solid var(--border)" }}>
                      <div>
                        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 4 }}>
                          {tab === "weekly" ? "Weekly Brief" : tab === "monthly" ? "Monthly Overview" : "Post-Incident Analysis"}
                        </div>
                        <div style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>
                          {report.district || report.state || "Report"}
                        </div>
                      </div>
                      <div className="surface-box" style={{ padding: "6px 12px", fontSize: 11, color: "var(--text-secondary)" }}>
                        {report.ai_source === "gemini" ? `Gemini${report.ai_model ? ` · ${report.ai_model}` : ""}` : "Mock fallback — Gemini not live"}
                      </div>
                    </div>

                    {/* Report body — preserve newlines */}
                    <div style={{ fontSize: 13, lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap", fontFamily: "var(--font-geist-sans, system-ui)", maxHeight: 600, overflowY: "auto" }}>
                      {report.report}
                    </div>

                    {/* Monthly extras */}
                    {tab === "monthly" && report.districts_count && (
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
                        <div style={{ background: "var(--accent-soft)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                          <div style={{ fontSize: 24, fontWeight: 800, color: "var(--accent-dark)" }}>{report.districts_count}</div>
                          <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>Districts covered</div>
                        </div>
                        <div style={{ background: "var(--low-soft)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                          <div style={{ fontSize: 24, fontWeight: 800, color: "var(--accent-dark)" }}>{report.phcs_count}</div>
                          <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>PHCs monitored</div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Backtesting */}
            {tab === "backtesting" && <BacktestingPanel />}

            {/* Leakage */}
            {tab === "leakage" && (
              <div className="card" style={{ padding: 24 }}>
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>Medicine Leakage Detection</div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>AI cross-references reported dispensing vs expected consumption by footfall. Flags anomalies for audit.</div>
                </div>
                <LeakagePanel />
              </div>
            )}

            {/* WhatsApp demo */}
            {tab === "whatsapp" && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                <div className="card" style={{ padding: 24 }}>
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>WhatsApp Alert Demo</div>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>Interactive preview of what District CMOs receive. Click Approve to see the flow.</div>
                  </div>
                  <WhatsAppPreview />
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div className="card" style={{ padding: 20 }}>
                    <div className="section-title">Alert Flow</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                      {[
                        { step: "1", title: "Risk Detected", desc: "Sentinel Agent fuses signals — weather, trends, stock levels", color: "#e11d48" },
                        { step: "2", title: "Plan Generated", desc: "Coordinator Agent proposes optimal redistribution plan", color: "#d4a017" },
                        { step: "3", title: "Alert Drafted", desc: "Reporter writes Marathi or Odia CMO copy (Gemini when live)", color: "#12b5a7" },
                        { step: "4", title: "One-Tap Approval", desc: "CMO approves / modifies / escalates — dashboard or WhatsApp", color: "#38bdf8" },
                        { step: "5", title: "Stock Moves", desc: "Approve decrements donor PHC stock and persists in SQLite", color: "#0e9488" },
                      ].map(({ step, title, desc, color }) => (
                        <div key={step} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                          <div style={{ width: 24, height: 24, borderRadius: "50%", background: color, color: "white", fontSize: 11, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>{step}</div>
                          <div>
                            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{title}</div>
                            <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>{desc}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="card" style={{ padding: 20 }}>
                    <div className="section-title">Graduated Autonomy</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {[
                        { range: "< 100 units", mode: "AUTO-EXECUTE", color: "#0e9488", bg: "#e6f7f5", border: "#b6e8e2" },
                        { range: "100–1,000 units", mode: "APPROVE REQUIRED (4h)", color: "#d4a017", bg: "#fbf6e8", border: "#f0dd9a" },
                        { range: "> 1,000 units", mode: "ESCALATE TO STATE", color: "#e11d48", bg: "#fff1f4", border: "#fecdd3" },
                      ].map(({ range, mode, color, bg, border }) => (
                        <div key={range} style={{ background: bg, border: `1px solid ${border}`, borderRadius: 8, padding: "8px 12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>{range}</span>
                          <span style={{ fontSize: 11, color, fontWeight: 700 }}>{mode}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
