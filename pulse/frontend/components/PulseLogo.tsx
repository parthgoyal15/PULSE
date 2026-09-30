"use client"

import { useId } from "react"

interface Props {
  size?: number
  className?: string
  round?: boolean
}

export default function PulseLogo({ size = 32, className, round = false }: Props) {
  const uid = useId().replace(/:/g, "")
  const bg = `pulse-bg-${uid}`
  const glow = `pulse-glow-${uid}`
  const radius = round ? 16 : 8

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      aria-hidden
      style={{ display: "block", flexShrink: 0, borderRadius: round ? "50%" : Math.round(size * 0.25) }}
    >
      <defs>
        <linearGradient id={bg} x1="3" y1="1" x2="30" y2="31" gradientUnits="userSpaceOnUse">
          <stop stopColor="#5eead4" />
          <stop offset="0.45" stopColor="#2f7a72" />
          <stop offset="1" stopColor="#1f5c56" />
        </linearGradient>
        <radialGradient id={glow} cx="16" cy="16" r="14" gradientUnits="userSpaceOnUse">
          <stop stopColor="#ffffff" stopOpacity="0.18" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="32" height="32" rx={radius} fill={`url(#${bg})`} />
      <rect width="32" height="32" rx={radius} fill={`url(#${glow})`} />
      <circle cx="16" cy="16" r="11.2" stroke="white" strokeOpacity="0.28" strokeWidth="1.15" />
      <circle cx="16" cy="16" r="7.2" stroke="white" strokeOpacity="0.16" strokeWidth="1" />
      <path
        d="M4.5 17.2 H9.2 L11.1 17.2 L13.15 8.2 L16.05 24.4 L18.7 13.1 L20.35 17.2 H27.5"
        stroke="white"
        strokeWidth="1.85"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="16.05" cy="8.2" r="1.7" fill="#fef08a" />
      <circle cx="16.05" cy="8.2" r="2.8" fill="#fef08a" fillOpacity="0.28" />
    </svg>
  )
}
