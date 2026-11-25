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


## ## TOI-700 reanalysis: detrending (wotan) and BLS prep (16 Nov 2026)

### What wotan does
- Removes slow trends (stellar variability, pointing, scattered light); keeps transits.
- Output: flat = flux / trend. It does NOT search for planets.
- Call: flatten(t, f, method="biweight", window_length=<days>,
  break_tolerance=0.5, return_trend=True)
- window_length is in DAYS. Rule: >= 3x longest transit duration
  (d: 3.21 h -> >= 9.6 h). Too short = eats transits; too long = leaves variability.
- break_tolerance=0.5: segments split at gaps > 0.5 d (TESS orbit gaps).
- Biweight = robust average that down-weights outliers (dips, flares).

### Transit mask (why and how)
- In-transit points pull the trend down -> shallower transits. So exclude them
  when estimating the trend.
- mask |= |t - tc| < half*margin + pad   (margin = 1.5)
- pad = hypot(T0_err, n * P_err): predicted-time error grows with epoch n.
- Procedure: wotan on t[~mask] only -> np.interp trend across masked gaps
  -> flat = f / trend.
- np.isfinite() filter first to drop NaN trend values.

### Window test (all planets, all sectors, masked transits)
- Depth = median(flat outside) - median(flat inside). Needs all transits, not
  one: a single transit is too noisy (sector-1 result was noise).
- Depth insensitive to window 9.6-18 h -> use 12-14.4 h.
- Caveat: masked test does not show whether a BLIND search would erase transits
  -> injection-recovery test is still to do.

### Results so far
- Test 1 (Tier A vs later sectors):
  - b: 0.00042 vs 0.00027 (expected 0.00049); d: 0.00070 vs 0.00019 (expected 0.00069)
    -> published ephemerides of b and d drift (P error x epoch). The planets
    did not change; the predictions got worse.
  - c: 0.00188 vs 0.00211 -> timing still holds, BUT depth ~0.6 of k^2 in both groups.
- Test 2 (sectors 27, 28, 97, 1-hour bins): no visible slow drifts.
  Scatter vs white noise: 27 = 1.34x, 28 = 1.14x, 97 = 1.07x.
- Possible dip near t ~ 2041.6 in sector 27; d predicted at ~2041.57. To check.

### Open issues
- c depth low in BOTH groups -> not timing. Check PLANETS["c"] k and T14_h
  vs paper; try central-half window test.
- `expected = 2*half*720` assumes 2-min cadence; wrong for 20 s / 200 s sectors.
- coverage(): add out-of-transit baseline column (distance to nearest gap).
- Sector 27 residual noise: robust 1-hour scatter 403 ppm vs 328 ppm white-noise
  expectation (1.23x; plain std gave 1.34x, inflated by outliers near t~2041.6).
  Small correlated noise left; not blocking. BLS uses per-sector robust sigma
  as dy so noisier sectors get less weight.

### BLS (next)
- Wotan cleans; BLS searches. BLS folds the flattened curve on many trial
  periods, slides a box, measures dip depth/SNR -> periodogram.
- Gives: best P, T0, duration, depth, SNR. Assumes box shape, strict periodicity.
- Plan: stack flat data -> clip upward outliers only -> narrow period grid
  around published P (±10 sigma, step = P*dur/baseline/3) -> BoxLeastSquares
  -> compare peak with published P.
- Order: c first (control, should return published P), then b, then d.
- Peak at grid edge -> widen range.
- After BLS: rebuild masks with new ephemerides, re-detrend (second pass),
  then injection-recovery, then proper transit-model fit.

### BLS results (pass 1, masks from old ephemerides, window 14.4 h) Date: 17/11/26
- Setup: per-sector robust sigma as dy; durations 0.6-1.5 x T14; period grid
  ±20 sigma around published P; step = P*dur_min/baseline/3.
- c (control): P offset +0.02 sigma, SNR 57.8 -> pipeline works.
  Depth 2425 ppm = 0.74 of k^2. Hypothesis: high impact parameter (published
  T14 = 1.41 h is short for P = 16 d) -> limb darkening + long ingress/egress.
  Test with batman fit, not box.
- b: P offset +0.9 sigma (consistent with paper), SNR 19.7, depth 445 ppm (0.91 k^2).
  Published times drift ~86 min by end of data (P_err x ~267 orbits) -> explains
  late-sector depth dilution in Test 1. The planet did not change.
- d: P offset -2.3 sigma (37.42367 vs 37.426), SNR 17.4, depth 599 ppm (0.87 k^2).
  Published times miss transit by ~235 min at end of data (> duration 196 min).
  Weaker bump at +0.004-0.006 d (SNR ~11) -> check.
- Odd/even depths agree within ~2 sigma for all three.
- BLS periods have NO error bars; need timing fit / MCMC for uncertainties.
- TODO: pass 2 (re-mask with new ephemerides, re-detrend, rerun BLS); refine
  periods; check d bump and sector-27 dip near t~2041.5-2041.6; batman fit;
  injection-recovery.

  ### BLS period uncertainties (bootstrap over sectors, 200 resamples)
- Method: resample 37 sectors with replacement, rerun BLS on fine grid
  (1-min shift of last transit per step, ±45 min), take spread of best P.
  Error = (P84 - P16)/2. Likelihood-curve method FAILED (BLS peak is a cusp,
  width fell below grid step) -> do not use.
