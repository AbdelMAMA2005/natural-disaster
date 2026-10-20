# Script Vidéo de Démo — CatNat France Dashboard
## Durée totale : ~3 min 00 s

---

## [00:00 – 00:15] HOOK — Accroche (15 s)

**À l'écran :** Page d'introduction, grand titre, 4 métriques KPI

**Script :**
> « Saviez-vous que 99 % des communes françaises ont été frappées par au moins une catastrophe naturelle reconnue depuis 1982 ? Cette application vous permet d'explorer 260 000 arrêtés CatNat — 43 ans d'histoire des risques — pour répondre à une question simple : où vit-on le plus à risque, et est-ce que ça s'aggrave ? »

---

## [00:15 – 00:30] CONTEXTE — Ce que mesure un arrêté (15 s)

**À l'écran :** Section Introduction — encadré de mise en garde

**Script :**
> « Attention : un arrêté CatNat n'est pas un événement physique. C'est une reconnaissance administrative qui ouvre le droit à indemnisation. En 1999, une seule série de tempêtes et d'inondations a généré près de 58 000 arrêtés en quelques semaines. Garder ça en tête, c'est essentiel pour ne pas sur-interpréter les courbes. »

---

## [00:30 – 01:00] PIÈGE DES PICS ET DU RETARD — Tendance globale (30 s)

**À l'écran :** Onglet Vue d'ensemble — courbe annuelle annotée, puis cocher "Masquer les grands épisodes"

**Script :**
> « Voici la tendance brute. Ce pic géant en 1999 — presque 58 000 arrêtés — correspond aux tempêtes Martin et Lothar. Il écrase toute lecture directe. [clic] En masquant ces grands épisodes, une tendance plus lisible apparaît : une hausse progressive depuis les années 2000, portée principalement par la sécheresse. Mais [pointer vers la zone grisée] cette zone grisée est cruciale : les années 2023 à 2025 sont sous-comptées — les arrêtés mettent en moyenne 6 mois à être publiés. Donc non, on ne peut pas conclure que "ça baisse depuis 2022". »

---

## [01:00 – 01:20] HEATMAP — Vue famille × année (20 s)

**À l'écran :** Heatmap, puis petits multiples

**Script :**
> « La heatmap révèle ce que la courbe cachait : les inondations dominent toutes les années, mais la sécheresse a littéralement explosé depuis 2000 — avec trois pics visibles en 2003, 2018 et 2022. Les petits multiples confirment des dynamiques très différentes selon les familles. »

---

## [01:20 – 02:05] CARTE ANIMÉE — Inégalités territoriales (45 s)

**À l'écran :** Onglet Analyses approfondies — carte animée, cliquer lecture, puis classement

**Script :**
> « Passons à la carte. [lancer l'animation] On voit l'intensification progressive sur certains départements du sud-ouest et du littoral atlantique. [arrêter sur 1999] Ce rouge en 1999, c'est la trace des tempêtes Lothar et Martin. [basculer sur % communes] En passant en mode normalisé — % de communes touchées — le classement change : certains petits départements atteignent 100 % de communes concernées. [passer au classement] La Gironde, la Haute-Garonne et le Pas-de-Calais arrivent en tête en valeur brute — mais c'est aussi les plus peuplés. La normalisation par nombre de communes est essentielle pour comparer équitablement. »

---

## [02:05 – 02:35] RECHERCHE PAR COMMUNE — Cas Nice (30 s)

**À l'écran :** Onglet Par commune — saisir "Nice", frise, métriques

**Script :**
> « L'onglet "Par commune" permet à n'importe quel citoyen de retrouver l'historique de sa commune. Prenons Nice. [taper Nice] 140 arrêtés depuis 1982, risque dominant : inondations, rang 1 dans les Alpes-Maritimes. La frise chronologique montre des clusters d'épisodes — notamment autour de 1994 et 2019-2020. En tant qu'acheteur immobilier ou élu municipal, cette "carte d'identité risque" donne une base de réflexion solide. »

---

## [02:35 – 03:00] QUALITÉ ET CONCLUSION (25 s)

**À l'écran :** Onglet Qualité → Onglet Conclusions

**Script :**
> « L'onglet Qualité documente toutes les limites : 31 000 lignes dupliquées conservées, 8 incohérences de dates, délai de reconnaissance qui s'allonge de décennie en décennie. On ne cache rien. [basculer Conclusions] En synthèse : les reconnaissances augmentent, portées par la sécheresse. Mais pour un élu, l'enjeu n'est pas de regarder les chiffres bruts — c'est d'identifier les communes à forte récurrence pour cibler la prévention. Et pour ça, les données sont là, gratuites, sur data.gouv.fr. »

---

## Notes de réalisation

- Enregistrer avec OBS Studio ou Loom (1080p, 30 fps)
- Démo en direct sur `localhost:8501` (app déjà lancée avant l'enregistrement)
- Cursor Spotlight activé pour guider le regard
- Pas de musique de fond (distraction)
- Sous-titres recommandés pour l'accessibilité
- Durée totale cible : 3 min (± 15 s)
