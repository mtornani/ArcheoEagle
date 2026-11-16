"""Cancello della flotta (CLAUDE.md §12). Offline: nessun test tocca la rete."""
import json
import tempfile
import unittest
from pathlib import Path

from core.fleet import gate
from core.fleet.__main__ import SOURCES, load_queue, load_sources, review, submit

SRC = {
    "ncei_tsunami": {"id": "ncei_tsunami", "status": "ok"},
    "pangaea": {"id": "pangaea", "status": "ok"},
    "xronos": {"id": "xronos", "status": "unverified"},
    "imlgs": {"id": "imlgs", "status": "dead"},
    "emag2": {"id": "emag2", "status": "ok", "role": "natural_explainer"},
}


def good(**over):
    f = {
        "agent": "scout-sismo-tsunami",
        "claim": "runup nel catalogo NCEI a data X senza sorgente sismica associata",
        "tipo": "seismic",
        "source_id": "ncei_tsunami",
        "source_ref": "hazel/api/v1/tsunamis/events?minYear=1700&maxYear=1700",
        "measure": {"value": 5.0, "unit": "m", "method": "runup massimo"},
        "null": {"description": "eventi casuali stessa regione/periodo", "p": 0.001, "n_tested": 20},
        "control": {"name": "Cascadia 1700", "passed": True},
        "can_say": "c'e' un runup documentato",
        "cannot_say": "chi c'era",
        "kill_shot": "aperto",
        "myth_blind": True,
        "where": {"lon": 1.0, "lat": 2.0, "place": "segreto"},
    }
    f.update(over)
    return f


class TriageTest(unittest.TestCase):
    def test_complete_calibrated_flag_asks_second_check(self):
        self.assertEqual(gate.triage(good(), SRC)[0], gate.SECONDA_VERIFICA)

    def test_failed_positive_control_is_not_an_anomaly(self):
        # Bama Ridge oggi: il controllo fallisce -> nessuna segnalazione dal terreno
        g, _ = gate.triage(good(control={"name": "Bama Ridge", "passed": False}), SRC)
        self.assertEqual(g, gate.NON_CALIBRATO)
        self.assertEqual(gate.triage(good(control=None), SRC)[0], gate.NON_CALIBRATO)

    def test_multiple_comparisons_count(self):
        # p=0.01 e' "significativo" finche' non dici che hai guardato 50 candidati
        g, why = gate.triage(good(null={"description": "x", "p": 0.01, "n_tested": 50}), SRC)
        self.assertEqual(g, gate.SOTTO_IL_CASO)
        self.assertIn("niente sopra il caso", why[0])

    def test_no_null_no_anomaly(self):
        self.assertEqual(gate.triage(good(null=None), SRC)[0], gate.SOTTO_IL_CASO)

    def test_missing_fields_rejected(self):
        g, why = gate.triage(good(kill_shot="", measure={}), SRC)
        self.assertEqual(g, gate.RESPINTO)
        self.assertEqual(len(why), 2)

    def test_dead_or_unknown_source_rejected(self):
        self.assertEqual(gate.triage(good(source_id="imlgs"), SRC)[0], gate.RESPINTO)
        self.assertEqual(gate.triage(good(source_id="blog"), SRC)[0], gate.RESPINTO)

    def test_explainer_sources_cannot_carry_a_flag(self):
        # la griglia magnetica a 3,7 km spiega un dicco, non trova un muro
        g, why = gate.triage(good(source_id="emag2"), SRC)
        self.assertEqual(g, gate.RESPINTO)
        self.assertIn("non e' un rilevatore", why[0])

    def test_unverified_source_is_uncalibrated(self):
        self.assertEqual(gate.triage(good(source_id="xronos"), SRC)[0], gate.NON_CALIBRATO)

    def test_traps_and_cartoon_strings_rejected(self):
        self.assertEqual(gate.triage(good(claim="anelli alla Richat"), SRC)[0], gate.RESPINTO)
        self.assertEqual(gate.triage(good(can_say="Atlantide found"), SRC)[0], gate.RESPINTO)

    def test_candidate_must_come_from_data_not_myth(self):
        self.assertEqual(gate.triage(good(myth_blind=False), SRC)[0], gate.RESPINTO)

    def test_text_is_a_column_never_a_flag(self):
        g, _ = gate.triage(good(tipo="plato_text", myth_blind=False), SRC)
        self.assertEqual(g, gate.COLONNA)


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.flag = good()
        self.flag["grade"] = gate.SECONDA_VERIFICA

    def rev(self, **over):
        r = {"reviewer": "scettico", "verdict": "sopravvive", "reason": "serie indipendente concorda",
             "independent_source_id": "pangaea"}
        r.update(over)
        return r

    def test_survives_with_independent_source_goes_deep(self):
        self.assertEqual(gate.apply_review(self.flag, self.rev(), SRC)[0], gate.VERIFICA_APPROFONDITA)

    def test_author_cannot_review_itself(self):
        self.assertIsNone(gate.apply_review(self.flag, self.rev(reviewer=self.flag["agent"]), SRC)[0])

    def test_same_or_unverified_source_stays_open(self):
        for sid in ("ncei_tsunami", "xronos", None):
            g, _ = gate.apply_review(self.flag, self.rev(independent_source_id=sid), SRC)
            self.assertEqual(g, gate.SECONDA_VERIFICA)

    def test_killed_is_a_public_fail(self):
        self.assertEqual(gate.apply_review(self.flag, self.rev(verdict="ucciso"), SRC)[0], gate.FAIL)

    def test_only_queued_flags_are_reviewed(self):
        self.flag["grade"] = gate.NON_CALIBRATO
        self.assertIsNone(gate.apply_review(self.flag, self.rev(), SRC)[0])


class BlindAndQueueTest(unittest.TestCase):
    def test_blind_pack_has_no_coordinates(self):
        pack = gate.make_blind_pack([good()], "2026-11-16T00:00:00+00:00")
        blob = json.dumps(pack)
        for leak in ("lon", "lat", "segreto", "where"):
            self.assertNotIn(leak, blob)
        again = gate.make_blind_pack([good()], "2026-11-16T00:00:00+00:00")
        self.assertEqual(pack["hash"], again["hash"])
        self.assertEqual(len(pack["hash"]), 64)

    def test_submit_then_review_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "queue.jsonl"
            f = submit(good(), queue=q)
            self.assertEqual(f["grade"], gate.SECONDA_VERIFICA)
            review({"flag_id": f["id"], "reviewer": "scettico", "verdict": "ucciso",
                    "reason": "artefatto di cucitura"}, queue=q)
            self.assertEqual(load_queue(q)[f["id"]]["grade"], gate.FAIL)
            # il rumore si registra: anche chi non passa resta agli atti
            bad = submit(good(null=None), queue=q)
            self.assertEqual(load_queue(q)[bad["id"]]["grade"], gate.SOTTO_IL_CASO)


class RegistryTest(unittest.TestCase):
    def test_registry_rows_are_complete(self):
        src = load_sources(SOURCES)
        self.assertGreaterEqual(len(src), 15)
        for s in src.values():
            for k in ("id", "domain", "name", "access", "status", "checked", "can_say", "cannot_say"):
                self.assertTrue(s.get(k), f"{s.get('id')}: {k}")
            self.assertIn(s["status"], {"ok", "unverified", "key", "manual", "dead"})
        self.assertEqual(src["imlgs"]["status"], "dead")


if __name__ == "__main__":
    unittest.main()
