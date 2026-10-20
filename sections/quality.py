# -*- coding: utf-8 -*-
"""
sections/quality.py — Section Qualité des données CatNat
=========================================================
Présente l'audit de qualité des données de la base GASPAR :
valeurs manquantes, doublons suspects, incohérences de dates,
retard administratif et limites intrinsèques du jeu de données.
"""

import sys
from pathlib import Path

# Insertion du répertoire racine pour les imports absolus
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from constants import ANNEES_INCOMPLETES_DEBUT, FAMILY_LABELS_EN, TYPE_LABELS_EN
from utils.prep import build_quality_report


def render(df: pd.DataFrame) -> None:
    """
    Affiche le rapport complet de qualité et d'intégrité des données CatNat.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame complet des arrêtés CatNat issu de load_and_prepare().
    """
    st.header("Data quality and limitations")

    qr = build_quality_report(df)

    # 1. Aperçu général
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total declarations", f"{qr['n_total']:,}")
    col2.metric("Excluding suspected duplicates", f"{qr['n_sans_doublons']:,}")
    col3.metric("Distinct municipalities", f"{qr['nb_communes']:,}")

    # 2. Valeurs manquantes
    st.subheader("Missing values")
    manquants_dict = {col: count for col, count in qr["manquants"].items() if count > 0}
    if manquants_dict:
        df_manquants = pd.DataFrame(
            [
                {
                    "Column": col,
                    "Missing values": count,
                    "Share of total (%)": round((count / qr["n_total"]) * 100, 2),
                }
                for col, count in manquants_dict.items()
            ]
        )
        st.dataframe(df_manquants, use_container_width=True, hide_index=True)
    else:
        st.info("No missing values detected.")

    st.markdown(
        "Columns with missing values (`ept`, `code_pnr`, `libelle_pnr`, `libelle_petr`) are not used in the "
        "analysis. The key municipality, department, region, hazard-type, and date fields have no missing values."
    )

    # 3. Doublons suspects
    st.subheader("Suspected duplicates")
    st.metric(
        "Rows with matching municipality, type, and dates",
        f"{qr['nb_dup']:,}",
        f"{qr['pct_dup']}% of total",
    )
    st.markdown(
        "**Definition:** rows with identical values for "
        "`code_geographique` + `type_catastrophe` + `date_debut` + `date_fin`, differing only in their "
        "index identifier."
    )
    st.markdown(
        f"If removed: {qr['n_total']:,} → {qr['n_sans_doublons']:,} rows "
        f"({qr['n_total'] - qr['n_sans_doublons']:,} rows removed)"
    )
    st.warning(
        "These rows are retained throughout the dashboard. Removing them automatically could erase distinct "
        "declarations made on the same day for the same municipality and event."
    )

    # 4. Incohérences de dates
    st.subheader("Date inconsistencies")
    st.metric("Declarations dated before the event ended", str(qr["nb_incoherent"]))
    if not qr["exemples_incoherent"].empty:
        display_examples = qr["exemples_incoherent"].rename(columns={
            "code_geographique": "INSEE code",
            "libelle_geographique": "Municipality",
            "departement": "Department code",
            "libelle_departement": "Department",
            "date_debut": "Event start",
            "date_fin": "Event end",
            "date_arrete": "Declaration date",
            "type_catastrophe": "Hazard type",
            "famille": "Risk family",
        }).copy()
        if "type_catastrophe" in qr["exemples_incoherent"].columns:
            display_examples["Hazard type"] = display_examples["Hazard type"].map(TYPE_LABELS_EN).fillna(display_examples["Hazard type"])
        if "famille" in qr["exemples_incoherent"].columns:
            display_examples["Risk family"] = display_examples["Risk family"].map(FAMILY_LABELS_EN).fillna(display_examples["Risk family"])
        st.dataframe(display_examples, use_container_width=True, hide_index=True)
    st.markdown(
        f"{qr['nb_incoherent']} cases out of {qr['n_total']:,}, likely minor data-entry errors. "
        "They are not corrected and have negligible impact."
    )

    # 5. Retard de reconnaissance et sous-comptage récent
    st.subheader("Recognition delays and recent undercounting")
    delai_records = [
        {"Decade": f"{int(dec)}s", "Median delay (days)": int(delai)}
        for dec, delai in sorted(qr["delai_median"].items())
    ]
    df_delai = pd.DataFrame(delai_records)
    st.dataframe(df_delai, use_container_width=True, hide_index=True)

    st.metric(
        "Declarations since " + str(ANNEES_INCOMPLETES_DEBUT),
        f"{qr['n_recent']:,}",
        "(incomplete data)",
    )
    st.warning(
        "The years "
        + str(ANNEES_INCOMPLETES_DEBUT)
        + "–2025 contain only "
        + str(qr["n_recent"])
        + " declarations. This figure is likely an undercount because many cases are still being processed. "
        "Comparisons with earlier years should account for this bias."
    )

    # 6. Années à grand épisode
    st.subheader("Major-event years")
    st.markdown(
        "1999 has about 57,907 rows (storms Martin and Lothar and widespread flooding); 1982–1983 have more "
        "than 52,000 rows. These peaks dominate the raw trend and can be hidden with the overview control."
    )

    # 7. Changements de périmètre du régime CatNat
    st.subheader("Changes in scheme coverage")
    st.markdown(
        "Storms left the CatNat scheme around 1989 and became covered by standard insurance. Hail and snow "
        "were removed around 2010. These changes make long-term comparisons difficult for those risk families."
    )

    # 8. Ce que les données ne contiennent pas
    st.subheader("What the data do not contain")
    st.info(
        "There are no population figures, damage costs, casualty counts, or physical intensity measures. "
        "A CatNat declaration records administrative recognition, not event severity."
    )

    # 9. Conclusion
    st.success(
        f"Overall data quality is satisfactory: key fields have no missing values, and {qr['n_total']:,} rows cover 43 years. "
        "The limitations above are documented and should inform interpretation."
    )
