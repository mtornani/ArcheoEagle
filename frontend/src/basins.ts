import type { Basin } from './types'

export const BASINS: Basin[] = [
  { id: 'tamanrasset', name: 'Tamanrasset', hint: 'Hoggar → Atlantico', center: [21.0, -4.0], zoom: 6 },
  { id: 'megachad', name: 'Mega-Chad', hint: 'sponda AHP', center: [13.8, 14.5], zoom: 6 },
  { id: 'sahabi', name: 'Sahabi', hint: 'radar sotto sabbia', center: [27.2, 19.4], zoom: 6 },
  { id: 'irharhar', name: 'Irharhar', hint: 'Hoggar → Chotts', center: [28.0, 7.2], zoom: 6 },
  { id: 'tilemsi', name: 'Tilemsi', hint: 'verso il Niger', center: [16.6, 0.0], zoom: 6 },
  { id: 'howar', name: 'Wadi Howar', hint: 'Nilo giallo', center: [17.4, 27.0], zoom: 6 },
]

export const TRAPS: Basin[] = [
  { id: 'richat', name: 'Richat', hint: 'trappola — anello fotografabile', center: [21.12, -11.4], zoom: 8 },
]

export const CORRIDOR_FEATURE_IDS: Record<string, string[]> = {
  tamanrasset: ['tamanrasset'],
  megachad: ['mega_chad_shore', 'taffassasset'],
  sahabi: ['sahabi'],
  irharhar: ['irharhar'],
  tilemsi: ['tilemsi'],
  howar: ['wadi_howar'],
}
