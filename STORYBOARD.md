# Storyboard — CatNat France Dashboard
## EFREI Paris — Data Storytelling 2026 — Groupe DAI

> **Question centrale :** Quelles communes et quels territoires sont les plus exposés aux arrêtés de catastrophe naturelle — et est-ce que cela s'aggrave ?
> **Audience :** Citoyen et élu local

---

## Section 1 — Introduction (Hook & Contexte)

**Titre-insight :** *« 99 % des communes françaises ont été reconnues en catastrophe naturelle au moins une fois — mais certains territoires accumulent les épisodes »*

**Question à laquelle elle répond :** Pourquoi regarder ces données ? Qu'est-ce qu'un arrêté CatNat ?

**Visuel :** 4 métriques KPI (total arrêtés, communes distinctes, période, famille dominante)

**Filtres actifs :** Aucun (vue globale obligatoire pour le hook)

**KPI :** 260 601 arrêtés / 34 598 communes / 1982–2025 / Inondations

**Texte d'interprétation :**
La France compte parmi les pays d'Europe les plus touchés par les catastrophes naturelles reconnues. La base GASPAR recense chaque arrêté de reconnaissance — acte administratif qui ouvre le droit à indemnisation. Un arrêté ne correspond pas nécessairement à un événement physique distinct : un même épisode peut générer des milliers d'arrêtés simultanés.

**Avertissements narratifs :**
- Arrêté ≠ événement physique
- Périmètre du régime a évolué (tempêtes ~1989, grêle/neige ~2010)
- Années récentes sous-comptées (délai de reconnaissance croissant)
- Pas de données de population, de coûts ni de victimes

---

## Section 2 — Vue d'ensemble

**Titre-insight :** *« Les inondations dominent depuis 1982, mais la sécheresse progresse fortement — et les données récentes sont mécaniquement incomplètes »*

**Question :** Quelle est la tendance globale ? Quelle famille de risque progresse ?

**Visuels (dans l'ordre) :**
1. Courbe annuelle avec annotations (pics 1999, 2003, 2022) + zone grisée "données incomplètes"
2. Heatmap année × famille de risque
3. Petits multiples (6 sous-graphes, 1 par famille)
4. Barres empilées région × famille (métropole seulement)

**Filtres actifs :** Période, Région, Famille — tous actifs

**KPI header :** nb arrêtés / communes / risque dominant / département #1

**Texte d'interprétation :**
Le pic de 1999 (~57 000 arrêtés) correspond aux tempêtes Martin & Lothar et aux inondations massives. La sécheresse et le retrait-gonflement des argiles progressent nettement depuis 2000 (pics 2003, 2018, 2022). La zone grisée signale que les années 2023–2025 sont mécaniquement sous-comptées en raison du délai de reconnaissance.

---

## Section 3 — Analyses approfondies

**Titre-insight :** *« La carte révèle des inégalités territoriales marquées — certains départements cumulent tous les risques »*

**Question :** Où sont les territoires les plus exposés ? Comment le risque évolue-t-il dans le temps et dans l'espace ?

**Sous-sections :**

### A. Carte animée (curseur 1982–2025)
- Visuel : Choroplèthe animée des départements (métropole + Corse)
- Toggle : valeur brute / % communes touchées
- Note : DROM absents de la carte

### B. Classement top/bottom N
- Visuel : Barres horizontales
- Onglets : brut / normalisé

### C. Délai de reconnaissance par décennie
- Visuel : Boîtes à moustaches
- Message : délai médian 0 j → 185+ j → sous-comptage récent

### D. Saisonnalité
- Visuel : Barres groupées mois × famille (facet_col=famille)
- Message : inondations en automne, sécheresse en été

**Filtres actifs :** Tous

---

## Section 4 — Par commune

**Titre-insight :** *« Chaque commune a son histoire — retrouvez la vôtre »*

**Question :** Quel est le risque historique de ma commune ?

**Visuel :**
1. Recherche full-text (nom ou code INSEE)
2. Frise chronologique (timeline Plotly)
3. Barres par famille
4. Comparaison vs médiane du département

**Filtres actifs :** Aucun (recherche sur dataset complet)

**KPI :** nb arrêtés, famille dominante, rang dans le département, 1ère reconnaissance

---

## Section 5 — Qualité des données

**Titre-insight :** *« Des données solides sur le fond, mais 8 limites importantes à connaître »*

**Question :** Peut-on faire confiance à ces données ? Quelles précautions prendre ?

**Contenu :**
- Tableau valeurs manquantes
- Doublons suspects (31 537 lignes)
- Incohérences date_arrete < date_fin (8 cas)
- Délai de reconnaissance par décennie
- Pics 1999 et 1982–83
- Changements de périmètre du régime
- Absence de contexte (population, coûts)

---

## Section 6 — Conclusions & Implications

**Titre-insight :** *« Les reconnaissances augmentent — agir maintenant, c'est protéger demain »*

**Question :** Que retenir ? Que faire ?

**Contenu :**
1. 4 insights principaux (inondations, sécheresse, délai, récurrence)
2. Implications par public (élu, citoyen, décideur)
3. Mises en garde (pas de causalité climatique directe)
4. Pistes d'extension (population INSEE, données météo, CCR)
5. Tableau sources & licences

---

## Arbre de filtres (sidebar)

| Contrôle | Type | Impact |
|----------|------|--------|
| Période (années) | Slider double | Toutes les sections |
| Région(s) | Multi-select | Toutes sauf Intro et Qualité |
| Famille de risque | Multi-select | Toutes sauf Intro et Qualité |
| Inclure DROM | Checkbox | Tous graphiques non-cartographiques |
