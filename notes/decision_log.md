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
