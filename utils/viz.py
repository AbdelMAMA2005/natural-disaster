# -*- coding: utf-8 -*-
"""
utils/viz.py — Fonctions de visualisation Plotly (style cohérent)
=================================================================
Chaque fonction retourne une figure Plotly prête à passer à st.plotly_chart().
Convention :
 - Axes et unités toujours étiquetés
 - Infobulles (hovertemplate) explicites
 - Palette conforme à constants.PALETTE_CAT / PALETTE_SEQ
 - Texte en français
"""

import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import (
    PALETTE_CAT, PALETTE_SEQ,
    FAMILY_LABELS_EN, TYPE_LABELS_EN, FAMILLES_ORDER,
    ANNEES_REMARQUABLES, ANNEES_INCOMPLETES_DEBUT,
)

# Shared presentation palette
_FONT_FAMILY = "Inter, Roboto, sans-serif"
_BG_COLOR    = "#ffffff"
_PAPER_COLOR = "#ffffff"
_FONT_COLOR  = "#18232d"
_GRID_COLOR  = "#e3e8ec"
_PALETTE_CAT_EN = {FAMILY_LABELS_EN[key]: value for key, value in PALETTE_CAT.items()}

_LAYOUT_BASE = dict(
    font=dict(family=_FONT_FAMILY, color=_FONT_COLOR, size=13),
    paper_bgcolor=_PAPER_COLOR,
    plot_bgcolor=_BG_COLOR,
    margin=dict(l=60, r=20, t=60, b=60),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
)


def _apply_base(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(title_text=title, title_font_size=15, height=height, **_LAYOUT_BASE)
    fig.update_xaxes(gridcolor=_GRID_COLOR, linecolor=_GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=_GRID_COLOR, linecolor=_GRID_COLOR, zeroline=False)
    return fig


# ── 1. Courbe temporelle ──────────────────────────────────────────────────────

def fig_courbe_annuelle(
    agg: pd.DataFrame,
    log_scale: bool = False,
    masquer_pics: bool = False,
    familles_agg: pd.DataFrame | None = None,
) -> go.Figure:
    """
    Courbe du nombre d'arrêtés par année.

    Paramètres :
        agg           : résultat de prep.agg_par_annee(df)
        log_scale     : axe Y en log
        masquer_pics  : retire les années avec grand_episode=True
        familles_agg  : si fourni, trace les lignes par famille (small multiples)
    """
    data = agg.copy()
    if masquer_pics:
        data = data[~data["grand_episode"]]

    fig = go.Figure()

    # Zone grisée : données incomplètes
    annee_max = int(data["annee"].max())
    fig.add_vrect(
        x0=ANNEES_INCOMPLETES_DEBUT - 0.5,
        x1=annee_max + 0.5,
        fillcolor="rgba(200,200,200,0.08)",
        line_width=0,
        annotation_text="Incomplete<br>data",
        annotation_position="top left",
        annotation_font=dict(color="#5f6b75", size=11),
    )

    # Courbe principale
    fig.add_trace(
        go.Scatter(
            x=data["annee"],
            y=data["nb_arretes"],
            mode="lines+markers",
            name="Total",
            line=dict(color="#002B49", width=2.5),
            marker=dict(size=4),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Declarations: <b>%{y:,}</b><extra></extra>"
            ),
        )
    )

    # Annotations années remarquables
    for annee, texte in ANNEES_REMARQUABLES.items():
        row = data[data["annee"] == annee]
        if row.empty:
            continue
        y_val = row.iloc[0]["nb_arretes"]
        fig.add_annotation(
            x=annee, y=y_val,
            text=texte,
            showarrow=True,
            arrowhead=2,
            arrowcolor="#9a5b20",
            font=dict(size=10, color="#714417"),
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#c9a36a",
            ax=20, ay=-40,
        )

    yaxis = dict(
        title="Number of declarations",
        type="log" if log_scale else "linear",
        gridcolor=_GRID_COLOR,
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis=yaxis,
        height=430,
        **_LAYOUT_BASE,
    )
    return fig


