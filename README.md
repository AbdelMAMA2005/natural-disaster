# Natural Disasters in France: CatNat Dashboard

An interactive Streamlit dashboard about natural-disaster declarations ("arrêtés CatNat") in France, built for the EFREI Paris Data Storytelling project (#EFREIDataStories2026, group DAI).

- **Live app:** https://natural-disaster.streamlit.app/
- **Demo video (2–4 min):** https://youtu.be/BVQXdMIbJD8
- **Repository:** https://github.com/AbdelMAMA2005/natural-disaster

## Overview

This project uses the GASPAR database, which records municipalities that were officially recognized as affected by a natural disaster. The dashboard covers 1982 to mid-2025 and helps readers explore the history of these declarations.

The central question is: **which communes and territories are the most exposed to natural-disaster declarations, and is it getting worse?**

The main purpose is to make a large public dataset easier to understand. Readers can compare years, regions, departments, and municipalities. The dashboard also explains important limits, so its charts are not mistaken for direct measurements of weather events, damage, or climate change.

**Intended audience:** citizens and local officials who want to understand the historical risk of their territory.

## Author

Created by **Abdel MAMA** (abdelmama2005@gmail.com, https://www.linkedin.com/in/abdel-mama-b43804313/)).

A profile photo can be added at `assets/<fichier>.jpg`. The application displays it in the sidebar when the file is present.

## Story structure

| Section | What it shows |
|---|---|
| **Introduction** | What the CatNat scheme and GASPAR represent, a national snapshot, and the main cautions. One administrative declaration is not one physical disaster event. |
| **Overview** | Changes over time: annual total, a year × risk-family matrix, separate trends per risk family, and a regional comparison. Recent years may be incomplete because declarations take time to be reviewed and published. |
| **Territorial analysis** | A department map, a ranking, recognition delays, and seasonal patterns. The ranking can show total declarations or the share of municipalities affected, which makes departments of different sizes more comparable. |
| **By municipality** | Search by municipality name or INSEE code: declaration history, leading risk family, rank within the department, and a table of recorded declarations. |
| **Data quality** | Missing values, possible duplicates, date inconsistencies, and other limits of the source. |
| **Conclusions** | Main patterns and suggested uses for residents, local officials, and decision-makers. These are starting points, not predictions or proof of climate causation. |

## Data

| | |
|---|---|
| **Dataset** | Arrêtés de catastrophe naturelle par commune |
| **Portal** | data.gouv.fr: https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-par-commune |
| **Stable CSV URL** | https://www.data.gouv.fr/api/1/datasets/r/b3d02000-5f25-4967-a210-a4051dd620a1 |
| **SHA-1 of the CSV** | `9776cdc55f506c648ab45a05ed184682870a689f` |
| **Original source** | GASPAR database (vintage: September 2025); file published on data.gouv.fr on 20 July 2026 |
| **Format** | CSV, `;` separator, UTF-8, 260,601 rows, 16 columns, **no header row** |
| **Granularity** | One row = one (commune, decree) pair |
| **Licence** | Open Licence 2.0 (Etalab) |
| **Map boundaries** | "Contours administratifs" dataset on data.gouv.fr: https://www.data.gouv.fr/datasets/contours-administratifs (licence: ODbL) |

Columns: `index`, `code_geographique`, `libelle_geographique`, `epci`, `libelle_epci`, `departement`, `libelle_departement`, `region`, `ept`, `libelle_petr`, `code_pnr`, `libelle_pnr`, `type_catastrophe`, `date_debut`, `date_fin`, `date_arrete`.

The raw CSV is **not** included in the repository. The app downloads it and keeps a local cache (`data/`).

## Data preparation

- The CSV is read with explicit column names and as text, so INSEE and department codes keep their leading zeros (for example `04054`, `2A`).
- Dates are converted and rounded to the day (some carry a `02:00` time offset).
- Risk types are grouped into families: floods, drought (including clay shrink-swell), ground movements, storms and cyclones, hail and snow, and others (avalanche, miscellaneous).
- Derived variables: start year, month and decade, episode duration, recognition delay (decree date minus end date), decrees per commune, share of communes affected per department.
- Aggregated tables are pre-computed and cached with `st.cache_data`.

## Key limits and caveats

- **A decree is an administrative recognition, not a physical event.** One episode can generate thousands of decrees. The 1999 peak (about 57,900 rows, almost all floods and ground movements) flattens the raw curve.
- **Recent years are undercounted.** The median delay between the end of an episode and its decree is about 185 days in the 2020s, versus a few days in the 1990s.
- **The rules and scope of the scheme have changed.** For example, storms almost disappear from the data after 1989, and hail/snow are absent in 2005–2015. These are observed gaps in the dataset, not a complete legal chronology: the dataset does not include a change log explaining them. A drop in decrees does not always mean fewer disasters.
- **Possible duplicates are kept and flagged.** 31,539 rows (12.1% of the dataset) belong to groups sharing the same municipality code, hazard type, event start date, and event end date after dates are normalized to the day. Collapsing each group to one row would remove 16,583 rows, leaving 244,018. These are suspected duplicates, not confirmed errors: identical dates and locations do not prove an accidental copy.
- **Mostly empty columns:** `ept`, `code_pnr`, `libelle_pnr`, `libelle_petr` are largely unfilled and are not used in the story.
- **Missing context:** no population, financial losses, casualties, or physical intensity.
- **No causal claim about climate.** The dashboard shows that recognitions rise for some risks (notably drought), and discusses partial explanations, without attributing a cause.
- **Overseas departments (DROM):** their records are included in the dataset and the non-map analyses, but they are not shown on the map because the geographic boundaries used by the app do not contain matching features for them.

## Ethics

The data is administrative, public, and aggregated at commune level. It contains no personal data. The source and licences are cited above.

## Project structure

```
app.py                  # Streamlit entry point and sidebar filters
constants.py            # URLs, licences, labels, and shared settings
sections/               # intro, overview, deep dives, commune, quality, conclusions
utils/
  io.py                 # data download, checksums, and local cache
  prep.py               # cleaning, derived fields, filters, and aggregations
  viz.py                # shared Plotly charts
data/                   # downloaded CSV and GeoJSON cache (not versioned)
assets/                 # banners and other images
.streamlit/config.toml  # Streamlit theme and server settings
requirements.txt        # pinned Python dependencies
```

Data loading and preparation are handled separately from the Streamlit section rendering and chart helpers.

## Run locally

Requires Python 3.9 or newer. The project was checked with Python 3.13.9.

```powershell
git clone https://github.com/AbdelMAMA2005/natural-disaster.git
cd natural-disaster
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. On first launch, the app downloads the CSV and department boundaries into `data/`, then reuses the local cache. An internet connection is required for the first download.

## Tech stack

Python, Streamlit 1.51.0, Pandas 2.3.3, Plotly 6.3.0, and Requests 2.32.5. Exact versions are pinned in `requirements.txt`.

## Deployment

Deployed on Streamlit Community Cloud: https://natural-disaster.streamlit.app/

## Possible extensions

Join INSEE population data to compute decrees per inhabitant, add climate or weather data, and cross with other risk datasets.