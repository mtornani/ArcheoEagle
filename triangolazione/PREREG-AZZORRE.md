# Azzorre — terrazze e ciglio della piattaforma insulare. Previsione registrata PRIMA di scaricare la batimetria delle isole.

Registrata: 2026-11-09 sera (Europe/Rome). Autore: Claude, su richiesta di Mirko.
Prima di questo file ho aperto solo un riquadro di prova in oceano aperto (45 N, 20 W) per verificare l'accesso.

## Tesi in esame (Randall Carlson, ledger)
L'altopiano delle Azzorre era emerso ed e' sprofondato a fine glaciazione (~11.6 ka).
Per emergere dovrebbe risalire di ~1000 m (misura GMRT: 91% del riquadro sotto -1000 m).

## Logica
Al massimo glaciale il mare stava a circa -130 m (Lambeck 2014: -134 m). Le onde tagliano una piattaforma
fino a quella quota; dove finisce, il fondale si rompe in pendio ("ciglio").
Se un'isola e' scesa di X metri dopo, il ciglio glaciale oggi sta a circa -(130 + X).

## Dato e metodo (fissati)
- EMODnet Bathymetry DTM, WCS `emodnet:mean`, passo 0.00104167 gradi (~115 m). Tre riquadri: est, centro, ovest.
- Unita': Santa Maria, Sao Miguel, Terceira, Graciosa, Sao Jorge, Faial-Pico (uniti se connessi), Flores, Corvo.
- Per unita': celle con -400 <= z < 0 connesse (4-vicini, passando per z >= -400) alla terra dell'isola.
- Pendenza con metrica sferica. Classi di 10 m: pendenza mediana e area per classe.
- Ciglio = classe piu' superficiale sotto -20 m in cui la pendenza mediana supera 2 volte la mediana
  della fascia -20..-80 m, per 3 classi consecutive.

## Controllo (strumento)
Santa Maria ha terrazze pubblicate a -40/-50, -70/-80, -85/-90, -100/-110, -120/-140 m (Ricchi et al. 2018).
C1: il ciglio di Santa Maria cade in [-90, -170] m.
C2 (debole, dichiarato): almeno 2 delle 3 classi di area massima fra -30 e -150 m cadono nelle bande pubblicate
(+-5 m). Le bande coprono circa meta' dell'intervallo: per caso riesce una volta su due. Non decide niente da solo.

## Previsioni
P1: ciglio in [-80, -180] m per almeno 6 unita' su 8.
P2: nessuna unita' con ciglio piu' profondo di -300 m.
Lettura: sprofondamento netto dal massimo glaciale ~ (profondita' del ciglio - 130 m).
Riga Carlson "Azzorre sprofondate a 11.6 ka" prende "-" se la mediana e' < 100 m. Gliene servono ~1000.

## Kill-shot della MIA previsione
- Meno di 5 unita' su 8 nell'intervallo, o ciglio non definibile su piu' di 3 unita' => FAIL / NON TESTABILE.
  In quel caso la riga di Carlson resta APERTA, non "-".
- C1 fallisce => strumento non tarato, risultato non valido.

## Cosa NON dimostra, anche se passa
- Le piattaforme sono poligeniche (molti cicli glaciali), il ciglio e' ritoccato da lave e sedimenti.
- Limita il movimento verticale NETTO dall'ultimo stazionamento basso. Non esclude oscillazioni che si annullano.
- 115 m di passo non risolve terrazze strette.
