import type { RankRow } from './types'

export interface CorridorBrief {
  id: string
  why: string
  whatWater: string
  whatYouCanSay: string
  whatYouCannot: string
  next: string[]
  source: string
}

export const BRIEFS: Record<string, CorridorBrief> = {
  tamanrasset: {
    id: 'tamanrasset',
    why: 'È la strada ovest: Hoggar verso l’Atlantico. Se una cultura stava sull’acqua del Sahara occidentale, i nodi di questo fiume sono il posto onesto da camminare. Non perché “sembra Atlantide”: perché l’acqua andava al mare oltre Gibilterra.',
    whatWater: 'Nel periodo umido africano (circa 14.500–5.500 anni fa) il Sahara non era deserto. Questo tracciato è schematico da letteratura (Skonieczny et al. 2015): un paleofiume, non un canale da te disegnato.',
    whatYouCanSay: 'Puoi dire: qui l’acqua c’era; qui due rami si toccano; qui il testo di Platone “oltre le Colonne” può applicarsi in lettura letterale (ovest di Gibilterra). Puoi classificare tappe. Non puoi proclamare una città.',
    whatYouCannot: 'Da casa non dati un palazzo, non trovi oricalco, non chiudi “è Atlantide”. Il radar L-band (sotto sabbia) ancora non gira qui. Lo scavo è un altro mestiere, e in zona spesso non ci vai.',
    next: [
      'Apri la tappa A (di solito una confluenza). Leggi “in parole povere”, non il numero.',
      'Confronta A, B, C con le stesse colonne. Se la classifica ti sembra ovvia, è un buon segno. Se no, il residuo è ancora alto.',
      'Chiediti cosa ucciderebbe A da casa (idrologia impossibile, età sbagliata). Se non trovi kill-shot, resta aperto — non “confermato”.',
    ],
    source: 'Skonieczny et al. 2015, Nature Communications — Tamanrasset paleoriver',
  },
  megachad: {
    id: 'megachad',
    why: 'Mega-Chad era un mare interno. Le sponde sono il posto dove “isola” può voler dire altura nell’acqua, non oceano. Platone parla di isola: questa è la lettura idrica, non l’icona circolare.',
    whatWater: 'Alta sponda del periodo umido. Taffassasset ci arriva da nord. Un anello schematico sulla mappa è la linea di riva, non una città.',
    whatYouCanSay: 'Puoi dire: qui un lago enorme ha lasciato una costa. Un insediamento starebbe sulla riva o su un’altura che l’acqua isolava. “Isola” può sostenere senza anelli.',
    whatYouCannot: 'L’anello sulla mappa non è Platone. È un paleolago. Confondere riva e città è pareidolia.',
    next: [
      'Guarda le tappe di tipo sponda, non il centro del lago.',
      'Nel confronto, una sponda con Platone “isola = +” non batte una confluenza se l’idro è più debole. Leggi le colonne, non il mito.',
    ],
    source: 'Ricostruzioni AHP Mega-Chad (highstand ~320 m) + Drake et al. 2011',
  },
  sahabi: {
    id: 'sahabi',
    why: 'Qui la scienza ha già visto fiumi sotto la sabbia (radar SIR-A). È il corridoio che insegna il metodo: non la pelle del deserto, ciò che è sepolto.',
    whatWater: 'Sistema libico sepolto, verso il golfo della Sirte. L’acqua non si vede in superficie. Si è vista col radar.',
    whatYouCanSay: 'Puoi dire: “sotto il Sahara” è un fatto per i canali. Una struttura, se c’è, starebbe su quei canali. Questo corridoio giustifica il radar come prossimo strumento.',
    whatYouCannot: 'Sentinel ottico qui vede sabbia. Senza L-band stai camminando uno schema, non l’immagine sotto.',
    next: [
      'Tratta ogni tappa come “qui il radar dovrebbe mostrare l’alveo”. Se un giorno il layer radar arriva, questa è la strada su cui accenderlo.',
      'Non cercare anelli in Libia perché YouTube li cerca in Mauritania.',
    ],
    source: 'Paillou / SIR-A–C — canali sepolti Sahabi',
  },
  irharhar: {
    id: 'irharhar',
    why: 'Hoggar verso nord, Chotts / Mediterraneo. Stessa testa d’acqua del Tamanrasset, direzione opposta. Serve a non innamorarti di un solo mare.',
    whatWater: 'Corridoio nord. Se la memoria è “verso un grande mare”, questo mare è il Mediterraneo, non l’Atlantico.',
    whatYouCanSay: 'Puoi confrontare nord vs ovest: due strade, una sorgente. La tesi deve sopravvivere a entrambe o dichiarare perché una sola.',
    whatYouCannot: 'Scegliere Irharhar perché “è più vicino all’Egitto del racconto” è già un prior sul testo. Dichiaralo.',
    next: [
      'Cammina Tamanrasset e Irharhar. Confronta le due classifiche, non una sola.',
      'Se Platone “Colonne” sostiene solo l’ovest, il nord resta un controllo, non uno scarto.',
    ],
    source: 'Corridoi verdi sahariani — Drake et al. 2011 PNAS',
  },
  tilemsi: {
    id: 'tilemsi',
    why: 'Verso il Niger, non verso un oceano. Se Atlantide-nel-Sahara fosse una civiltà dell’acqua interna (delta, non mare), questa è una strada.',
    whatWater: 'Adrar des Ifoghas verso il Niger. Delta interno = nodi, non foce marina.',
    whatYouCanSay: 'Puoi testare la lettura “non serve l’Atlantico”. Se i nodi qui sono deboli e a ovest no, la tesi marina tiene meglio. Se è il contrario, rivedi Platone “oltre le Colonne”.',
    whatYouCannot: 'Il Niger di oggi non è il paleofiume. Non mescolare il fiume vivo e quello fossile.',
    next: [
      'Confronta una tappa Tilemsi con una Tamanrasset. Stesse colonne. Quale residuo è più basso, e perché.',
    ],
    source: 'Paleodrenaggio Sahel / Niger',
  },
  howar: {
    id: 'howar',
    why: 'Wadi Howar, il “Nilo giallo”: il Sahara est parla al Nilo. Se la memoria passa per l’Egitto (Solone, i preti), questa è la strada che tocca quel racconto senza cercare anelli a ovest.',
    whatWater: 'Corridoio est verso il Nilo. Acqua che finisce in un fiume famoso, non in oceano.',
    whatYouCanSay: 'Puoi dire: esiste un nastro d’acqua che collega deserto e Nilo. Il telefono senza fili egizio può essere memoria di questo, o di altro. Qui Platone “Colonne” è N/A: siamo a est di Gibilterra.',
    whatYouCannot: 'Vicino all’Egitto ≠ è il testo di Platone. È un controllo. Non una conferma.',
    next: [
      'Nota i N/A su “oltre le Colonne”. Non forzarli a −. Non forzarli a +.',
      'Chiediti: il racconto parte dall’Egitto. Questa strada è più vicina al narratore. È un vantaggio o un bias?',
    ],
    source: 'Ghoneim & El-Baz — paleodrenaggio Sahara orientale / Yellow Nile',
  },
}

