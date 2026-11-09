# Tentativo 11 — integrale di bacino. Previsione registrata PRIMA di scaricare il DEM.

Registrata: 2026-11-09 (sera, Europe/Rome). Autore: Claude, su richiesta di Mirko.
Nessun tile DEM del bacino e' stato aperto prima di scrivere questo file.

## Metodo (fissato)
- DEM: Copernicus GLO-90 (S3 pubblico), bbox lat 6..21 N, lon 8..23 E (225 tile).
- Aggregazione a 12" (blocchi 4x4) in DUE modi: media e minimo. Entrambi riportati.
- Priority-flood dal bordo del bbox (riempimento depressioni). Seme: cella piu' bassa
  della depressione del Bodele (attesa ~16-17.5 N, 17-19 E).
- Misure: quota di sfioro, posizione del pour point, area e volume a sfioro
  (area sferica per cella, non conteggio di pixel).
- Raffinamento: quota della soglia a 1" (GLO-30) in una finestra attorno al pour point.

## Bersaglio esterno (letteratura, non mio)
- Sponda piu' alta 325 +/- 5 m, area ~340.000 km2 (Leblanc et al. 2006, SRTM30).
- Soglia del Mayo Kebbi 325 m (Mémin et al. 2020). Area ~350-360.000 km2 (Armitage 2015).
- Creste Bama 320/335/338 m (repo, docs/CALIBRAZIONE.md).

## Previsioni
- P1  quota di sfioro (12", media) in [315, 335] m.
- P2  pour point entro 100 km da (9.9 N, 15.0 E), cioe' la soglia del Mayo Kebbi.
- P3  area a sfioro in [300.000, 400.000] km2.
- P4  il bordo della maschera allagata passa a <= 10 km dal Bama Ridge
      (tile N11 E013), SENZA aver usato il ridge per costruirla.

## Kill-shot
- Sfioro fuori da [300, 350] m, oppure pour point a > 300 km dal Mayo Kebbi  => FAIL.
- P1-P3 passano ma P4 no => PARZIALE: la conca e' misurata, il legame con la sponda datata no.
- "Truncated" (la maschera tocca il bordo del bbox) => risultato NON VALIDO, si allarga il bbox
  e si dichiara. Unico ritocco ammesso al metodo.

## Cosa NON dimostra, anche se passa
- Non e' "sponda individuata" su un tile: e' la quota a cui la conca tracima, oggi.
- La topografia e' quella moderna (dune, alluvioni, incisione post-AHP, DSM = chioma).
- Non data niente. La data la danno OSL/14C di terzi.
- Il bersaglio di Leblanc 2006 e' a sua volta ricavato da un DEM (SRTM30): replica indipendente
  di dato e codice, non di principio. L'indipendenza vera sta in P4 (OSL sul Bama).
