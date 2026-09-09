# ArcheoEagle

Motore forense sui **paleofiumi del Sahara**. Da un PC di casa. Open source.

Repo: https://github.com/mtornani/ArcheoEagle

GIS host da qui in poi: **[GeoLibre](https://github.com/opengeos/GeoLibre)** (browser, desktop, iOS, Android). ArcheoEagle resta il dominio forense (ledger, pack cieco, Platone). Non un secondo GIS. Vedi `docs/GEOLIBRE.md`.

Non è un bottone “Atlantide found”. Non cerca anelli. Cammina la rete idrica fossile, misura dopo la forma, e tiene Platone come colonna a due facce (`+` / `−` / `N/A`). L’assenza di anelli **non contraddice**.

## Cosa fa

1. Carica una rete schematica di paleodrenaggi sahariani (Tamanrasset, Irharhar, Sahabi, Mega-Chad, Tilemsi, Azawagh, Wadi Howar).
2. Sull’AOI che disegni, genera **nodi idrici** (confluenze, sponde, alvei). Nessun prior di forma urbana.
3. Aggiunge NDVI/BSI/DEM come colonna, non come bersaglio. I dati satellitari reali arrivano se hai credenziali Copernicus; senza, è mock dichiarato.
4. Costruisce un **ledger**: pro, contro, residuo, kill-shot remoto, test platonici.
5. Esporta due oggetti:
   - **Dossier locale** — coordinate. Resta sul tuo disco. Non pubblicare.
   - **Pack cieco** — etichette A/B/C + rubrica + **SHA-256 + timestamp**. Niente pin. Priorità senza dare la preda agli squali.

Due umani, stessi layer, stessa classifica. Mai 100%. L’operatore non è il peer.

I tracciati in `data/sahara_paleodrainage.geojson` sono **schematici da letteratura**, non idrografia da rilievo. Un vertice non è un sito.

## Campo e mobile

- **Claude Code da telefono:** clone questo repo, apri la cartella, leggi `CLAUDE.md`.
- **Mappa:** GeoLibre app (iOS/Android / [web](https://web.geolibre.app)) → apri `data/sahara_paleodrainage.geolibre.json`.
- UI a foglio dal basso sul telefono, target da 44px, PWA (Aggiungi a Home) — frontend legacy Leaflet, ancora avviabile.
- GPS + note da campo in `localStorage` (restano sul device).
- Vite in `host: true` — apri `http://<IP-LAN>:5173` dal telefono sulla stessa rete.
- Service worker: solo shell. `/api` non viene cachata.

## Avvio (€0, locale)

```bash
# backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# frontend
cd frontend
npm install
npm run dev
```

Apri `http://127.0.0.1:5173`. Disegna un’area su un bacino (bottoni Tamanrasset / Mega-Chad / …) → **Classifica nodi**.

Opzionale: `COPERNICUS_USER` / `COPERNICUS_PASSWORD`, `OPENTOPOGRAPHY_API_KEY` in `.env`.

## Test

```bash
cd backend
python -m unittest discover -s tests -v
```

## Cosa questo software non può fare

- Datare un crollo, trovare oricalco, scavalcare uno scavo.
- Sostituire uno storico o un archeologo. Il terminale umano, se arriva, lavora sul pack cieco.
- Trasformare una classifica in una scoperta.

MIT. Vedi `LICENSE`.
