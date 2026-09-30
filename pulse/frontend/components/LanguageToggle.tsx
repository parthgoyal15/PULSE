"use client"

interface Props {
  lang: "en" | "hi"
  onChange: (lang: "en" | "hi") => void
}

export default function LanguageToggle({ lang, onChange }: Props) {
  return (
    <div
      title="Content language"
      style={{
        display: "flex", gap: 2, background: "var(--surface-muted)",
        border: "1px solid var(--border)", borderRadius: 999, padding: 2,
      }}
    >
      {(["en", "hi"] as const).map(l => (
        <button
          key={l}
          onClick={() => onChange(l)}
          style={{
            padding: "4px 11px",
            borderRadius: 999,
            border: "none",
            cursor: "pointer",
            fontSize: 11,
            fontWeight: 700,
            background: lang === l ? "var(--nav-fill)" : "transparent",
            color: lang === l ? "white" : "var(--text-secondary)",
            transition: "all 0.15s",
          }}
        >
          {l === "en" ? "EN" : "हिं"}
        </button>
      ))}
    </div>
  )
}
