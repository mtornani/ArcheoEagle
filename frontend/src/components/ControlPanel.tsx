/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from 'react'
import {
  ChevronDown, EyeOff, Hash, Download, BookOpen,
  Columns3, Footprints, RotateCcw, Loader2,
} from 'lucide-react'
import { BASINS, TRAPS } from '../basins'
import { walkCorridor, runAnalysis, dossierLocal, blindLocal } from '../api'
import { BRIEFS, METHOD, nextQuestions, plainSpeak, walkSummary } from '../investigate'
import type { AnalysisResult, PlatoVerdict, RankRow, ViewTarget } from '../types'

interface Props {
  closePanel: () => void
  aoi: any
  result: AnalysisResult | null
  setResult: (r: AnalysisResult | null) => void
  onLayersData: (layers: Record<string, string>, bbox: number[]) => void
  onFly: (t: ViewTarget) => void
  selectedLabel: string | null
  onSelect: (label: string) => void
  blindMode: boolean
  fieldMode: boolean
  allowDraw: boolean
  setAllowDraw: (v: boolean) => void
  walkingId: string | null
  setWalkingId: (id: string | null) => void
}

const VERDICT_IT: Record<PlatoVerdict, string> = {
  support: '+',
  contradict: '−',
  na: 'N/A',
}

const NODE_IT: Record<string, string> = {
  confluence: 'confluenza',
  paleolake_shore: 'sponda paleolago',
  channel: 'alveo',
  head_or_mouth: 'testa o foce',
}

