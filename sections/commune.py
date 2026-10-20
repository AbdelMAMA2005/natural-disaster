# -*- coding: utf-8 -*-
"""
sections/commune.py — Fiche communale interactive CatNat
========================================================
Permet la recherche par nom ou code INSEE d'une commune pour afficher :
- Métriques clés (arrêtés, risque dominant, rang départemental, historique)
- Frise chronologique détaillée des événements reconnus
- Répartition par famille de risque
- Comparaison avec la médiane du département
- Tableau exhaustif des arrêtés
"""

import sys
from pathlib import Path

# Insertion du répertoire racine pour les imports absolus
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from constants import FAMILLES_ORDER, FAMILY_LABELS_EN, PALETTE_CAT, TYPE_LABELS_EN
from utils.prep import agg_par_commune
from utils.viz import fig_frise_commune


def render(df: pd.DataFrame) -> None:
    """
    Rendu de la fiche communale : recherche textuelle ou par code INSEE,
    métriques communales, frise chronologique et comparaison départementale.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet des arrêtés CatNat issu de load_and_prepare().
    """
    st.header("Explore a municipality's declaration history")
    st.markdown(
        "Search by official name or INSEE code to review the municipality's natural-disaster declarations since 1982."
    )

    recherche = st.text_input(
        "Search by municipality name or INSEE code",
        placeholder="For example: Nice, 06088, Bordeaux",
    )

    if len(recherche) >= 2:
        mask = (
            df["libelle_geographique"].str.contains(recherche, case=False, na=False, regex=False)
            | (df["code_geographique"] == recherche)
        )
        communes_trouvees = df[mask][
            ["code_geographique", "libelle_geographique", "departement", "libelle_departement"]
        ].drop_duplicates()

        if communes_trouvees.empty:
            st.warning("No municipality found. Check the spelling or INSEE code.")
        else:
            if len(communes_trouvees) > 1:
                options = communes_trouvees["code_geographique"].tolist()
                labels_map = {
                    row["code_geographique"]: f"{row['libelle_geographique']} ({row['departement']})"
                    for _, row in communes_trouvees.iterrows()
                }
                code_sel = st.selectbox(
                    "Select a municipality",
                    options=options,
                    format_func=lambda c: labels_map.get(c, str(c)),
                )
            else:
                code_sel = communes_trouvees.iloc[0]["code_geographique"]

            df_com = df[df["code_geographique"] == code_sel]
            nom_com = df_com["libelle_geographique"].iloc[0]
            dept_com = df_com["libelle_departement"].iloc[0]

            st.subheader(f"{nom_com} ({dept_com})")

            # Calculs pour les 4 métriques
            nb_com = int(df_com.shape[0])
            famille_dom = (
                df_com["famille"].value_counts().index[0]
                if not df_com["famille"].empty
                else "Not available"
            )
            annee_min = df_com["annee"].dropna().min()
            annee_min_str = str(int(annee_min)) if pd.notna(annee_min) else "Not available"

            dept_agg = agg_par_commune(
                df[df["departement"] == df_com["departement"].iloc[0]]
            ).reset_index(drop=True)
            row_matches = dept_agg.index[dept_agg["code_geographique"] == code_sel].tolist()
            if row_matches:
                rang_dept_str = f"{row_matches[0] + 1}e / {len(dept_agg)}"
            else:
                rang_dept_str = "1er"

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total declarations", f"{nb_com:,}")
            col2.metric("Leading risk family", FAMILY_LABELS_EN.get(famille_dom, famille_dom))
            col3.metric("Department rank", rang_dept_str)
            col4.metric("First declaration", annee_min_str)

            st.subheader("Declaration timeline")
            st.plotly_chart(fig_frise_commune(df_com, nom_com), use_container_width=True)
            st.caption("Each bar represents a recognized event period.")

            st.subheader("Declarations by risk family")
            fam_counts = df_com.groupby("famille").size().reset_index(name="nb_arretes")
            fam_counts["famille"] = fam_counts["famille"].map(FAMILY_LABELS_EN).fillna(fam_counts["famille"])
            fig_fam = px.bar(
                fam_counts,
                x="famille",
                y="nb_arretes",
                color="famille",
                color_discrete_map={FAMILY_LABELS_EN[key]: value for key, value in PALETTE_CAT.items()},
                category_orders={"famille": [FAMILY_LABELS_EN[value] for value in FAMILLES_ORDER]},
                labels={"nb_arretes": "Declarations", "famille": "Risk family"},
            )
            fig_fam.update_layout(
                showlegend=False,
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(family="Inter, Roboto, sans-serif", color="#18232d"),
                height=300,
            )
            st.plotly_chart(fig_fam, use_container_width=True)
            st.caption(f"Risk-family breakdown for {nom_com}.")

            st.subheader("Compared with the department")
            mediane_dept = int(dept_agg["nb_arretes"].median())
            st.metric(
                "Municipality declarations",
                nb_com,
                delta=f"{nb_com - mediane_dept:+d} vs department median ({mediane_dept})",
            )
            st.caption(f"Difference between {nom_com} and the municipal median in {dept_com}.")

            display_events = df_com[["date_debut", "date_fin", "date_arrete", "type_catastrophe", "famille"]].sort_values("date_debut").copy()
            display_events["type_catastrophe"] = display_events["type_catastrophe"].map(TYPE_LABELS_EN).fillna(display_events["type_catastrophe"])
            display_events["famille"] = display_events["famille"].map(FAMILY_LABELS_EN).fillna(display_events["famille"])
            display_events = display_events.rename(columns={
                "date_debut": "Event start",
                "date_fin": "Event end",
                "date_arrete": "Declaration date",
                "type_catastrophe": "Hazard type",
                "famille": "Risk family",
            })
            st.expander("Full declaration table").dataframe(
                display_events,
                use_container_width=True,
                hide_index=True,
            )
            st.caption("These records reflect administrative recognition and may not include every physical event experienced by the municipality.")
    else:
        st.info("Enter at least two characters to search.")
