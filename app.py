# -*- coding: utf-8 -*-
"""
app.py — Point d'entrée principal de l'application Streamlit CatNat
====================================================================
Lance avec : streamlit run app.py
"""

import sys
import random
import base64
from pathlib import Path

# Assure que la racine du projet est dans PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd

from constants import (
    FOOTER_TEXT, REGION_LABELS,
    FAMILLES_ORDER, FAMILY_LABELS_EN, ANNEE_MIN_DEFAULT, ANNEE_MAX_DEFAULT,
)
from utils.io import load_geojson, get_source_info
from utils.prep import load_and_prepare, apply_filters

#  Configuration de la page 
st.set_page_config(
    page_title="Natural Disasters in France | GASPAR",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://www.data.gouv.fr/fr/datasets/arretes-de-catastrophe-naturelle-par-commune/",
        "Report a bug": None,
        "About": (
            "An editorial dashboard about natural-disaster declarations in France. "
            "Source: the GASPAR database on data.gouv.fr."
        ),
    },
)

#  Import des sections (après set_page_config) ─
import sections.intro       as s_intro
import sections.overview    as s_overview
import sections.deep_dives  as s_deep
import sections.commune     as s_commune
import sections.quality     as s_quality
import sections.conclusions as s_concl

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {
        --ink: #18232d;
        --muted: #5f6b75;
        --accent: #002B49;
        --rule: #d9e0e5;
        --sidebar: #F8F9FA;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Inter', 'Roboto', sans-serif;
        color: var(--ink);
    }
    .stApp, [data-testid="stAppViewContainer"] { background: #ffffff; }
    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--rule);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    h1, h2, h3 { color: var(--accent); font-weight: 600; letter-spacing: 0; }
    h1 { font-size: 2.35rem; line-height: 1.15; margin-bottom: 0.35rem; }
    [data-testid="stMetric"] {
        padding: 0.35rem 0.75rem;
        border-left: 4px solid var(--accent);
        background: transparent;
    }
    [data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-size: 0.7rem;
        line-height: 1.2;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    [data-testid="stMetricValue"] {
        color: var(--accent);
        font-size: 1.3rem;
        line-height: 1.2;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    [data-testid="stMetricValue"] > div {
        font-size: 1.05rem !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        overflow-wrap: anywhere;
    }
    [data-testid="stImage"] img { max-height: 230px; object-fit: cover; }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 88px;
        height: 88px;
        border-radius: 50%;
        object-fit: cover;
    }
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"] {
        font-size: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
        content: "‹";
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
    }
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"]::after {
        content: "›";
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
    }
    @media (max-width: 768px) {
        h1 { font-size: 1.55rem; }
        [data-testid="stMetricValue"] { font-size: 1.15rem; }
        [data-testid="stMetricValue"] > div { font-size: 0.9rem !important; }
        [data-testid="stMetric"] { padding: 0.25rem 0.45rem; }
        [data-testid="stImage"] img { max-height: 150px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

hero_banners = [
    "assets/HeroBanner01.jpg",
    "assets/HeroBanner02.jpg",
    "assets/HeroBanner03.jpeg",
]
available_banners = [banner for banner in hero_banners if Path(banner).exists()]
if "hero_banner" not in st.session_state and available_banners:
    st.session_state["hero_banner"] = random.choice(available_banners)
if st.session_state.get("hero_banner"):
    st.image(st.session_state["hero_banner"], use_container_width=True)

def image_to_base64(image_path: str) -> str:
    return base64.b64encode(Path(image_path).read_bytes()).decode("ascii")


efrei_logo_base64 = image_to_base64("assets/logo_efrei.png")
st.markdown(
    """
    <style>
    h1.academic-header-title {
        color: #002B49;
        font-size: 1.8rem !important;
        font-weight: 600;
        line-height: 1.12;
        letter-spacing: 0;
        margin: 0;
        overflow-wrap: anywhere;
    }
    .academic-identity {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        min-height: 40px;
        margin-bottom: 0.45rem;
    }
    .academic-logo {
        display: block;
        width: auto;
        height: 40px;
        object-fit: contain;
    }
    .academic-author {
        color: #18232d;
        font-size: 0.9rem;
        line-height: 1.35;
    }
    .academic-author strong { color: #002B49; }
    .academic-author-program {
        color: #5f6b75;
        font-size: 0.78rem;
    }
    .academic-info p { margin: 0.3rem 0; }
    .academic-info a { color: #002B49; }
    @media (max-width: 768px) {
        h1.academic-header-title { font-size: 1.45rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

title_column, academic_column = st.columns([3.2, 1.8], gap="large", vertical_alignment="center")
with title_column:
    st.markdown(
        '<h1 class="academic-header-title">Natural Disasters in France (1982-2025)</h1>',
        unsafe_allow_html=True,
    )

with academic_column:
    identity_column, info_column = st.columns([1.45, 1], vertical_alignment="center")
    with identity_column:
        st.markdown(
            f"""
            <div class="academic-identity">
                <img class="academic-logo" src="data:image/png;base64,{efrei_logo_base64}" alt="EFREI Logo">
                <div class="academic-author">
                    <strong>Abdel MAMA</strong>
                    <div class="academic-author-program">DAI</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with info_column:
        with st.popover("Project Info", use_container_width=True):
            st.markdown(
                """
                <div class="academic-info">
                    <p><strong>Name:</strong> Abdel MAMA</p>
                    <p><strong>Program:</strong> DAI</p>
                    <p><strong>Email:</strong> <a href="mailto:abdelmama2005@gmail.com">abdelmama2005@gmail.com</a></p>
                    <p><strong>Year:</strong> 2026</p>
                    <p><strong>Graduation:</strong> DAI</p>
                    <p><strong>Course Name:</strong> Data Storytelling</p>
                    <p><strong>Prof Name:</strong> Mano Joseph Mathew</p>
                    <p><strong>Project Period:</strong> Oct 2026</p>
                    <p><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/abdel-mama-b43804313/?isSelfProfile=true">Abdel MAMA</a></p>
                    <p><strong>GitHub:</strong> <a href="https://github.com/AbdelMAMA2005">AbdelMAMA2005</a></p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# Chargement des données (une seule fois, mis en cache)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=86_400, show_spinner=False)
def get_df() -> pd.DataFrame:
    return load_and_prepare()


# Chargement avec gestion d'erreur
try:
    df_full = get_df()
    geojson = load_geojson()
except Exception as e:
    st.error(f"Unable to load the dashboard data: {e}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar — filtres globaux
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("Explore the data")
    st.caption(
        "Filters apply across the dashboard. Clear selections to return to the full view."
    )

    section = st.radio(
        "Dashboard sections",
        ["Introduction", "Overview", "Territorial analysis", "By municipality", "Data quality", "Conclusions"],
        label_visibility="collapsed",
    )

    st.subheader("Time period")
    annee_min_data = int(df_full["annee"].min())
    annee_max_data = int(df_full["annee"].max())

    annees = st.slider(
        "Years",
        min_value=annee_min_data,
        max_value=annee_max_data,
        value=(ANNEE_MIN_DEFAULT, ANNEE_MAX_DEFAULT),
        step=1,
        help="Filter by the year in which an event began.",
    )

    st.subheader("Region")
    region_options = sorted(df_full["region"].dropna().unique().tolist())
    region_labels_map = {r: REGION_LABELS.get(r, r) for r in region_options}
    region_display = [region_labels_map[r] for r in region_options]

    selected_regions_display = st.multiselect(
        "Regions",
        options=region_display,
        default=[],
        placeholder="All regions",
        help="Choose one or more regions. Leave empty to include all regions.",
    )
    # Convertir les libellés sélectionnés en codes
    inv_map = {v: k for k, v in region_labels_map.items()}
    selected_regions = [inv_map[r] for r in selected_regions_display] or None

    st.subheader("Risk family")
    family_values = {label: value for value, label in FAMILY_LABELS_EN.items()}
    selected_familles = st.multiselect(
        "Risk families",
        options=[FAMILY_LABELS_EN[value] for value in FAMILLES_ORDER],
        default=[],
        placeholder="All risk families",
        help="Choose one or more risk families.",
    )
    familles_filter = [family_values[value] for value in selected_familles] or None

    #  DROM 
    inclure_drom = st.checkbox(
        "Include overseas departments",
        value=True,
        help="Overseas departments are included in the data but are not present on the map.",
    )

    st.caption(
        "**Sources**\n\n"
        "GASPAR — Open Licence v2.0\n\n"
        "Administrative boundaries — ODbL\n\n"
        "GASPAR edition: September 2025"
    )

    st.subheader("Author")
    author_photo = Path("assets/abdel-mama.jpg")
    if author_photo.exists():
        st.image(str(author_photo))
    st.markdown(
        "**Abdel MAMA**\n\n"
        "[LinkedIn](https://www.linkedin.com/in/abdel-mama-b43804313/)\n\n"
        "[abdelmama2005@gmail.com](mailto:abdelmama2005@gmail.com)"
    )


#  Application du filtre global 
df = apply_filters(
    df_full,
    annees=annees,
    regions=selected_regions,
    familles=familles_filter,
    inclure_drom=inclure_drom,
)

#  KPI d'en-tête ─
n_total      = len(df)
n_communes   = df["code_geographique"].nunique()
n_full       = len(df_full)  # référence pour les deltas

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    "Declarations in selection",
    f"{n_total:,}",
    delta=f"{n_total - n_full:+,} vs total",
    delta_color="off",
    help="Total CatNat declarations in the current filtered selection.",
)
c2.metric(
    "Municipalities affected",
    f"{n_communes:,}",
    help="Distinct municipalities in the current selection.",
)
c3.metric(
    "Period",
    f"{annees[0]} – {annees[1]}",
    help="Selected reporting period.",
)
top_famille = df["famille"].value_counts().index[0] if n_total > 0 else "—"
c4.metric(
    "Leading risk family",
    FAMILY_LABELS_EN.get(top_famille, top_famille),
    help="Most frequent risk family in the current selection.",
)
top_dept = (
    df.groupby("libelle_departement").size().idxmax()
    if n_total > 0 else "—"
)
c5.metric(
    "Leading department",
    top_dept,
    help="Department with the highest declaration count in the current selection.",
)

if section == "Introduction":
    s_intro.render(df_full)
elif section == "Overview":
    s_overview.render(df)
elif section == "Territorial analysis":
    s_deep.render(df, geojson)
elif section == "By municipality":
    s_commune.render(df_full)
elif section == "Data quality":
    s_quality.render(df_full)
else:
    s_concl.render(df)

st.caption(FOOTER_TEXT)
