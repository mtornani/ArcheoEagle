# Vaglio blind test: sealed deposit

The fingerprint below seals `deposito.csv`, the full list of candidate complexes with coordinates.
The CSV itself is not in this repository: it goes privately to the key holder only
(PREREGISTRATION.md, sections 4 and 9). The commit that fills in this table is the seal.

| Field | Value |
|---|---|
| SHA-256 of `deposito.csv` | `53c140758f263560d998ce4ea256038ddd0dabc6cc4da566b8c8a013722fc8de` |
| Rows (candidate complexes) | 11,916 |
| Transects with at least one complex | 427 (of 456 scanned) |
| Created (UTC) | 2026-11-17T14:07:43+00:00 |
| Pre-registration | `PREREGISTRATION.md`, version 1 |

How it was produced, from a full re-scan of all 456 transects run on 17 November 2026 in a cloud container
(same code and frozen model as the scan behind `pack_cieco.json`):

```
cd vaglio
python -m vaglio deposito
```

The command prints the fingerprint and writes `vaglio_lavoro/deposito/MANIFEST.json`. Anyone holding the
CSV checks it with `sha256sum deposito.csv` (Linux/macOS) or `Get-FileHash deposito.csv` (Windows).

Consistency with `pack_cieco.json`, checked before sealing: same 11,916 complexes and the same blind-review
outcomes (15 `regge_alla_revisione`, 25 `incerto`, 11,876 `da_rivedere`). 47 complexes differ only in
decimals (for example area 1,791.2 vs 1,790.5 m²), most likely from different versions of the geometry libraries in the two environments;
the number of reliefs per complex is identical for all 11,916, and one maximum height differs by 0.01 m
(0.95 vs 0.96 m). The deposit, not the pack, is what is scored.

## Independent timestamp

`DEPOSIT.md.ots` is an OpenTimestamps proof of this file (and of the SHA-256 of `deposito.csv` recorded in the table above). It was submitted to the public calendar servers on 17 November 2026. Verify, with this file next to the proof:

```
ots verify DEPOSIT.md.ots
```

(`opentimestamps-client`; no account needed.) A pending attestation means the calendars have accepted the hash but it is not yet in a Bitcoin block. When it is, run `ots upgrade DEPOSIT.md.ots` and verify again. The original seal of the deposit remains git commit `525c212` (17 November 2026, 14:08 UTC).
