"use client"

import { useState, useEffect, useCallback, type ReactNode } from "react"
import dynamic from "next/dynamic"
import Link from "next/link"
import { api } from "@/lib/api"
import type { PHC, District, RiskAssessment, Transfer, Alert, Impact, PulseStatus } from "@/lib/types"
import type { MapLevel } from "@/components/PHCMap"
import RiskPanel from "@/components/RiskPanel"
import AlertFeed from "@/components/AlertFeed"
import TransferCard from "@/components/TransferCard"
import ImpactCounter from "@/components/ImpactCounter"
import PulseLogo from "@/components/PulseLogo"
import { groupTransfers, groupAlerts, countGrouped } from "@/lib/scope"
import { RISK_COLORS, colors } from "@/lib/theme"
import LanguageToggle from "@/components/LanguageToggle"
import CmoCopilot from "@/components/CmoCopilot"

const PHCMap = dynamic(() => import("@/components/PHCMap"), { ssr: false })

const EMPTY_IMPACT: Impact = {
  stockout_days_prevented: 0, patients_served: 0,
  units_redistributed: 0, warnings_issued: 0, leakage_flagged: 0,
}

const RISK_LEGEND = [
  [colors.low, "Low"],
  [colors.medium, "Medium"],
  [colors.high, "High"],
  [colors.critical, "Critical"],
] as const

const LEVEL_LABELS: Record<MapLevel, { title: string; subtitle: string }> = {
  national: { title: "National View", subtitle: "India · All States" },
  state:    { title: "State View",    subtitle: "Maharashtra · All Districts" },
  district: { title: "District View", subtitle: "Select a district from state view" },
}

