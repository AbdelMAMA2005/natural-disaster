# -*- coding: utf-8 -*-
"""
constants.py — Constantes centralisées du projet CatNat
=========================================================
Toutes les valeurs "dures" sont ici : chemins, couleurs, mappings.
N'importe quel module peut faire `from constants import ...`.
"""

import os

# ── Chemins ───────────────────────────────────────────────────────────────────
ROOT_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(ROOT_DIR, "data")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

CSV_PATH     = os.path.join(DATA_DIR, "catnat.csv")
GEOJSON_PATH = os.path.join(DATA_DIR, "departements_100m.geojson")

# ── URLs et métadonnées de la source ─────────────────────────────────────────
CSV_URL  = "https://www.data.gouv.fr/api/1/datasets/r/b3d02000-5f25-4967-a210-a4051dd620a1"
CSV_SHA1 = "9776cdc55f506c648ab45a05ed184682870a689f"
CSV_PUBLISHED  = "20/07/2026"          # date de publication du fichier CSV
DATA_MILLESIME = "September 2025"      # GASPAR edition
CSV_SOURCE_URL = "https://www.data.gouv.fr/fr/datasets/arretes-de-catastrophe-naturelle-par-commune/"
CSV_LICENSE    = "Open Licence v2.0 (Etalab)"

GEOJSON_URL     = "https://www.data.gouv.fr/api/1/datasets/r/90b9341a-e1f7-4d75-a73c-bbc010c7feeb"
GEOJSON_SOURCE  = "Administrative boundaries — data.gouv.fr"
GEOJSON_LICENSE = "ODbL (Open Database License)"

# ── Colonnes du CSV (pas d'en-tête dans le fichier brut) ─────────────────────
CSV_COLS = [
    "index", "code_geographique", "libelle_geographique",
    "epci", "libelle_epci",
    "departement", "libelle_departement",
    "region",
    "ept", "libelle_petr",
    "code_pnr", "libelle_pnr",
    "type_catastrophe",
    "date_debut", "date_fin", "date_arrete",
]

# ── Familles de risque (regroupement pour le récit) ───────────────────────────
# Clé = valeur exacte dans type_catastrophe ; Valeur = famille affichée
FAMILLE_MAP: dict[str, str] = {
    "Inondations":                       "Inondations",
    "Sécheresse":                        "Sécheresse & retrait argiles",
    "Retrait-gonflement des argiles":    "Sécheresse & retrait argiles",
    "Mouvements de terrain":             "Mouvements de terrain",
    "Cyclones / Tempêtes":               "Tempêtes & cyclones",
    "Grêle / neige":                     "Grêle & neige",
    "Avalanche":                         "Autres",
    "Divers":                            "Autres",
}

FAMILLES_ORDER = [
    "Inondations",
    "Sécheresse & retrait argiles",
    "Mouvements de terrain",
    "Tempêtes & cyclones",
    "Grêle & neige",
    "Autres",
]

FAMILY_LABELS_EN: dict[str, str] = {
    "Inondations": "Floods",
    "Sécheresse & retrait argiles": "Drought and soil shrinkage",
    "Mouvements de terrain": "Ground movements",
    "Tempêtes & cyclones": "Storms and cyclones",
    "Grêle & neige": "Hail and snow",
    "Autres": "Other",
}

TYPE_LABELS_EN: dict[str, str] = {
    "Inondations": "Floods",
    "Sécheresse": "Drought",
    "Retrait-gonflement des argiles": "Soil shrinkage and swelling",
    "Mouvements de terrain": "Ground movements",
    "Cyclones / Tempêtes": "Cyclones and storms",
    "Grêle / neige": "Hail and snow",
    "Avalanche": "Avalanche",
    "Divers": "Other events",
}

# ── Palette accessible (daltonisme-friendly, séquentielle + catégorielle) ─────
# Source : ColorBrewer2 / Okabe-Ito
PALETTE_CAT: dict[str, str] = {
    "Inondations":                   "#1f77b4",   # bleu
    "Sécheresse & retrait argiles":  "#d62728",   # rouge/brun
    "Mouvements de terrain":         "#8c6d31",   # marron
    "Tempêtes & cyclones":           "#7f7f7f",   # gris
    "Grêle & neige":                 "#17becf",   # cyan
    "Autres":                        "#bcbd22",   # jaune-vert
}

PALETTE_SEQ = "Blues"           # choroplèthe valeur brute
PALETTE_SEQ_NORMALIZED = "YlOrRd"  # choroplèthe normalisée (% communes)

# ── Mapping codes région INSEE → libellé ─────────────────────────────────────
# Source : code.travail.gouv.fr / INSEE — 18 régions métropole + DROM
REGION_LABELS: dict[str, str] = {
    "01": "Guadeloupe",
    "02": "Martinique",
    "03": "Guyane",
    "04": "La Réunion",
    "06": "Mayotte",
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}

DROM_CODES = {"971", "972", "973", "974", "976"}

# ── Années remarquables à annoter ─────────────────────────────────────────────
ANNEES_REMARQUABLES: dict[int, str] = {
    1999: "Storms Martin & Lothar\n+ major floods",
    2003: "Heatwave — drought peak",
    2010: "Storm Xynthia + Var floods",
    2018: "Drought peak",
    2022: "Record drought",
}

# Années récentes sous-comptées (retard de reconnaissance)
ANNEES_INCOMPLETES_DEBUT = 2023   # à partir de cette année, données partielles

# ── Période par défaut dans la sidebar ───────────────────────────────────────
ANNEE_MIN_DEFAULT = 1982
ANNEE_MAX_DEFAULT = 2025

# ── Seuil pour la détection de "grand épisode" ───────────────────────────────
SEUIL_GRAND_EPISODE = 5_000   # lignes par année → annotation sur la courbe

# ── Textes de l'app ───────────────────────────────────────────────────────────
APP_TITLE  = "Natural Disasters in France"
APP_SUBTITLE = "A record of local natural-disaster declarations, 1982–2025"
FOOTER_TEXT = (
    "Sources: GASPAR municipal disaster declarations "
    f"(data.gouv.fr, {CSV_LICENSE}); "
    f"administrative boundaries (data.gouv.fr, {GEOJSON_LICENSE}). "
    f"GASPAR edition: {DATA_MILLESIME}; CSV published {CSV_PUBLISHED}."
)
