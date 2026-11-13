import glob
import numpy as np
import lightkurve as lk


def clean_sector(lc, k=4.0):
    """Remove NaNs, normalize, and clip points more than k robust sigma ABOVE the median.
    Returns the cleaned light curve and the number of points removed."""
    lc = lc.remove_nans().normalize()
    f = np.array(lc.flux.value, dtype=float)
    med = np.median(f)
    sig = 1.4826 * np.median(np.abs(f - med))
    z = (f - med) / sig
    keep = z <= k
    return lc[keep], int(np.sum(~keep))


def load_all_clean(data_dir="../data", k=4.0):
    """Read every sector file under data_dir, clean it, and return a list of dicts
    (sector, time, flux, flux_err, n_removed) with plain numpy arrays, sorted by sector."""
    files = sorted(glob.glob(f"{data_dir}/**/*_lc.fits", recursive=True))
    out = []
    for path in files:
        lc = lk.read(path)
        sector = int(lc.meta["SECTOR"])
        lc_c, n_removed = clean_sector(lc, k=k)
        out.append({
            "sector": sector,
            "time": np.array(lc_c.time.value, dtype=float),
            "flux": np.array(lc_c.flux.value, dtype=float),
            "flux_err": np.array(lc_c.flux_err.value, dtype=float),
            "n_removed": n_removed,
        })
    out.sort(key=lambda d: d["sector"])
    return out
