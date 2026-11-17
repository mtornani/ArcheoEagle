# Vaglio blind test: sealed deposit

The fingerprint below seals `deposito.csv`, the full list of candidate complexes with coordinates.
The CSV itself is not in this repository: it goes privately to the key holder only
(PREREGISTRATION.md, sections 4 and 9). The commit that fills in this table is the seal.

| Field | Value |
|---|---|
| SHA-256 of `deposito.csv` | `TO BE FILLED BY THE OPERATOR` |
| Rows (candidate complexes) | `TO BE FILLED` (expected 11,916) |
| Transects with at least one complex | `TO BE FILLED` |
| Created (UTC) | `TO BE FILLED` |
| Pre-registration | `PREREGISTRATION.md`, version 1 |

How it was produced, on the operator's computer, from the full scan:

```
cd vaglio
python -m vaglio deposito
```

The command prints the fingerprint and writes `vaglio_lavoro/deposito/MANIFEST.json`. Anyone holding the
CSV checks it with `sha256sum deposito.csv` (Linux/macOS) or `Get-FileHash deposito.csv` (Windows).