- Results (P +/- err, d):
  b 9.977211 +/- 0.000023 (paper 9.97701 +/- 0.00028; +0.7 sigma; 12x better)
  c 16.051120 +/- 0.000013 (paper 16.051098 +/- 0.000092; +0.24 sigma; 7x better)
  d 37.423631 +/- 0.000093 (paper 37.426 +/- 0.001; -2.4 sigma; 11x better)
- Timing uncertainty at end of data (~7 yr): b 108 -> ~9 min, c 22 -> ~3 min,
  d 102 -> ~10 min (period error only; ignores T0 and correlation).
- Caveats: statistical only; inflate 30-50% for a first report; c's error is
  only 3 grid steps wide (rerun with 30 s steps); bootstrap grid too narrow to
  test d's second bump (+0.004-0.006 d) -> run wide bootstrap check.
- File: ../data/bls_period_bootstrap.csv
- NEXT: check edge/bump, then pass 2 (re-mask with new ephemerides, re-detrend,
  rerun BLS), then batman fit, injection-recovery.
## BLS, new ephemerides, pass 2 (19 Nov 2026)

WHAT I DID
- Stacked all 37 flattened sectors (589,399 points; a second 4-sigma upward clip removed 19 more), baseline 2663 d.
- BLS near each planet's published period (box widths 0.6-1.5 x T14), all sectors together.
- Bootstrap over sectors (200 resamples, drawn with replacement) for the period error.
- Pass 2: rebuilt transit masks from my new periods, re-detrended, repeated BLS and the depth test.

RESULTS (period in days)
  b 9.977211 +/- 0.000022   (2020 paper 9.97701 +/- 0.00028; 2023 paper 9.977219 +/- 0.000041)
  c 16.051120 +/- 0.000013  (2020: 16.051098 +/- 0.000092; 2023: 16.051137 +/- 0.000020)
  d 37.423631 +/- 0.000093  (2020: 37.4260 +/- 0.0010; 2023: 37.42396 +/- 0.00039)
- d is 2.4 sigma below the 2020 period but 0.8 sigma from the 2023 one: the 2020 period had drifted.
- Gain over the 2023 errors is about 1.9x (b), 1.5x (c), 4.2x (d); over 2020 about 12x, 7x, 11x.
- c odd/even depths agree (2439 vs 2410 ppm). No peak at the grid edge. No competing peak for d within +/-0.02 d.
- Pass 2: d BLS S/N 17.4 -> 18.7; masked fraction 3.4% -> 2.8%.
- Depth test after pass 2 (ppm, Tier A / later): b 530/410, c 1970/2110, d 660/450 (before: b 420/270, d 700/190).
- BLS depth / k^2 (2023 radii): b 1.13, c 0.76, d 1.18. Fits limb darkening (central vs near-edge transits).

CAUTIONS
- BLS S/N assumes white noise; red noise makes true S/N about 20% lower.
- Pass 1 = pass 2 in period only because the search grid was not re-centred.
- T0 error not yet measured; mask padding of 0.01 d is a guess.

NEXT
1. Bootstrap T0, finer period grid for c.
2. Literature comparison table (2020 and 2023).
3. Save pass-2 data; move functions into src/.
4. Blind BLS over 1-60 d (optional: look for planet e at 27.8 d after masking b, c, d).
5. Phase 4: transit fits, starting with c.

## Ephemeris bootstrap and first batman fit, planet c (25 Nov 2026)

WHAT I DID
- Moved the pipeline into src/pipeline.py, pass-2 ephemerides into src/eph_pass2.py; checkpoints in data/.
- Bootstrap of period AND T0 (200 resamples of whole sectors), saved in data/ephemeris_bootstrap_pass2.csv.
- Started Phase 4: batman + emcee fit of planet c (9 parameters: T0, P, k, b, rho, q1, q2, f0, lns), 36 walkers x 15000 steps. Density prior 8.0 +/- 1.8 g/cm3 (2020 paper); uniform Kipping q1, q2; circular orbit; 2-min exposure supersampled x3.

RESULTS
- Bootstrap (P in d, T0 in BTJD at mid-data):
    b P 9.977214 +/- 0.000022, T0 2658.3228 +/- 0.0016 (2.3 min)
    c P 16.051109 +/- 0.000012, T0 2656.2789 +/- 0.0006 (0.8 min)   (finer grid did not change c's error)
    d P 37.423557 +/- 0.000098, T0 2640.3097 +/- 0.0028 (4.1 min)
- Planet c fit: k 0.0572 +0.0027 -0.0024, b 0.900 +0.013 -0.020, a/Rs 48.9, T14 1.399 h, rho 8.6 +/- 1.2, depth k^2 3267 ppm, Rp about 2.62 Re (R* = 0.420). All within errors of the 2020 paper; T14 about 3x tighter.
- Fit period error (6e-6 d) is half the bootstrap error (1.2e-5 d): the fit assumes white noise.

PROBLEM FOUND
- Corner plot showed a second small blob (k about 0.038, b about 0) and acceptance min 0.01: a stuck walker. The half-chain test could not catch it.
- Fix: drop walkers with acceptance < 0.1 or mean log_prob 10 below the median. For b and d: start walkers in a ball around an optimizer solution.

NEXT
1. Remove stuck walker(s), redo table and corner plot for c; print lns.
2. Robustness runs for c: 2023 density prior (7.86 +/- 0.90); flat density prior (independent stellar density).
3. Limb-darkening priors from tables (decide and log).
4. Fit b and d with the same code (move into src/).
5. Still open from Phase 3: literature comparison table, blind BLS over 1-60 d.
