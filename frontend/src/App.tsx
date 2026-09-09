/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback, useEffect, useState } from 'react'
import MapCanvas from './components/MapCanvas'
import ControlPanel from './components/ControlPanel'
import { Menu, X, LocateFixed, EyeOff, Eye, NotebookPen } from 'lucide-react'
import { fetchNetwork } from './api'
import type { AnalysisResult, FieldNote, ViewTarget } from './types'

const NOTES_KEY = 'archeoeagle.fieldnotes'

export default function App() {
  const [panelOpen, setPanelOpen] = useState(true)
  const [aoi, setAoi] = useState<any>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [network, setNetwork] = useState<any>(null)
  const [layersData, setLayersData] = useState<Record<string, string>>({})
  const [activeLayers, setActiveLayers] = useState<string[]>([])
  const [bbox, setBbox] = useState<number[] | null>(null)
  const [viewTarget, setViewTarget] = useState<ViewTarget | null>(null)
  const [blindMode, setBlindMode] = useState(false)
  const [fieldMode, setFieldMode] = useState(false)
  const [fieldPos, setFieldPos] = useState<{ lat: number, lon: number } | null>(null)
  const [fieldNotes, setFieldNotes] = useState<FieldNote[]>(() => {
    try { return JSON.parse(localStorage.getItem(NOTES_KEY) || '[]') } catch { return [] }
  })
  const [noteDraft, setNoteDraft] = useState('')
  const [selectedLabel, setSelectedLabel] = useState<string | null>(null)
  const [allowDraw, setAllowDraw] = useState(false)
  const [walkingId, setWalkingId] = useState<string | null>(null)

  useEffect(() => {
    fetchNetwork().then(setNetwork).catch(() => setNetwork(null))
    try {
      const cached = localStorage.getItem('archeoeagle.last')
      if (cached) {
        const data = JSON.parse(cached) as AnalysisResult
        if (data.method === 'corridor-walk' && data.ranking?.length) {
          setResult(data)
          if (data.layers && data.bbox) {
            setLayersData(data.layers)
            setBbox(data.bbox)
          }
        }
      }
    } catch { /* ignore */ }
  }, [])

  const handleLayersData = useCallback((layers: Record<string, string>, newBbox: number[]) => {
    setLayersData(layers)
    setBbox(newBbox)
    setActiveLayers([])
  }, [])

  const locate = () => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const next = { lat: pos.coords.latitude, lon: pos.coords.longitude }
        setFieldPos(next)
        setViewTarget({ center: [next.lat, next.lon], zoom: 12 })
        setFieldMode(true)
      },
      () => setFieldMode(true),
      { enableHighAccuracy: true, timeout: 12000 },
    )
  }

  const addNote = () => {
    if (!fieldPos || !noteDraft.trim()) return
    const n: FieldNote = {
      id: String(Date.now()),
      lat: fieldPos.lat,
      lon: fieldPos.lon,
      text: noteDraft.trim(),
      at: new Date().toISOString(),
    }
    const next = [n, ...fieldNotes]
    setFieldNotes(next)
    localStorage.setItem(NOTES_KEY, JSON.stringify(next))
    setNoteDraft('')
  }

  return (
    <div className="relative h-screen w-full bg-pitch text-bone overflow-hidden flex flex-col">
      <header className="flex items-center justify-between px-3 py-2 bg-pitch/90 backdrop-blur-md z-30 border-b border-bone/10 shrink-0">
        <div className="min-w-0">
          <h1 className="serif text-[15px] tracking-wide leading-none">
            ARCHEO<span className="text-ochre">EAGLE</span>
          </h1>
          <p className="text-[10px] text-mute leading-none mt-0.5 truncate">
            Prove, non il cartone. Sahara = ipotesi. Anelli = trappola.
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setBlindMode((v) => !v)}
            className={`p-2.5 min-w-11 min-h-11 ${blindMode ? 'text-sage' : 'text-bone/80'}`}
            title="Pack cieco in anteprima"
          >
            {blindMode ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
          <button
            onClick={locate}
            className={`p-2.5 min-w-11 min-h-11 ${fieldMode ? 'text-sage' : 'text-bone/80'}`}
            title="Posizione campo"
          >
            <LocateFixed size={18} />
          </button>
          <button
            onClick={() => setPanelOpen(!panelOpen)}
            className="p-2.5 min-w-11 min-h-11 text-bone"
          >
            {panelOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        <div className="flex-1 relative z-0">
          <MapCanvas
            setAoi={setAoi}
            ranking={result?.ranking ?? []}
            rivers={result?.rivers}
            network={network}
            layers={layersData}
            activeLayers={activeLayers}
            bbox={bbox}
            viewTarget={viewTarget}
            blindMode={blindMode}
            selectedLabel={selectedLabel}
            onSelect={setSelectedLabel}
            fieldPos={fieldPos}
            fieldNotes={fieldNotes}
            allowDraw={allowDraw}
            activeCorridor={walkingId || result?.corridor_id || null}
          />
        </div>

        <div
          className={`
            ${panelOpen ? 'translate-x-0 translate-y-0' : 'translate-x-full md:translate-x-full translate-y-full md:translate-y-0'}
            absolute md:static right-0 bottom-0 md:top-0 w-full md:w-[26rem] h-[46vh] md:h-full min-h-0
            z-20 transition-transform duration-300 ease-out
            flex flex-col control-panel field-sheet
          `}
        >
          <ControlPanel
            closePanel={() => setPanelOpen(false)}
            aoi={aoi}
            result={result}
            setResult={setResult}
            onLayersData={handleLayersData}
            onFly={setViewTarget}
            selectedLabel={selectedLabel}
            onSelect={setSelectedLabel}
            blindMode={blindMode}
            fieldMode={fieldMode}
            allowDraw={allowDraw}
            setAllowDraw={setAllowDraw}
            walkingId={walkingId}
            setWalkingId={setWalkingId}
          />
        </div>
      </div>

      {fieldMode && fieldPos && (
        <div className="absolute left-3 bottom-[calc(52vh+12px)] md:bottom-6 z-30 w-[min(92vw,22rem)] bg-dust/95 border border-bone/15 p-2.5">
          <p className="mono text-[10px] text-sage mb-1">
            {fieldPos.lat.toFixed(5)} N  {fieldPos.lon.toFixed(5)} E
          </p>
          <div className="flex gap-1.5">
            <input
              value={noteDraft}
              onChange={(e) => setNoteDraft(e.target.value)}
              placeholder="Nota da campo (resta sul telefono)"
              className="flex-1 bg-pitch border border-bone/10 px-2 py-2 text-xs text-bone placeholder:text-mute"
            />
            <button onClick={addNote} className="px-3 bg-ochre text-pitch min-h-11">
              <NotebookPen size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
