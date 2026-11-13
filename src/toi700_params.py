# Values from Gilbert et al. 2020 (arXiv:2001.00952): Table 1 (star), Table 2 (planets)
# Times are BJD - 2457000 (same as BTJD). Durations in hours. Errors are (+, -).

STAR = {
    "tic": 150428135,
    "mass_msun": 0.416, "mass_err": 0.010,
    "radius_rsun": 0.420, "radius_err": 0.031,
    "teff_k": 3480, "teff_err": 135,
    "lum_lsun": 0.0233, "lum_err": 0.0011,
    "density_gcc": 8.0, "density_err": 1.8,
    "logg": 4.81, "logg_err": 0.06,
}

PLANETS = {
    "b": {"P": 9.97701,   "P_err": (0.00024, 0.00028),   "T0": 1331.3547, "T0_err": (0.0048, 0.0032),
          "T14_h": 2.15, "T14_err": (0.15, 0.7), "k": 0.0221, "impact": 0.20,  "a_over_R": 34.8, "Rp_earth": 1.010},
    "c": {"P": 16.051098, "P_err": (0.000089, 0.000092), "T0": 1340.0887, "T0_err": (0.0011, 0.0010),
          "T14_h": 1.41, "T14_err": (0.14, 0.09), "k": 0.0574, "impact": 0.904, "a_over_R": 47.8, "Rp_earth": 2.63},
    "d": {"P": 37.4260,   "P_err": (0.0007, 0.0010),     "T0": 1330.4737, "T0_err": (0.0035, 0.0040),
          "T14_h": 3.21, "T14_err": (0.27, 0.26), "k": 0.0262, "impact": 0.40,  "a_over_R": 84.0, "Rp_earth": 1.19},
}
