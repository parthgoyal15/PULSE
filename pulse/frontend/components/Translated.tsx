"use client"

import { useEffect, useState, type CSSProperties } from "react"
import { api } from "@/lib/api"
import SpeakButton from "./SpeakButton"

// Module-level cache — shared across every Translated instance so the 15s
// dashboard poll doesn't re-translate identical text over and over.
const cache = new Map<string, string>()

interface Props {
  text: string
  lang: "en" | "hi"
  style?: CSSProperties
  withSpeak?: boolean
  speakSize?: number
  as?: "p" | "span" | "div"
}

export default function Translated({ text, lang, style, withSpeak = true, speakSize, as = "p" }: Props) {
  const [display, setDisplay] = useState(text)
  const [note, setNote] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!text) { setDisplay(""); setNote(null); return }
    if (lang === "en") { setDisplay(text); setNote(null); return }

    const key = `hi::${text}`
    const cached = cache.get(key)
    if (cached) { setDisplay(cached); setNote(null); return }

    let cancelled = false
    setLoading(true)
    api.translate(text, "hi")
      .then(res => {
        if (cancelled) return
        const translated = res?.translated || text
        cache.set(key, translated)
        setDisplay(translated)
        setNote(res?.ai_source === "mock" ? "Hindi unavailable — showing English" : null)
      })
      .catch(() => {
        if (cancelled) return
        setDisplay(text)
        setNote("Hindi unavailable — showing English")
      })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [text, lang])

  const Tag = as
  if (!text) return null

  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
      <Tag style={{ flex: 1, margin: 0, opacity: loading ? 0.55 : 1, transition: "opacity 0.15s", ...style }}>
        {display}
        {note && (
          <span style={{ display: "block", fontSize: 10, color: "var(--text-muted)", marginTop: 3, fontStyle: "italic" }}>
            {note}
          </span>
        )}
      </Tag>
      {withSpeak && <SpeakButton text={display} lang={lang} size={speakSize} />}
    </div>
  )
}
