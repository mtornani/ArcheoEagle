# Vaglio blind test: pre-registration

Version 1 · written 17 November 2026 · committed to the public repository before any catalogue is seen.
This file, `score.py` and `footprints.geojson` are frozen from the commit that adds them. Any change
after that commit makes a new version (v2) with a new deposit; v1 results stay on record.

Operator: Mirko Tornani, independent researcher, not an archaeologist. Analysis and code were produced
by AI assistants (Claude, GPT) under his supervision.

---

## 1. Question

Do the candidate complexes that Vaglio extracted from the public G-LiHT lidar over the Yucatán coincide
with structures in an independent catalogue of the same data more often than chance, and how much of
that catalogue do they cover?

This is a test of the method against a key that the operator, the code and the AI assistants have
never seen. It is not a claim that any candidate is unknown.

## 2. What is tested

- **Data.** NASA G-LiHT 2013 transects over the Yucatán, reprocessed by B. J. Britton (2026) and
  distributed by OpenTopography (doi:10.5069/G9Z899N1, doi:10.5069/G9TH8JX9): 456 transects, 1,272.7 km².
- **Output under test.** Every candidate complex produced by the full Vaglio scan (11,916 complexes),
  exactly as sealed in the deposit (section 4). The detector, its thresholds and the grouping rules are
  frozen. The detector was trained on archaeologist annotations from Chactún (Kokalj et al. 2023) and
  passed a pre-registered held-out test there (recall 0.764, precision 0.830 on 942 structures).
- **Unit.** A *candidate complex*: reliefs that the detector judged structure-shaped, grouped when less
  than 60 m apart, represented by a centroid, an extent and an area.

## 3. Roles

| Role | Who | Does | Never does |
|---|---|---|---|
| Operator | Mirko Tornani | seals and sends the deposit; publishes the outcome | sees the key before scoring |
| Key holder | proposed: B. J. Britton | holds the catalogue; chooses the evaluation area and exclusions; runs `score.py` | receives anything but the deposit and these files |
| Code and AI assistants | Vaglio | nothing after the deposit | receive the key, ever |

The key holder may be anyone with a structure catalogue of these transects compiled independently of
Vaglio. If the key holder is not B. J. Britton, the name is added in a dated note below section 10
before scoring.

## 4. Sequence

1. The operator runs `python -m vaglio deposito` on the full scan. This writes `deposito.csv` (one row
   per complex: `deposit_id, transect, lon, lat, radius_m, extent_m, area_m2, n_objects, max_height_m,
   outcome`) and its SHA-256 fingerprint.
2. The operator commits the fingerprint to `DEPOSIT.md` in the public repository. The commit time is
   the seal. From this point the deposit cannot change.
3. The operator sends the key holder this file, `score.py`, `footprints.geojson`, and, privately,
   `deposito.csv`.
4. **Before running anything**, the key holder writes down the evaluation area (default: every transect
   the catalogue covers) and any exclusions with a one-line reason each. Mandatory exclusion: any
   transect that overlaps the Chactún, Lagunita or Tamchén lidar survey, because the detector was
   trained there.
5. The key holder runs `score.py` with `--expected-sha256` set to the committed fingerprint. The script
   stops if the deposit differs from the sealed one.
6. The key holder returns `results.json`. The part `for_key_holder_only` (lists of unmatched ids) may be
   withheld.
7. The operator publishes the outcome, pass or fail, in the project report, with wording agreed with
   the key holder. The key holder is free to publish independently.

## 5. Measures

All distances are in metres on the ground.

- **Match radius of a complex** `r = max(extent/2, sqrt(area/π), 10) + 20`. The extent is the largest
  distance between reliefs in the complex; the 20 m term absorbs centroid offsets between two methods
  that outline the same building differently.
- **Precision.** Share of deposit complexes in the evaluation area with at least one catalogue structure
  (point, or polygon centroid) within `r`. 95% interval: bootstrap over complexes, 2,000 resamples.
- **Coverage.** Share of catalogue structures in the evaluation area that lie within `r` of at least one
  complex.
- **Null 1, uniform.** Each complex replaced by a uniformly random point inside its own transect
  footprint, same radius. 200 repetitions.
- **Null 2, jitter.** Each complex moved 150–300 m in a random direction, kept inside its own transect
  footprint, same radius. 200 repetitions. This null keeps the large-scale settlement density and breaks
  the local alignment. It is the one that matters: in dense settlement a complex can sit near *someone
  else's* structure by chance, and only a null that keeps density measures that.
- **Breakdowns, descriptive only.** Precision by blind-review outcome (`regge_alla_revisione`, `incerto`,
  `da_rivedere`) and by flight block.
- **Evaluation area.** Only points inside the chosen transect footprints, for both sides. Footprints are
  simplified to about 120 vertices; points within a few metres of a transect edge may be dropped, the
  same way for both sides, and the count is reported.

Random seed: 20261117. Constants are at the top of `score.py`.

## 6. Pre-registered criteria

| | Criterion | Why this level |
|---|---|---|
| P1 | Precision ≥ 0.60 | On the Chactún test the detector reached 0.83 on terrain dense with ruins. 0.60 allows for a different sensor, sparser ground returns under canopy, and empty terrain. |
| P2 | Precision exceeds the jitter null mean by ≥ 0.20, **and** the lower end of its 95% interval is above the jitter null's 97.5th percentile | Agreement must come from position at the scale of a building, not from being in a settled area. |
| P3 | Coverage ≥ 0.30 | Vaglio keeps only complexes above a size and height gate, and isolated low mounds are often dropped. It is not expected to find most catalogue structures. Below 0.30 it misses too much to be useful as a first filter. |

**PASS** means P1, P2 and P3 all hold. Anything else is **FAIL**, reported with all numbers.

## 7. How to read the outcome

- If the catalogue was itself produced by an automated detector, the test measures **agreement between
  two methods**, not truth. Disagreements are not errors of either side by default.
- Optional, not part of the verdict: the key holder looks at up to 30 random unmatched deposit complexes
  and up to 30 random uncovered catalogue structures, and marks each as *structure*, *not a structure* or
  *unclear*. This says which side the disagreements fall on.
- A PASS does not mean any candidate is new, ancient or Maya. It means the method's output can be used
  with a known error rate as a first filter.
- A FAIL is published. The method is then changed only through a new pre-registration and a new deposit.

## 8. Known limitations, declared in advance

- 40 complexes went through blind review, all from one flight block (Centro). Review outcomes are
  descriptive in this test.
- The AI reviewers recognised 3–4 of 10 known buildings on hidden controls and flagged none of 10 empty
  tiles. They are not used to filter the deposit: the deposit contains every complex.
- Present-day land cover (ESA WorldCover 2021) is not used to filter the deposit.
- Chactún-like training bias: the detector learned from one area of dense, sharp-edged architecture.
  Eroded or low structures are expected to be under-detected, which lowers coverage.

## 9. Privacy

`deposito.csv` contains coordinates. It is sent only to the key holder, is never published, and may be
deleted after scoring. `results.json` contains no coordinates. Locations of unexcavated remains are not
published by either side.

## 10. What will not happen

- No re-run with different parameters after seeing any part of the key.
- No dropping of transects after scoring; exclusions are declared before.
- No reporting of a subset of the measures.

---

Notes added after the commit of this file (dated, appended only):
