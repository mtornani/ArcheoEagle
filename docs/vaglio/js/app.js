/* Rapporti pubblico Vaglio. Dati già nel repository; nessuna coordinata di candidato. */
(function () {
  "use strict";

  const ZONE_COLORS = {
    Centro: "#5e4fa2",
    South: "#3288bd",
    Norte: "#66c2a5",
    North2: "#abdda4",
    OutYuc: "#fdae61",
    Chiaps1: "#f46d43",
    ChiapsCampeche: "#c51b8a",
  };

  const OUTCOME = {
    regge_alla_revisione: { it: "Regge alla revisione", en: "Holds up under blind review", cls: "ok" },
    incerto: { it: "Incerto", en: "Uncertain", cls: "mid" },
    scartato: { it: "Scartato", en: "Discarded", cls: "no" },
    da_rivedere: { it: "Da rivedere", en: "Not yet reviewed", cls: "new" },
  };
  const VERDICT = {
    struttura: { it: "struttura", en: "structure" },
    naturale: { it: "naturale", en: "natural" },
    incerto: { it: "incerto", en: "uncertain" },
    moderno: { it: "moderno", en: "modern" },
  };
  const KNOWN = {
    rilievo_gia_analizzato: {
      it: "Rilievo già analizzato da altri: presumi già visto",
      en: "Survey already analysed by others: presume already seen",
    },
    sito_noto_vicino: {
      it: "Sito noto entro 2 km",
      en: "Known site within 2 km",
    },
  };

  const T = {
    it: {
      docTitle: "Vaglio: una ri-analisi con errori misurati del LiDAR pubblico G-LiHT sullo Yucatán",
      brand: "Vaglio · ArcheoEagle",
      title: "Vaglio: una ri-analisi con errori misurati del LiDAR pubblico G-LiHT sullo Yucatán",
      lead: "Vaglio legge rilievi LiDAR pubblici, segnala i punti in cui il terreno nudo ha la forma di una costruzione, li fa rivedere al buio e misura quanto sbaglia nel farlo. Non dichiara siti. Questo è il rapporto divulgativo sui fatti già pubblici nel repository; il rapporto scientifico per la revisione tra pari arriverà dopo.",
      tocMap: "Mappa",
      tocHow: "Come funziona",
      tocMeasure: "Misure",
      tocCards: "Candidati rivisti",
      tocLimits: "Cosa non sappiamo",
      nTransects: "transetti scansionati",
      nArea: "chilometri quadrati",
      nCand: "complessi candidati",
      nHold: "reggono alla revisione",
      nUnc: "restano incerti",
      nTodo: "da rivedere",
      nOut: "scartati",
      s1: "Questo rilievo è già stato analizzato da altri gruppi (Estrada-Belli et al. 2025; Britton 2026, con un catalogo di 57.181 strutture non ancora pubblico). Ogni candidato si presume già noto finché un confronto non mostra il contrario.",
      s2: "Nessun candidato è stato verificato sul campo. Non si afferma nulla sull'età, sulla cultura o sulla funzione di alcun candidato.",
      s3: "La revisione è stata fatta da agenti AI dello stesso modello. Sui riquadri di controllo hanno riconosciuto 3–4 edifici noti su 10 e non hanno indicato come struttura nessuno dei 10 riquadri vuoti. Per questo il loro giudizio vale per confermare, non per scartare.",
      s4: "Le posizioni dei candidati non sono in questo documento, per non esporre i luoghi al saccheggio.",
      s5: "Analisi e testi prodotti da assistenti AI (Claude, GPT) con la supervisione di Mirko Tornani, [qualifica: la scrive l'operatore].",
      whyH: "Da dove nasce",
      why: "A novembre 2026 Pietro Miotti ha pubblicato un progetto personale: 48 agenti AI hanno guardato circa 1.200 km² di LiDAR NASA sullo Yucatán e hanno segnalato un sito maya che l'istituto messicano INAH non aveva nel registro. Sarah Parcak ha fatto notare che il sito era già pubblicato (Estrada-Belli et al. 2025). L'11 novembre Miotti ha riconosciuto che gli agenti l'avevano riscoperto. Ha fatto per primo una cosa che funziona, e ha corretto in pubblico. Vaglio riprende il suo metodo e aggiunge le misure che lì non c'erano.",
      mapH: "Dove è passato il LiDAR",
      mapCap: "I 456 transetti pubblici (strisce larghe circa 400 m) campionano la penisola, non la coprono: 1.272,7 km² sono meno dell'1% dello Yucatán. I candidati non sono riportati sulla mappa, per scelta. L'indicatore è Chactún, sito già pubblicato: lì il rilevatore è stato addestrato e misurato, su annotazioni di archeologi.",
      chactunPop: "Chactún (sito pubblicato, Wikidata Q13518345). Qui il rilevatore è stato addestrato e misurato. Non è un candidato di Vaglio.",
      howH: "Come lavora",
      step1t: "Visualizzazioni del terreno",
      step1: "Dal modello del terreno nudo calcola sky-view factor, apertura e pendenza, con i parametri di Kokalj et al. 2023. Solo il computer, senza chiave e senza scheda grafica.",
      step2t: "Rilevatore",
      step2: "Un classificatore a gradient boosting, per pixel, addestrato sulle annotazioni di Chactún. Dice dove il terreno ha la forma di una costruzione. I contorni sono grossolani (sovrapposizione 0,566): serve a dire dove guardare, non a disegnare piante.",
      step3t: "Complessi candidati",
      step3: "Rilievi entro 60 m diventano un complesso: è l'unità che si rivede. Un complesso candidato non è un sito. È un punto dove il rilevatore ha visto una forma.",
      step4t: "Revisione al buio",
      step4: "I candidati sono mostrati come riquadri di 120 m, senza nome né posizione, mescolati a controlli di cui la risposta è nota. Servono almeno due revisori.",
      step5t: "Già noto e uso del suolo",
      step5: "Ogni candidato su un rilievo già studiato si presume già visto. Si può anche leggere l'uso del suolo di oggi (ESA WorldCover 2021) nel riquadro.",
      measH: "Quanto sbaglia il rilevatore",
      meas: "Su 942 strutture annotate in 329 riquadri di Chactún non usati in addestramento, il rilevatore ne ritrova il 76,4%. Delle 677 segnalazioni, l'83,0% cade su una struttura annotata. Il criterio, scritto e committato prima di guardare il test, chiedeva almeno il 70% in entrambi i casi: è stato superato.",
      measLim: "Ogni riquadro di Chactún contiene almeno una struttura: la precisione dell'83% vale in terreno denso di rovine, non è stata misurata in terreno vuoto, carsico o coltivato. Chactún è stato rilevato con un altro strumento, a densità di punti più alta. Quanto il rilevatore perda passando ai dati NASA del 2013 non è noto.",
      figH: "Cosa vede chi rivede",
      figLead: "Questi riquadri sono controlli di Chactún (Kokalj et al. 2023, CC BY 4.0), già pubblici nel repository. Non sono i candidati della scansione sullo Yucatán: quelle immagini restano nel fascicolo locale, perché il contesto potrebbe esporre i luoghi. La scala di grigi originale è stata colorata con la rampa viridis, tenendo l'ombreggiatura del rilievo: i corpi in rilievo appaiono giallo-verde, il terreno aperto è viola. Ogni riquadro ha 240 m di lato. Non è una fotografia.",
      capStruct: "Controllo con struttura annotata da archeologi.",
      capEmpty: "Controllo vuoto: niente edificio annotato. Può comunque contenere forme naturali.",
      open: "terreno aperto",
      relief: "rilievo / basso sky-view",
      revH: "Quanto sbagliano i revisori",
      rev: "Secondo giro, dopo che il primo è stato annullato per un difetto nei controlli: 40 candidati e 20 controlli, tre revisori (agenti AI Claude, indipendenti fra loro). Sui 10 controlli con struttura ne hanno riconosciuti 4, 3 e 4. Sui 10 controlli vuoti nessuno dei tre ha mai detto «struttura». Concordano fra loro sul 90–97% dei candidati.",
      cardsH: "I 40 candidati già rivisti",
      cardsLead: "Sono stati estratti quando erano scansionati solo i primi transetti, tutti nel blocco Centro: 20 col punteggio più alto in quel momento, 20 a caso fra gli altri. Dei 20 allora più alti ne reggono 12. Dei 20 a caso ne reggono 3. Nella scansione completa quei «20 più alti» stanno fra la 13ª e la 433ª posizione su 11.916. Dei primi 100 candidati della scansione completa ne sono stati rivisti 3. Il punteggio decide cosa guardare prima: non è una probabilità. Tre revisori dello stesso modello che concordano non sono tre conferme indipendenti. Gli agenti riconoscono gli edifici a lati netti e non i tumuli consumati: «15 reggono» è una stima per difetto di quanti, fra quei 40, sono costruiti; «25 incerti» non vuol dire 25 falsi.",
      all: "Tutti",
      holds: "Reggono",
      uncertain: "Incerti",
      discarded: "Scartati",
      score: "Punteggio d'ordine (non è una probabilità)",
      votes: "Voti al buio",
      noPos: "Posizione omessa.",
      isolated: "un rilievo isolato",
      nearby: "rilievi vicini",
      area: "per {n} m² in tutto",
      height: "il più alto sporge di circa {n} m",
      extent: "distribuiti su {n} m",
      scanH: "La scansione",
      scan: "Scansionati 456 transetti su 456, 1.272,7 km². 11.916 complessi candidati, con 24.265 rilievi singoli. 7.328 complessi (61%) sono fatti di un solo rilievo; 845 ne hanno almeno 5; 214 almeno 10. Area mediana di un complesso: 1.018 m²; il rilievo più alto sporge in mediana di 1,4 m. 249 candidati stanno entro 2 km da uno dei 229 siti elencati su Wikidata; gli altri 11.667 sono marcati «rilievo già analizzato: presumi già noto». Nessun candidato è stato confrontato con il catalogo di Britton né con il registro INAH.",
      land: "Sui 1.548 candidati dei primi 51 transetti, 11 hanno almeno il 5% di «costruito» nell'uso del suolo di oggi (ESA WorldCover 2021). Guardati uno per uno, non al buio, sono tutti e 11 strade asfaltate con le loro scarpate. Lo stesso conto sulla scansione completa non è stato ancora fatto. Il LiDAR è del 2013, la carta del 2021. Una pista sterrata nel bosco non risulta «costruito». Un abitato moderno sta spesso sopra un sito antico: «costruito oggi» non vuol dire «non antico».",
      failH: "Cose provate che non hanno funzionato",
      fail: "Prima di Vaglio, un rilevatore di tumuli sul modello del terreno gratuito a 30 m (alto Khabur, Siria) ha fallito due volte un test pre-registrato: ritrovava dal 6 al 24% dei tumuli alti, e scansionando al buio da 86 a 98 allarmi su 100 non erano tumuli a catalogo. Per questo Vaglio lavora solo dove c'è LiDAR ad alta risoluzione. Il primo giro di revisione è stato annullato. La misura di ortogonalità dei bordi, sui 33 casi di un solo blocco, non pesa nel predire cosa i revisori tengono. Un «ordine appreso» dalle 40 revisioni non è adottato finché non supera una prova scritta prima.",
      unkH: "Cosa non sappiamo",
      unk1: "Quanti degli 11.916 candidati sono costruzioni. Il campione rivisto viene da un solo blocco e non si estende agli altri sei. Non si estrapola «12 su 20» o «3 su 20» a 11.916.",
      unk2: "Quanti sono già nel catalogo di Britton o nel registro INAH.",
      unk3: "Età, cultura, funzione di qualunque candidato.",
      unk4: "Quanto il rilevatore perde su questi dati rispetto a Chactún.",
      unk5: "Quanto valgono i candidati fuori dal blocco Centro (Chiapas montuoso, nord coltivato e abitato).",
      askH: "Cosa chiediamo",
      ask: "Tre cose, a chi quei dati li conosce per mestiere: il confronto col catalogo già esistente; un revisore umano su un pacco al buio, misurato sugli stessi controlli (è l'unico modo per avere qualcuno che possa anche scartare); un parere sul metodo. Il modo di fare il confronto si concorda. Le posizioni, se servono, le decide l'operatore verso un ricercatore con nome e istituto.",
      reproH: "Riproducibilità",
      repro: "Codice e pack cieco (11.916 candidati, senza posizioni) sono nel repository pubblico mtornani/ArcheoEagle, cartella vaglio/. Il pack è firmato SHA-256 il 16 novembre 2026, ore 17:27 UTC. Si controlla con: python -m vaglio verifica pack_cieco.json. I transetti si scaricano da OpenTopography (circa 31 GB). Una scansione completa impiega circa quattro ore su quattro core. I criteri di test del rilevatore sono stati scritti prima di eseguire il test.",
      creditsH: "Crediti e licenze",
      credits: "LiDAR: NASA G-LiHT (AMIGA-Carb, 2013); riprocessamento B. J. Britton (2026), distribuito da OpenTopography, doi:10.5069/G9Z899N1 e doi:10.5069/G9TH8JX9, PDDL. Addestramento e controlli: Kokalj, Ž., Džeroski, S., Šprajc, I. et al. (2023). Machine learning-ready remote sensing data for Maya archaeology. Scientific Data 10, 558. Dati: doi:10.6084/m9.figshare.22202395, CC BY 4.0. Uso del suolo: ESA WorldCover 10 m 2021 v200, CC BY 4.0. Mappa: Natural Earth, pubblico dominio. Siti noti: Wikidata, CC0. Questo rapporto usa solo dati già pubblici nel repository.",
      sourcesH: "Da dove viene ogni numero",
      footer: "Rapporto divulgativo, 16 novembre 2026. Non sostituisce un articolo scientifico.",
      repo: "Codice e pack cieco su GitHub",
    },
    en: {
      docTitle: "Vaglio: an error-measured re-analysis of public G-LiHT lidar over the Yucatán",
      brand: "Vaglio · ArcheoEagle",
      title: "Vaglio: an error-measured re-analysis of public G-LiHT lidar over the Yucatán",
      lead: "Vaglio reads public lidar surveys, flags places where bare earth has the shape of a built structure, has them reviewed blind, and measures how often it is wrong. It does not declare sites. This is the public-facing report of facts already in the repository; the scientific report for peer review will come later.",
      tocMap: "Map",
      tocHow: "How it works",
      tocMeasure: "Measurements",
      tocCards: "Reviewed candidates",
      tocLimits: "What we do not know",
      nTransects: "transects scanned",
      nArea: "square kilometres",
      nCand: "candidate complexes",
      nHold: "hold up under review",
      nUnc: "remain uncertain",
      nTodo: "not yet reviewed",
      nOut: "discarded",
      s1: "This lidar survey has already been analysed by other teams (Estrada-Belli et al. 2025; Britton 2026, with a catalogue of 57,181 structures that is not yet public). Every candidate is presumed already known unless a comparison shows otherwise.",
      s2: "No candidate has been verified in the field. No claim is made about the age, culture or function of any candidate.",
      s3: "The review was carried out by AI agents of the same model. On control tiles they recognised 3–4 of 10 known buildings and flagged none of the 10 empty tiles as a structure. Their judgement is therefore used to confirm, not to rule out.",
      s4: "Candidate locations are not included in this document, to avoid exposing the places to looting.",
      s5: "Analysis and text were produced by AI assistants (Claude, GPT) under the supervision of Mirko Tornani, [role: to be filled in by the operator].",
      whyH: "How this started",
      why: "In November 2026 Pietro Miotti published a personal project: 48 AI agents looked at about 1,200 km² of NASA lidar over the Yucatán and flagged a Maya site that was not in the Mexican INAH register. Sarah Parcak noted that the site had already been published (Estrada-Belli et al. 2025). On 11 November Miotti recognised that the agents had rediscovered it. He was first to do something that works, and he corrected the record in public. Vaglio takes up his method and adds the measurements that were missing there.",
      mapH: "Where the lidar flew",
      mapCap: "The 456 public transects (strips about 400 m wide) sample the peninsula; they do not cover it. 1,272.7 km² is less than 1% of the Yucatán. Candidates are not plotted on the map, by design. The marker is Chactún, an already published site: the detector was trained and tested there, on annotations by archaeologists.",
      chactunPop: "Chactún (published site, Wikidata Q13518345). The detector was trained and tested here. It is not a Vaglio candidate.",
      howH: "How it works",
      step1t: "Terrain visualisations",
      step1: "From the bare-earth model it computes sky-view factor, openness and slope, with the parameters of Kokalj et al. 2023. It runs on a laptop, with no key and no graphics card.",
      step2t: "Detector",
      step2: "A per-pixel gradient-boosting classifier, trained on the Chactún annotations. It flags where the ground has the shape of a built structure. Outlines are coarse (overlap 0.566): it tells you where to look, not how to draw a plan.",
      step3t: "Candidate complexes",
      step3: "Reliefs within 60 m become a complex: that is the unit that is reviewed. A candidate complex is not a site. It is a place where the detector saw a shape.",
      step4t: "Blind review",
      step4: "Candidates are shown as 120 m tiles, with no name and no location, mixed with controls whose answer is known. At least two reviewers are required.",
      step5t: "Already known, and land cover",
      step5: "Every candidate on a survey that has already been studied is presumed already seen. Today's land cover (ESA WorldCover 2021) can also be read in the tile.",
      measH: "How often the detector is wrong",
      meas: "On 942 annotated structures in 329 Chactún tiles not used in training, the detector recovers 76.4%. Of 677 flags, 83.0% fall on an annotated structure. The success rule, written and committed before the test was run, required at least 70% on both counts: it was met.",
      measLim: "Every Chactún tile contains at least one structure: the 83% precision holds in ruin-dense terrain and has not been measured on empty, karst or cultivated ground. Chactún was surveyed with a different instrument, at a higher point density. How much the detector loses on the 2013 NASA data is not known.",
      figH: "What a reviewer sees",
      figLead: "These tiles are Chactún controls (Kokalj et al. 2023, CC BY 4.0), already public in the repository. They are not the Yucatán scan candidates: those images stay in the local dossier, because the surrounding terrain could expose the places. The original greyscale was coloured with the viridis ramp, keeping the relief shading: raised bodies appear yellow-green, open ground is purple. Each tile is 240 m across. This is not a photograph.",
      capStruct: "Control tile with a structure annotated by archaeologists.",
      capEmpty: "Empty control: no annotated building. Natural shapes may still be present.",
      open: "open ground",
      relief: "relief / low sky-view",
      revH: "How often the reviewers are wrong",
      rev: "Second round, after the first was voided because of a flaw in the controls: 40 candidates and 20 controls, three reviewers (Claude AI agents, independent of each other). On the 10 structure controls they recognised 4, 3 and 4. On the 10 empty controls none of the three ever said “structure”. They agree with each other on 90–97% of the candidates.",
      cardsH: "The 40 candidates already reviewed",
      cardsLead: "They were drawn when only the first transects had been scanned, all in the Centro block: the 20 with the highest score at that time, and 20 taken at random from the rest. Of the 20 then-highest, 12 hold up. Of the 20 random ones, 3 hold up. In the full scan those “top 20” sit between ranks 13 and 433 of 11,916. Of the first 100 candidates in the full scan, 3 have been reviewed. The score decides what to look at first: it is not a probability. Three reviewers of the same model who agree are not three independent confirmations. The agents recognise buildings with sharp sides and miss worn mounds: “15 hold up” undercounts how many of those 40 are built, and “25 uncertain” does not mean 25 false.",
      all: "All",
      holds: "Hold up",
      uncertain: "Uncertain",
      discarded: "Discarded",
      score: "Ordering score (not a probability)",
      votes: "Blind votes",
      noPos: "Location omitted.",
      isolated: "an isolated relief",
      nearby: "nearby reliefs",
      area: "covering {n} m² in all",
      height: "the tallest stands about {n} m above the ground",
      extent: "spread over {n} m",
      scanH: "The scan",
      scan: "All 456 transects were scanned, 1,272.7 km². 11,916 candidate complexes, containing 24,265 individual reliefs. 7,328 complexes (61%) are a single relief; 845 have at least 5; 214 have at least 10. Median complex area: 1,018 m²; the tallest relief stands a median 1.4 m above the ground. 249 candidates lie within 2 km of one of the 229 sites listed on Wikidata; the other 11,667 are marked “survey already analysed: presume already known”. No candidate has been compared with Britton’s catalogue or with the INAH register.",
      land: "Of the 1,548 candidates in the first 51 transects, 11 have at least 5% “built” in today’s land cover (ESA WorldCover 2021). Looked at one by one, not blind, all 11 are paved roads and their embankments. The same count on the full scan has not yet been run. The lidar is from 2013, the map from 2021. A dirt track in the forest is not classed as “built”. A modern settlement often sits on an older site: “built today” does not mean “not ancient”.",
      failH: "Things that were tried and did not work",
      fail: "Before Vaglio, a mound detector on the free 30 m terrain model (upper Khabur, Syria) failed a pre-registered test twice: it recovered 6 to 24% of the tall mounds, and in a blind scan 86 to 98 alarms in 100 were not catalogue mounds. That is why Vaglio works only where high-resolution lidar exists. The first review round was voided. Edge orthogonality, on 33 cases from a single block, does not help predict what reviewers keep. A “learned order” from the 40 reviews is not adopted until it passes a test written in advance.",
      unkH: "What we do not know",
      unk1: "How many of the 11,916 candidates are built structures. The reviewed sample comes from a single block and does not extend to the other six. “12 of 20” or “3 of 20” is not to be projected onto 11,916.",
      unk2: "How many are already in Britton’s catalogue or in the INAH register.",
      unk3: "The age, culture or function of any candidate.",
      unk4: "How much the detector loses on these data relative to Chactún.",
      unk5: "How the candidates fare outside the Centro block (mountainous Chiapas, the cultivated and inhabited north).",
      askH: "What we are asking",
      ask: "Three things, of people who know these data as their work: a comparison with the existing catalogue; a human reviewer on a blind pack, measured on the same controls (the only way to have someone who can also discard); and a view on the method. How the comparison is done is to be agreed. Locations, if they are needed, are decided by the operator, towards a named researcher at an institution.",
      reproH: "Reproducibility",
      repro: "Code and the blind pack (11,916 candidates, no locations) are in the public repository mtornani/ArcheoEagle, folder vaglio/. The pack was SHA-256 signed on 16 November 2026 at 17:27 UTC. Check it with: python -m vaglio verifica pack_cieco.json. Transects are downloaded from OpenTopography (about 31 GB). A full scan takes about four hours on four cores. The detector’s test criteria were written before the test was run.",
      creditsH: "Credits and licences",
      credits: "Lidar: NASA G-LiHT (AMIGA-Carb, 2013); reprocessed by B. J. Britton (2026), distributed by OpenTopography, doi:10.5069/G9Z899N1 and doi:10.5069/G9TH8JX9, PDDL. Training and controls: Kokalj, Ž., Džeroski, S., Šprajc, I. et al. (2023). Machine learning-ready remote sensing data for Maya archaeology. Scientific Data 10, 558. Data: doi:10.6084/m9.figshare.22202395, CC BY 4.0. Land cover: ESA WorldCover 10 m 2021 v200, CC BY 4.0. Map: Natural Earth, public domain. Known sites: Wikidata, CC0. This report uses only data already public in the repository.",
      sourcesH: "Where every figure comes from",
      footer: "Public-facing report, 16 November 2026. It is not a substitute for a scientific article.",
      repo: "Code and blind pack on GitHub",
    },
  };

  let lang = localStorage.getItem("vaglio-lang");
  if (lang !== "en" && lang !== "it") {
    lang = (navigator.language || "").toLowerCase().startsWith("en") ? "en" : "it";
  }

  function t(key) {
    return T[lang][key] || T.it[key] || key;
  }

  function fmtNum(n, digits) {
    const opts = digits == null ? {} : { minimumFractionDigits: digits, maximumFractionDigits: digits };
    return Number(n).toLocaleString(lang === "it" ? "it-IT" : "en-US", opts);
  }

  function applyText() {
    document.documentElement.lang = lang;
    document.title = t("docTitle");
    document.querySelectorAll("[data-i]").forEach((el) => {
      const key = el.getAttribute("data-i");
      el.textContent = t(key);
    });
    document.querySelectorAll(".lang button").forEach((b) => {
      b.setAttribute("aria-pressed", b.dataset.lang === lang ? "true" : "false");
    });
    const area = document.getElementById("n-area");
    if (area) area.textContent = fmtNum(1272.7, 1);
    const nCand = document.getElementById("n-cand");
    if (nCand) nCand.textContent = fmtNum(11916);
    const nTodo = document.getElementById("n-todo");
    if (nTodo) nTodo.textContent = fmtNum(11876);
    renderCards();
    renderGallery();
    const pop = document.getElementById("chactun-pop");
    if (pop) pop.textContent = t("chactunPop");
  }

  function plain(c) {
    const bits = [];
    bits.push(c.n_objects > 1 ? `${fmtNum(c.n_objects)} ${t("nearby")}` : t("isolated"));
    bits.push(t("area").replace("{n}", fmtNum(Math.round(c.area_m2))));
    bits.push(t("height").replace("{n}", fmtNum(Math.max(0, c.max_height_m), 1)));
    if (c.extent_m) bits.push(t("extent").replace("{n}", fmtNum(Math.round(c.extent_m))));
    return bits.join(", ") + ".";
  }

  function renderGallery() {
    const box = document.getElementById("gallery");
    const data = window.VAGLIO_REPORT;
    if (!box || !data) return;
    box.innerHTML = data.controls
      .map((c) => {
        const cap = c.kind === "struttura" ? t("capStruct") : t("capEmpty");
        return `<figure class="tile"><img src="${c.file}" alt="${cap}" width="480" height="480" loading="lazy"><figcaption>${cap}</figcaption></figure>`;
      })
      .join("");
  }

  let filter = "all";

  function renderCards() {
    const box = document.getElementById("cards");
    const data = window.VAGLIO_REPORT;
    if (!box || !data) return;
    const rows = data.reviewed.filter((c) => filter === "all" || c.outcome === filter);
    box.innerHTML = rows
      .map((c) => {
        const o = OUTCOME[c.outcome];
        const votes = (c.votes || [])
          .map((v) => {
            const lab = VERDICT[v.verdict] ? VERDICT[v.verdict][lang] : v.verdict;
            return `<span class="vote ${v.verdict}">${v.reviewer}: ${lab}</span>`;
          })
          .join("");
        const known = KNOWN[c.known] ? KNOWN[c.known][lang] : c.known;
        return `<article class="card" data-o="${c.outcome}" id="${c.label}">
          <div class="body">
            <span class="tag ${o.cls}">${o[lang]}</span>
            <h3>${c.label}</h3>
            <p class="plain">${plain(c)}</p>
            <p class="k">${t("score")}: ${fmtNum(c.score, 1)}</p>
            <p class="k">${t("votes")}</p>
            <div class="votes">${votes}</div>
            <p class="k">${known}.</p>
            <p class="k">${t("noPos")}</p>
          </div>
        </article>`;
      })
      .join("");
    document.querySelectorAll(".filters button").forEach((b) => {
      b.setAttribute("aria-pressed", b.dataset.f === filter ? "true" : "false");
    });
    const nAll = data.reviewed.length;
    const nHold = data.reviewed.filter((c) => c.outcome === "regge_alla_revisione").length;
    const nUnc = data.reviewed.filter((c) => c.outcome === "incerto").length;
    const nNo = data.reviewed.filter((c) => c.outcome === "scartato").length;
    const set = (id, label, n) => {
      const el = document.getElementById(id);
      if (el) el.textContent = `${label} (${n})`;
    };
    set("f-all", t("all"), nAll);
    set("f-ok", t("holds"), nHold);
    set("f-mid", t("uncertain"), nUnc);
    set("f-no", t("discarded"), nNo);
  }

  function initMap() {
    const el = document.getElementById("map");
    const cov = window.VAGLIO_COVERAGE;
    if (!el || !cov || typeof L === "undefined") return;

    // Vista iniziale prima di aggiungere i vettori (altrimenti Leaflet non proietta).
    const map = L.map(el, { scrollWheelZoom: false, attributionControl: true }).setView([18.8, -89.5], 6);
    // Nessuna base satellitare: solo i tratti già pubblici nel repository.
    map.attributionControl.setPrefix("");
    map.attributionControl.addAttribution("Natural Earth, pubblico dominio · transetti: OpenTopography / Britton 2026");

    const toLatLngs = (line) => line.map((p) => [p[1], p[0]]);
    const coast = L.layerGroup().addTo(map);
    cov.coast.forEach((ln) => {
      if (ln && ln.length >= 2) L.polyline(toLatLngs(ln), { color: "#1a1915", weight: 1.4, opacity: 0.9, interactive: false }).addTo(coast);
    });
    cov.borders.forEach((ln) => {
      if (ln && ln.length >= 2) L.polyline(toLatLngs(ln), { color: "#5c574c", weight: 1.1, dashArray: "5 3", opacity: 0.75, interactive: false }).addTo(coast);
    });
    cov.states.forEach((ln) => {
      if (ln && ln.length >= 2) L.polyline(toLatLngs(ln), { color: "#8a8478", weight: 0.8, opacity: 0.5, interactive: false }).addTo(coast);
    });

    const pad = L.featureGroup().addTo(map);
    // Rettangoli dei sette blocchi (visibili a scala di penisola) e assi dei transetti
    // (400 m di larghezza sarebbero invisibili come area: si disegnano come linee).
    Object.keys(cov.zones).forEach((z) => {
      const b = cov.zones[z].bbox; // w,s,e,n
      const color = ZONE_COLORS[z] || "#3a5fa8";
      L.rectangle([[b[1], b[0]], [b[3], b[2]]], {
        color, weight: 1, fillColor: color, fillOpacity: 0.12, interactive: false,
      }).addTo(pad);
    });
    cov.strips.forEach((s) => {
      const [w, s0, e, n] = s.bbox;
      const color = ZONE_COLORS[s.zone] || "#3a5fa8";
      const mid = (w + e) / 2;
      L.polyline([[s0, mid], [n, mid]], { color, weight: 3, opacity: 0.9, lineCap: "butt", interactive: false }).addTo(pad);
    });

    cov.places.forEach((p) => {
      L.circleMarker([p.lat, p.lon], {
        radius: 3,
        color: "#1a1915",
        fillColor: "#fffcf6",
        fillOpacity: 1,
        weight: 1,
      })
        .bindTooltip(p.name, { direction: "top", opacity: 0.9 })
        .addTo(map);
    });

    const ch = cov.chactun;
    const icon = L.divIcon({
      className: "chactun-icon",
      html: '<div style="width:16px;height:16px;border-radius:50%;background:#fde725;border:3px solid #1a1915;box-shadow:0 0 0 2px #fde725"></div>',
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    });
    const marker = L.marker([ch.lat, ch.lon], { icon, title: ch.name, keyboard: true }).addTo(map);
    marker.bindPopup(`<div id="chactun-pop">${t("chactunPop")}</div>`);

    map.fitBounds(pad.getBounds(), { padding: [16, 16] });

    const legend = document.getElementById("zone-legend");
    if (legend) {
      legend.innerHTML = Object.keys(cov.zones)
        .map((z) => {
          const rec = cov.zones[z];
          const col = ZONE_COLORS[z] || "#888";
          const km = fmtNum(rec.km2, 1);
          return `<span><i style="background:${col}"></i>${z} · ${km} km²</span>`;
        })
        .join("");
    }
  }

  function init() {
    document.querySelectorAll(".lang button").forEach((b) => {
      b.addEventListener("click", () => {
        lang = b.dataset.lang;
        localStorage.setItem("vaglio-lang", lang);
        applyText();
      });
    });
    document.querySelectorAll(".filters button").forEach((b) => {
      b.addEventListener("click", () => {
        filter = b.dataset.f;
        renderCards();
      });
    });
    applyText();
    initMap();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