export const METHOD = [
  {
    term: 'Residuo (ρ)',
    meaning: 'Quanto le colonne non si parlano. Basso = idro, (eventuale) forma e Platone applicabile sono d’accordo. Non significa “più Atlantide”. Un ρ basso su una confluenza vuol dire: è un buon nodo d’acqua. Punto.',
  },
  {
    term: 'Tappa',
    meaning: 'Un punto sulla rete: confluenza, sponda, alveo, testa/foce. Non è un sito. È dove, se qualcuno viveva sull’acqua, avrebbe avuto un motivo per stare.',
  },
  {
    term: 'Platone + / − / N/A',
    meaning: '+ = quella frase, letta in un modo dichiarato, è compatibile. − = la contraddice e non è deriva linguistica. N/A = non misurabile da casa, o il testo può voler dire altro. N/A non è un no. Non è un sì.',
  },
  {
    term: 'Kill-shot',
    meaning: 'Cosa, da questo PC, chiude la tappa. Se non c’è, resta aperta. Aperto ≠ trovato.',
  },
  {
    term: 'Pareidolia',
    meaning: 'Il cervello 2026 cerca anelli e palazzi. Questo strumento li nasconde finché non sono misurati. Se li cerchi comunque, stai usando lo strumento contro di te.',
  },
]

