/* eslint-disable @typescript-eslint/no-explicit-any */
import { MapContainer, TileLayer, FeatureGroup, GeoJSON, ImageOverlay, CircleMarker, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'
import { useEffect, useRef } from 'react'
import L from 'leaflet'
import type { RankRow, ViewTarget, FieldNote } from '../types'
import { CORRIDOR_FEATURE_IDS } from '../basins'

;(window as any).L = L
import 'leaflet-draw'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

function RawDrawControl({ setAoi, fgRef }: { setAoi: (aoi: any) => void, fgRef: any }) {
  const map = useMap()

  useEffect(() => {
    if (!map || !fgRef.current) return
    const drawnItems = fgRef.current
    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: {
        polyline: false, polygon: {}, circle: false,
        rectangle: {}, marker: false, circlemarker: false,
      },
    })
    map.addControl(drawControl)

    const onDrawCreated = (e: any) => {
      drawnItems.clearLayers()
      drawnItems.addLayer(e.layer)
      setAoi(e.layer.toGeoJSON())
    }
    const onDrawEdited = (e: any) => {
      e.layers.eachLayer((layer: any) => setAoi(layer.toGeoJSON()))
    }
    const onDrawDeleted = () => {
      if (drawnItems.getLayers().length === 0) setAoi(null)
    }

    map.on('draw:created', onDrawCreated)
    map.on('draw:edited', onDrawEdited)
    map.on('draw:deleted', onDrawDeleted)
    return () => {
      map.removeControl(drawControl)
      map.off('draw:created', onDrawCreated)
      map.off('draw:edited', onDrawEdited)
      map.off('draw:deleted', onDrawDeleted)
    }
  }, [map, fgRef, setAoi])

  return null
}

function FlyTo({ target }: { target: ViewTarget | null }) {
  const map = useMap()
  useEffect(() => {
    if (!target) return
    map.flyTo(target.center, target.zoom, { duration: 0.8 })
  }, [map, target])
  return null
}

interface Props {
  setAoi: (a: any) => void
  ranking: RankRow[]
  rivers: any
  network: any
  layers: Record<string, string>
  activeLayers: string[]
  bbox: number[] | null
  viewTarget: ViewTarget | null
  blindMode: boolean
  selectedLabel: string | null
  onSelect: (label: string) => void
  fieldPos: { lat: number, lon: number } | null
  fieldNotes: FieldNote[]
  allowDraw: boolean
  activeCorridor: string | null
}

export default function MapCanvas({
  setAoi, ranking, rivers, network, layers, activeLayers, bbox,
  viewTarget, blindMode, selectedLabel, onSelect, fieldPos, fieldNotes,
  allowDraw, activeCorridor,
}: Props) {
  const featureGroupRef = useRef(null)
  const bounds: L.LatLngBoundsExpression | null = bbox
    ? [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]
    : null
  const riverData = rivers?.features?.length ? rivers : network

  return (
    <MapContainer center={[21.2, 2.5]} zoom={5} className="w-full h-full" zoomControl>
      <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="Tiles &copy; Esri"
        maxZoom={18}
      />
      <FlyTo target={viewTarget} />

      {bounds && activeLayers.map((layerId) => {
        const b64 = layers[layerId]
        if (!b64) return null
        return (
          <ImageOverlay
            key={layerId}
            url={`data:image/png;base64,${b64}`}
            bounds={bounds}
            opacity={0.62}
            zIndex={layerId === 'dem' ? 400 : 420}
          />
        )
      })}

      {riverData && (
        <GeoJSON
          key={`rivers-${riverData.features?.length || 0}-${activeCorridor || 'all'}`}
          data={riverData}
          style={(feature) => {
            const ids = activeCorridor ? (CORRIDOR_FEATURE_IDS[activeCorridor] || [activeCorridor]) : []
            const fid = feature?.properties?.id
            const on = ids.length === 0 || ids.includes(fid)
            return {
              className: on && ids.length ? 'river-line river-line-on' : 'river-line',
              color: on && ids.length ? '#c45c26' : '#8fc4ae',
              weight: on && ids.length ? 4 : 2.2,
              opacity: on ? 0.95 : 0.35,
              dashArray: '10 6',
            }
          }}
        />
      )}

      <FeatureGroup ref={featureGroupRef}>
        {allowDraw && <RawDrawControl setAoi={setAoi} fgRef={featureGroupRef} />}
      </FeatureGroup>

      {!blindMode && ranking.map((row) => (
        <CircleMarker
          key={row.label}
          center={[row.lat, row.lon]}
          radius={row.label === selectedLabel ? 14 : 9}
          pathOptions={{
            color: row.label === selectedLabel ? '#e8dcc8' : '#c45c26',
            fillColor: '#c45c26',
            fillOpacity: 0.85,
            weight: 2,
          }}
          eventHandlers={{ click: () => onSelect(row.label) }}
        />
      ))}

      {fieldPos && (
        <CircleMarker
          center={[fieldPos.lat, fieldPos.lon]}
          radius={8}
          pathOptions={{ color: '#6b9e8a', fillColor: '#6b9e8a', fillOpacity: 0.9, weight: 2 }}
        />
      )}

      {fieldNotes.map((n) => (
        <CircleMarker
          key={n.id}
          center={[n.lat, n.lon]}
          radius={6}
          pathOptions={{ color: '#e8dcc8', fillColor: '#2a2420', fillOpacity: 1, weight: 2 }}
        />
      ))}
    </MapContainer>
  )
}