# ── 2. Heatmap année × famille ────────────────────────────────────────────────

def fig_heatmap(agg: pd.DataFrame) -> go.Figure:
    """
    Heatmap (année × famille de risque) du nombre d'arrêtés.
    Paramètre : résultat de prep.agg_par_annee_famille(df).
    """
    pivot = (
        agg.pivot_table(
            index="famille", columns="annee",
            values="nb_arretes", fill_value=0,
        )
        .reindex(FAMILLES_ORDER)
    )
    pivot = pivot.rename(index=FAMILY_LABELS_EN)

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="YlOrRd",
            hovertemplate=(
                "Risk family: <b>%{y}</b><br>"
                "Year: <b>%{x}</b><br>"
                "Declarations: <b>%{z:,}</b><extra></extra>"
            ),
            colorbar=dict(title="Declarations"),
        )
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="",
        height=340,
        **_LAYOUT_BASE,
    )
    return fig


# ── 3. Carte choroplèthe départements ─────────────────────────────────────────

def fig_carte_dept(
    agg_dept: pd.DataFrame,
    geojson: dict,
    colonne: str = "nb_arretes",
    titre_legende: str = "Declarations",
    annee_label: str = "",
) -> go.Figure:
    """
    Carte choroplèthe des départements (métropole + Corse).

    Paramètres :
        agg_dept       : DataFrame with department declaration counts and leading risk family
        geojson        : GeoJSON chargé par io.load_geojson()
        colonne        : column to visualize; currently only 'nb_arretes' is supported
        titre_legende  : légende de l'échelle de couleur
        annee_label    : affichée dans le titre si fournie
    """
    if colonne != "nb_arretes":
        raise ValueError("Department maps currently support declaration counts only.")

    display_data = agg_dept.copy()
    display_data["famille_dominante"] = display_data["famille_dominante"].map(FAMILY_LABELS_EN).fillna(display_data["famille_dominante"])

    fig = px.choropleth_map(
        display_data,
        geojson=geojson,
        locations="departement",
        featureidkey="properties.code",
        color=colonne,
        color_continuous_scale=PALETTE_SEQ,
        map_style="carto-positron",
        center={"lat": 46.6, "lon": 2.5},
        zoom=4.3,
        hover_name="libelle_departement",
        hover_data={
            "departement": True,
            "nb_arretes": True,
            "famille_dominante": True,
        },
        labels={
            colonne: titre_legende,
            "departement": "Department code",
            "nb_arretes": "Declarations",
            "famille_dominante": "Leading risk family",
        },
    )

    fig.update_coloraxes(colorbar_title_text=titre_legende)
    titre = f"Department map — {annee_label}" if annee_label else "Department map"
    fig.update_layout(
        title_text=titre,
        title_font_size=14,
        height=520,
        map=dict(style="carto-positron"),
        **_LAYOUT_BASE,
    )
    return fig


# ── 4. Carte animée (slider année) ────────────────────────────────────────────

