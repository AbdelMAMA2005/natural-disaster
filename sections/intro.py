# -*- coding: utf-8 -*-
"""
sections/intro.py — Section Accroche & Contexte du tableau de bord CatNat
========================================================================
Présente la problématique citoyenne et territoriale, le cadre du régime
CatNat / GASPAR, les limites méthodologiques majeures, ainsi que les
indicateurs clés (KPI) de cadrage national.
"""

import sys
from pathlib import Path

# Résolution des imports relatifs à la racine du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from constants import (
    FOOTER_TEXT,
    CSV_SOURCE_URL,
    CSV_LICENSE,
    CSV_PUBLISHED,
    DATA_MILLESIME,
    GEOJSON_LICENSE,
    GEOJSON_SOURCE,
    FAMILLES_ORDER,
    FAMILY_LABELS_EN,
    PALETTE_CAT,
)


def render(df: pd.DataFrame) -> None:
    """
    Affiche la section d'introduction et de contexte :
    - Titre et sous-titre de l'application
    - Accroche narrative et justification citoyenne
    - Cadrage institutionnel (base GASPAR, régime CatNat)
    - Avertissements méthodologiques fondamentaux
    - Public cible
    - 4 métriques de synthèse (KPIs)
    - Mentions légales et sources de données

    Paramètres :
        df : DataFrame complet ou filtré des arrêtés de catastrophe naturelle.
    """
    st.header("Purpose and context")

    # ── 1. Accroche narrative ────────────────────────────────────────────────
    st.markdown(
        """
        ### Why does this question matter?

        France has recorded a large number of natural-disaster declarations. Since the compensation
        scheme began in 1982, **34,598 municipalities have at least one declaration in this dataset**.

        This dashboard provides a clear way to explore that administrative record, compare places,
        and understand where declarations recur. The figures describe recognized claims, not a direct
        measurement of physical hazard or climate change.
        """
    )

    # ── 2. Cadre institutionnel (GASPAR & CatNat) ───────────────────────────
    with st.container():
        st.markdown(
            """
            ### The CatNat scheme and the GASPAR database

            Established by the **1982 Natural Disaster Act**, the French CatNat scheme is a public-private
            compensation system backed by the state through the Central Reinsurance Fund (CCR). It covers
            certain direct property damage caused by unusually intense natural events.

            The **GASPAR** database, maintained by the French government, records interministerial
            declarations of natural-disaster status at municipality level.

            > **Key point:** A CatNat declaration is an administrative decision, not a direct physical
            > measurement of a weather event. One storm may produce many declarations in populated areas,
            > while a similar event in an uninhabited area may produce none.
            """
        )

    # ── 3. Avertissements méthodologiques cruciaux ──────────────────────────
    st.warning(
        """
          **How to interpret the figures:**

          1. **A declaration is not a physical event.** Counts depend on municipal applications, insurance
              claims, and legal eligibility criteria.
          2. **The scheme has changed over time.** Storm coverage changed around 1989, and hail and snow
              coverage changed around 2010, making long-term comparisons difficult for those categories.
          3. **Recent years are incomplete.** Administrative review can take 12 to 24 months, so figures
              from 2023 onward are likely to be undercounted.
          4. **The database has no financial or human-impact measures.** It does not report damage costs,
              casualties, or the number of people displaced.
        """
    )

    # ── 4. Public cible ──────────────────────────────────────────────────────
    st.markdown(
        """
                ### Who can use this dashboard?

                Residents can review their municipality's declaration history and learn how local exposure has
                changed over time. Local officials and planners can compare territories and use the record as one
                input to prevention and land-use decisions.
        """
    )

    # ── 5. Indicateurs clés de cadrage (KPI) ──────────────────────────────────
    st.markdown("### National snapshot")

    if df is None or df.empty:
        st.error("No data are available to calculate the summary indicators.")
        return

    try:
        total_arretes = len(df)
        communes_distinctes = (
            int(df["code_geographique"].nunique())
            if "code_geographique" in df.columns
            else 0
        )

        annee_min = int(df["annee"].min()) if "annee" in df.columns and df["annee"].notna().any() else 1982
        annee_max = int(df["annee"].max()) if "annee" in df.columns and df["annee"].notna().any() else 2025
        periode_libelle = f"{annee_min} – {annee_max}"

        famille_top = (
            str(df["famille"].value_counts().index[0])
            if "famille" in df.columns and not df["famille"].empty
            else "Non renseignée"
        )
    except Exception as exc:
        st.error(f"Unable to calculate the summary indicators: {exc}")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total declarations",
            value=f"{total_arretes:,}".replace(",", " "),
            help="Total municipality-level declarations recorded in the database.",
        )
    with col2:
        st.metric(
            label="Municipalities covered",
            value=f"{communes_distinctes:,}".replace(",", " "),
            help="Distinct municipalities with at least one declaration.",
        )
    with col3:
        st.metric(
            label="Period covered",
            value=periode_libelle,
            help="Range of event start years represented in the data.",
        )
    with col4:
        st.metric(
            label="Most frequent risk family",
            value=FAMILY_LABELS_EN.get(famille_top, famille_top),
            help="Risk family with the most recorded declarations.",
        )

    with st.expander("Sources and metadata", expanded=False):
        st.markdown(
            f"""
            - **CatNat data:** [Municipal natural-disaster declarations (data.gouv.fr)]({CSV_SOURCE_URL})
            - **Licence:** {CSV_LICENSE}
            - **File publication date:** {CSV_PUBLISHED}
            - **GASPAR edition:** {DATA_MILLESIME}
            - **Geographic boundaries:** {GEOJSON_SOURCE} ({GEOJSON_LICENSE})
            """
        )
        st.caption(FOOTER_TEXT)
