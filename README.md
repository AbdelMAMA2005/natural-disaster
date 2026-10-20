# Student Report

## Natural Disasters in France

This project is an interactive dashboard about natural-disaster declarations in France. It uses the GASPAR database, which records municipalities that were officially recognized as affected by a natural disaster. The dashboard covers the years 1982 to 2025 and is designed to help students and readers explore the history of these declarations.

The main purpose of the project is to make a large public dataset easier to understand. Readers can compare years, regions, departments, and municipalities. The dashboard also explains important limits, so its charts are not mistaken for direct measurements of weather events, damage, or climate change.

## Author

This project was created by **Abdel MAMA**. His email address is [abdelmama2005@gmail.com](mailto:abdelmama2005@gmail.com), and his profile is available on [LinkedIn](https://www.linkedin.com/in/abdel-mama-b43804313/).

A profile photo can be added at `assets/abdel-mama.jpg`. The application displays it in the sidebar when the file is present.

The Introduction explains what the CatNat compensation scheme and the GASPAR database represent. It gives a national snapshot and outlines the main cautions for reading the figures. In particular, one administrative declaration is not the same thing as one physical disaster event.

The Overview presents changes over time. It includes the annual total, a matrix comparing years and risk families, separate trends for each risk family, and a regional comparison. Recent years may be incomplete because declarations can take time to be reviewed and published.

The Territorial analysis section includes a department map, a ranking table, recognition delays, and seasonal patterns. The ranking can be viewed as total declarations or as the share of municipalities affected. The second measure makes comparisons between departments of different sizes more useful.

The By municipality section lets a reader search by municipality name or INSEE code. It shows the municipality's declaration history, its leading risk family, its rank within the department, and a table of recorded declarations.

The Data quality section reports missing values, possible duplicates, date inconsistencies, and other limits in the source. Suspected duplicates are retained because identical dates and locations do not prove that two records are accidental copies. The database does not include population, financial losses, casualties, or the physical intensity of events.

The Conclusions section summarizes the main patterns and suggests how residents, local officials, and decision-makers might use the information. These suggestions should be treated as starting points for further investigation, not as predictions or proof of climate causation.

The application is built with Python, Streamlit, Pandas, and Plotly. The entry point is `app.py`; the dashboard sections are in the `sections` folder; shared chart formatting is in `utils/viz.py`; and data loading and preparation are handled by the other modules in `utils`. The underlying data preparation and filtering functions are kept separate from the presentation layer.

To run the dashboard locally, install the packages listed in `requirements.txt` and start Streamlit with `streamlit run app.py`. The application loads the public GASPAR data and geographic boundaries used for the maps.
