# -*- coding: utf-8 -*-
"""
utils/io.py — Téléchargement, cache local, vérification sha1, métadonnées
==========================================================================
- download_csv()     : télécharge catnat.csv si absent, vérifie sha1
- download_geojson() : télécharge le GeoJSON des départements si absent
- get_source_info()  : renvoie un dict de métadonnées (licences, dates)
Toutes les fonctions utilisent st.cache_data (TTL 24 h) là où c'est possible.
"""

import os
import hashlib
import json
import logging
from pathlib import Path

import requests
import streamlit as st

# Import absolu pour que le script fonctionne depuis n'importe où
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import (
    CSV_URL, CSV_SHA1, CSV_PATH,
    GEOJSON_URL, GEOJSON_PATH,
    DATA_DIR,
)

logger = logging.getLogger(__name__)
os.makedirs(DATA_DIR, exist_ok=True)

# ── Helpers internes ──────────────────────────────────────────────────────────

def _sha1(path: str) -> str:
    """Calcule le sha1 d'un fichier par blocs de 1 Mo."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: str, label: str) -> None:
    """
    Télécharge `url` vers `dest`.
    Affiche une barre de progression Streamlit.
    Lève RuntimeError si le réseau échoue.
    """
    try:
        r = requests.get(url, stream=True, timeout=180)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0

        progress = st.progress(0, text=f"Downloading {label}…")
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    progress.progress(
                        min(downloaded / total, 1.0),
                        text=f"Downloading {label}… {downloaded/1e6:.1f}/{total/1e6:.1f} MB",
                    )
        progress.empty()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Unable to download {label}. "
            f"Check your connection or copy the file manually into `data/`. "
            f"Details: {exc}"
        ) from exc


# ── Fonctions publiques ───────────────────────────────────────────────────────

def ensure_csv() -> str:
    """
    S'assure que catnat.csv est présent et intègre (sha1).
    Retourne le chemin local du fichier.
    Affiche un message d'erreur Streamlit et stoppe l'app si le téléchargement échoue.
    """
    if not os.path.exists(CSV_PATH):
        st.info(
            "First use: downloading the CatNat database (about 50 MB).\n"
            "This may take around 30 seconds, depending on your connection."
        )
        try:
            _download(CSV_URL, CSV_PATH, "the GASPAR database")
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

    # Vérification sha1 (rapide, fichier déjà en cache)
    actual = _sha1(CSV_PATH)
    if actual != CSV_SHA1:
        st.warning(
            f"The local CSV does not match the expected SHA-1 checksum.\n"
            f"Expected: `{CSV_SHA1}`\n"
            f"Calculated: `{actual}`\n"
            "The source file may have changed on data.gouv.fr. Remove `data/catnat.csv` "
            "and restart the app to download it again."
        )
    return CSV_PATH


def ensure_geojson() -> str:
    """
    S'assure que le GeoJSON des départements est présent.
    Retourne le chemin local du fichier.
    """
    if not os.path.exists(GEOJSON_PATH):
        st.info("Downloading department boundaries (about 3 MB).")
        try:
            _download(GEOJSON_URL, GEOJSON_PATH, "department boundaries")
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()
    return GEOJSON_PATH


@st.cache_data(ttl=86_400, show_spinner=False)
def load_geojson() -> dict:
    """Charge et met en cache le GeoJSON des départements (TTL 24 h)."""
    path = ensure_geojson()
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_source_info() -> dict:
    """
    Renvoie un dictionnaire de métadonnées de source pour l'affichage dans l'app.
    """
    from constants import (
        CSV_SOURCE_URL, CSV_LICENSE, CSV_PUBLISHED, DATA_MILLESIME,
        GEOJSON_SOURCE, GEOJSON_LICENSE,
    )
    return {
        "csv_source_url":  CSV_SOURCE_URL,
        "csv_license":     CSV_LICENSE,
        "csv_published":   CSV_PUBLISHED,
        "data_millesime":  DATA_MILLESIME,
        "geojson_source":  GEOJSON_SOURCE,
        "geojson_license": GEOJSON_LICENSE,
    }