def fig_carte_animee(
    agg_dept_annee: pd.DataFrame,
    agg_dept_ref: pd.DataFrame,
    geojson: dict,
    colonne: str = "nb_arretes",
    titre_legende: str = "Arrêtés / an",
) -> go.Figure:
    """
    Carte choroplèthe animée avec curseur d'année.

    Paramètres :
        agg_dept_annee : résultat de prep.agg_par_dept_annee(df)
        agg_dept_ref   : résultat de prep.agg_par_dept(df) pour les infobulles
        geojson        : GeoJSON chargé
        colonne        : 'nb_arretes'
    """
    # Join department-level context for the hover labels.
    agg = agg_dept_annee.merge(
        agg_dept_ref[["departement", "famille_dominante"]],
        on="departement", how="left",
    )
    agg["annee_str"] = agg["annee"].astype(str)
    agg["famille_dominante"] = agg["famille_dominante"].map(FAMILY_LABELS_EN).fillna(agg["famille_dominante"])

    fig = px.choropleth_map(
        agg,
        geojson=geojson,
        locations="departement",
        featureidkey="properties.code",
        color=colonne,
        animation_frame="annee_str",
        color_continuous_scale=PALETTE_SEQ,
        range_color=[0, agg[colonne].quantile(0.97)],
        map_style="carto-positron",
        center={"lat": 46.6, "lon": 2.5},
        zoom=4.3,
        hover_name="libelle_departement",
        hover_data={
            "departement": True,
            "nb_arretes": True,
            "famille_dominante": True,
        },
        labels={
            colonne: titre_legende,
            "nb_arretes": "Declarations",
            "departement": "Department code",
            "famille_dominante": "Leading risk family",
        },
    )

    fig.update_layout(
        title_text="Declarations by department, 1982–2025",
        title_font_size=14,
        height=540,
        map=dict(style="carto-positron"),
        **_LAYOUT_BASE,
    )
    return fig


# ── 5. Petits multiples par famille ──────────────────────────────────────────

def fig_small_multiples(agg: pd.DataFrame) -> go.Figure:
    """
    6 sous-graphiques (un par famille de risque), courbe d'arrêtés par année.
    Paramètre : résultat de prep.agg_par_annee_famille(df).
    """
    familles = FAMILLES_ORDER
    n_cols = 3
    n_rows = (len(familles) + n_cols - 1) // n_cols

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[FAMILY_LABELS_EN[value] for value in familles],
        shared_xaxes=False,
        shared_yaxes=False,
        vertical_spacing=0.14,
        horizontal_spacing=0.08,
    )

    for i, fam in enumerate(familles):
        row = i // n_cols + 1
        col = i % n_cols + 1
        sub = agg[agg["famille"] == fam].sort_values("annee")
        couleur = PALETTE_CAT.get(fam, "#aaaaaa")

        fig.add_trace(
            go.Scatter(
                x=sub["annee"],
                y=sub["nb_arretes"],
                mode="lines",
                name=FAMILY_LABELS_EN.get(fam, fam),
                line=dict(color=couleur, width=1.5),
                hovertemplate=(
                    f"<b>{FAMILY_LABELS_EN.get(fam, fam)}</b><br>"
                    "Year: %{x}<br>"
                    "Declarations: %{y:,}<extra></extra>"
                ),
                showlegend=False,
            ),
            row=row, col=col,
        )

    fig.update_layout(
        height=n_rows * 200 + 60,
        **_LAYOUT_BASE,
    )
    # Ajouter zone données incomplètes sur chaque sous-graphe
    for i in range(1, len(familles) + 1):
        row = (i - 1) // n_cols + 1
        col = (i - 1) % n_cols + 1
        fig.add_vrect(
            x0=ANNEES_INCOMPLETES_DEBUT - 0.5, x1=2025.5,
            fillcolor="rgba(200,200,200,0.07)", line_width=0,
            row=row, col=col,
        )

    return fig


# ── 6. Classement top/bottom départements ────────────────────────────────────

