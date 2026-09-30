import type { Alert, Transfer } from "@/lib/types"
import type { MapLevel } from "@/components/PHCMap"

export type ScopeGroup<T> = {
  key: string
  title: string
  hint?: string
  items: T[]
}

export function transferTouchesState(t: Transfer, state: string) {
  return t.to_state === state || t.from_state === state
}

export function transferTouchesDistrict(t: Transfer, district: string) {
  return t.to_district === district || t.from_district === district
}

export function alertTouchesState(a: Alert, state: string) {
  return a.state === state
}

export function alertTouchesDistrict(a: Alert, district: string) {
  return a.district === district
}

function uniquePush(order: string[], value?: string | null) {
  if (value && !order.includes(value)) order.push(value)
}

export function groupTransfers(
  transfers: Transfer[],
  level: MapLevel,
  activeState: string,
  selectedDistrict: string | null,
  stateOrder: string[],
): ScopeGroup<Transfer>[] {
  if (level === "national") {
    const groups: ScopeGroup<Transfer>[] = []
    const seen = new Set<string>()
    for (const state of stateOrder) {
      const items = transfers.filter(t => t.to_state === state)
      if (items.length) {
        groups.push({ key: `state-${state}`, title: state, items })
        seen.add(state)
      }
    }
    const extras: string[] = []
    for (const t of transfers) uniquePush(extras, t.to_state)
    for (const state of extras.filter(s => !seen.has(s))) {
      groups.push({
        key: `state-${state}`,
        title: state,
        items: transfers.filter(t => t.to_state === state),
      })
    }
    const unassigned = transfers.filter(t => !t.to_state)
    if (unassigned.length) groups.push({ key: "unassigned", title: "Unassigned", items: unassigned })
    return groups
  }

  const inState = transfers.filter(t => transferTouchesState(t, activeState))
  if (level === "district" && selectedDistrict) {
    const focus = inState.filter(t => transferTouchesDistrict(t, selectedDistrict))
    const rest = inState.filter(t => !transferTouchesDistrict(t, selectedDistrict))
    const groups: ScopeGroup<Transfer>[] = []
    if (focus.length) {
      groups.push({ key: selectedDistrict, title: selectedDistrict, hint: activeState, items: focus })
    }
    if (rest.length) {
      groups.push({ key: `rest-${activeState}`, title: `Rest of ${activeState}`, items: rest })
    }
    return groups
  }

  const dests: string[] = []
  const byDest = new Map<string, Transfer[]>()
  for (const t of inState) {
    const dest = t.to_district || "Other"
    if (!byDest.has(dest)) {
      byDest.set(dest, [])
      dests.push(dest)
    }
    byDest.get(dest)!.push(t)
  }
  return dests.map(d => ({
    key: d,
    title: d,
    hint: activeState,
    items: byDest.get(d)!,
  }))
}

export function groupAlerts(
  alerts: Alert[],
  level: MapLevel,
  activeState: string,
  selectedDistrict: string | null,
  stateOrder: string[],
): ScopeGroup<Alert>[] {
  if (level === "national") {
    const groups: ScopeGroup<Alert>[] = []
    const seen = new Set<string>()
    for (const state of stateOrder) {
      const items = alerts.filter(a => a.state === state)
      if (items.length) {
        groups.push({ key: `state-${state}`, title: state, items })
        seen.add(state)
      }
    }
    const extras: string[] = []
    for (const a of alerts) uniquePush(extras, a.state)
    for (const state of extras.filter(s => !seen.has(s))) {
      groups.push({
        key: `state-${state}`,
        title: state,
        items: alerts.filter(a => a.state === state),
      })
    }
    const network = alerts.filter(a => !a.state)
    if (network.length) groups.push({ key: "network", title: "Network-wide", items: network })
    return groups
  }

  const inState = alerts.filter(a => alertTouchesState(a, activeState))
  const statewide = inState.filter(a => !a.district)
  const withDistrict = inState.filter(a => a.district)

  if (level === "district" && selectedDistrict) {
    const focus = withDistrict.filter(a => alertTouchesDistrict(a, selectedDistrict))
    const rest = withDistrict.filter(a => !alertTouchesDistrict(a, selectedDistrict))
    const groups: ScopeGroup<Alert>[] = []
    if (focus.length) {
      groups.push({ key: selectedDistrict, title: selectedDistrict, hint: activeState, items: focus })
    }
    if (rest.length) {
      groups.push({ key: `rest-${activeState}`, title: `Rest of ${activeState}`, items: rest })
    }
    if (statewide.length) {
      groups.push({ key: `statewide-${activeState}`, title: `${activeState} statewide`, items: statewide })
    }
    return groups
  }

  const dests: string[] = []
  const byDest = new Map<string, Alert[]>()
  for (const a of withDistrict) {
    const dest = a.district as string
    if (!byDest.has(dest)) {
      byDest.set(dest, [])
      dests.push(dest)
    }
    byDest.get(dest)!.push(a)
  }
  const groups: ScopeGroup<Alert>[] = dests.map(d => ({
    key: d,
    title: d,
    hint: activeState,
    items: byDest.get(d)!,
  }))
  if (statewide.length) {
    groups.push({ key: `statewide-${activeState}`, title: `${activeState} statewide`, items: statewide })
  }
  return groups
}

export function countGrouped<T>(groups: ScopeGroup<T>[]) {
  return groups.reduce((n, g) => n + g.items.length, 0)
}
