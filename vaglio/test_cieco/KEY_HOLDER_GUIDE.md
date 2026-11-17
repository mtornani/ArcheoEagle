# For the key holder: running the blind test in about ten minutes

Thank you for considering this. You hold the answer; Vaglio never sees it.

## You receive

- `PREREGISTRATION.md`: what is tested, how it is scored, and the pass criteria, fixed in advance.
- `score.py`: the scorer. Python 3.8 or newer, standard library only.
- `footprints.geojson`: the 456 transect boundaries (WGS84).
- `deposito.csv`, sent privately: Vaglio's candidate complexes with coordinates. Please do not share it.
- The SHA-256 fingerprint of `deposito.csv`, published in `DEPOSIT.md` in the repository.

## Steps

1. Write down, before running anything, the transects you want to evaluate (default: all the transects
   your catalogue covers) and any you exclude, with a reason. Please exclude any transect that overlaps
   the Chactún, Lagunita or Tamchén lidar survey: the detector was trained there.
   Save them as plain text files, one transect id per line, for example `area.txt` and `excluded.txt`.
2. Export your catalogue as CSV (`id, lon, lat`) or GeoJSON (points or polygons). If it is in UTM, note
   the EPSG code (15N is 32615, 16N is 32616) and install `pyproj`.
3. Run:

```
python score.py --deposit deposito.csv --expected-sha256 <fingerprint from DEPOSIT.md> \
                --catalog your_catalogue.csv --footprints footprints.geojson \
                --transects area.txt --exclude excluded.txt --out results.json
```

   Add `--catalog-epsg 32616` if your coordinates are projected. If your catalogue is split by UTM zone,
   merge it into one lon/lat file first, or run once per zone with the matching transect list.
4. The script prints a short summary and writes `results.json`. It stops if the deposit is not the one
   that was sealed.
5. Send back `results.json`. You may remove the `for_key_holder_only` section, which lists the ids that
   did not match on either side.

On a laptop the run takes under a minute for the full survey.

## Optional, and very useful

Look at up to 30 random unmatched deposit complexes and up to 30 random uncovered catalogue structures,
and mark each as structure, not a structure, or unclear. This is not part of the verdict; it tells us on
which side the disagreements fall.

## What you will be credited for, and what you will not be asked

You will be credited as the key holder in every report of the result, with wording you approve.
You will not be asked to share your catalogue, its coordinates, or anything beyond `results.json`.