def fig_classement_dept(
    agg_dept: pd.DataFrame,
    n: int = 15,
    colonne: str = "nb_arretes",
    etiquette_x: str = "Nombre d'arrêtés",
    titre: str = "Classement des départements",
) -> go.Figure:
    """Horizontal bar chart of the top N departments."""
    top = agg_dept.nlargest(n, colonne).sort_values(colonne)
    couleurs = [PALETTE_CAT.get(f, "#002B49") for f in top["famille_dominante"]]

    fig = go.Figure(
        go.Bar(
            x=top[colonne],
            y=top["libelle_departement"],
            orientation="h",
            marker_color=couleurs,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{etiquette_x}: " + "%{x:,}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        xaxis_title=etiquette_x,
        yaxis_title="",
        height=max(350, n * 26),
        **_LAYOUT_BASE,
    )
    return fig


# ── 7. Boîtes à moustaches — délai de reconnaissance ─────────────────────────

def fig_delai_boxplot(agg: pd.DataFrame) -> go.Figure:
    """
    Boîtes à moustaches du délai de reconnaissance (date_arrete - date_fin)
    par décennie.
    Paramètre : résultat de prep.agg_delai_par_decennie(df).
    """
    decennies = sorted(agg["decennie_label"].unique())
    fig = go.Figure()

    for dec in decennies:
        sub = agg[agg["decennie_label"] == dec]["delai_reconnaissance_j"]
        fig.add_trace(
            go.Box(
                y=sub,
                name=dec,
                boxmean="sd",
                marker_color="#4C9BE8",
                hovertemplate=(
                    f"<b>{dec}</b><br>"
                    "Delay (days): %{y:,}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.update_layout(
        title_text="Recognition delays by decade",
        title_font_size=15,
        yaxis_title="Recognition delay (days)",
        xaxis_title="Decade",
        height=400,
        **_LAYOUT_BASE,
    )
    return fig


# ── 8. Frise chronologique commune ───────────────────────────────────────────

def fig_frise_commune(df_commune: pd.DataFrame, nom_commune: str) -> go.Figure:
    """
    Frise chronologique des arrêtés d'une commune.
    Chaque arrêté est un segment coloré par famille.
    Paramètre : sous-ensemble df filtré sur une commune.
    """
    df_c = df_commune.sort_values("date_debut").copy()
    df_c["date_fin_safe"] = df_c["date_fin"].fillna(df_c["date_debut"] + pd.Timedelta(days=1))
    df_c["famille"] = df_c["famille"].map(FAMILY_LABELS_EN).fillna(df_c["famille"])
    df_c["type_catastrophe"] = df_c["type_catastrophe"].map(TYPE_LABELS_EN).fillna(df_c["type_catastrophe"])

    fig = px.timeline(
        df_c,
        x_start="date_debut",
        x_end="date_fin_safe",
        y="famille",
        color="famille",
        color_discrete_map=_PALETTE_CAT_EN,
        hover_data=["type_catastrophe", "date_debut", "date_fin", "date_arrete"],
        labels={"famille": "Risk family", "type_catastrophe": "Hazard type", "date_debut": "Event start", "date_fin": "Event end", "date_arrete": "Declaration date"},
        title=f"Declaration history — {nom_commune}",
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="",
        showlegend=True,
        height=max(300, df_c["famille"].nunique() * 60 + 100),
        **_LAYOUT_BASE,
    )
    return fig


# ── 9. Barres famille par région ─────────────────────────────────────────────

def fig_barres_famille_region(df: pd.DataFrame) -> go.Figure:
    """
    Barres empilées : nombre d'arrêtés par région × famille.
    """
    agg = (
        df[~df["is_drom"]]
        .groupby(["libelle_region", "famille"])
        .size()
        .reset_index(name="nb_arretes")
    )
    agg["famille"] = agg["famille"].map(FAMILY_LABELS_EN).fillna(agg["famille"])
    fig = px.bar(
        agg,
        x="nb_arretes",
        y="libelle_region",
        color="famille",
        orientation="h",
        color_discrete_map=_PALETTE_CAT_EN,
        category_orders={"famille": [FAMILY_LABELS_EN[value] for value in FAMILLES_ORDER]},
        labels={"nb_arretes": "Declarations", "libelle_region": "Region", "famille": "Risk family"},
        barmode="stack",
    )
    fig.update_layout(
        xaxis_title="Number of declarations",
        yaxis_title="",
        height=520,
        **_LAYOUT_BASE,
    )
    return fig
