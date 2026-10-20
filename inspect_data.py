# -*- coding: utf-8 -*-
"""
ETAPE 1 - Script d'inspection des donnees
==========================================
Lance avec : python inspect_data.py
Telecharge (une seule fois) le CSV CatNat et un GeoJSON des departements,
puis affiche tous les faits dont on a besoin pour coder l'app.
"""

import sys
import io
# Force UTF-8 sur stdout pour eviter les erreurs cp1252 sous Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import hashlib
import json
import requests
import pandas as pd

# ── Repertoire de cache local ─────────────────────────────────────────────────
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(CACHE_DIR, exist_ok=True)

# ── Constantes ────────────────────────────────────────────────────────────────
CSV_URL  = "https://www.data.gouv.fr/api/1/datasets/r/b3d02000-5f25-4967-a210-a4051dd620a1"
CSV_SHA1 = "9776cdc55f506c648ab45a05ed184682870a689f"
CSV_PATH = os.path.join(CACHE_DIR, "catnat.csv")

# Deux candidats GeoJSON departements a tester
GEOJSON_CANDIDATES = [
    {
        "label": "dep-100m (tres simplifie, recommande pour Plotly)",
        "url":   "https://www.data.gouv.fr/api/1/datasets/r/90b9341a-e1f7-4d75-a73c-bbc010c7feeb",
        "path":  os.path.join(CACHE_DIR, "departements_100m.geojson"),
    },
    {
        "label": "dep-1000m (simplifie alternatif)",
        "url":   "https://www.data.gouv.fr/api/1/datasets/r/3096e365-0a65-4c5c-b43e-9fff91f6dbc8",
        "path":  os.path.join(CACHE_DIR, "departements_1000m.geojson"),
    },
]

# Noms des colonnes du CSV (pas d'en-tete dans le fichier)
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

