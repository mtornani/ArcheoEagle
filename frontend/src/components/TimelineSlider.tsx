import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react'
import { useState } from 'react'

interface Props {
  dates: string[]
  selectedIndex: number
  onChange: (index: number) => void
}

export default function TimelineSlider({ dates, selectedIndex, onChange }: Props) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  if (dates.length === 0) return null

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs text-muted">
        <Calendar size={12} />
        <span>Timeline Temporale</span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onChange(Math.max(0, selectedIndex - 1))}
          disabled={selectedIndex === 0}
          className="p-1 rounded hover:bg-white/10 text-muted disabled:opacity-30 transition-colors"
        >
          <ChevronLeft size={14} />
        </button>

        <div className="flex-1 relative">
          {/* Track */}
          <div className="h-1 bg-white/10 rounded-full relative">
            <div
              className="absolute h-full bg-secondary rounded-full transition-all duration-300"
              style={{ width: `${dates.length > 1 ? (selectedIndex / (dates.length - 1)) * 100 : 100}%` }}
            />
          </div>

          {/* Dots */}
          <div className="absolute top-1/2 -translate-y-1/2 w-full flex justify-between px-0">
            {dates.map((date, i) => (
              <button
                key={i}
                onClick={() => onChange(i)}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="relative group"
              >
                <span
                  className={`
                    block w-3 h-3 rounded-full border-2 transition-all duration-200
                    ${i === selectedIndex
                      ? 'bg-secondary border-secondary scale-125'
                      : i < selectedIndex
                        ? 'bg-secondary/40 border-secondary/60'
                        : 'bg-white/10 border-white/20 hover:border-secondary/50'
                    }
                  `}
                />
                {/* Tooltip */}
                {hoveredIndex === i && (
                  <span className="absolute -top-7 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] bg-surface px-2 py-0.5 rounded text-light shadow-lg">
                    {date}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => onChange(Math.min(dates.length - 1, selectedIndex + 1))}
          disabled={selectedIndex === dates.length - 1}
          className="p-1 rounded hover:bg-white/10 text-muted disabled:opacity-30 transition-colors"
        >
          <ChevronRight size={14} />
        </button>
      </div>

      {/* Current date label */}
      <p className="text-center text-xs font-medium text-secondary">
        {dates[selectedIndex]}
      </p>
    </div>
  )
}