export default function ControlPanel({
  closePanel, aoi, result, setResult, onLayersData,
  onFly, selectedLabel, onSelect, blindMode, fieldMode,
  allowDraw, setAllowDraw, walkingId, setWalkingId,
}: Props) {
  const [error, setError] = useState('')
  const [tab, setTab] = useState<'tappa' | 'confronta' | 'capire'>('tappa')
  const ranking = result?.ranking ?? []
  const selected = ranking.find((r) => r.label === selectedLabel) || ranking[0]
  const corridor = BASINS.find((b) => b.id === result?.corridor_id)
  const tap = fieldMode ? 'min-h-12' : ''

  const apply = (data: AnalysisResult) => {
    setResult(data)
    if (data.layers && data.bbox) onLayersData(data.layers, data.bbox)
    if (data.ranking[0]) onSelect(data.ranking[0].label)
    try { localStorage.setItem('archeoeagle.last', JSON.stringify(data)) } catch { /* quota */ }
  }

  const walk = async (id: string) => {
    const basin = BASINS.find((b) => b.id === id) || TRAPS.find((b) => b.id === id)
    if (basin) onFly({ center: basin.center, zoom: basin.zoom })
    setWalkingId(id)
    setError('')
    setTab('tappa')
    try {
      apply(await walkCorridor(id))
    } catch (e) {
      console.error(e)
      setError('Backend non raggiungibile sulla porta 8000.')
    } finally {
      setWalkingId(null)
    }
  }

  const restrict = async () => {
    if (!aoi) return
    setWalkingId('restrict')
    setError('')
    try {
      apply(await runAnalysis(aoi, true))
    } catch (e) {
      console.error(e)
      setError('Backend non raggiungibile.')
    } finally {
      setWalkingId(null)
    }
  }

  const reset = () => {
    setResult(null)
    setTab('tappa')
    try { localStorage.removeItem('archeoeagle.last') } catch { /* */ }
  }

  return (
    <div className="h-full min-h-0 flex flex-col overflow-hidden bg-dust/95">
      <div className="px-4 pt-3 pb-2 border-b border-bone/10 shrink-0">
        <div className="mx-auto mb-2 h-1 w-10 rounded-full bg-bone/20 md:hidden" />
        <div className="flex items-center justify-between">
          <h2 className="serif text-sm font-semibold">Fascicolo</h2>
          <button onClick={closePanel} className="md:hidden p-2 rounded hover:bg-bone/10 text-mute">
            <ChevronDown size={16} />
          </button>
        </div>
        <p className="text-[11px] text-mute mt-1 leading-snug">
          {result
            ? (corridor ? `Corridoio ${corridor.name}. Tappe sulla rete, non icone.` : 'Tratto ristretto a mano. Bias dichiarato.')
            : 'Scegli un fiume. Non disegnare dove “sembra” Atlantide.'}
        </p>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
        {!result && (
          <section className="space-y-1.5">
            <div className="border border-bone/10 px-3 py-2 space-y-1.5">
              <p className="serif text-xs text-bone">Una cosa sola</p>
              <p className="text-[11px] text-mute leading-relaxed">
                Da casa: prove oggettive su paleoidrologia sahariana. Il cartone (anelli, isola atlantica, “Atlantide found”) è telefono senza fili. Mega-Chad tenta una misura DEM 320 m. Gli altri corridoi restano disegni da paper finché non c’è radar. Platone è colonna, non stampo.
              </p>
            </div>
            {BASINS.map((b) => (
              <button
                key={b.id}
                onClick={() => walk(b.id)}
                disabled={!!walkingId}
                className={`w-full text-left px-3 py-2.5 border border-bone/10 bg-ink/50 hover:border-ochre/50 flex items-center gap-3 ${tap}`}
              >
                {walkingId === b.id
                  ? <Loader2 size={14} className="animate-spin text-ochre shrink-0" />
                  : <Footprints size={14} className="text-ochre shrink-0" />}
                <span className="min-w-0">
                  <span className="block text-xs text-bone">{b.name}</span>
                  <span className="block text-[10px] text-mute">
                    {b.id === 'megachad' ? 'misura DEM se c’è · senno disegno' : `${b.hint} · schematico`}
                  </span>
                </span>
              </button>
            ))}
            {TRAPS.map((b) => (
              <button
                key={b.id}
                onClick={() => walk(b.id)}
                disabled={!!walkingId}
                className={`w-full text-left px-3 py-2.5 border border-danger/40 bg-ink/50 flex items-center gap-3 ${tap}`}
              >
                {walkingId === b.id
                  ? <Loader2 size={14} className="animate-spin text-danger shrink-0" />
                  : <EyeOff size={14} className="text-danger shrink-0" />}
                <span className="min-w-0">
                  <span className="block text-xs text-danger">{b.name}</span>
                  <span className="block text-[10px] text-mute">{b.hint}</span>
                </span>
              </button>
            ))}
          </section>
        )}

        {result && result.method === 'trap' && (
          <section className="border border-danger/40 px-3 py-3 space-y-2">
            <p className="serif text-sm text-danger">Trappola · {result.trap_id}</p>
            <p className="text-[12px] text-bone leading-relaxed">{result.message}</p>
            <p className="text-[11px] text-mute">{String(result.stats?.warning || '')}</p>
          </section>
        )}

        {result && result.method !== 'trap' && (
          <>
            {typeof result.stats?.grade === 'string' && (
              <div className={`px-3 py-2 border text-[11px] leading-relaxed ${
                result.stats.grade === 'dem-contour'
                  ? 'border-sage/40 text-bone'
                  : 'border-ochre/30 text-mute'
              }`}>
                <span className="uppercase tracking-[0.12em] text-[10px] text-ochre">
                  grado {String(result.stats.grade)}
                </span>
                <p className="mt-1">{String(result.stats.warning || '')}</p>
              </div>
            )}
            <HashBar pack={result.blind} />

            <Briefing rows={ranking} corridorId={result.corridor_id} />

            <div className="flex gap-1">
              {(['tappa', 'confronta', 'capire'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`flex-1 py-2 text-[11px] border capitalize ${tab === t ? 'border-ochre/50 text-bone' : 'border-bone/10 text-mute'}`}
                >
                  {t === 'confronta' ? <span className="inline-flex items-center gap-1"><Columns3 size={11} /> Confronta</span> : t}
                </button>
              ))}
            </div>

            {tab === 'capire' && <Capire corridorId={result.corridor_id} />}
            {tab === 'confronta' && (
              <>
                <p className="text-[11px] text-mute leading-snug">
                  Stesse colonne, tre tappe. Se due persone mettono lo stesso ordine, il fascicolo tiene. Se no, il residuo è ancora alto. Non votare “quale sembra Atlantide”.
                </p>
                <CompareGrid rows={ranking.slice(0, 3)} blind={blindMode} />
              </>
            )}
            {tab === 'tappa' && (
              <>
                <ol className="space-y-1">
                  {ranking.map((row) => (
                    <li key={row.label}>
                      <button
                        onClick={() => onSelect(row.label)}
                        className={`w-full text-left px-3 py-2 border flex items-baseline gap-2 ${tap}
                          ${selected?.label === row.label ? 'border-ochre/50 bg-ochre/10' : 'border-bone/10 bg-ink/40'}`}
                      >
                        <span className="serif text-base w-6 text-ochre">{row.label}</span>
                        <span className="text-[11px] text-mute flex-1 truncate">
                          {blindMode
                            ? (NODE_IT[row.node_type || ''] || 'nodo')
                            : (row.river_name || NODE_IT[row.node_type || ''] || 'fuori rete')}
                          {row.grade === 'dem-contour' ? ' · DEM' : ''}
                          {row.vs_schematic_km != null ? ` · Δ ${row.vs_schematic_km} km` : ''}
                        </span>
                        <span className="mono text-[11px] text-bone">ρ {row.residual.toFixed(2)}</span>
                      </button>
                    </li>
                  ))}
                </ol>
                {selected && <CasePage row={selected} blind={blindMode} />}
              </>
            )}

            <div className="grid grid-cols-2 gap-1.5">
              <button
                onClick={() => dossierLocal(ranking, result.corridor_id || 'archeoeagle')}
                disabled={blindMode}
                className={`flex items-center justify-center gap-1.5 py-2.5 text-xs border border-bone/15 ${tap} ${blindMode ? 'opacity-40' : ''}`}
              >
                <BookOpen size={12} /> Dossier
              </button>
              <button
                onClick={() => blindLocal(result.blind, result.corridor_id || 'archeoeagle')}
                className={`flex items-center justify-center gap-1.5 py-2.5 text-xs border border-sage/40 text-sage ${tap}`}
              >
                <Download size={12} /> Pack cieco
              </button>
            </div>
          </>
        )}

        {error && <div className="p-3 border border-danger/40 text-xs text-danger">{error}</div>}

        <details className="border border-bone/10">
          <summary className="px-3 py-2 text-[10px] uppercase tracking-[0.12em] text-mute cursor-pointer">
            Restringi a mano — qui entra il bias
          </summary>
          <div className="px-3 pb-3 space-y-2">
            <p className="text-[11px] text-mute leading-snug">
              Disegnare un box è scegliere dove guardare. Usa solo per accorciare un fiume già camminato.
            </p>
            <button
              onClick={() => setAllowDraw(!allowDraw)}
              className={`w-full py-2 text-xs border ${allowDraw ? 'border-ochre/50 text-ochre' : 'border-bone/15 text-mute'}`}
            >
              {allowDraw ? 'Disegno attivo' : 'Attiva disegno'}
            </button>
            {allowDraw && aoi && (
              <button onClick={restrict} className="w-full py-2 text-xs border border-bone/20 text-bone">
                {walkingId === 'restrict' ? '…' : 'Ricalcola sul tratto'}
              </button>
            )}
          </div>
        </details>
      </div>

      <div className="shrink-0 p-3 border-t border-bone/10 bg-dust">
        {result ? (
          <button onClick={reset} className={`w-full py-3 text-sm flex justify-center items-center gap-2 border border-bone/20 ${tap}`}>
            <RotateCcw size={16} /> Altro corridoio
          </button>
        ) : (
          <p className="text-[11px] text-center text-mute">
            Un tap = un fiume intero. Tu non scegli la forma.
          </p>
        )}
      </div>
    </div>
  )
}

