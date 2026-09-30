"use client"

import { useEffect, useRef, useState } from "react"
import type { PHC, District } from "@/lib/types"
import { colors, riskColor } from "@/lib/theme"

export type MapLevel = "national" | "state" | "district"

interface Props {
  level: MapLevel
  phcs?: PHC[]
  districts?: District[]
  states?: any[]
  selectedDistrict?: string
  selectedState?: string
  onStateClick?: (state: string) => void
  onDistrictClick?: (district: string) => void
  onPHCClick?: (phc: PHC) => void
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
}

function mapLabelIcon(L: any, text: string, placement: "below" | "above" = "below") {
  return L.divIcon({
    className: "pulse-map-label-wrap",
    html: `<div class="pulse-map-label pulse-map-label--${placement}">${escapeHtml(text)}</div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  })
}

const LEVEL_CONFIG = {
  national: { center: [22.5, 78.9] as [number, number], zoom: 5 },
  state:    { center: [19.2, 73.8] as [number, number], zoom: 7 },
  district: { center: [18.3, 73.2] as [number, number], zoom: 9 },
}

const STATE_VIEW: Record<string, { center: [number, number]; zoom: number }> = {
  Maharashtra: { center: [19.2, 73.8], zoom: 7 },
  Odisha: { center: [20.5, 85.5], zoom: 7 },
  Rajasthan: { center: [26.4, 73.8], zoom: 6.5 },
}

export default function PHCMap({ level, phcs = [], districts = [], states = [], selectedDistrict, selectedState = "Maharashtra", onStateClick, onDistrictClick, onPHCClick }: Props) {
  const mapRef = useRef<any>(null)
  const layersRef = useRef<any[]>([])
  const containerRef = useRef<HTMLDivElement>(null)
  const prevLevel = useRef<string | null>(null)
  const [mapReady, setMapReady] = useState(false)

  const clearLayers = () => {
    const map = mapRef.current
    layersRef.current.forEach(l => { try { map?.removeLayer(l) } catch {} })
    layersRef.current = []
  }

  const addLayer = (layer: any) => {
    const map = mapRef.current
    if (!map) return layer
    layersRef.current.push(layer)
    layer.addTo(map)
    return layer
  }

  const ensureLabelPane = (map: any) => {
    if (!map?.getPane) return
    let pane = map.getPane("labels")
    if (!pane && map.createPane) pane = map.createPane("labels")
    if (!pane?.style) return
    pane.style.zIndex = "650"
    pane.style.pointerEvents = "none"
  }

  const syncMapSize = (map: any = mapRef.current) => {
    if (!map?.invalidateSize) return
    try { map.invalidateSize({ animate: false }) } catch {}
  }

  // Init map once
  useEffect(() => {
    if (typeof window === "undefined") return
    let cancelled = false
    let created: any = null
    let ro: ResizeObserver | null = null
    const timers: number[] = []
    let onResize: (() => void) | null = null

    const waitForBox = (el: HTMLElement) => new Promise<void>((resolve) => {
      if (el.clientWidth > 0 && el.clientHeight > 0) {
        resolve()
        return
      }
      const wait = new ResizeObserver(() => {
        if (el.clientWidth > 0 && el.clientHeight > 0) {
          wait.disconnect()
          resolve()
        }
      })
      wait.observe(el)
      timers.push(window.setTimeout(() => { wait.disconnect(); resolve() }, 1500))
    })

    import("leaflet").then(async (mod) => {
      const L = (mod as any).default ?? mod
      const el = containerRef.current
      if (cancelled || !el) return
      await waitForBox(el)
      if (cancelled || !containerRef.current) return
      if ((containerRef.current as any)._leaflet_id && !mapRef.current) {
        delete (containerRef.current as any)._leaflet_id
        containerRef.current.innerHTML = ""
      }
      if ((containerRef.current as any)._leaflet_id) {
        if (mapRef.current && !cancelled) setMapReady(true)
        return
      }
      delete (L.Icon.Default.prototype as any)._getIconUrl
      const cfg = LEVEL_CONFIG[level]
      created = L.map(containerRef.current, {
        center: cfg.center,
        zoom: cfg.zoom,
        zoomControl: true,
      })
      mapRef.current = created
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap",
      }).addTo(created)
      const bump = () => { if (!cancelled) syncMapSize(created) }
      onResize = bump
      bump()
      requestAnimationFrame(bump)
      timers.push(window.setTimeout(bump, 80))
      timers.push(window.setTimeout(bump, 300))
      ro = new ResizeObserver(bump)
      ro.observe(containerRef.current)
      window.addEventListener("resize", bump)
      if (!cancelled) setMapReady(true)
    })

    return () => {
      cancelled = true
      timers.forEach(id => window.clearTimeout(id))
      ro?.disconnect()
      if (onResize) window.removeEventListener("resize", onResize)
      setMapReady(false)
      try { created?.remove() } catch {}
      try {
        if (mapRef.current && mapRef.current !== created) mapRef.current.remove()
      } catch {}
      mapRef.current = null
    }
  }, [])

  // Re-draw markers whenever level or data changes
  useEffect(() => {
    if (!mapReady) return
    let cancelled = false
    import("leaflet").then(L => {
      const map = mapRef.current
      if (cancelled || !map) return
      syncMapSize(map)
      ensureLabelPane(map)
      clearLayers()

      const cfg = level === "state" && STATE_VIEW[selectedState]
        ? STATE_VIEW[selectedState]
        : LEVEL_CONFIG[level]
      const viewKey = `${level}:${selectedState}`
      if (prevLevel.current !== viewKey) {
        map.setView(cfg.center, cfg.zoom, { animate: true })
        prevLevel.current = viewKey
      }

      if (level === "national") {
        states.forEach(s => {
          const color = riskColor(s.risk_score)
          const marker = L.circleMarker([s.lat, s.lng], {
            radius: 14, fillColor: color, color: "#fff", weight: 2, opacity: 1, fillOpacity: 0.85,
          })
          marker.bindTooltip(`<strong>${s.name}</strong><br/>Risk: ${s.risk_score}/100 · ${s.risk_level}`, { sticky: true })
          marker.bindPopup(`
            <div style="min-width:220px;font-family:Inter,sans-serif">
              <div style="font-weight:700;font-size:14px;margin-bottom:4px">${s.name}</div>
              <div style="color:${color};font-weight:600;font-size:12px;margin-bottom:8px">${s.risk_level} · ${s.risk_score}/100</div>
              <div style="font-size:11px;color:#475569;line-height:1.5">${s.primary_driver}</div>
              <div style="margin-top:8px;font-size:11px;color:#94a3b8">PHCs: ${s.phc_count.toLocaleString()} · Pop: ${(s.population/1000000).toFixed(1)}M</div>
            </div>
          `)
          if (onStateClick) marker.on("click", () => onStateClick(s.name))
          addLayer(marker)

          // State label
          const label = L.marker([s.lat, s.lng], {
            icon: mapLabelIcon(L, s.name, "below"),
            interactive: false,
            pane: "labels",
            zIndexOffset: 1000,
          })
          addLayer(label)
        })
      }

      if (level === "state") {
        districts.forEach(d => {
          const color = riskColor(d.risk_score)
          const isSelected = d.name === selectedDistrict
          const marker = L.circleMarker([d.lat, d.lng], {
            radius: isSelected ? 18 : 14,
            fillColor: color, color: isSelected ? colors.accentDark : "#fff",
            weight: isSelected ? 3 : 2, opacity: 1, fillOpacity: 0.85,
          })
          marker.bindTooltip(`<strong>${d.name}</strong><br/>Risk: ${d.risk_score}/100`, { sticky: true })
          if (onDistrictClick) marker.on("click", () => onDistrictClick(d.name))

          const label = L.marker([d.lat, d.lng], {
            icon: mapLabelIcon(L, `${d.name}  ${d.risk_score}`, "below"),
            pane: "labels",
            zIndexOffset: 1000,
          })
          if (onDistrictClick) label.on("click", () => onDistrictClick(d.name))
          addLayer(marker)
          addLayer(label)
        })

        // Also show individual PHC dots smaller
        phcs.forEach(p => {
          const color = riskColor(p.district_risk_score || 0)
          const dot = L.circleMarker([p.lat, p.lng], {
            radius: 5, fillColor: color, color: "white", weight: 1.5, fillOpacity: 0.7,
          })
          dot.bindPopup(`
            <div style="min-width:180px;font-family:Inter,sans-serif">
              <div style="font-weight:700;font-size:13px;margin-bottom:4px">${p.name}</div>
              <div style="font-size:11px;color:#64748b;margin-bottom:6px">${p.block} Block · ${p.district}</div>
              <div style="font-size:11px">
                ${Object.entries(p.stock).map(([k,v]) =>
                  `<div style="display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid #f1f5f9">
                    <span style="color:#64748b">${k}</span><strong>${v}</strong>
                  </div>`
                ).join("")}
              </div>
              <div style="margin-top:6px;font-size:11px;color:#94a3b8">
                Beds: ${p.beds.occupied}/${p.beds.total} · Staff: ${p.staff.present}/${p.staff.total}
              </div>
            </div>
          `)
          addLayer(dot)
        })
      }

      if (level === "district") {
        const districtPHCs = selectedDistrict ? phcs.filter(p => p.district === selectedDistrict) : phcs
        if (districtPHCs.length > 0) {
          const bounds = L.latLngBounds(districtPHCs.map(p => [p.lat, p.lng]))
          map.fitBounds(bounds.pad(0.45), { animate: true })
          syncMapSize(map)
        }

        districtPHCs.forEach((p, i) => {
          const lowStock = Object.values(p.stock).some((v: any) => v < 50)
          const color = lowStock ? colors.critical : riskColor(p.district_risk_score || 0)
          const marker = L.circleMarker([p.lat, p.lng], {
            radius: 10, fillColor: color, color: "white", weight: 2.5, fillOpacity: 0.9,
          })

          const stockBars = Object.entries(p.stock).map(([k, v]) => {
            const pct = Math.min(100, Math.round((v as number) / 500 * 100))
            const bc = (v as number) < 50 ? colors.critical : (v as number) < 150 ? colors.medium : colors.low
            return `<div style="margin-bottom:6px">
              <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">
                <span style="color:#475569">${k}</span><span style="font-weight:600;color:${bc}">${v}</span>
              </div>
              <div style="background:#f1f5f9;border-radius:3px;height:5px">
                <div style="width:${pct}%;height:5px;background:${bc};border-radius:3px"></div>
              </div>
            </div>`
          }).join("")

          marker.bindPopup(`
            <div style="min-width:200px;font-family:Inter,sans-serif">
              <div style="font-weight:700;font-size:14px;margin-bottom:2px">${p.name}</div>
              <div style="font-size:11px;color:#64748b;margin-bottom:10px">${p.block} Block</div>
              <div style="font-size:11px;font-weight:700;color:#94a3b8;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.06em">Stock Levels</div>
              ${stockBars}
              <div style="border-top:1px solid #f1f5f9;margin-top:6px;padding-top:6px;display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11px">
                <div><span style="color:#94a3b8">Beds</span><br/><strong>${p.beds.occupied}/${p.beds.total}</strong></div>
                <div><span style="color:#94a3b8">Staff</span><br/><strong>${p.staff.present}/${p.staff.total}</strong></div>
              </div>
            </div>
          `, { maxWidth: 240 })

          if (onPHCClick) marker.on("click", () => onPHCClick(p))

          // PHC name label
          const label = L.marker([p.lat, p.lng], {
            icon: mapLabelIcon(L, p.name.replace("PHC ", ""), i % 2 === 0 ? "below" : "above"),
            interactive: false,
            pane: "labels",
            zIndexOffset: 1000,
          })
          addLayer(marker)
          addLayer(label)
        })
      }
      syncMapSize(map)
      requestAnimationFrame(() => { if (!cancelled) syncMapSize(map) })
    })
    return () => { cancelled = true }
  }, [mapReady, level, phcs, districts, states, selectedDistrict, selectedState])

  return (
    <div style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <style>{`
        .pulse-map-canvas,
        .pulse-map-canvas .leaflet-container {
          width: 100% !important;
          height: 100% !important;
        }
        .leaflet-container { background: #d7e6e8; }
        .pulse-map-label-wrap {
          background: none !important;
          border: none !important;
        }
        .pulse-map-label {
          position: absolute;
          left: 0;
          top: 0;
          background: #2f7a72;
          color: #fff;
          font-size: 12px;
          font-weight: 700;
          line-height: 1.2;
          padding: 4px 8px;
          border-radius: 6px;
          border: 1px solid #fff;
          white-space: nowrap;
          box-shadow: 0 2px 8px rgba(5, 22, 28, 0.35);
          pointer-events: none;
        }
        .pulse-map-label--below {
          transform: translate(-50%, 14px);
        }
        .pulse-map-label--above {
          transform: translate(-50%, calc(-100% - 14px));
        }
      `}</style>
      <div
        ref={containerRef}
        className="pulse-map-canvas"
        style={{ width: "100%", height: "100%", borderRadius: "0 0 12px 12px" }}
      />
    </div>
  )
}
