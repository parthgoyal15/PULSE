import type { Alert } from "@/lib/types"
import { RISK_COLORS, colors } from "@/lib/theme"
import Translated from "./Translated"

interface Props { alerts: Alert[]; emptyHint?: string; lang?: "en" | "hi" }

const typeLabel: Record<string, { label: string; color: string; bg: string }> = {
  sentinel:    { label: "Sentinel", color: colors.high, bg: colors.highSoft },
  coordinator: { label: "Coordinator", color: colors.accentDark, bg: colors.accentSoft },
  pipeline:    { label: "Pipeline", color: colors.accentDark, bg: colors.accentSoft },
  approve:     { label: "Approved", color: "#0f766e", bg: colors.lowSoft },
  escalate:    { label: "Escalated", color: "#c2410c", bg: colors.highSoft },
  modify:      { label: "Modified", color: colors.textSecondary, bg: colors.surfaceMuted },
  leakage:     { label: "Leakage", color: "#be123c", bg: colors.criticalSoft },
  default:     { label: "System", color: colors.textSecondary, bg: colors.surfaceMuted },
}

function timeAgo(iso: string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

export default function AlertFeed({ alerts, emptyHint, lang = "en" }: Props) {
  if (alerts.length === 0) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 200, color: "var(--text-muted)" }}>
        <div style={{ fontSize: 32, marginBottom: 10 }}>🔔</div>
        <p style={{ fontSize: 13, margin: 0 }}>No alerts in this view</p>
        <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0 0", opacity: 0.7 }}>{emptyHint || "Run the pipeline to generate alerts"}</p>
      </div>
    )
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 460, overflowY: "auto" }}>
      {[...alerts].reverse().map((alert, i) => {
        const t = typeLabel[alert.type] || typeLabel.default
        return (
          <div key={i} style={{
            background: "white",
            border: "1px solid var(--border)",
            borderRadius: 12,
            padding: "10px 12px",
            display: "flex",
            gap: 10,
          }}>
            {/* Type pill */}
            <div style={{ paddingTop: 1 }}>
              <span style={{ fontSize: 10, fontWeight: 700, background: t.bg, color: t.color, padding: "2px 7px", borderRadius: 4 }}>
                {t.label}
              </span>
            </div>

            {/* Content */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3 }}>
                {alert.district && (
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>{alert.district}</span>
                )}
                {alert.risk_level && (
                  <span style={{ display: "flex", alignItems: "center", gap: 3 }}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: RISK_COLORS[alert.risk_level] || colors.textMuted, display: "inline-block" }} />
                    <span style={{ fontSize: 11, fontWeight: 600, color: RISK_COLORS[alert.risk_level] || colors.textMuted }}>{alert.risk_level}</span>
                  </span>
                )}
              </div>
              <Translated
                text={alert.message}
                lang={lang}
                speakSize={11}
                style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 }}
              />
            </div>

            {/* Time */}
            <div style={{ fontSize: 11, color: "var(--text-muted)", whiteSpace: "nowrap", paddingTop: 2 }}>
              {timeAgo(alert.timestamp)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
