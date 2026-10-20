# -*- coding: utf-8 -*-
"""
sections/overview.py — Section Vue d'ensemble du tableau de bord CatNat
========================================================================
Présente l'évolution temporelle globale des arrêtés, la décomposition
par famille de risque (heatmap et petits multiples), ainsi que la
répartition géographique par région en France métropolitaine.
"""

import sys
from pathlib import Path

# Résolution des imports relatifs à la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from constants import ANNEES_INCOMPLETES_DEBUT
from utils.prep import (
    agg_par_annee,
    agg_par_annee_famille,
    agg_saisonnalite,
    apply_filters,
)
from utils.viz import (
    fig_courbe_annuelle,
    fig_heatmap,
    fig_small_multiples,
    fig_barres_famille_region,
)


def render(df: pd.DataFrame) -> None:
    """
    Affiche la vue d'ensemble macroscopique des catastrophes naturelles :
    - Évolution chronologique globale avec options d'échelle et filtrage des pics
    - Matrice thermique (Heatmap) par année et par famille
    - Petits multiples déclinant chaque famille de risque individuellement
    - Composition par région métropolitaine

    Paramètres :
        df : DataFrame des arrêtés de catastrophe naturelle.
    """
    if df is None or df.empty:
        st.warning("No data are available for the overview.")
        return

    # 1. En-tête avec titre-insight
    st.header(
        "Floods dominate the record; drought declarations have risen, while recent years remain incomplete"
    )

    # 2. Contrôles interactifs
    col1, col2 = st.columns(2)
    with col1:
        log_scale = st.checkbox("Logarithmic scale", value=False)
    with col2:
        masquer_pics = st.checkbox(
            "Hide major-event years (5,000 or more declarations)",
            value=False,
        )

    # 3. Pré-agrégations
    try:
        annee_agg = agg_par_annee(df)
        famille_agg = agg_par_annee_famille(df)
    except Exception as exc:
        st.error(f"Unable to calculate the annual summaries: {exc}")
        return

    # 4 & 5. Tendance globale : courbe annuelle
    st.subheader("Annual trend")
    try:
        fig_annuelle = fig_courbe_annuelle(
            annee_agg,
            log_scale=log_scale,
            masquer_pics=masquer_pics,
        )
        st.plotly_chart(fig_annuelle, use_container_width=True)
    except Exception as exc:
        st.error(f"Unable to display the annual trend: {exc}")

    # 6. Alt text accessible
    st.caption(
        "Annual CatNat declarations in France from 1982 to 2025. Major events produce visible peaks; "
        f"the shaded area from {ANNEES_INCOMPLETES_DEBUT} marks years with incomplete data."
    )

    # 7. Interprétation en 3 phrases
    st.markdown(
        """
        The series includes exceptional peaks. In **1999**, storms Lothar and Martin and widespread flooding
        produced an unusually high number of municipal declarations. **2022** saw a major concentration of
        drought and soil-shrinkage declarations. The shaded period from 2023 reflects reporting delays and
        should not be read as evidence of lower physical risk.
        """
    )

    # 8 & 9. Heatmap : quelle famille, quelle année ?
    st.subheader("Declarations by year and risk family")
    try:
        fig_heat = fig_heatmap(famille_agg)
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as exc:
        st.error(f"Unable to display the annual risk-family matrix: {exc}")

    # 10. Alt text + interprétation
    st.caption(
        "The matrix compares years and risk families. Darker colors represent more declarations."
    )
    st.markdown(
        """
        Flood declarations appear throughout the record. Drought and soil-shrinkage declarations became
        more prominent over the last two decades, while storm declarations drop sharply after the 1989
        change in coverage.
        """
    )

    # 11 & 12. Petits multiples : chaque famille de risque
    st.subheader("Trends by risk family")
    try:
        fig_mult = fig_small_multiples(famille_agg)
        st.plotly_chart(fig_mult, use_container_width=True)
    except Exception as exc:
        st.error(f"Unable to display risk-family trends: {exc}")

    # 13. Alt text + interprétation
    st.caption(
        "Separate time series for each risk family make it easier to compare their different patterns."
    )
    st.markdown(
        """
        The families have different patterns. Flood declarations remain numerous, while drought declarations
        cluster in major episodes such as 2003, 2018, and 2022. Ground movements are more evenly distributed;
        storm, hail, and snow trends are also shaped by changes in insurance coverage.
        """
    )

    # 14 & 15. Composition par région (métropole)
    st.subheader("Declarations by region")
    try:
        fig_reg = fig_barres_famille_region(df)
        st.plotly_chart(fig_reg, use_container_width=True)
    except Exception as exc:
        st.error(f"Unable to display the regional breakdown: {exc}")

    st.caption(
        "Stacked bars compare the total declarations by risk family across mainland regions."
    )
    st.markdown(
        """
        Occitanie, Nouvelle-Aquitaine, and Auvergne-Rhône-Alpes have high declaration counts. These totals
        reflect both exposure and administrative recognition, and should not be interpreted as a normalized
        measure of risk. Flood declarations are prominent in north-western regions.
        """
    )