function HashBar({ pack }: { pack: AnalysisResult['blind'] }) {
  return (
    <div className="border border-ochre/30 bg-ochre/5 px-3 py-2">
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.14em] text-ochre">
        <Hash size={12} /> Priorità SHA-256
      </div>
      <p className="mono text-xs text-bone mt-1">{pack.hash.slice(0, 12)}…</p>
      <p className="text-[10px] text-mute">{pack.timestamp}</p>
      <button className="mt-1 text-[10px] text-sage underline" onClick={() => navigator.clipboard?.writeText(pack.hash)}>
        copia hash
      </button>
    </div>
  )
}

function Briefing({ rows, corridorId }: { rows: RankRow[], corridorId?: string | null }) {
  const brief = corridorId ? BRIEFS[corridorId] : null
  return (
    <div className="border border-bone/15 px-3 py-2 space-y-2">
      <p className="text-[11px] text-bone leading-relaxed">{walkSummary(rows)}</p>
      {brief && (
        <p className="text-[11px] text-mute leading-relaxed">{brief.why}</p>
      )}
    </div>
  )
}

function Capire({ corridorId }: { corridorId?: string | null }) {
  const brief = corridorId ? BRIEFS[corridorId] : null
  return (
    <div className="space-y-3">
      {brief && (
        <section className="space-y-2">
          <p className="serif text-xs text-ochre">Questo corridoio</p>
          <Block title="Perché camminarlo" text={brief.why} />
          <Block title="Che acqua è" text={brief.whatWater} />
          <Block title="Cosa puoi dire da casa" text={brief.whatYouCanSay} />
          <Block title="Cosa non puoi dire" text={brief.whatYouCannot} />
          <div>
            <p className="text-[10px] uppercase tracking-[0.12em] text-ochre mb-1">Cosa fai adesso</p>
            {brief.next.map((s, i) => (
              <p key={i} className="text-[11px] text-bone leading-snug mb-1">{i + 1}. {s}</p>
            ))}
          </div>
          <p className="text-[10px] text-mute italic">{brief.source}</p>
        </section>
      )}
      <section className="space-y-2">
        <p className="serif text-xs text-ochre">Lessico — così non ti perdi</p>
        {METHOD.map((m) => (
          <div key={m.term}>
            <p className="text-[11px] text-bone">{m.term}</p>
            <p className="text-[11px] text-mute leading-relaxed">{m.meaning}</p>
          </div>
        ))}
      </section>
    </div>
  )
}

