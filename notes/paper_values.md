# Values from Gilbert et al. 2020 (arXiv:2001.00952)

Checked 11 Nov 2026: density, luminosity, log g, a/R*, durations and planet radii are consistent with each other (Winn eqs. 14 and 30).

## Star
- TIC ID: 150428135
- TESS sectors used: 1, 3, 4, 5, 6, 7, 8, 9, 10, 11 and 13, spanning 25 July 2018 to 18 July 2019 (this is Tier A in our analysis)
- Mass (Msun): 0.416 ± 0.010
- Radius (Rsun): 0.420 ± 0.031
- Effective temperature Teff (K): 3480 ± 135
- Luminosity (Lsun): 0.0233 ± 0.0011
- Density: 8.0 ± 1.8 g/cm³ (derived by me: 5.7 ± 1.3 solar densities, using 1.41 g/cm³ for the Sun)
- Surface gravity log g: 4.81 ± 0.06

## Planets (add the table number next to each value)
|                          | b       | c         | d       |
|--------------------------|---------|-----------|---------|
| Period P (d)             | 9.97701 | 16.051098 | 37.4260 |
| T0 (BJD - 2457000)       | 1331.3547 | 1340.0887 | 1330.4737 |
| Duration T14 (h)         | 2.15    | 1.41      | 3.21    |
| Rp/R*                    | 0.0221  | 0.0574    | 0.0262  |
| Impact parameter b       | 0.20    | 0.904     | 0.40    |
| a/R*                     | 34.8    | 47.8      | 84.0    |
| Rp (Earth radii)         | 1.010   | 2.63      | 1.19    |

## Still to record
- Uncertainties on P and T0 for each planet (needed for the transit mask width)
- Table numbers for each value
- Uncertainties on the other planet parameters

## Notes
- BJD - 2457000 is the same as BTJD, so T0 values can be used directly with our data.

## Uncertainties and sources (Gilbert et al. 2020; checked 12 Nov 2026)
- Star: Table 1. Planets: Table 2 ("Model Parameters" for T0, "Derived Parameters" for the rest). Photodynamical fit (Table 3) not used.
- P (d), +/-: b 9.97701 (+0.00024, -0.00028); c 16.051098 (+0.000089, -0.000092); d 37.4260 (+0.0007, -0.0010)
- T0 (BJD-2457000), +/-: b 1331.3547 (+0.0048, -0.0032); c 1340.0887 (+0.0011, -0.0010); d 1330.4737 (+0.0035, -0.0040)
- Rp/R*, +/-: b 0.0221 (+0.0011, -0.0012); c 0.0574 (+0.0032, -0.0026); d 0.0262 (+0.0014, -0.0015)
- Impact parameter, +/-: b 0.20 (+0.19, -0.14); c 0.904 (+0.016, -0.024); d 0.40 (+0.15, -0.22)
- TO VERIFY in the PDF: duration uncertainty for b (maybe -0.07) and for d; a/R* for d (84.0)
- Fit setup in the paper: 2-min SPOC light curves, each sector modelled separately with a Gaussian process; density prior 8.0 g/cm3 with 0.3 dex width; Kipping limb darkening; Beta eccentricity prior
- Duration T14 (h) as printed in Table 2: b 2.15 (+0.15, -0.7); c 1.41 (+0.14, -0.09); d 3.21 (+0.27, -0.26)
- Note: the -0.7 for b looks inconsistent with +0.15 and the ~5% error on a/R* (possible typo in the paper). Not used for anything except mask width; recorded as printed.
