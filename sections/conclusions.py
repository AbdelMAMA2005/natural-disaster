# -*- coding: utf-8 -*-
"""
sections/conclusions.py — Section Conclusions & Perspectives
=============================================================
Synthèse des enseignements de l'analyse, recommandations ciblées
par profil d'utilisateur, limites méthodologiques et références
légales et techniques des données sources.
"""

import sys
from pathlib import Path

# Insertion du répertoire racine pour les imports absolus
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from constants import (
    ANNEES_INCOMPLETES_DEBUT,
    CSV_LICENSE,
    CSV_PUBLISHED,
    CSV_SOURCE_URL,
    DATA_MILLESIME,
    GEOJSON_LICENSE,
    GEOJSON_SOURCE,
    GEOJSON_URL,
)


def render(df: pd.DataFrame) -> None:
    """
    Affiche la section Conclusions & Perspectives du tableau de bord.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet des arrêtés CatNat issu de load_and_prepare().
    """
    # 1. En-tête
    st.header("What the declaration record can tell us")

    # 2. Ce que les données nous enseignent
    st.subheader("Key findings")
    st.markdown(
        "- **Floods are the most frequently declared hazard**, with declarations recorded in every department.\n"
        "- **Drought declarations have increased since 2000**, with peaks in 2003, 2018, and 2022. "
        "The data do not establish a direct causal link to climate change.\n"
        f"- **Recognition delays are increasing**, so the {ANNEES_INCOMPLETES_DEBUT}–2025 record is incomplete.\n"
        "- **Nearly every municipality has had at least one declaration**; recurrence is more informative "
        "than a simple exposed/not-exposed measure."
    )

    # 3. Implications
    st.subheader("Implications by audience")

    with st.expander("For local officials", expanded=False):
        st.markdown(
            "- Prioritize prevention in municipalities with frequent declarations.\n"
            "- Compare departments using rates per municipality, not only raw totals.\n"
            "- Consider declaration history in land-use plans and local risk-prevention plans."
        )

    with st.expander("For residents", expanded=False):
        st.markdown(
            "- Review the declaration history for your municipality in *By municipality*.\n"
            "- Treat the number of declarations as a proxy for historical local exposure, not a forecast.\n"
            "- Ask your local authority about risk-prevention plans and emergency measures."
        )

    with st.expander("For decision-makers", expanded=False):
        st.markdown(
            "- Longer recognition delays may indicate administrative pressure.\n"
            "- Improve digital processing and reduce avoidable delays.\n"
            "- Combine this record with insurance-loss data from the Central Reinsurance Fund (CCR)."
        )

    # 4. Mises en garde
    st.warning(
        "Important limitations: these data record administrative decisions, not physical events, and do not "
        "prove direct climate causation. Changes in scheme coverage make long-term storm, hail, and snow "
        "comparisons difficult. Overseas departments are not shown on the map, but are included in other charts."
    )

    # 5. Pistes d'extension
    st.info(
        "Possible extensions: add population data from INSEE to calculate per-capita exposure, compare with "
        "weather and climate records from Météo-France, and incorporate compensation amounts from the CCR."
    )

    # 6. Sources et licences
    st.subheader("Sources and licences")
    sources_df = pd.DataFrame(
        [
            {
                "Source": "Municipal natural-disaster declarations (GASPAR)",
                "URL": CSV_SOURCE_URL,
                "Licence": CSV_LICENSE,
                "Date": f"GASPAR edition {DATA_MILLESIME} (published {CSV_PUBLISHED})",
            },
            {
                "Source": GEOJSON_SOURCE,
                "URL": GEOJSON_URL,
                "Licence": GEOJSON_LICENSE,
                "Date": "2024 boundaries (Etalab)",
            },
        ]
    )
    st.dataframe(sources_df, use_container_width=True, hide_index=True)
