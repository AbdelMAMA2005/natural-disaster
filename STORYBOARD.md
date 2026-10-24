# Storyboard: CatNat France Dashboard

**EFREI Paris, Data Storytelling 2026, Group DAI**
Author: Abdel MAMA

> **Central question:** Which communes and territories are the most exposed to natural disaster decrees, and is it getting worse?
>
> **Audience:** Citizens and local officials who want to understand the historical risk of their territory.

**Data:** *Arrêtés de catastrophe naturelle par commune*, data.gouv.fr (GASPAR database, vintage September 2025).
**Licences:** Open Licence 2.0 (Etalab) for the CatNat dataset; ODbL for administrative boundaries.
**Narrative arc:** Hook → Context → Key insights → Implications / Next steps.

---

## Section 1: Introduction (Hook and Context)

**Insight title:** *"34,598 municipalities have at least one declaration in the dataset, but some territories pile up episodes."*

**Question answered:** Why look at this data? What is a CatNat decree?

**Visual:** 4 KPI metrics (total decrees, distinct communes, period, dominant risk family).

**Active filters:** None (global view, required for the hook).

**KPIs:** 260,601 decrees / 34,598 communes / 1982–2025 / Floods.

**Interpretation text:**
The GASPAR database records every natural disaster recognition decree, an administrative act that opens the right to compensation. A decree does not necessarily match one distinct physical event: a single episode can generate thousands of decrees at once.

**Narrative warnings:**
- A decree is not a physical event.
- The scope of the scheme has changed over time (for example, storms almost disappear from the data after 1989, and hail/snow are absent in 2005–2015).
- Recent years are undercounted because of the recognition delay.
- The data has no population, cost or casualty information.

---

## Section 2: Overview

**Insight title:** *"Floods are the largest category overall, but drought is rising strongly, and recent data is mechanically incomplete."*

**Question:** What is the overall trend? Which risk family is growing?

**Visuals (in order):**
1. Yearly curve with annotations (peaks in 1999, 2003, 2022) and a grey zone marking incomplete recent years.
2. Heatmap: year × risk family.
3. Small multiples: one panel per risk family.
4. Stacked bars: region × risk family (mainland only).

**Active filters:** Period, Region, Risk family.

**KPI header:** number of decrees / communes affected / dominant risk / top department.

**Interpretation text:**
The 1999 peak (about 57,900 rows, almost all floods and ground movements) flattens the whole curve. After the peak, the level returns to normal, so it is not a real drop in disasters. Drought and clay shrink-swell have progressed clearly since 2000, with peaks in 2003, 2018 and 2022. The grey zone shows that the most recent years are mechanically undercounted because of the recognition delay.

---

## Section 3: Deep Dives

**Insight title:** *"The map reveals marked territorial inequalities: some departments accumulate every risk."*

**Question:** Where are the most exposed territories? How does risk change over time and space?

### A. Animated map (slider 1982–2025)
- Visual: animated choropleth of raw declaration counts by department.
- Caveat: counts are not normalized by population or the total number of municipalities.
- Note: overseas departments (DROM) are not shown on the map because matching boundaries are unavailable in the geographic dataset; their records remain in the other charts.

### B. Top / bottom N ranking
- Visual: horizontal bars.
- Visual: ranking by raw declaration counts.
- Caveat: large departments may have higher counts because they contain more municipalities; a fair rate comparison needs an independent municipality or population denominator.

### C. Recognition delay by decade
- Visual: box plots.
- Message: the median delay between the end of an episode and its decree grows over time, which explains the undercounting of recent years.

### D. Seasonality
- Visual: grouped bars, month × risk family.
- Message: risk families peak in different seasons.

**Active filters:** All.

---

## Section 4: By Commune

**Insight title:** *"Every commune has its own history: find yours."*

**Question:** What is the historical risk of my commune?

**Visuals:**
1. Search by name or INSEE code.
2. Timeline of recognised episodes.
3. Bars by risk family.
4. Comparison with the department median.

**Active filters:** None (search runs on the full dataset).

**KPIs:** number of decrees, dominant family, rank within the department, first recognition.

---

## Section 5: Data Quality

**Insight title:** *"Solid data overall, but important limits to know."*

**Question:** Can we trust this data? What precautions should we take?

**Content:**
- Missing values per column (several columns are almost empty and are not used in the story).
- Suspected duplicates: rows sharing the same commune, type and dates. They are kept and flagged, because identical dates and locations do not prove an accidental copy.
- Date inconsistencies (decree date earlier than the end date of the episode).
- Recognition delay by decade.
- The 1999 and 1982–83 peaks.
- Changes in the scope of the scheme over time.
- Missing context: population, financial losses, casualties, physical intensity.

---

## Section 6: Conclusions and Implications

**Insight title:** *"Recognitions are increasing for some risks: acting where the same communes are hit again and again protects tomorrow."*

**Question:** What should we remember? What should we do?

**Content:**
1. Main insights: floods, drought, recognition delay, recurrence.
2. Implications by audience: local official, citizen, decision-maker.
3. Warnings: no direct climate causality is claimed.
4. Extension ideas: INSEE population data, climate and weather data, other risk datasets.
5. Sources and licences table.

---

## Sidebar Filter Tree

| Control | Type | Impact |
|---|---|---|
| Period (years) | Range slider | Overview, Territorial analysis, and Conclusions |
| Region(s) | Multi-select | Overview, Territorial analysis, and Conclusions |
| Risk family | Multi-select | Overview, Territorial analysis, and Conclusions |
| Include DROM | Checkbox | Filtered sections; DROM are not displayed on the map |

Introduction, By Commune, and Data Quality use the full dataset and are not affected by the sidebar filters.

---

## Sources

- Arrêtés de catastrophe naturelle par commune, data.gouv.fr: https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-par-commune
- Contours administratifs, data.gouv.fr: https://www.data.gouv.fr/datasets/contours-administratifs
- Licences: Open Licence 2.0 (Etalab) for the CatNat dataset; ODbL for administrative boundaries.