export default function Dashboard() {
  const [level, setLevel] = useState<MapLevel>("state")
  const [phcs, setPHCs] = useState<PHC[]>([])
  const [districts, setDistricts] = useState<District[]>([])
  const [states, setStates] = useState<any[]>([])
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null)
  const [selectedRisk, setSelectedRisk] = useState<RiskAssessment | null>(null)
  const [selectedState, setSelectedState] = useState<any | null>(null)
  const [activeState, setActiveState] = useState("Maharashtra")
  const [pulseStatus, setPulseStatus] = useState<PulseStatus | null>(null)
  const [transfers, setTransfers] = useState<Transfer[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [impact, setImpact] = useState<Impact>(EMPTY_IMPACT)
  const [loading, setLoading] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [statusText, setStatusText] = useState("Ready")
  const [activeTab, setActiveTab] = useState<"risk" | "transfers" | "alerts">("risk")
  const [contentLang, setContentLang] = useState<"en" | "hi">("en")

  const fetchAll = useCallback(async () => {
    try {
      const [phcData, districtData, stateData, transferData, alertData, impactData, statusData] = await Promise.all([
        api.getPHCs(undefined, activeState),
        api.getDistricts(activeState),
        api.getStates(),
        api.getTransfers(),
        api.getAlerts(),
        api.getImpact(),
        api.getStatus(),
      ])
      setPHCs(phcData)
      setDistricts(districtData)
      setStates(stateData)
      setTransfers(transferData.transfers || [])
      setAlerts(alertData.alerts || [])
      setImpact(impactData)
      setPulseStatus(statusData)
    } catch { }
  }, [activeState])

  useEffect(() => { fetchAll(); const t = setInterval(fetchAll, 15000); return () => clearInterval(t) }, [fetchAll])

  const handleDistrictClick = async (district: string) => {
    setSelectedDistrict(district)
    setLevel("district")
    setActiveTab("risk")
    const known = districts.find(d => d.name === district)
    if (known?.state) setActiveState(known.state)
    try {
      const risk = await api.getDistrictRisk(district)
      setSelectedRisk(risk)
      if (risk?.state) setActiveState(risk.state)
    } catch { }
  }

  const handleStateClick = (stateName: string) => {
    const s = states.find(st => st.name === stateName)
    setSelectedState(s || null)
    setActiveState(stateName)
    if (s?.operational) {
      setLevel("state")
      setSelectedDistrict(null)
      setSelectedRisk(null)
    }
  }

  const runPipeline = async () => {
    setLoading(true); setStatusText("Running Sentinel + Coordinator…")
    try {
      await api.runAll(false, activeState)
      await fetchAll()
      if (selectedDistrict) { const r = await api.getDistrictRisk(selectedDistrict); setSelectedRisk(r) }
      setStatusText("Pipeline complete")
    } catch (err: any) {
      setStatusText(err?.message || "Backend unreachable")
    }
    finally { setLoading(false) }
  }

  const simulateOutbreak = async () => {
    setSimulating(true); setStatusText(`Injecting ${activeState} outbreak…`)
    try {
      const result = await api.simulateOutbreak(activeState)
      if (result.state) setActiveState(result.state)
      await fetchAll()
      if (result.affected_district) await handleDistrictClick(result.affected_district)
      setStatusText(`${result.affected_district || activeState} critical — outbreak simulated`)
    } catch (err: any) {
      setStatusText(err?.message || "Backend unreachable")
    }
    finally { setSimulating(false) }
  }

  const approveTransfer = async (id: string) => {
    try {
      await api.approveTransfer(id)
      await fetchAll()
      setStatusText("Transfer approved — stock moved")
    } catch (err: any) {
      setStatusText(err?.message || "Approve failed")
    }
  }

  const escalateTransfer = async (id: string) => {
    try {
      await api.escalateTransfer(id)
      await fetchAll()
      setStatusText("Transfer escalated")
    } catch (err: any) {
      setStatusText(err?.message || "Escalate failed")
    }
  }

  const modifyTransfer = async (id: string) => {
    const current = transfers.find(t => t.id === id)
    const raw = window.prompt("New quantity", String(current?.quantity ?? 500))
    if (!raw) return
    const qty = parseInt(raw, 10)
    if (!Number.isFinite(qty) || qty <= 0) return
    try {
      await api.modifyTransfer(id, qty, "CMO modified from dashboard")
      await fetchAll()
      setStatusText(`Quantity set to ${qty}`)
    } catch (err: any) {
      setStatusText(err?.message || "Modify failed")
    }
  }

  const criticalDistricts = districts.filter(d => d.risk_score >= 75)
  const mapSubtitle = level === "national"
    ? `India · 12 states (${(pulseStatus?.operational_states || ["Maharashtra", "Odisha", "Rajasthan"]).join(", ")} operational)`
    : level === "state"
    ? `${activeState} · Districts`
    : selectedDistrict || activeState

  const stateOrder = pulseStatus?.operational_states?.length
    ? pulseStatus.operational_states
    : ["Maharashtra", "Odisha", "Rajasthan"]
  const transferGroups = groupTransfers(transfers, level, activeState, selectedDistrict, stateOrder)
  const alertGroups = groupAlerts(alerts, level, activeState, selectedDistrict, stateOrder)
  const transferCount = countGrouped(transferGroups)
  const alertCount = countGrouped(alertGroups)
  const scopeLabel = level === "national"
    ? "All operational states"
    : level === "district" && selectedDistrict
      ? `${activeState} · ${selectedDistrict}`
      : activeState

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── Header ── */}
      <header className="app-chrome" style={{
        borderBottom: "1px solid var(--nav-line)",
        padding: "20px 28px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          {/* Brand */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <PulseLogo size={44} />
            <div>
              <div style={{ fontSize: 20, fontWeight: 800, color: "var(--nav-text)", letterSpacing: "0.14em" }}>PULSE</div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 500 }}>Health surge intelligence</div>
            </div>
          </div>

          {/* Level switcher */}
          <div style={{
            display: "flex", gap: 4, background: "#ffffff",
            padding: 5, borderRadius: 14, border: "1.5px solid var(--accent-border)",
          }}>
            {(["national", "state", "district"] as MapLevel[]).map(l => (
              <button key={l} onClick={() => setLevel(l)} style={{
                padding: "8px 16px", borderRadius: 10, cursor: "pointer",
                fontSize: 13, fontWeight: 700, transition: "all 0.15s",
                background: level === l ? "var(--nav-fill)" : "transparent",
                color: level === l ? "#ffffff" : "var(--text-secondary)",
                border: level === l ? "1.5px solid var(--nav-fill)" : "1.5px solid transparent",
                boxShadow: level === l ? "0 4px 12px rgba(47,122,114,0.2)" : "none",
                textTransform: "capitalize",
              }}>{l}</button>
            ))}
          </div>

          {/* Breadcrumb */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>
            <span>India</span>
            {(level === "state" || level === "district") && <><span style={{ color: "var(--text-muted)" }}>/</span><span style={{ color: "var(--nav-text)" }}>{activeState}</span></>}
            {level === "district" && selectedDistrict && <><span style={{ color: "var(--text-muted)" }}>/</span><span style={{ color: "var(--nav-text)" }}>{selectedDistrict}</span></>}
          </div>

          {/* Critical alerts */}
          {criticalDistricts.map(d => (
            <button key={d.name} onClick={() => handleDistrictClick(d.name)} style={{
              display: "flex", alignItems: "center", gap: 6,
              background: "var(--critical-soft)", border: "1.5px solid var(--critical-border)",
              color: "#be123c", fontSize: 12, fontWeight: 700,
              padding: "8px 12px", borderRadius: 999, cursor: "pointer",
            }}>
              <span className="pulse-dot critical" />
              {d.name} {d.risk_score}
            </button>
          ))}
        </div>

        {/* Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Link href="/reports" className="nav-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            Reports
          </Link>
          <div className="nav-btn" style={{ cursor: "default" }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: loading || simulating ? colors.sky : colors.accent, boxShadow: `0 0 0 3px ${loading || simulating ? "rgba(56,189,248,0.22)" : "rgba(18,181,167,0.25)"}` }} />
            {statusText}
          </div>
          <button className="nav-btn nav-btn-light" onClick={runPipeline} disabled={loading}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            {loading ? "Running…" : "Run Pipeline"}
          </button>
          <button className="nav-btn nav-btn-danger" onClick={simulateOutbreak} disabled={simulating}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            {simulating ? "Simulating…" : "Simulate Outbreak"}
          </button>
        </div>
      </header>

      {pulseStatus && (
        <div className={pulseStatus.gemini_live ? "banner-live" : "banner-mock"} style={{
          padding: "9px 24px", fontSize: 12,
          display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap",
        }}>
          <span>
            {pulseStatus.gemini_live
              ? "Google AI live — Sentinel, Coordinator, Copilot, and delay analysis are Gemini. Scores are labelled on the risk panel."
              : pulseStatus.quota_blocked
                ? "Gemini free-tier quota is used up. Sentinel and Coordinator continue on labelled mock scores. Quota often resets tomorrow."
                : "Google AI is offline. Add GEMINI_API_KEY in pulse/backend/.env. Every score is labelled MOCK until then."}
          </span>
          <span style={{ opacity: 0.85 }}>
            Persistence: {pulseStatus.persistence}
            {" · "}WhatsApp: {pulseStatus.whatsapp_live ? "Cloud API" : "console demo"}
            {" · "}Live states: {(pulseStatus.operational_states || []).join(", ")}
          </span>
        </div>
      )}

      <main style={{ flex: 1, padding: "22px 22px 28px", maxWidth: 1640, width: "100%", margin: "0 auto", display: "flex", flexDirection: "column", gap: 16 }}>

        {/* KPI row */}
        <ImpactCounter impact={impact} />

        {/* Map + right panel */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 16 }}>

          {/* Map card */}
          <div className="card" style={{ display: "flex", flexDirection: "column", overflow: "hidden", height: 520 }}>
            {/* Map header */}
            <div className="card-head" style={{ justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{LEVEL_LABELS[level].title}</span>
                <span className="chip">{mapSubtitle}</span>
                {level === "district" && selectedDistrict && (
                  <button onClick={() => setLevel("state")} className="link-accent" style={{ fontSize: 11, fontWeight: 700 }}>
                    ← Back to State
                  </button>
                )}
              </div>
              <div style={{ display: "flex", gap: 12 }}>
                {RISK_LEGEND.map(([c, l]) => (
                  <span key={l} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "var(--text-secondary)" }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: c, display: "inline-block" }} />{l}
                  </span>
                ))}
              </div>
            </div>
            <div style={{ flex: 1, minHeight: 0, position: "relative" }}>
              <PHCMap
                level={level}
                phcs={phcs}
                districts={districts}
                states={states}
                selectedDistrict={selectedDistrict || undefined}
                selectedState={activeState}
                onStateClick={handleStateClick}
                onDistrictClick={handleDistrictClick}
              />
            </div>
          </div>

          {/* Right panel */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div className="tab-bar" style={{ flex: 1 }}>
                {(["risk", "transfers", "alerts"] as const).map(tab => (
                  <button key={tab} className={`tab ${activeTab === tab ? "active" : ""}`} onClick={() => setActiveTab(tab)}>
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    {tab === "transfers" && transferCount > 0 && (
                      <span style={{ marginLeft: 4, background: colors.accent, color: "white", fontSize: 10, fontWeight: 700, padding: "1px 5px", borderRadius: 10 }}>{transferCount}</span>
                    )}
                    {tab === "alerts" && alertCount > 0 && (
                      <span style={{ marginLeft: 4, background: colors.critical, color: "white", fontSize: 10, fontWeight: 700, padding: "1px 5px", borderRadius: 10 }}>{alertCount}</span>
                    )}
                  </button>
                ))}
              </div>
              <LanguageToggle lang={contentLang} onChange={setContentLang} />
            </div>

            <div className="card" style={{ flex: 1, padding: 16, overflowY: "auto", minHeight: 440 }}>
              {activeTab === "risk" && (
                level === "national" && selectedState
                  ? <NationalStatePanel state={selectedState} />
                  : selectedRisk
                  ? <RiskPanel risk={selectedRisk} lang={contentLang} />
                  : <EmptyPanel level={level} />
              )}
              {activeTab === "transfers" && (
                <div>
                  <div className="section-title">Transfers · {scopeLabel}</div>
                  {transferGroups.length === 0
                    ? <EmptyTransfers scope={scopeLabel} />
                    : transferGroups.map(group => (
                        <ScopeSection key={group.key} title={group.title} hint={group.hint} count={group.items.length}>
                          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                            {group.items.map(t => (
                              <TransferCard
                                key={t.id}
                                transfer={t}
                                lang={contentLang}
                                onApprove={approveTransfer}
                                onEscalate={escalateTransfer}
                                onModify={modifyTransfer}
                              />
                            ))}
                          </div>
                        </ScopeSection>
                      ))
                  }
                </div>
              )}
              {activeTab === "alerts" && (
                <div>
                  <div className="section-title">Alerts · {scopeLabel}</div>
                  {alertGroups.length === 0
                    ? <AlertFeed alerts={[]} emptyHint={`No alerts for ${scopeLabel}. Run Pipeline or Simulate Outbreak.`} />
                    : alertGroups.map(group => (
                        <ScopeSection key={group.key} title={group.title} hint={group.hint} count={group.items.length}>
                          <AlertFeed alerts={group.items} lang={contentLang} />
                        </ScopeSection>
                      ))
                  }
                </div>
              )}
            </div>
          </div>
        </div>

        <CmoCopilot state={activeState} district={selectedDistrict} lang={contentLang} />

        {/* Context-aware table */}
        {level === "national" && states.length > 0 && <StatesTable states={states} onStateClick={handleStateClick} />}
        {(level === "state" || level === "district") && districts.length > 0 && (
          <DistrictsTable stateName={activeState} districts={districts} onDistrictClick={handleDistrictClick} />
        )}
      </main>

      {/* Footer */}
      <footer className="app-chrome" style={{
        borderTop: "1px solid var(--nav-line)",
        padding: "12px 24px", display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>PULSE · Predictive Unified Health Surge Engine · India PHC Network</span>
        <div style={{ display: "flex", gap: 16 }}>
          {["Sentinel","Coordinator","Reporter","Copilot"].map(a => (
            <span key={a} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--text-secondary)" }}>
              <span style={{ width: 6, height: 6, background: pulseStatus?.gemini_live ? colors.accent : colors.medium, borderRadius: "50%", display: "inline-block" }} />{a}
            </span>
          ))}
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
            {pulseStatus?.gemini_live
              ? "Gemini live"
              : pulseStatus?.quota_blocked
                ? "Gemini quota exceeded (mock labelled)"
                : "Gemini offline (mock labelled)"}
          </span>
        </div>
      </footer>
    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function EmptyPanel({ level }: { level: MapLevel }) {
  const msg = level === "national"
    ? { icon: "🗺️", title: "Click a state", sub: "Select any state on the national map" }
    : level === "district"
    ? { icon: "🏥", title: "Select a district", sub: "Switch to State view and click a district" }
    : { icon: "🗺️", title: "Select a district", sub: "Click on the map or run the pipeline first" }
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 280, color: "var(--text-muted)", textAlign: "center" }}>
      <div style={{ fontSize: 40, marginBottom: 12 }}>{msg.icon}</div>
      <p style={{ fontSize: 14, fontWeight: 600, color: "var(--text-secondary)", margin: 0 }}>{msg.title}</p>
      <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0 0" }}>{msg.sub}</p>
    </div>
  )
}

