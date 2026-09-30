import type { ReactNode } from "react"
import type { Impact } from "@/lib/types"

interface Props { impact: Impact }

const stats: { key: keyof Impact; label: string; color: string; tint: string; icon: ReactNode }[] = [
  {
    key: "stockout_days_prevented",
    label: "Stock-out days prevented",
    color: "#0f766e",
    tint: "rgba(15,118,110,0.12)",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
  },
  {
    key: "patients_served",
    label: "Patients served without gap",
    color: "#0369a1",
    tint: "rgba(3,105,161,0.12)",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
    ),
  },
  {
    key: "units_redistributed",
    label: "Units redistributed",
    color: "#6d28d9",
    tint: "rgba(109,40,217,0.12)",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
      </svg>
    ),
  },
  {
    key: "warnings_issued",
    label: "Early warnings issued",
    color: "#c2410c",
    tint: "rgba(194,65,12,0.12)",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
  },
  {
    key: "leakage_flagged",
    label: "Leakage incidents flagged",
    color: "#be123c",
    tint: "rgba(190,18,60,0.12)",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    ),
  },
]

function formatNum(n: number): string {
  if (n >= 100000) return `${(n / 100000).toFixed(1)}L`
  return n.toLocaleString("en-IN")
}

export default function ImpactCounter({ impact }: Props) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.92)",
      border: "1px solid var(--accent-border)",
      borderRadius: 18,
      padding: "14px 6px",
      display: "grid",
      gridTemplateColumns: "repeat(5, 1fr)",
      boxShadow: "var(--shadow)",
    }}>
      {stats.map((stat, i) => {
        const val = impact[stat.key] as number
        return (
          <div
            key={stat.key}
            style={{
              padding: "4px 16px",
              borderLeft: i === 0 ? "none" : "1px solid var(--border)",
              minWidth: 0,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{
                width: 30, height: 30, borderRadius: 9, flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: stat.tint, color: stat.color,
              }}>
                {stat.icon}
              </div>
              <div style={{
                fontSize: 28,
                fontWeight: 800,
                color: stat.color,
                letterSpacing: "-0.04em",
                lineHeight: 1,
                fontVariantNumeric: "tabular-nums",
              }}>
                {formatNum(val)}
              </div>
            </div>
            <div style={{
              fontSize: 13,
              fontWeight: 800,
              color: stat.color,
              marginTop: 8,
              whiteSpace: "nowrap",
              letterSpacing: "-0.01em",
            }}>
              {stat.label}
            </div>
          </div>
        )
      })}
    </div>
  )
}