function Block({ title, text }: { title: string, text: string }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-[0.12em] text-mute mb-0.5">{title}</p>
      <p className="text-[11px] text-bone leading-relaxed">{text}</p>
    </div>
  )
}

function CasePage({ row, blind }: { row: RankRow, blind: boolean }) {
  const questions = nextQuestions(row)
  return (
    <article className="border border-bone/15 bg-pitch/40">
      <header className="px-3 py-2 border-b border-bone/10 flex items-baseline justify-between">
        <span className="serif text-lg text-ochre">Tappa {row.label}</span>
        <span className="mono text-[11px] text-mute">ρ {row.residual.toFixed(3)}</span>
      </header>
      <div className="px-3 py-2">
        <p className="text-[10px] uppercase tracking-[0.12em] text-ochre mb-1">In parole povere</p>
        <p className="text-[12px] text-bone leading-relaxed">{plainSpeak(row)}</p>
      </div>
      <div className="px-3 py-2 grid grid-cols-2 gap-2 text-center">
        <Metric label="idro" value={row.hydro_score.toFixed(2)} />
        <Metric label="forma" value={row.geometry_score == null ? 'non misurata' : row.geometry_score.toFixed(2)} />
      </div>
      {!blind ? (
        <p className="px-3 py-1 mono text-[10px] text-mute">
          {row.lat.toFixed(4)} N  {row.lon.toFixed(4)} E
          {row.river_name ? `  ·  ${row.river_name}` : ''}
        </p>
      ) : (
        <p className="px-3 py-1 text-[10px] text-sage flex items-center gap-1">
          <EyeOff size={10} /> coordinate nascoste
        </p>
      )}
      <div className="px-3 py-2 space-y-1.5">
        <p className="text-[10px] uppercase tracking-[0.12em] text-sage">Sostiene</p>
        {row.pro.map((p, i) => <p key={i} className="text-[11px] text-bone leading-snug">· {p}</p>)}
        <p className="text-[10px] uppercase tracking-[0.12em] text-ochre pt-1">Uccide o tiene aperto</p>
        {row.contro.map((p, i) => <p key={i} className="text-[11px] text-mute leading-snug">· {p}</p>)}
        <p className="text-[11px] text-mute pt-1 italic">{row.kill_shot}</p>
      </div>
      <div className="px-3 pb-2">
        <p className="text-[10px] uppercase tracking-[0.12em] text-mute mb-1.5">Platone + / − / N/A</p>
        <ul className="space-y-1">
          {row.plato.map((t) => (
            <li key={t.id} className="flex gap-2 text-[11px] items-start">
              <span className={`mono w-8 shrink-0 ${
                t.verdict === 'support' ? 'text-sage' : t.verdict === 'contradict' ? 'text-danger' : 'text-bone/70'
              }`}>{VERDICT_IT[t.verdict]}</span>
              <span>
                <span className="text-bone">{t.label}</span>
                <span className="block text-[10px] text-mute leading-snug">{t.detail}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
      <div className="px-3 pb-3 border-t border-bone/10 pt-2">
        <p className="text-[10px] uppercase tracking-[0.12em] text-ochre mb-1">Domande — indaga, non concludere</p>
        {questions.map((q, i) => (
          <p key={i} className="text-[11px] text-bone leading-snug mb-1.5">{i + 1}. {q}</p>
        ))}
      </div>
    </article>
  )
}

function CompareGrid({ rows, blind }: { rows: RankRow[], blind: boolean }) {
  return (
    <div className="grid grid-cols-3 gap-1">
      {rows.map((row) => (
        <div key={row.label} className="border border-bone/10 p-1.5">
          <p className="serif text-ochre text-sm">{row.label}</p>
          <p className="mono text-[10px] text-bone">ρ {row.residual.toFixed(2)}</p>
          <p className="text-[10px] text-mute mt-1">
            {blind ? (NODE_IT[row.node_type || ''] || 'nodo') : (row.river_name || '—')}
          </p>
          <ul className="mt-1 space-y-0.5">
            {row.plato.map((t) => (
              <li key={t.id} className="mono text-[9px] text-mute">
                {VERDICT_IT[t.verdict]} {t.id.replace(/_/g, ' ')}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}

function Metric({ label, value }: { label: string, value: string }) {
  return (
    <div className="bg-ink/50 px-2 py-1.5 text-center">
      <p className="mono text-sm text-bone leading-none">{value}</p>
      <p className="text-[10px] text-mute mt-1">{label}</p>
    </div>
  )
}
