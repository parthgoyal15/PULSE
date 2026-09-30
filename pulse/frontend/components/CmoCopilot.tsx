"use client"

import { useEffect, useRef, useState } from "react"
import { api } from "@/lib/api"
import type { CopilotReply } from "@/lib/types"
import SpeakButton from "./SpeakButton"

interface Props {
  state: string
  district?: string | null
  lang?: "en" | "hi"
}

type ChatTurn = { role: "user" | "assistant"; text: string; source?: string | null }

function suggestions(state: string, district?: string | null) {
  const place = district || state
  return [
    `Why is ${place} at risk, and what should I approve first?`,
    district
      ? `If I wait 48 hours on transfers into ${district}, who stocks out?`
      : `Which pending transfer in ${state} should I approve first?`,
    `Draft a 4-line ASHA WhatsApp for ${place} field workers.`,
  ]
}

export default function CmoCopilot({ state, district, lang = "en" }: Props) {
  const [input, setInput] = useState("")
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastMeta, setLastMeta] = useState<Pick<CopilotReply, "ai_source" | "ai_model"> | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setTurns([])
    setLastMeta(null)
    setError(null)
  }, [state, district, lang])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [turns, loading])

  const send = async (question: string) => {
    const q = question.trim()
    if (!q || loading) return
    setInput("")
    setError(null)
    setTurns(prev => [...prev, { role: "user", text: q }])
    setLoading(true)
    try {
      const res = await api.askCopilot(q, { state, district, lang })
      setLastMeta({ ai_source: res.ai_source, ai_model: res.ai_model })
      setTurns(prev => [...prev, { role: "assistant", text: res.answer, source: res.ai_source }])
    } catch (err: any) {
      setError(err?.message || "Copilot unavailable")
    } finally {
      setLoading(false)
    }
  }

  const chips = suggestions(state, district)
  const scope = district ? `${state} · ${district}` : state

  return (
    <div className="card" style={{ padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>CMO Copilot</div>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
            Ask about live risk, transfers, and stock in {scope}. Answers are grounded in current PULSE state.
          </div>
        </div>
        <span style={{
          fontSize: 10, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase",
          padding: "4px 8px", borderRadius: 6, whiteSpace: "nowrap",
          background: lastMeta?.ai_source === "gemini" ? "var(--accent-soft)" : "var(--surface-muted)",
          color: lastMeta?.ai_source === "gemini" ? "var(--accent-dark)" : "var(--text-muted)",
          border: `1px solid ${lastMeta?.ai_source === "gemini" ? "var(--accent-border)" : "var(--border)"}`,
        }}>
          {lastMeta?.ai_source === "gemini"
            ? `Gemini${lastMeta.ai_model ? ` · ${lastMeta.ai_model}` : ""}`
            : "Ask to run"}
        </span>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {chips.map(chip => (
          <button
            key={chip}
            type="button"
            disabled={loading}
            onClick={() => send(chip)}
            style={{
              fontSize: 11, fontWeight: 600, color: "var(--accent-dark)",
              background: "var(--accent-soft)", border: "1px solid var(--accent-border)",
              borderRadius: 999, padding: "5px 10px", cursor: loading ? "default" : "pointer",
            }}
          >
            {chip}
          </button>
        ))}
      </div>

      <div style={{
        minHeight: 120, maxHeight: 220, overflowY: "auto",
        background: "var(--surface-muted)", border: "1px solid var(--border)",
        borderRadius: 10, padding: 12, display: "flex", flexDirection: "column", gap: 10,
      }}>
        {turns.length === 0 && !loading && (
          <div style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
            Tap a question or type your own. Copilot will not invent PHCs or transfer IDs — it only uses the live dashboard data.
          </div>
        )}
        {turns.map((t, i) => (
          <div
            key={`${t.role}-${i}`}
            style={{
              alignSelf: t.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "88%",
              background: t.role === "user" ? "var(--nav-fill)" : "white",
              color: t.role === "user" ? "white" : "var(--text-secondary)",
              border: t.role === "user" ? "none" : "1px solid var(--border)",
              borderRadius: t.role === "user" ? "12px 12px 4px 12px" : "12px 12px 12px 4px",
              padding: "8px 11px",
              fontSize: 12,
              lineHeight: 1.55,
              whiteSpace: "pre-wrap",
            }}
          >
            {t.role === "assistant" ? (
              <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                <span style={{ flex: 1 }}>{t.text}</span>
                <SpeakButton text={t.text} lang={lang} size={11} />
              </div>
            ) : t.text}
          </div>
        ))}
        {loading && (
          <div style={{ fontSize: 12, color: "var(--text-muted)", fontStyle: "italic" }}>
            Reading live scores and stock…
          </div>
        )}
        <div ref={endRef} />
      </div>

      {error && (
        <div style={{ fontSize: 12, color: "var(--critical)" }}>{error}</div>
      )}

      <form
        onSubmit={e => { e.preventDefault(); send(input) }}
        style={{ display: "flex", gap: 8 }}
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={lang === "hi" ? "CMO से कोई सवाल पूछें…" : "Ask as a CMO… e.g. which transfer first?"}
          disabled={loading}
          style={{
            flex: 1, border: "1px solid var(--border)", borderRadius: 10,
            padding: "9px 12px", fontSize: 13, color: "var(--text-primary)",
            background: "white", outline: "none",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn btn-approve"
          style={{ flex: "0 0 auto", minWidth: 84 }}
        >
          {loading ? "…" : "Ask"}
        </button>
      </form>
    </div>
  )
}
