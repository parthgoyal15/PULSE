"use client"

import { useState } from "react"
import PulseLogo from "@/components/PulseLogo"

interface Props {
  transfer?: any
}

export default function WhatsAppPreview({ transfer }: Props) {
  const [step, setStep] = useState<"alert" | "approved" | "confirmed">("alert")

  const defaultTransfer = transfer || {
    urgency: "CRITICAL",
    medicine: "ORS",
    quantity: 2400,
    from_district: "Nashik",
    to_district: "Raigad",
    deadline_days: 3,
    estimated_cost_inr: 18400,
    justification: "Dengue surge predicted in 8 days. Raigad stock at 3-day supply.",
    autonomy_level: "ESCALATE",
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.6 }}>
        This is what the District CMO receives on WhatsApp — Marathi for Maharashtra, Odia for Odisha — plus a short English summary. Live Cloud API send if credentials are set; otherwise the backend prints the same copy.
      </div>

      {/* Phone mockup */}
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{
          width: 300,
          background: "#05161c",
          borderRadius: 36,
          padding: "12px 8px",
          boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
          border: "2px solid #1e293b",
        }}>
          {/* Phone top bar */}
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 8 }}>
            <div style={{ width: 60, height: 6, background: "#1e293b", borderRadius: 3 }} />
          </div>

          {/* WhatsApp UI */}
          <div style={{ background: "#111b21", borderRadius: 24, overflow: "hidden", minHeight: 480 }}>
            {/* WA Header */}
            <div style={{ background: "#1f2c34", padding: "12px 14px", display: "flex", alignItems: "center", gap: 10 }}>
              <PulseLogo size={36} round />
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "white" }}>PULSE Alert</div>
                <div style={{ fontSize: 11, color: "#8696a0" }}>Health Intelligence Bot · online</div>
              </div>
            </div>

            {/* Chat background */}
            <div style={{ background: "#0b141a", padding: 12, minHeight: 340, backgroundImage: "radial-gradient(circle at 1px 1px, #1a2430 1px, transparent 0)", backgroundSize: "20px 20px" }}>

              {/* Date chip */}
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <span style={{ background: "#1f2c34", color: "#8696a0", fontSize: 11, padding: "3px 10px", borderRadius: 8 }}>Today</span>
              </div>

              {/* Incoming alert bubble */}
              <div style={{ maxWidth: "88%", background: "#1f2c34", borderRadius: "0 10px 10px 10px", padding: "10px 12px", marginBottom: 8, borderLeft: "3px solid #e11d48" }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#fb7185", marginBottom: 6 }}>PULSE ALERT — {defaultTransfer.to_district}</div>
                <div style={{ fontSize: 12, color: "#e9edef", lineHeight: 1.5, marginBottom: 8, whiteSpace: "pre-wrap" }}>
                  {defaultTransfer.whatsapp_text || (
                    <>
                      <strong>Risk:</strong> {defaultTransfer.urgency} | Surge in {defaultTransfer.deadline_days} days<br/>
                      <strong>Reason:</strong> {defaultTransfer.justification}<br/><br/>
                      <strong>Proposed Transfer:</strong><br/>
                      {defaultTransfer.quantity.toLocaleString()} units {defaultTransfer.medicine}<br/>
                      {defaultTransfer.from_district} → {defaultTransfer.to_district}<br/>
                      Est. cost: ₹{defaultTransfer.estimated_cost_inr.toLocaleString()}
                    </>
                  )}
                </div>
                <div style={{ fontSize: 11, color: "#8696a0", fontStyle: "italic", marginBottom: 8 }}>
                  {defaultTransfer.autonomy_level === "AUTO" ? "Auto-executing in 1h. No action needed." : "Auto-executes in 4h if no response."}
                </div>

                {/* Quick reply buttons */}
                {step === "alert" && (
                  <div style={{ display: "flex", gap: 6, borderTop: "1px solid #2a3942", paddingTop: 8 }}>
                    {["✅ Approve", "✏️ Modify", "⬆️ Escalate"].map((btn, i) => (
                      <button key={btn} onClick={() => i === 0 && setStep("approved")} style={{
                        flex: 1, background: "transparent", border: "1px solid #2a3942",
                        color: "#00a884", fontSize: 10, fontWeight: 600,
                        padding: "5px 2px", borderRadius: 5, cursor: "pointer",
                        transition: "background 0.1s",
                      }}
                        onMouseEnter={e => (e.currentTarget.style.background = "#2a3942")}
                        onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                      >{btn}</button>
                    ))}
                  </div>
                )}

                {step !== "alert" && (
                  <div style={{ background: "#2a3942", borderRadius: 5, padding: "6px 8px", marginTop: 4 }}>
                    <span style={{ fontSize: 11, color: "#00a884" }}>✅ Approve</span>
                    <span style={{ fontSize: 10, color: "#8696a0" }}> · tapped</span>
                  </div>
                )}
                <div style={{ textAlign: "right", fontSize: 10, color: "#8696a0", marginTop: 4 }}>9:32 AM ✓✓</div>
              </div>

              {/* Confirmation message */}
              {(step === "approved" || step === "confirmed") && (
                <div style={{ maxWidth: "88%", background: "#1f2c34", borderRadius: "0 10px 10px 10px", padding: "10px 12px", marginBottom: 8, borderLeft: "3px solid #12b5a7", animation: "fadeIn 0.3s" }}>
                  <div style={{ fontSize: 12, color: "#e9edef", lineHeight: 1.5 }}>
                    ✅ <strong>Transfer approved and logged.</strong><br/>
                    {defaultTransfer.quantity.toLocaleString()} units {defaultTransfer.medicine} will be dispatched from {defaultTransfer.from_district} to {defaultTransfer.to_district} within {defaultTransfer.deadline_days} days.<br/><br/>
                    <span style={{ color: "#8696a0", fontSize: 11 }}>Transfer ID: TXF_001 · Audit logged · District CMO notified</span>
                  </div>
                  <div style={{ textAlign: "right", fontSize: 10, color: "#8696a0", marginTop: 4 }}>9:32 AM ✓✓</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Reset button */}
      {step !== "alert" && (
        <div style={{ textAlign: "center" }}>
          <button onClick={() => setStep("alert")} className="link-accent" style={{ fontSize: 12, fontWeight: 700, textDecoration: "underline" }}>
            Reset demo
          </button>
        </div>
      )}

      {/* Key stats */}
      <div style={{ background: "#f8fafc", borderRadius: 10, padding: 14, border: "1px solid #e2e8f0" }}>
        <div className="section-title">Why WhatsApp</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {[
            ["500M+ users in India", "No app install needed"],
            ["Works on 2G networks", "PHC officers always reachable"],
            ["One-tap approval", "4-hour auto-execute if no response"],
            ["Full audit trail", "Approve / escalate persist in SQLite"],
          ].map(([a, b]) => (
            <div key={a} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, padding: "4px 0", borderBottom: "1px solid #f1f5f9" }}>
              <span style={{ fontWeight: 600, color: "#374151" }}>{a}</span>
              <span style={{ color: "#64748b" }}>{b}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
