# TOI-700 transit reanalysis

Independent reanalysis of TESS transits of the TOI-700 system (planets c and d), covering data retrieval, detrending, transit fitting, an accuracy and precision study, and a habitability assessment.

Status: work in progress.

## Setup

    conda env create -f environment.yml
    conda activate toi700
    pip install -r requirements.txt

## Layout

- `notebooks/`: one notebook per phase
- `src/`: reusable code
- `notes/decision_log.md`: every analysis choice and why
- `figures/`, `report/`: outputs
- `data/`: downloaded TESS files (not tracked; re-download with lightkurve)

Data: TESS 2-minute SPOC light curves of TIC 150428135, from MAST.