const NODE_WHY: Record<string, string> = {
  confluence: 'Due acque si toccano. Campi, porti interni, villaggi nascono qui in quasi ogni idrografia umana nota. Prior alto. Non è un palazzo.',
  paleolake_shore: 'Riva di un lago morto. Pesca, approdo, isola stagionale. “Isola” nel testo può essere questo, non un cerchio in mezzo al mare.',
  channel: 'Sei sull’alveo, non su un incrocio. Meno speciale. Serve come controllo: se un alveo batte una confluenza, qualcosa nella classifica puzza.',
  head_or_mouth: 'Inizio o fine dell’acqua. Sorgente in montagna, o foce in mare/lago. La foce atlantica è dove “oltre le Colonne” diventa geografica, non poetica.',
}

export function plainSpeak(row: RankRow): string {
  const kind = NODE_WHY[row.node_type || ''] || 'Questo punto non è sulla rete nota. Alto residuo. Trattalo come rumore finché un fiume o un radar non lo collega.'
  const rho = row.residual < 0.15
    ? 'Le colonne che abbiamo sono d’accordo. Va letto, non festeggiato.'
    : row.residual < 0.35
      ? 'C’è accordo parziale. Qualcosa manca o tira da un’altra parte.'
      : 'Le colonne non si parlano. Non costruire una storia sopra.'
  const shape = row.geometry_score == null
    ? 'Nessuna forma misurata: corretto. Non inventarla.'
    : 'C’è una forma misurata. Guardala dopo l’acqua, non prima.'
  return `${kind} ${rho} ${shape}`
}

export function nextQuestions(row: RankRow): string[] {
  const q: string[] = []
  if (row.node_type === 'confluence') {
    q.push('Se qui c’era acqua, che cosa (altro da un palazzo) spiegherebbe un’anomalia? Canale, argine, nulla.')
  }
  if (row.node_type === 'paleolake_shore') {
    q.push('Questa sponda sarebbe stata isola, penisola o riva secca a seconda del livello. Quale livello stai immaginando, e da dove lo sai?')
  }
  if (row.plato.some((p) => p.id === 'beyond_pillars' && p.verdict === 'support')) {
    q.push('“Oltre le Colonne” qui è +. Va bene. Non farne il resto del caso. Quante altre colonne sono N/A?')
  }
  if (row.plato.every((p) => p.verdict === 'na' || p.verdict === 'support') && !row.plato.some((p) => p.verdict === 'contradict')) {
    q.push('Nessun −. Non è una vittoria: molte frasi sono N/A. Conta quante sono misurabili. Poche = testo debole qui, non testo vero.')
  }
  q.push('Cosa, da questo schermo, ucciderebbe la tappa? Se non lo sai, scrivilo nel pack: “kill-shot assente”.')
  q.push('Un secondo umano, senza coordinate, metterebbe questa lettera prima delle altre? Apri Confronta e rispondi da lì.')
  return q
}

export function walkSummary(rows: RankRow[]): string {
  const n = rows.length
  const top = rows[0]
  if (!top) return 'Nessuna tappa. Fuori rete o corridoio vuoto.'
  const kind = top.node_type === 'confluence'
    ? 'una confluenza'
    : top.node_type === 'paleolake_shore'
      ? 'una sponda di paleolago'
      : 'un nodo di rete'
  return `Hai camminato ${n} tappe. La prima in classifica (${top.label}) è ${kind}, residuo ${top.residual.toFixed(2)}. Questo dice dove l’acqua ha un nodo, non dove sta una civiltà. Adesso leggi quella tappa in parole povere, poi Confronta le prime tre.`
}