function EmptyTransfers({ scope }: { scope: string }) {
  return (
    <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-muted)" }}>
      <div style={{ fontSize: 32, marginBottom: 8 }}>📦</div>
      <p style={{ fontSize: 13, margin: 0, fontWeight: 500 }}>No transfers for {scope}</p>
      <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0 0", opacity: 0.7 }}>Run pipeline or simulate outbreak in this view</p>
    </div>
  )
}

function ScopeSection({ title, hint, count, children }: { title: string; hint?: string; count: number; children: ReactNode }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 8, marginBottom: 8,
        paddingBottom: 6, borderBottom: "1px solid var(--border)",
      }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>{title}</span>
        {hint && <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{hint}</span>}
        <span style={{
          marginLeft: "auto", fontSize: 10, fontWeight: 700, color: "var(--text-secondary)",
          background: "var(--surface-muted)", padding: "1px 7px", borderRadius: 10,
        }}>{count}</span>
      </div>
      {children}
    </div>
  )
}

function NationalStatePanel({ state }: { state: any }) {
  const color = RISK_COLORS[state.risk_level as string] || colors.low
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>{state.name}</div>
        <span className={`badge badge-${state.risk_level?.toLowerCase()}`}>{state.risk_level}</span>
      </div>
      <div className="surface-box" style={{ padding: "12px 14px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color }}>Risk Score</span>
          <span style={{ fontSize: 28, fontWeight: 800, color, letterSpacing: "-1px" }}>{state.risk_score}<span style={{ fontSize: 14, color: "var(--text-muted)", fontWeight: 500 }}>/100</span></span>
        </div>
        <div className="risk-bar"><div className="risk-bar-fill" style={{ width: `${state.risk_score}%`, background: color }} /></div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <div className="surface-box" style={{ padding: "10px 12px" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>PHC Network</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>{state.phc_count?.toLocaleString()}</div>
        </div>
        <div className="surface-box" style={{ padding: "10px 12px" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Population</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>{state.population ? (state.population / 1000000).toFixed(1) + "M" : "—"}</div>
        </div>
      </div>
      <div className="surface-box" style={{ padding: "10px 12px" }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 5 }}>Primary Signal</div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0, lineHeight: 1.5 }}>{state.primary_driver}</p>
      </div>
      {state.operational && (
        <div style={{ background: "var(--accent-soft)", borderRadius: 8, padding: "10px 12px", border: "1px solid var(--accent-border)", fontSize: 12, color: "var(--accent-dark)" }}>
          Operational state — open State view to drill into {state.name} districts (shared Sentinel/Coordinator model).
        </div>
      )}
      {!state.operational && (
        <div className="surface-box" style={{ padding: "10px 12px", fontSize: 12, color: "var(--text-secondary)" }}>
          Live pipeline currently runs for operational states (Maharashtra, Odisha, Rajasthan). Click one of those markers, then open State view.
        </div>
      )}
    </div>
  )
}

function StatesTable({ states, onStateClick }: { states: any[], onStateClick: (s: string) => void }) {
  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div className="card-head">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>
        <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>State Risk Overview — India</span>
        <span className="chip">{states.length} states monitored</span>
      </div>
      <table>
        <thead><tr><th>State</th><th>Risk Score</th><th>Level</th><th>PHCs</th><th>Population</th><th>Primary Signal</th><th></th></tr></thead>
        <tbody>
          {[...states].sort((a,b) => b.risk_score - a.risk_score).map(s => (
            <tr key={s.name} onClick={() => onStateClick(s.name)}>
              <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{s.name}</td>
              <td>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ width: 80, background: "var(--surface-muted)", borderRadius: 3, height: 6 }}>
                    <div style={{ width: `${s.risk_score}%`, height: 6, borderRadius: 3, background: RISK_COLORS[s.risk_level] || colors.low, transition: "width 0.8s" }} />
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", fontVariantNumeric: "tabular-nums" }}>{s.risk_score}</span>
                </div>
              </td>
              <td><span className={`badge badge-${s.risk_level?.toLowerCase()}`}>{s.risk_level}</span></td>
              <td>{s.phc_count?.toLocaleString()}</td>
              <td>{s.population ? (s.population/1000000).toFixed(1)+"M" : "—"}</td>
              <td style={{ color: "var(--text-muted)", fontSize: 12, maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.primary_driver}</td>
              <td><span style={{ fontSize: 12, color: "var(--accent-dark)", fontWeight: 700 }}>View →</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function DistrictsTable({ stateName, districts, onDistrictClick }: { stateName: string, districts: District[], onDistrictClick: (d: string) => void }) {
  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div className="card-head">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>
        <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>District Overview — {stateName}</span>
      </div>
      <table>
        <thead><tr><th>District</th><th>Risk Score</th><th>Level</th><th>Days to Surge</th><th>Primary Signal</th><th></th></tr></thead>
        <tbody>
          {[...districts].sort((a,b) => b.risk_score - a.risk_score).map(d => (
            <tr key={d.name} onClick={() => onDistrictClick(d.name)}>
              <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{d.name}</td>
              <td>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ width: 80, background: "var(--surface-muted)", borderRadius: 3, height: 6 }}>
                    <div style={{ width: `${d.risk_score}%`, height: 6, borderRadius: 3, background: RISK_COLORS[d.risk_level] || colors.low, transition: "width 0.8s" }} />
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)" }}>{d.risk_score}</span>
                </div>
              </td>
              <td><span className={`badge badge-${d.risk_level.toLowerCase()}`}>{d.risk_level}</span></td>
              <td>{d.days_to_surge || "—"}</td>
              <td style={{ color: "var(--text-muted)", fontSize: 12, maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.primary_driver || "—"}</td>
              <td><span style={{ fontSize: 12, color: "var(--accent-dark)", fontWeight: 700 }}>View →</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
