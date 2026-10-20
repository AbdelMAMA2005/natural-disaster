# -*- coding: utf-8 -*-
"""
utils/prep.py — Nettoyage, feature engineering et tables pré-agrégées
======================================================================
Point d'entrée principal : load_and_prepare() → DataFrame nettoyé + cache.
Fonctions d'agrégation : chacune est décorée @st.cache_data pour éviter
tout calcul lourd dans la boucle d'affichage.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import (
    CSV_COLS, FAMILLE_MAP, FAMILLES_ORDER,
    ANNEES_REMARQUABLES, ANNEES_INCOMPLETES_DEBUT,
    SEUIL_GRAND_EPISODE, DROM_CODES, REGION_LABELS,
)
from utils.io import ensure_csv


# ── Lecture et nettoyage de base ─────────────────────────────────────────────

@st.cache_data(ttl=86_400, show_spinner="Chargement de la base CatNat…")
def load_and_prepare() -> pd.DataFrame:
    """
    Charge catnat.csv, applique tout le nettoyage et le feature engineering.
    Résultat mis en cache 24 h.

    Étapes :
    1. Lecture avec header=None, dtype=str, sep=";"
    2. Parse dates — arrondi au jour (supprime le décalage 02:00)
    3. Normalisation code région (zfill 2 → '01', '11'…)
    4. Colonnes dérivées : année, mois, décennie, durée, délai de reconnaissance
    5. Famille de risque (regroupement)
    6. Libellé région (join sur REGION_LABELS)

    Retourne un DataFrame avec toutes les colonnes originales + colonnes dérivées.
    """
    path = ensure_csv()

    df = pd.read_csv(
        path,
        sep=";",
        header=None,
        names=CSV_COLS,
        dtype=str,
        encoding="utf-8",
    )

    # ── 1. Parse dates ────────────────────────────────────────────────────────
    for col in ["date_debut", "date_fin", "date_arrete"]:
        df[col] = (
            pd.to_datetime(df[col], errors="coerce")
            .dt.floor("D")    # arrondi au jour → supprime 02:00
        )

    # ── 2. Normalisation code région ──────────────────────────────────────────
    # Certains codes sont '1','2','3','4','6' sans zéro initial
    df["region"] = df["region"].str.zfill(2)

    # ── 3. Colonnes dérivées ─────────────────────────────────────────────────
    df["annee"]    = df["date_debut"].dt.year.astype("Int64")
    df["mois"]     = df["date_debut"].dt.month.astype("Int64")
    df["decennie"] = (df["annee"] // 10 * 10).astype("Int64")

    # Durée de l'épisode en jours
    df["duree_j"]  = (df["date_fin"] - df["date_debut"]).dt.days

    # Délai de reconnaissance : date_arrete - date_fin (en jours)
    df["delai_reconnaissance_j"] = (df["date_arrete"] - df["date_fin"]).dt.days

    # ── 4. Famille de risque ─────────────────────────────────────────────────
    df["famille"] = df["type_catastrophe"].map(FAMILLE_MAP).fillna("Autres")

    # ── 5. Libellé région ────────────────────────────────────────────────────
    df["libelle_region"] = df["region"].map(REGION_LABELS).fillna("Inconnu")

    # ── 6. Flag DROM ─────────────────────────────────────────────────────────
    df["is_drom"] = df["departement"].isin(DROM_CODES)

    # ── 7. Flag données incomplètes (années récentes) ─────────────────────────
    df["donnees_incompletes"] = df["annee"] >= ANNEES_INCOMPLETES_DEBUT

    return df


# ── Tables pré-agrégées ──────────────────────────────────────────────────────

@st.cache_data(ttl=86_400, show_spinner=False)
def agg_par_annee(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nombre d'arrêtés par année.
    Colonnes : annee, nb_arretes, grand_episode (bool), annotation.
    """
    agg = (
        df.groupby("annee", dropna=True)
        .size()
        .reset_index(name="nb_arretes")
    )
    agg["grand_episode"] = agg["nb_arretes"] >= SEUIL_GRAND_EPISODE
    agg["annotation"] = agg["annee"].map(ANNEES_REMARQUABLES).fillna("")
    agg["donnees_incompletes"] = agg["annee"] >= ANNEES_INCOMPLETES_DEBUT
    return agg.sort_values("annee")


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_par_annee_famille(df: pd.DataFrame) -> pd.DataFrame:
    """Nombre d'arrêtés par (année, famille). Pour la heatmap et les petits multiples."""
    return (
        df.groupby(["annee", "famille"], dropna=True)
        .size()
        .reset_index(name="nb_arretes")
        .sort_values(["annee", "famille"])
    )


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_par_dept(df: pd.DataFrame) -> pd.DataFrame:
    """
    Statistiques par département :
    - nb_arretes brut
    - nb_communes_touchees (communes distinctes ayant au moins 1 arrêté)
    - nb_communes_total (communes distinctes dans le CSV pour ce dept)
    - pct_communes (nb_communes_touchees / nb_communes_total * 100)
    - famille_dominante
    """
    # Nombre total de communes distinctes par département (référence de normalisation)
    ref_communes = (
        df.groupby("departement")["code_geographique"]
        .nunique()
        .reset_index(name="nb_communes_total")
    )

    agg = (
        df.groupby(["departement", "libelle_departement"], dropna=True)
        .agg(
            nb_arretes=("index", "count"),
            nb_communes_touchees=("code_geographique", "nunique"),
        )
        .reset_index()
    )

    agg = agg.merge(ref_communes, on="departement", how="left")
    agg["pct_communes"] = (
        agg["nb_communes_touchees"] / agg["nb_communes_total"] * 100
    ).round(1)

    # Famille dominante par département
    fam_dom = (
        df.groupby(["departement", "famille"])
        .size()
        .reset_index(name="cnt")
        .sort_values("cnt", ascending=False)
        .drop_duplicates("departement")
        [["departement", "famille"]]
        .rename(columns={"famille": "famille_dominante"})
    )
    agg = agg.merge(fam_dom, on="departement", how="left")

    return agg


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_par_dept_annee(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nombre d'arrêtés par (département, année).
    Utilisé pour la carte animée.
    """
    return (
        df.groupby(["departement", "libelle_departement", "annee"], dropna=True)
        .size()
        .reset_index(name="nb_arretes")
        .sort_values(["annee", "departement"])
    )


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_par_commune(df: pd.DataFrame) -> pd.DataFrame:
    """
    Statistiques par commune :
    - nb_arretes, nb_types, familles_liste, annee_min, annee_max,
      famille_dominante, departement, libelle_departement, region, libelle_region
    """
    agg = (
        df.groupby(
            ["code_geographique", "libelle_geographique",
             "departement", "libelle_departement", "region", "libelle_region"],
            dropna=True,
        )
        .agg(
            nb_arretes=("index", "count"),
            annee_min=("annee", "min"),
            annee_max=("annee", "max"),
        )
        .reset_index()
    )

    fam_dom = (
        df.groupby(["code_geographique", "famille"])
        .size()
        .reset_index(name="cnt")
        .sort_values("cnt", ascending=False)
        .drop_duplicates("code_geographique")
        [["code_geographique", "famille"]]
        .rename(columns={"famille": "famille_dominante"})
    )
    agg = agg.merge(fam_dom, on="code_geographique", how="left")
    return agg.sort_values("nb_arretes", ascending=False)


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_delai_par_decennie(df: pd.DataFrame) -> pd.DataFrame:
    """
    Distribution du délai de reconnaissance (date_arrete - date_fin) par décennie.
    Filtre les valeurs aberrantes (délai > 5 ans ou négatif) pour les boîtes à moustaches.
    """
    sub = df[
        df["delai_reconnaissance_j"].notna()
        & (df["delai_reconnaissance_j"] >= 0)
        & (df["delai_reconnaissance_j"] <= 5 * 365)
    ].copy()
    sub["decennie_label"] = sub["decennie"].astype(str) + "s"
    return sub[["decennie_label", "delai_reconnaissance_j", "famille"]]


@st.cache_data(ttl=86_400, show_spinner=False)
def agg_saisonnalite(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nombre d'arrêtés par (mois, famille).
    Permet un graphique en petits multiples saisonniers.
    """
    mois_labels = {
        1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Aoû",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
    }
    agg = (
        df.groupby(["mois", "famille"], dropna=True)
        .size()
        .reset_index(name="nb_arretes")
    )
    agg["mois_label"] = agg["mois"].map(mois_labels)
    return agg


# ── Rapport de qualité ───────────────────────────────────────────────────────

@st.cache_data(ttl=86_400, show_spinner=False)
def build_quality_report(df: pd.DataFrame) -> dict:
    """
    Construit un dictionnaire de métriques de qualité des données.
    Utilisé par sections/quality.py pour afficher la section Qualité.
    """
    n = len(df)

    # Manquants (NaN)
    manquants = {col: int(df[col].isna().sum()) for col in df.columns}

    # Doublons (même commune + type + dates, sans tenir compte de l'index)
    cle_dup = ["code_geographique", "type_catastrophe", "date_debut", "date_fin"]
    dup_mask = df.duplicated(subset=cle_dup, keep=False)
    nb_dup = int(dup_mask.sum())

    # Incohérences date_arrete < date_fin
    incoherent_mask = df["date_arrete"] < df["date_fin"]
    nb_incoherent = int(incoherent_mask.sum())
    exemples_incoherent = df[incoherent_mask][
        ["code_geographique", "libelle_geographique", "type_catastrophe",
         "date_fin", "date_arrete"]
    ].head(8)

    # Couverture temporelle
    annee_min = int(df["annee"].min())
    annee_max = int(df["annee"].max())

    # Valeurs annee_recent
    n_recent = int((df["annee"] >= ANNEES_INCOMPLETES_DEBUT).sum())

    # Délai médian par décennie
    delai_median = (
        df[df["delai_reconnaissance_j"] >= 0]
        .groupby("decennie")["delai_reconnaissance_j"]
        .median()
        .round(0)
        .to_dict()
    )

    # Communes distinctes
    nb_communes = int(df["code_geographique"].nunique())

    # Nombre d'arrêtés si on déduplique
    df_dedup = df.drop_duplicates(subset=cle_dup)
    n_sans_dup = len(df_dedup)

    return {
        "n_total":            n,
        "n_sans_doublons":    n_sans_dup,
        "nb_dup":             nb_dup,
        "pct_dup":            round(nb_dup / n * 100, 1),
        "manquants":          manquants,
        "nb_incoherent":      nb_incoherent,
        "exemples_incoherent": exemples_incoherent,
        "annee_min":          annee_min,
        "annee_max":          annee_max,
        "nb_communes":        nb_communes,
        "n_recent":           n_recent,
        "annee_incompletes":  ANNEES_INCOMPLETES_DEBUT,
        "delai_median":       delai_median,
    }


# ── Filtre commun (appliqué par la sidebar) ──────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    annees: tuple[int, int] | None = None,
    regions: list[str] | None = None,
    familles: list[str] | None = None,
    inclure_drom: bool = True,
) -> pd.DataFrame:
    """
    Applique les filtres de la sidebar au DataFrame complet.
    Paramètres :
        annees   : (annee_min, annee_max) — inclusif
        regions  : liste de codes région (str, zfillés) ; None = toutes
        familles : liste de familles ; None = toutes
        inclure_drom : si False, exclut les départements DROM
    Retourne un DataFrame filtré.
    """
    mask = pd.Series(True, index=df.index)

    if annees is not None:
        mask &= df["annee"].between(annees[0], annees[1])

    if regions:
        mask &= df["region"].isin(regions)

    if familles:
        mask &= df["famille"].isin(familles)

    if not inclure_drom:
        mask &= ~df["is_drom"]

    return df[mask].copy()