SEP = "\n" + "="*72 + "\n"


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha1_of_file(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: str, label: str) -> bool:
    """Telecharge si absent. Retourne True si succes ou deja present."""
    if os.path.exists(dest):
        print(f"  [OK] Deja en cache : {os.path.basename(dest)}")
        return True
    print(f"  [DL] Telechargement de {label} ...")
    try:
        r = requests.get(url, stream=True, timeout=180)
        r.raise_for_status()
        size = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                size += len(chunk)
                print(f"\r    {size/1e6:.1f} Mo recus...", end="", flush=True)
        print(f"\r  [OK] {size/1e6:.1f} Mo telecharges -> {os.path.basename(dest)}")
        return True
    except Exception as e:
        print(f"  [ERR] Erreur reseau : {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 1. CSV CatNat
# ══════════════════════════════════════════════════════════════════════════════

print(SEP + "1. CSV CatNat" + SEP)

ok = download_file(CSV_URL, CSV_PATH, "CSV CatNat (~50 Mo)")

if ok:
    # Verification sha1
    print("\n  Calcul du sha1 ...")
    actual_sha1 = sha1_of_file(CSV_PATH)
    match = "[OK]" if actual_sha1 == CSV_SHA1 else "[MISMATCH]"
    print(f"  sha1 attendu  : {CSV_SHA1}")
    print(f"  sha1 calcule  : {actual_sha1}  ->  {match}")

    # Lecture
    print("\n  Lecture du CSV ...")
    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        header=None,
        names=CSV_COLS,
        dtype=str,
        encoding="utf-8",
    )

    print(f"\n  Forme : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    print(f"  Colonnes : {df.columns.tolist()}")

    print("\n-- Apercu des 3 premieres lignes --")
    print(df.head(3).to_string())

    print("\n-- Valeurs manquantes par colonne (NaN) --")
    miss = df.isnull().sum()
    miss_pct = (miss / len(df) * 100).round(1)
    missing_df = pd.DataFrame({"manquants": miss, "pct_%": miss_pct})
    has_missing = missing_df[missing_df["manquants"] > 0]
    if len(has_missing) > 0:
        print(has_missing.to_string())
    else:
        print("  -> Aucune valeur NaN (toutes colonnes lues en str).")

    print("\n-- Chaines vides ou whitespace par colonne --")
    found_empty = False
    for col in df.columns:
        empty = (df[col].str.strip() == "").sum()
        if empty > 0:
            print(f"  {col:30s}: {empty:>7,} vides ({empty/len(df)*100:.1f} %)")
            found_empty = True
    if not found_empty:
        print("  -> Aucune chaine vide detectee.")

    print("\n-- Valeurs uniques cles --")
    for col in ["departement", "region", "type_catastrophe"]:
        uniq = sorted(df[col].dropna().unique().tolist())
        print(f"\n  {col} ({len(uniq)} valeurs uniques) :")
        print(f"  {uniq}")

    print("\n-- Couverture temporelle --")
    for col in ["date_debut", "date_fin", "date_arrete"]:
        vals = df[col].dropna()
        print(f"  {col} : min={vals.min()} / max={vals.max()} / n={len(vals):,}")

    print("\n-- Types de catastrophe --")
    print(df["type_catastrophe"].value_counts().to_string())

    print("\n-- Doublons suspects --")
    key_cols = ["code_geographique", "type_catastrophe", "date_debut", "date_fin"]
    dup_count = df.duplicated(subset=key_cols, keep=False).sum()
    print(f"  Lignes partageant meme {key_cols} : {dup_count:,}")

    print("\n-- Incoherence date_arrete < date_fin --")
    df_tmp = df.copy()
    for c in ["date_fin", "date_arrete"]:
        df_tmp[c] = pd.to_datetime(df_tmp[c], errors="coerce")
    incoherent = (df_tmp["date_arrete"] < df_tmp["date_fin"]).sum()
    print(f"  date_arrete < date_fin : {incoherent:,} lignes")

    print("\n-- Horaire 02:00 dans les dates --")
    for col in ["date_debut", "date_fin", "date_arrete"]:
        n = df[col].str.contains("02:00", na=False).sum()
        if n > 0:
            print(f"  {col}: {n:,} occurrences de '02:00'")

    print("\n-- Top communes (nombre d'arrets) --")
    top_com = df["libelle_geographique"].value_counts().head(10)
    print(top_com.to_string())

    print("\n-- Nombre de communes distinctes --")
    print(f"  code_geographique unique : {df['code_geographique'].nunique():,}")
    print(f"  libelle_geographique unique : {df['libelle_geographique'].nunique():,}")

    print("\n-- Codes region (format) --")
    print(f"  Valeurs uniques region : {sorted(df['region'].dropna().unique().tolist())}")

else:
    print("  [ERR] CSV non disponible, inspection impossible.")


# ══════════════════════════════════════════════════════════════════════════════
# 2. GeoJSON des departements
# ══════════════════════════════════════════════════════════════════════════════

print(SEP + "2. GeoJSON des departements (Contours administratifs)" + SEP)

for candidate in GEOJSON_CANDIDATES:
    print(f"\n-- Candidat : {candidate['label']} --")
    ok_geo = download_file(candidate["url"], candidate["path"], candidate["label"])

    if ok_geo:
        # Verifier si c'est un vrai JSON ou un binaire (ZIP, shapefile...)
        try:
            with open(candidate["path"], "rb") as f:
                header = f.read(4)
            is_zip = header[:2] == b"PK"
            print(f"  En-tete binaire (hex) : {header.hex()} {'-> ZIP/binaire !' if is_zip else '-> probablement JSON'}")

            if is_zip:
                print("  [WARN] Ce fichier est un ZIP, pas un GeoJSON direct.")
                print("         Il faudra l'extraire ou trouver la bonne URL directe.")
                continue

            with open(candidate["path"], encoding="utf-8", errors="replace") as f:
                geo = json.load(f)

            ftype = geo.get("type", "?")
            features = geo.get("features", [])
            print(f"  type GeoJSON : {ftype}")
            print(f"  nombre de features : {len(features)}")

            if features:
                first_props = features[0].get("properties", {})
                print(f"  cles properties (1ere feature) : {list(first_props.keys())}")
                print(f"  exemple properties : {first_props}")

                # Chercher le champ code departement
                candidate_fields = ["code", "dep", "code_dep", "CODE_DEP",
                                    "num_dep", "INSEE_DEP", "code_insee",
                                    "code_departement", "DEP", "NUM_DEP"]
                for cf in candidate_fields:
                    vals = [f["properties"].get(cf) for f in features]
                    vals = [v for v in vals if v is not None]
                    if vals:
                        print(f"\n  [MATCH] Champ '{cf}' : {len(set(vals))} valeurs uniques")
                        print(f"  Echantillon (tries) : {sorted(set(vals))[:20]}")
                        corse = [v for v in vals if str(v) in ("2A", "2B", "20")]
                        drom  = [v for v in vals if str(v).startswith(("97",))]
                        print(f"  Corse presente ? {corse}")
                        print(f"  DROM presents ? {drom}")
                        break

                size_kb = os.path.getsize(candidate["path"]) / 1024
                print(f"\n  Taille fichier : {size_kb:.0f} Ko")

        except json.JSONDecodeError as e:
            print(f"  [ERR] Pas un GeoJSON valide : {e}")
        except Exception as e:
            print(f"  [ERR] Erreur lecture : {e}")
    else:
        print(f"  [ERR] Impossible de telecharger {candidate['label']}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Recapitulatif des incertitudes
# ══════════════════════════════════════════════════════════════════════════════

print(SEP + "3. Points incertains -- A verifier avant de coder" + SEP)
print("""
  [A] GEOJSON -- L'URL retourne-t-elle un GeoJSON ou un ZIP ?
      -> Voir le resultat 'En-tete binaire' ci-dessus.

  [B] GEOJSON -- Les DROM (971-976) et la Corse (2A/2B) sont-ils presents ?
      -> Voir la sortie 'Corse presente / DROM presents' ci-dessus.

  [C] GEOJSON -- Le code departement dans le GeoJSON correspond-il exactement
      aux valeurs de la colonne 'departement' du CSV ?
      -> Comparer les deux ensembles de codes manuellement.

  [D] CSV -- Les codes region sont-ils des codes INSEE (11, 24...) ou des
      libelles ? -> Voir 'Codes region (format)' ci-dessus.

  [E] CSV -- Changement de perimetre du regime : tempetes exclues apres 1989,
      grele/neige apres 2010 ? -> A verifier par histogramme dans prep.py.

  [F] Doublons -- Les lignes partageant (commune, type, date_debut, date_fin)
      sont-elles de vrais doublons ou des arretes distincts ?
      -> Politique retenue : conserver mais signaler.

  [G] Licence du GeoJSON : ODbL / Licence Ouverte ?
      -> Verifier sur https://www.data.gouv.fr/datasets/contours-administratifs
""")

print("Script termine.\n")
