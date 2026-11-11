# Decision log: TOI-700 transit reanalysis

## Setup (work done 29-31 Oct 2026)
- Environment: conda env "toi700", Python 3.11. conda-forge: numpy, scipy, pandas, matplotlib, astropy, emcee, corner, dynesty, jupyterlab, ipykernel. pip: lightkurve, wotan, batman-package.
- Problems and fixes:
  - conda stuck on "Solving environment" -> smaller installs, conda-forge only
  - pip error building fbpca (setuptools not found) -> installed setuptools and wheel, then pip install --no-build-isolation fbpca
  - plot not displayed -> %matplotlib inline as first line of the notebook
  - NameError: search not defined -> kernel was fresh; run cells from the top
- Repo: github.com/astroshantanu/toi700-transit-reanalysis (private for now)

## Data
- Target: TIC 150428135 (TOI-700), TESS SPOC 2-min cadence
- Search result: 37 sectors (1, 3-11, 13, 27-28, 30-31, 33-38, 61-66, 68-69, 87-90, 93, 95-97). Not available: 2, 12
- Flux used: PDCSAP (lightkurve default)
- Sector 1: 18279 cadences after default quality mask; remove_nans removed 0
- Seen in plot: orbit gap near BTJD 1338-1339; small discontinuity near 1348 (cause unknown)
- Transits not visible by eye (expected: depth far below single-point scatter)

## Scatter test, sector 1 (raw, before flare clipping or detrending)
- Per-point (2 min): 1656 ppm
- 30-min bins: 489 ppm (ratio 3.38 vs white-noise 3.87)
- 60-min bins: 369 ppm (ratio 4.49 vs 5.48)
- Measured/ideal scatter: 1.02 at 4 min, 1.14 at 32 min, 1.20 at 128 min, 1.31 at 256 min
- Interpretation: nearly white at short timescales, mildly red on transit timescales (2-4 h)
- S/N of one transit of d (assumed depth ~600 ppm, ~3 h): ~3.4 if white, ~2.8 with measured scatter; ~12 for ~20 transits (to verify)

## To do
- Check that TIC 150428135 matches the discovery paper
- Check which sectors the discovery paper used
- Look into the discontinuity near BTJD 1348
- Repeat scatter test after flare clipping and detrending
- Download all sectors

## Phase 2, all-sector table (31 Oct 2026)
- 37 sectors downloaded to data/ (not tracked by git); table saved in notes/sector_table.csv
- Good cadences per sector: 12379 (S3) to 20257 (S89); S97 anomalous at 29075 over 52 days (to check)
- Per-point scatter 1605-1840 ppm; no sector stands out
- Total about 589,500 cadences (about 820 days); Year 1 (S1-13) about 169,000 (about 234 days)
- Rough expected transits (all sectors): b about 82, c about 51, d about 22
- Many sectors lost 25-40% of cadences to the default quality mask
- To do: check S97 gaps; choose flare-clipping threshold from the sigma counts

## Sector 97 (1 Nov 2026)
- 29075 cadences over 52 days: four TESS orbits (extended sector, Cycle 8). Not an error.
- Gaps: 3.2, 3.3, 3.9 d (BTJD 3946.9-3950.1, 3960.3-3963.6, 3974.4-3978.3)
- Short breaks (<0.5 d) inside each orbit near BTJD 3941, 3954, 3967, 3982 (cause not verified)
- Handling: detrend per orbit (wotan break_tolerance splits at gaps); normalize per sector

## Outlier counts, all sectors (1 Nov 2026)
- Robust sigma per sector; counted points beyond 4 and 5 sigma, high and low
- Totals beyond 4 sigma: 114 high, 27 low, about 18.7 expected per side from random noise
- Beyond 5 sigma: 8 high, 0 low. Sector 6 stands out (13 high beyond 4 sigma)
- Rule under consideration: clip upward only (transits are dips), 4-5 sigma
- Threshold not yet fixed; to do: look at sector 6 flagged points, then apply to all sectors
- Counts made on raw flux, before detrending; revisit after Phase 3

## Why robust sigma instead of the ordinary standard deviation (11 Nov 2026)
- Flares are extreme points. They inflate the ordinary standard deviation, which makes the flares themselves look less extreme.
- Toy example: a point of 30 among values near 10 has z = 2.62 with the ordinary std (missed at 3 sigma) but z = 26.3 with robust sigma.
- Robust sigma = 1.4826 x median(|x - median(x)|). It uses medians, which ignore extreme values, so flares cannot inflate it. The factor 1.4826 puts it on the same scale as an ordinary sigma for a bell-shaped distribution.
- Sector 1 check: robust sigma 1672 ppm vs ordinary std 1656 ppm (within 1%), so sector 1 has no significant flares. Counts beyond 3 sigma (29 high, 17 low) reproduced step by step.

## Flare and outlier clipping rule (11 Nov 2026)
- Sector 6 inspected: 13 points above 4 sigma (0.46 expected from noise); mostly isolated single points; only one adjacent pair
- Most extreme (BTJD 1476.1791, z = 5.3) is a one-point spike with normal neighbours
- 7 of 13 fall within ~1 day after an orbit start (BTJD ~1468.3 and ~1478.5): suggests instrumental origin
- Decision: clip points more than 4 robust sigma ABOVE the median, per sector. Never clip low points (transits are dips).
- Cost: ~0.5 good points per sector removed by chance; all-sector total expected ~19 of ~114 removed
- To revisit after detrending (Phase 3)

## Clipping applied (11 Nov 2026)
- clean_sector(lc, k=4.0): remove NaNs, normalize, robust sigma per sector, remove points with z > 4 (upward only)
- Result: 114 points removed out of 589,532 (0.02%); 589,418 kept. Matches earlier counts sector by sector.
- Sectors with 0 removed: 1, 11, 89, 93. Most removed: sector 6 (13)
- The lightkurve warning about 30% of cadences masked (5871/19412) is the default quality mask; it did not refer to sector 6 (14,483 before clipping)
