export type PlatoVerdict = 'support' | 'contradict' | 'na'

export interface PlatoTest {
  id: string
  label: string
  verdict: PlatoVerdict
  detail: string
}

export interface RankRow {
  label: string
  rank: number
  lon: number
  lat: number
  residual: number
  hydro_score: number
  spectral_score: number | null
  geometry_score: number | null
  circularity?: number | null
  node_type: string | null
  basin: string | null
  river_id?: string | null
  river_name?: string | null
  source: string
  pro: string[]
  contro: string[]
  kill_shot: string
  plato: PlatoTest[]
}

export interface BlindPack {
  algorithm: string
  hash: string
  timestamp: string
  ranking: Record<string, unknown>[]
  note: string
}

export interface AnalysisResult {
  message: string
  method: string
  corridor_id?: string | null
  candidates: { type: string, features: unknown[] }
  ranking: RankRow[]
  blind: BlindPack
  rivers: { type: string, features: unknown[] }
  stats: Record<string, unknown>
  layers: Record<string, string>
  bbox: number[]
}

export interface Basin {
  id: string
  name: string
  hint: string
  center: [number, number]
  zoom: number
}

export interface FieldNote {
  id: string
  lat: number
  lon: number
  text: string
  at: string
}

export interface ViewTarget {
  center: [number, number]
  zoom: number
}
