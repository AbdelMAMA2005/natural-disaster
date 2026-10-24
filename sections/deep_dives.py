# -*- coding: utf-8 -*-
"""
sections/deep_dives.py — Analyses approfondies des arrêtés CatNat
================================================================
Composant Streamlit pour l'exploration spatiale et temporelle :
- Carte animée de l'exposition par département (1982–2025)
- Classements bruts et normalisés des départements
- Analyse des délais administratifs de reconnaissance
- Profil de saisonnalité par famille de risque
"""

import sys
from pathlib import Path

# Insertion du répertoire racine pour les imports absolus
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from constants import FAMILY_LABELS_EN, FAMILLES_ORDER, PALETTE_CAT
from utils.prep import (
    agg_delai_par_decennie,
    agg_par_dept,
    agg_par_dept_annee,
    agg_saisonnalite,
)
from utils.viz import (
    fig_carte_animee,
    fig_carte_dept,
    fig_classement_dept,
    fig_delai_boxplot,
)


def render(df: pd.DataFrame, geojson: dict) -> None:
    """
    Rendu de la section Deep Dives : disparités territoriales,
    délais de reconnaissance et saisonnalité des catastrophes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet des arrêtés CatNat issu de load_and_prepare().
    geojson : dict
        GeoJSON des départements français pour le tracé choroplèthe.
    """
    # Titre principal de la section
    st.header("Natural-disaster declarations vary across departments")

    # ── SECTION A — Carte ────────────────────────────────────────────────────────
    st.subheader("Department map")

    agg_dept = agg_par_dept(df)
    agg_dept_an = agg_par_dept_annee(df)

    st.info(
        "Use the animation controls to explore declaration counts from 1982 to 2025. "
        "Counts are not adjusted for department population or number of municipalities."
    )
    fig_anim = fig_carte_animee(
        agg_dept_an,
        agg_dept,
        geojson,
    )
    st.plotly_chart(fig_anim, use_container_width=True)
    st.caption("Department-level map for mainland France and Corsica. Source: GASPAR and data.gouv.fr.")
    st.warning("Overseas departments are not shown because matching boundaries are unavailable in this geographic dataset. Their records remain in the other charts.")

    # ── SECTION B — Classement ───────────────────────────────────────────────────
    st.subheader("Department rankings")
    n_top = st.slider("Departments to show", 5, 30, 15)
    top_departments = agg_dept.nlargest(n_top, "nb_arretes")[
        ["libelle_departement", "nb_arretes"]
    ].copy()
    top_departments = top_departments.rename(columns={
        "libelle_departement": "Department",
        "nb_arretes": "Declarations",
    })
    st.dataframe(
        top_departments,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Department": st.column_config.TextColumn("Department"),
            "Declarations": st.column_config.ProgressColumn(
                "Declarations", format="%d", min_value=0,
                max_value=max(1, int(top_departments["Declarations"].max())),
            ),
        },
    )
    st.caption(
        "These are raw totals, not rates. Departments with more municipalities may rank higher; "
        "a fair rate comparison requires an independent municipality or population denominator."
    )

    # ── SECTION C — Délai ────────────────────────────────────────────────────────
    st.subheader("Recognition delays are increasing")
    st.plotly_chart(fig_delai_boxplot(agg_delai_par_decennie(df)), use_container_width=True)
    st.caption("Time from the end of an event to publication, by decade. Delays longer than five years are excluded. Source: GASPAR.")
    st.markdown("The median delay rose from almost zero days in the 1980s and 1990s to more than 185 days in the 2020s. Recent years are therefore likely to be undercounted.")

    # ── SECTION D — Saisonnalité ─────────────────────────────────────────────────
    st.subheader("Seasonality by risk family")
    sais = agg_saisonnalite(df)
    sais = sais.copy()
    sais["famille"] = sais["famille"].map(FAMILY_LABELS_EN).fillna(sais["famille"])
    month_labels = {"Jan": "Jan", "Fév": "Feb", "Mar": "Mar", "Avr": "Apr", "Mai": "May", "Jun": "Jun", "Jul": "Jul", "Aoû": "Aug", "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Déc": "Dec"}
    sais["mois_label"] = sais["mois_label"].map(month_labels).fillna(sais["mois_label"])
    colors_en = {FAMILY_LABELS_EN[key]: value for key, value in PALETTE_CAT.items()}
    fig_s = px.bar(
        sais,
        x="mois_label",
        y="nb_arretes",
        color="famille",
        barmode="group",
        facet_col="famille",
        facet_col_wrap=3,
        color_discrete_map=colors_en,
        category_orders={
            "famille": [FAMILY_LABELS_EN[value] for value in FAMILLES_ORDER],
            "mois_label": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        },
        labels={"nb_arretes": "Declarations", "mois_label": "Month", "famille": "Risk family"},
    )
    fig_s.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_s.update_layout(
        title_text="Monthly declarations by risk family",
        title_font_size=15,
        height=500,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, Roboto, sans-serif", color="#18232d"),
    )
    st.plotly_chart(fig_s, use_container_width=True)
    st.caption("Monthly declaration totals by risk family, aggregated across all years.")
