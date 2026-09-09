import { Eye, EyeOff, Mountain, Leaf, Globe, TrendingUp } from 'lucide-react'

interface LayerInfo {
  id: string
  label: string
  icon: React.ReactNode
  color: string
  description: string
}

const LAYERS: LayerInfo[] = [
  { id: 'ndvi', label: 'NDVI', icon: <Leaf size={14} />, color: '#22c55e', description: 'Indice vegetazione' },
  { id: 'bsi', label: 'BSI', icon: <Globe size={14} />, color: '#d97706', description: 'Indice suolo nudo' },
  { id: 'dem', label: 'DEM', icon: <Mountain size={14} />, color: '#8b5cf6', description: 'Elevazione SRTM 30m' },
  { id: 'slope', label: 'Pendenza', icon: <TrendingUp size={14} />, color: '#ef4444', description: 'Gradi di pendenza' },
]

interface Props {
  activeLayers: string[]
  onToggle: (layerId: string) => void
  availableLayers: string[]
}

export default function LayerToggle({ activeLayers, onToggle, availableLayers }: Props) {
  return (
    <div className="space-y-1.5">
      {LAYERS.map((layer) => {
        const available = availableLayers.includes(layer.id)
        const active = activeLayers.includes(layer.id)

        return (
          <button
            key={layer.id}
            onClick={() => available && onToggle(layer.id)}
            disabled={!available}
            className={`
              w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs
              transition-all duration-200
              ${!available
                ? 'opacity-30 cursor-not-allowed bg-white/3'
                : active
                  ? 'bg-white/10 ring-1 ring-white/20'
                  : 'bg-white/5 hover:bg-white/8 cursor-pointer'
              }
            `}
          >
            <span style={{ color: active ? layer.color : '#64748b' }}>
              {layer.icon}
            </span>
            <div className="flex-1 text-left">
              <span className={`font-medium ${active ? 'text-light' : 'text-muted'}`}>
                {layer.label}
              </span>
              <span className="ml-1.5 text-[10px] text-muted">{layer.description}</span>
            </div>
            <span className="text-muted">
              {active ? <Eye size={14} /> : <EyeOff size={14} />}
            </span>
          </button>
        )
      })}
    </div>
  )
}
