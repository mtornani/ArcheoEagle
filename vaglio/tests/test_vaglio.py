"""Test offline di Vaglio. I terreni qui sono FIXTURE: verificano l'aritmetica,
non sostengono nessuna affermazione su siti reali."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from vaglio import known, relief, report, review, scan
from vaglio import model as M
from vaglio.__main__ import _is_candidate


class ReliefTest(unittest.TestCase):
    def test_flat_ground_is_fully_open(self):
        svf, opn = relief.svf_openness(np.zeros((60, 60), np.float32))
        self.assertAlmostEqual(float(svf.min()), 1.0, places=5)
        self.assertAlmostEqual(float(opn.mean()), 90.0, places=3)

    def test_pit_closes_the_sky_and_mound_top_opens_it(self):
        yy, xx = np.mgrid[0:80, 0:80]
        bump = 3 * np.exp(-((yy - 40) ** 2 + (xx - 40) ** 2) / 50.0)
        svf_pit, opn_pit = relief.svf_openness((-bump).astype(np.float32))
        svf_top, opn_top = relief.svf_openness(bump.astype(np.float32))
        self.assertLess(svf_pit[40, 40], 0.9)
        self.assertGreater(opn_top[40, 40], 95.0)       # sopra un dosso l'orizzonte scende sotto l'orizzontale
        self.assertAlmostEqual(float(svf_top[40, 40]), 1.0, places=5)

    def test_bands_survive_nodata_without_inventing_edges(self):
        dem = np.full((50, 50), 100.0, np.float32)
        dem[:, 30:] = np.nan
        b, valid = relief.bands(dem)
        self.assertEqual(b.shape, (50, 50, 3))
        self.assertFalse(valid[:, 30:].any())
        self.assertEqual(int(b[25, 10, 2]), 255)         # piano = pendenza zero = bianco


class ObjectsTest(unittest.TestCase):
    def test_small_blobs_are_not_objects(self):
        m = np.zeros((100, 100), bool)
        m[10:14, 10:14] = True        # 4 m2
        m[40:60, 40:60] = True        # 100 m2
        self.assertEqual(M.objects(m)[1], 1)

    def test_score_counts_found_and_right_separately(self):
        truth = np.zeros((120, 120), bool); truth[20:40, 20:40] = True; truth[80:100, 80:100] = True
        prob = np.zeros((120, 120), np.float32); prob[20:40, 20:40] = 1; prob[20:40, 80:100] = 1
        s = M.score_tile(prob, truth)
        self.assertEqual((s["truth"], s["found"], s["pred"], s["right"]), (2, 1, 2, 1))

    def test_features_have_fixed_width(self):
        self.assertEqual(M.features(np.zeros((32, 32, 3), np.uint8)).shape, (32, 32, 24))


class ClusterTest(unittest.TestCase):
    def obj(self, x, y, area=60.0, h=1.0):
        return {"x": x, "y": y, "area_m2": area, "prob": 0.9, "height_m": h, "elong": 1.5, "rect": 0.8}

    def test_near_objects_form_one_complex_far_ones_do_not(self):
        cs = scan.cluster([self.obj(0, 0), self.obj(30, 0), self.obj(55, 10), self.obj(900, 900)])
        self.assertEqual(sorted(c["n_objects"] for c in cs), [1, 3])

    def test_overlap_duplicates_count_once(self):
        self.assertEqual(len(scan._dedupe([self.obj(0, 0, 80), self.obj(2, 1, 60), self.obj(100, 0)])), 2)

    def test_square_platform_is_more_orthogonal_than_round_mound(self):
        yy, xx = np.mgrid[0:120, 0:120]
        sq = np.zeros((120, 120), np.float32); sq[40:80, 40:80] = 2.0
        rd = (2.0 * (np.hypot(yy - 60, xx - 60) < 20)).astype(np.float32)
        o_sq = scan.orthogonality(sq, sq > 0)
        o_rd = scan.orthogonality(rd, rd > 0)
        self.assertGreater(o_sq, 0.6)
        self.assertLess(o_rd, 0.2)

    def test_priority_gate_is_explicit(self):
        base = {"n_objects": 1, "area_m2": 60.0, "max_height_m": 2.0}
        self.assertFalse(_is_candidate(base))
        self.assertTrue(_is_candidate({**base, "n_objects": 3, "area_m2": 180.0}))
        self.assertTrue(_is_candidate({**base, "area_m2": 200.0}))
        self.assertFalse(_is_candidate({**base, "area_m2": 200.0, "max_height_m": 0.2}))


class ReviewTest(unittest.TestCase):
    key = {**{f"r_{i:04d}": {"kind": "pos", "ref": f"p{i}"} for i in range(1, 9)},
           **{f"r_{i:04d}": {"kind": "neg", "ref": f"n{i}"} for i in range(9, 17)},
           "r_0017": {"kind": "cand", "ref": "V-aaa"}, "r_0018": {"kind": "cand", "ref": "V-bbb"}}

    def answers(self, pos, neg, cand):
        out = [{"item": i, "verdict": pos if v["kind"] == "pos" else neg if v["kind"] == "neg" else cand}
               for i, v in self.key.items()]
        return out

    def test_yes_man_can_neither_confirm_nor_be_trusted(self):
        g = review.grade_reviewer(self.key, self.answers("struttura", "struttura", "struttura"))
        self.assertEqual((g["sensitivity"], g["specificity"]), (1.0, 0.0))
        self.assertFalse(g["can_confirm"])
        self.assertTrue(g["can_discard"])      # ma non scartera' mai niente

    def test_two_reviewers_are_needed_to_hold(self):
        good = self.answers("struttura", "naturale", "struttura")
        self.assertEqual(review.ingest(self.key, {"a": good})["candidates"]["V-aaa"]["outcome"], "incerto")
        self.assertEqual(review.ingest(self.key, {"a": good, "b": good})["candidates"]["V-aaa"]["outcome"], "regge_alla_revisione")

    def test_cautious_reviewer_confirms_but_cannot_discard(self):
        # trova 2 strutture note su 8, non sbaglia mai un vuoto: e' il caso misurato il 16 nov 2026
        def cautious(cand):
            out = self.answers("naturale", "naturale", cand)
            for r in out[:2]:
                r["verdict"] = "struttura"
            return out
        g = review.grade_reviewer(self.key, cautious("naturale"))
        self.assertTrue(g["can_confirm"]); self.assertFalse(g["can_discard"])
        no = review.ingest(self.key, {"a": cautious("naturale"), "b": cautious("naturale")})
        self.assertEqual(no["candidates"]["V-aaa"]["outcome"], "incerto")          # il suo "naturale" non scarta
        yes = review.ingest(self.key, {"a": cautious("struttura"), "b": cautious("struttura")})
        self.assertEqual(yes["candidates"]["V-aaa"]["outcome"], "regge_alla_revisione")

    def test_yes_man_vote_is_recorded_but_does_not_confirm(self):
        bad = self.answers("struttura", "struttura", "struttura")
        res = review.ingest(self.key, {"x": bad, "y": bad})
        c = res["candidates"]["V-aaa"]
        self.assertEqual(c["outcome"], "incerto")
        self.assertEqual(len(c["all_votes"]), 2)

    def test_balanced_reviewers_can_discard(self):
        good = self.answers("struttura", "naturale", "naturale")
        self.assertEqual(review.ingest(self.key, {"a": good, "b": good})["candidates"]["V-aaa"]["outcome"], "scartato")

    def test_pack_hides_which_images_are_controls(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as d:
            d = Path(d); (d / "chips").mkdir()
            cands = [{"id": f"V-{k}"} for k in range(5)]
            for c in cands:
                Image.new("L", (480, 480)).save(d / "chips" / f"{c['id']}.jpg")
            info = review.make_pack(cands, d / "chips", d / "review", "p1", n_controls=10)
            names = sorted(p.name for p in (d / "review" / "p1").glob("*.jpg"))
            self.assertEqual((info["candidates"], info["controls"], len(names)), (5, 10, 15))
            self.assertTrue(all(n.startswith("r_") for n in names))        # nessun nome rivela l'origine
            self.assertFalse((d / "review" / "p1" / "p1.json").exists())   # la chiave non sta nel pacco
            self.assertTrue((d / "review" / "keys" / "p1.json").exists())


class LearnTest(unittest.TestCase):
    def cand(self, i, ortho, area=300.0):
        return {"id": f"V-{i}", "area_m2": area, "n_objects": 2, "max_height_m": 1.0, "mean_prob": 0.8, "ortho": ortho, "max_rect": 0.6}

    def test_refuses_to_learn_from_too_few_reviews(self):
        from vaglio import learn
        cs = [self.cand(i, 0.5) for i in range(6)]
        self.assertFalse(learn.fit(cs, {c["id"]: "scartato" for c in cs})["fitted"])

    def test_learns_what_reviewers_kept_and_reports_held_out_skill(self):
        from vaglio import learn
        rng = np.random.default_rng(0)
        kept = [self.cand(i, 0.5 + 0.2 * rng.random()) for i in range(15)]
        drop = [self.cand(100 + i, 0.2 * rng.random()) for i in range(15)]
        m = learn.fit(kept + drop, {**{c["id"]: "regge_alla_revisione" for c in kept}, **{c["id"]: "scartato" for c in drop}})
        self.assertTrue(m["fitted"])
        self.assertGreater(m["auc_loo"], 0.9)
        self.assertGreater(learn.priority(self.cand(999, 0.6), m), learn.priority(self.cand(998, 0.05), m))


class KnownAndBlindTest(unittest.TestCase):
    def test_surveyed_data_is_presumed_already_seen(self):
        s = known.status({"lat": 18.0, "lon": -89.0}, [("X", 19.5, -89.0, "t")], "G-LiHT Yucatan 2013")
        self.assertEqual(s["label"], "rilievo_gia_analizzato")
        self.assertTrue(s["prior_work"])

    def test_known_site_nearby_wins(self):
        s = known.status({"lat": 18.0, "lon": -89.0}, [("Sito", 18.005, -89.0, "t")], "G-LiHT Yucatan 2013")
        self.assertEqual(s["label"], "sito_noto_vicino")
        self.assertLess(s["nearest"]["km"], 1.0)

    def test_no_outcome_is_ever_called_new_or_found(self):
        words = " ".join(list(report.OUTCOME) + list(report.KNOWN) + [v[0] for v in report.OUTCOME.values()] + list(report.KNOWN.values())).lower()
        for banned in ("scopert", "trovat", "nuovo", "confermat"):
            self.assertNotIn(banned, words)

    def test_blind_pack_has_no_location(self):
        c = {"id": "V-1", "lon": -89.123456, "lat": 18.654321, "x": 831000.5, "y": 2055000.5, "transect": "South_GLAS_l3s459",
             "score": 10.0, "n_objects": 3, "area_m2": 200.0, "max_height_m": 1.2, "outcome": "da_rivedere", "votes": [],
             "known": {"label": "sito_noto_vicino", "nearest": {"name": "Nadzcaan", "km": 0.4, "source": "w"}, "prior_work": []}}
        pack = report.blind_pack([c], "2026-11-16T00:00:00+00:00")
        blob = json.dumps(pack)
        for leak in ("89.123", "18.654", "831000", "South_GLAS", "Nadzcaan", "V-1"):
            self.assertNotIn(leak, blob)
        self.assertEqual(pack["hash"], report.blind_pack([c], "2026-11-16T00:00:00+00:00")["hash"])


if __name__ == "__main__":
    unittest.main()
