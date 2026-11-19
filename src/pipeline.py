import glob
import os
import numpy as np
from wotan import flatten
from astropy.timeseries import BoxLeastSquares


def robust_std(y):
    return 1.4826 * np.median(np.abs(y - np.median(y)))


def make_mask(t, eph, margin=1.5, t0_pad=0.01):
    """True where a point lies near a predicted transit of any planet in eph."""
    mask = np.zeros(len(t), dtype=bool)
    for name, e in eph.items():
        half = e["T14_h"] / 24 / 2
        n_lo = int(np.ceil((t.min() - half - e["T0"]) / e["P"]))
        n_hi = int(np.floor((t.max() + half - e["T0"]) / e["P"]))
        for n in range(n_lo, n_hi + 1):
            tc = e["T0"] + n * e["P"]
            pad = np.hypot(t0_pad, abs(n) * e["P_err"])
            mask |= np.abs(t - tc) < half * margin + pad
    return mask


def detrend_sector(t, f, eph, window=0.6, margin=1.5, t0_pad=0.01):
    """Biweight detrend using only out-of-transit points; trend is interpolated across the masks."""
    mask = make_mask(t, eph, margin, t0_pad)
    t_oot, f_oot = t[~mask], f[~mask]
    fl, tr = flatten(t_oot, f_oot, method="biweight", window_length=window,
                     break_tolerance=0.5, return_trend=True)
    good = np.isfinite(tr)
    trend = np.interp(t, t_oot[good], tr[good])
    return f / trend, trend, mask


def detrend_all(sectors_data, eph, window=0.6, margin=1.5, t0_pad=0.01):
    out = []
    for d in sectors_data:
        flat, trend, mask = detrend_sector(d["time"], d["flux"], eph, window, margin, t0_pad)
        out.append({"sector": d["sector"], "time": d["time"],
                    "flat": flat, "trend": trend, "mask": mask})
    return out


def save_detrended(det, folder):
    os.makedirs(folder, exist_ok=True)
    for x in det:
        np.savez_compressed(f"{folder}/sector_{x['sector']:03d}.npz",
                            time=x["time"], flat=x["flat"], trend=x["trend"], mask=x["mask"])


def load_detrended(folder):
    out = []
    for path in sorted(glob.glob(f"{folder}/sector_*.npz")):
        d = np.load(path)
        out.append({"sector": int(path[-7:-4]), "time": d["time"], "flat": d["flat"],
                    "trend": d["trend"], "mask": d["mask"]})
    return out


def stack(det, k=4.0):
    """Per sector: drop NaNs, clip upward outliers above k robust sigma, record the noise level."""
    t_l, f_l, dy_l = [], [], []
    for x in det:
        ok = np.isfinite(x["flat"])
        s = robust_std(x["flat"][ok])
        keep = ok & (x["flat"] < 1 + k * s)
        t_l.append(x["time"][keep]); f_l.append(x["flat"][keep]); dy_l.append(np.full(keep.sum(), s))
    return t_l, f_l, dy_l


def concat_sorted(t_l, f_l, dy_l):
    t, f, dy = np.concatenate(t_l), np.concatenate(f_l), np.concatenate(dy_l)
    o = np.argsort(t)
    return t[o], f[o], dy[o]


def bootstrap_ephemeris(t_list, f_list, dy_list, P0, dur0, t_ref, n_boot=200,
                        oversample=100, step_min=1.0, half_span_min=45, seed=42):
    """Resample whole sectors with replacement; return the best period and T0 (at t_ref) of each resample."""
    t_all = np.concatenate(t_list)
    baseline = t_all.max() - t_all.min()
    dP = (step_min / 1440) / (baseline / P0)          # period step that moves the last transit by step_min minutes
    n_steps = int(round(half_span_min / step_min))
    grid = P0 + np.arange(-n_steps, n_steps + 1) * dP

    rng = np.random.default_rng(seed)
    n = len(t_list)
    P_out, T0_out = [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        t = np.concatenate([t_list[j] for j in idx])
        f = np.concatenate([f_list[j] for j in idx])
        dy = np.concatenate([dy_list[j] for j in idx])
        o = np.argsort(t)
        r = BoxLeastSquares(t[o], f[o], dy=dy[o]).power(
            grid, dur0, objective="likelihood", oversample=oversample)
        k = int(np.argmax(r.power))
        P_k, tc_k = grid[k], r.transit_time[k]
        P_out.append(P_k)
        T0_out.append(tc_k + np.round((t_ref - tc_k) / P_k) * P_k)
    return np.array(P_out), np.array(T0_out)


def summarize(x):
    lo, hi = np.percentile(x, [16, 84])
    return np.median(x), (hi - lo) / 2
