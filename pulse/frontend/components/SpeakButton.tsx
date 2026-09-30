"use client"

import { useEffect, useRef, useState } from "react"

interface Props {
  text: string
  lang: "en" | "hi"
  size?: number
}

// Chrome loads its voice list asynchronously — the first getVoices() call
// right after page load can return []. Cache the list once it's ready and
// keep it warm across every SpeakButton instance on the page.
let cachedVoices: SpeechSynthesisVoice[] = []
let voicesPrimed = false

function primeVoices(): Promise<SpeechSynthesisVoice[]> {
  if (typeof window === "undefined" || !window.speechSynthesis) return Promise.resolve([])
  const existing = window.speechSynthesis.getVoices()
  if (existing.length > 0) {
    cachedVoices = existing
    return Promise.resolve(existing)
  }
  if (voicesPrimed) return Promise.resolve(cachedVoices)
  voicesPrimed = true
  return new Promise(resolve => {
    const handler = () => {
      cachedVoices = window.speechSynthesis.getVoices()
      window.speechSynthesis.removeEventListener("voiceschanged", handler)
      resolve(cachedVoices)
    }
    window.speechSynthesis.addEventListener("voiceschanged", handler)
    // Some browsers never fire the event if there's truly nothing to load.
    setTimeout(() => resolve(window.speechSynthesis.getVoices()), 800)
  })
}

function findVoice(voices: SpeechSynthesisVoice[], lang: "en" | "hi"): SpeechSynthesisVoice | undefined {
  const target = lang === "hi" ? "hi" : "en"
  const wantedCode = lang === "hi" ? "hi-in" : "en-in"
  const exact = voices.filter(v => v.lang?.toLowerCase() === wantedCode)
  const byPrefix = voices.filter(v => v.lang?.toLowerCase().startsWith(target))
  const byName = voices.filter(v => v.name?.toLowerCase().includes(lang === "hi" ? "hindi" : "english"))
  const pool = exact.length ? exact : byPrefix.length ? byPrefix : byName
  if (pool.length === 0) return undefined
  // Prefer a device-installed (local) voice over a network voice — network
  // voices need connectivity and fail silently (falling back to default
  // English) far more often.
  return pool.find(v => v.localService) || pool[0]
}

const RESET_DELAY_MS = 120

export default function SpeakButton({ text, lang, size = 13 }: Props) {
  const [speaking, setSpeaking] = useState(false)
  const [hindiUnavailable, setHindiUnavailable] = useState(false)
  const primed = useRef(false)
  const requestId = useRef(0)

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis || primed.current) return
    primed.current = true
    primeVoices()
  }, [])

  useEffect(() => {
    return () => {
      if (speaking && typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const speak = async () => {
    if (typeof window === "undefined" || !window.speechSynthesis) return
    const synth = window.speechSynthesis

    if (speaking) {
      synth.cancel()
      setSpeaking(false)
      return
    }
    const clean = (text || "").trim()
    if (!clean) return

    const myRequest = ++requestId.current

    // Always fully stop whatever is queued and give the engine a moment to
    // actually reset — Chrome silently keeps using the *previous* utterance's
    // voice/lang if speak() runs in the same tick (or too soon after) cancel().
    synth.cancel()
    await new Promise(resolve => setTimeout(resolve, RESET_DELAY_MS))
    if (myRequest !== requestId.current) return // superseded by a newer click

    const voices = await primeVoices()
    const match = findVoice(voices, lang)

    if (lang === "hi" && !match) {
      // No Hindi voice pack on this device/browser — reading Devanagari with
      // an English voice comes out as garbled English. Tell the user why
      // instead of silently mispronouncing.
      setHindiUnavailable(true)
      return
    }
    setHindiUnavailable(false)

    const utter = new SpeechSynthesisUtterance(clean)
    utter.lang = match?.lang || (lang === "hi" ? "hi-IN" : "en-IN")
    utter.rate = 0.98
    utter.voice = match ?? null

    utter.onend = () => setSpeaking(false)
    utter.onerror = () => setSpeaking(false)

    // A resume() right before speak() clears a known Chrome bug where the
    // engine gets "stuck" after repeated cancel/speak cycles.
    synth.resume()
    synth.speak(utter)
    setSpeaking(true)
  }

  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <button
        onClick={speak}
        title={
          speaking
            ? "Stop reading"
            : hindiUnavailable
              ? "No Hindi voice installed on this device"
              : lang === "hi" ? "हिंदी में सुनें" : "Read aloud"
        }
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: size + 12, height: size + 12, borderRadius: "50%", flexShrink: 0,
          border: `1px solid ${speaking ? "var(--accent)" : hindiUnavailable ? "var(--high-border)" : "var(--accent-border)"}`,
          background: speaking ? "var(--accent)" : hindiUnavailable ? "var(--high-soft)" : "var(--accent-soft)",
          color: speaking ? "white" : hindiUnavailable ? "var(--high)" : "var(--accent-dark)",
          cursor: "pointer", transition: "all 0.15s", padding: 0,
        }}
      >
        {speaking ? (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 5 6 9H2v6h4l5 4V5z" />
            <path d="M15.5 8.5a5 5 0 0 1 0 7" />
          </svg>
        )}
      </button>
      {hindiUnavailable && (
        <span style={{ fontSize: 10, color: "var(--high)", fontStyle: "italic" }}>
          No Hindi voice on this device
        </span>
      )}
    </span>
  )
}
