import type { AnalysisResult, RankRow } from './types'

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export async function walkCorridor(corridorId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/api/v1/analysis/walk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      corridor_id: corridorId,
      include_dem: true,
      include_spectral: false,
    }),
  })
  if (!response.ok) throw new Error(`walk HTTP ${response.status}`)
  return response.json()
}

export async function runAnalysis(aoi: object, includeDem: boolean): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/api/v1/analysis/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      aoi_geojson: aoi,
      layer_id: 'sentinel-2',
      include_dem: includeDem,
      include_spectral: false,
    }),
  })
  if (!response.ok) throw new Error(`analisi HTTP ${response.status}`)
  return response.json()
}

export async function fetchNetwork(): Promise<{ type: string, features: unknown[] }> {
  const response = await fetch(`${API_BASE}/api/v1/analysis/network`)
  if (!response.ok) throw new Error(`network HTTP ${response.status}`)
  return response.json()
}

export function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function dossierLocal(ranking: RankRow[], name: string) {
  downloadJson(`${name}_dossier.json`, {
    kind: 'operator-dossier',
    project: name,
    export_date: new Date().toISOString(),
    ranking,
    warning: 'Dossier operatore. Coordinate private.',
  })
}

export function blindLocal(blind: AnalysisResult['blind'], name: string) {
  downloadJson(`${name}_blind.json`, { ...blind, project: name, kind: 'blind-pack' })
}
