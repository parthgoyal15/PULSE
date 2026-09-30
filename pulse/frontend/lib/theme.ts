/** Shared PULSE color system — keep in sync with app/globals.css :root */

export const colors = {
  ink: "#2f7a72",
  inkMid: "#3d8a82",
  accent: "#12b5a7",
  accentDark: "#0e9488",
  accentSoft: "#e6f7f5",
  accentBorder: "#b6e8e2",
  sky: "#38bdf8",
  text: "#0c1f24",
  textSecondary: "#4d636c",
  textMuted: "#7a8f97",
  border: "#d5e3e6",
  surfaceMuted: "#f2f8f9",
  critical: "#e11d48",
  criticalSoft: "#fff1f4",
  criticalBorder: "#fecdd3",
  high: "#f97316",
  highSoft: "#fff4eb",
  highBorder: "#fed7aa",
  medium: "#d4a017",
  mediumSoft: "#fbf6e8",
  mediumBorder: "#f0dd9a",
  low: "#12b5a7",
  lowSoft: "#e6f7f5",
  lowBorder: "#b6e8e2",
} as const

export const RISK_COLORS: Record<string, string> = {
  CRITICAL: colors.critical,
  HIGH: colors.high,
  MEDIUM: colors.medium,
  LOW: colors.low,
}

export const RISK_LEVEL = {
  CRITICAL: {
    color: colors.critical,
    bg: colors.criticalSoft,
    border: colors.criticalBorder,
    label: "Critical Risk",
  },
  HIGH: {
    color: colors.high,
    bg: colors.highSoft,
    border: colors.highBorder,
    label: "High Risk",
  },
  MEDIUM: {
    color: colors.medium,
    bg: colors.mediumSoft,
    border: colors.mediumBorder,
    label: "Medium Risk",
  },
  LOW: {
    color: colors.low,
    bg: colors.lowSoft,
    border: colors.lowBorder,
    label: "Low Risk",
  },
} as const

export function riskColor(score: number): string {
  if (score >= 75) return colors.critical
  if (score >= 50) return colors.high
  if (score >= 25) return colors.medium
  return colors.low
}
