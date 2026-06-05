# HTML Report Guide — Alan Competitive Intel

Spécifications pour générer le rapport HTML autonome. CSS inline, JS embarqué, aucune dépendance externe sauf Chart.js CDN.

---

## Principes visuels

**Palette :**
- Fond principal : `#0a0a0f` (quasi-noir)
- Fond cards : `#12121a`
- Fond section : `#1a1a2e`
- Texte principal : `#e8e8f0`
- Texte secondaire : `#8888a8`
- Accent Meta : `#1877F2` (bleu officiel)
- Accent TikTok : `#ff0050` (rose/rouge officiel)
- Vert succès / white space : `#00c896`
- Orange warning / saturé : `#ff8c42`
- Rouge danger / non-validé : `#ff4757`
- Jaune neutre : `#ffd32a`
- Bordures : `#2a2a3e`

**Typographie :**
- Font stack : `'Inter', 'Segoe UI', system-ui, sans-serif`
- Titres sections : 20px bold, uppercase tracking
- Données métriques : 28-36px bold, accent color
- Labels : 11px uppercase, letter-spacing 0.1em, secondary color

**Layout :**
- Max-width : 1200px, centré
- Padding container : 24px mobile, 40px desktop
- Cards avec border-radius 12px
- Séparateurs subtils avec gradient

---

## Structure du HTML

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analyse Concurrentielle — {PRODUCT_NAME}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>/* CSS COMPLET INLINE */</style>
</head>
<body>

  <!-- 1. HEADER -->
  <!-- 2. SIGNAL MARCHÉ -->
  <!-- 3. MATRICE CONCURRENTS -->
  <!-- 4. ANALYSE META ADS -->
  <!-- 5. ANALYSE TIKTOK ADS -->
  <!-- 6. CARTE DES ANGLES -->
  <!-- 7. MÉTRIQUES REVENUS -->
  <!-- 8. WHITE SPACES -->
  <!-- 9. ANGLES RECOMMANDÉS (conditionnel) -->
  <!-- 10. SOURCES & MÉTHODOLOGIE -->

  <script>/* JS Charts INLINE */</script>
</body>
</html>
```

---

## Section 1 — Header

```html
<header>
  <div class="header-meta">
    <span class="badge">Analyse Concurrentielle</span>
    <span class="date">Généré le {DATE}</span>
    <span class="confidence-badge confidence-{GLOBAL_CONFIDENCE}">{GLOBAL_CONFIDENCE} Confiance</span>
  </div>
  <h1>{PRODUCT_NAME}</h1>
  <p class="subtitle">{MARKET} · {NB_COMPETITORS} concurrents analysés · {NB_ADS} ads observées</p>
  
  <div class="summary-bullets">
    <div class="bullet">🎯 <strong>Concurrent dominant :</strong> {TOP_COMPETITOR} (Score {SCORE})</div>
    <div class="bullet">📈 <strong>Angle n°1 prouvé :</strong> {TOP_ANGLE} ({NB_HERO_ADS} ads Hero+ chez {NB_COMPETITORS_USING} concurrents)</div>
    <div class="bullet">💡 <strong>Meilleur white space :</strong> {WHITE_SPACE}</div>
    <div class="bullet">💰 <strong>Signal revenu le plus fiable :</strong> {REVENUE_SIGNAL}</div>
    <div class="bullet">⚡ <strong>Action recommandée :</strong> {ACTION}</div>
  </div>
</header>
```

---

## Section 2 — Signal Marché

Cards métriques clés + graphique Google Trends (si données disponibles).

Contenu :
- Volume de recherche estimé `[CONFIDENCE]`
- Tendance 12 mois (icône ↗️ ↔️ ↘️)
- Niveau de saturation (Émergent / Actif / Mature / Saturé)
- Plateformes les plus actives

Si données de tendance disponibles : graphique Line Chart Chart.js montrant l'évolution.

Si données insuffisantes : afficher un card "Signal marché — données indisponibles" avec les sources consultées.

---

## Section 3 — Matrice Concurrents

Tableau complet avec badge de scoring visuel.

Colonnes :
| # | Marque | Score Global | Ads Actives | Winner+ | Hero+ | Angle Dominant | Trafic/mois | CA Estimé | Confiance |

Chaque ligne :
- Logo/favicon si disponible (sinon initiales dans un cercle coloré)
- Score affiché comme barre de progression colorée
- Badges Winner/Hero/Evergreen en couleur
- Badge confiance revenue

Trier par Score Global décroissant.

Ligne de pied de tableau : "X concurrents significatifs (Score Ads ≥16) — Y annonceurs tests exclus"

---

## Section 4 — Analyse Meta Ads Library

Deux colonnes :

**Colonne gauche :** Distribution des angles (Donut Chart ou Bar Chart horizontal)
- Axe Y : 8 angles
- Valeur : nombre d'ads Hero+ par angle
- Colorer les barres : vert si Prouvé (≥2 concurrents Hero+), orange si Winner uniquement, rouge si Test/Validation seulement

**Colonne droite :** Top 5 ads Hero+ observées
Pour chaque ad :
- Card avec : Concurrent, Angle badge, Durée active (ex: "214 jours"), Format, Hook résumé, URL si disponible

Section pied : "Mode d'extraction : {MODE} — Accédé le {DATE}"

---

## Section 5 — Analyse TikTok Ads

Même structure que Section 4 mais couleurs TikTok (rose/rouge).

**Colonne gauche :** Distribution formats TikTok (Donut Chart) : UGC / Founder / Demo / Animation / Trend

**Colonne droite :** Observations principales :
- Durée vidéo dominante
- Hook pattern récurrent
- CTA le plus utilisé
- Format dominant

Si aucune donnée TikTok trouvée : section "TikTok — Données insuffisantes" avec raison.

---

## Section 6 — Carte des Angles (Heatmap)

Tableau croisé : Angles × Concurrents.

Chaque cellule affiche le label Winner/Hero/Evergreen du meilleur ad du concurrent pour cet angle.

Code couleur cellule :
- Fond vert foncé + "Evergreen" : 180j+
- Fond vert + "Hero" : 60-179j
- Fond bleu + "Winner" : 22-59j
- Fond gris + "Validation" : 8-21j
- Vide/gris très foncé : aucun ad sur cet angle

Ligne de synthèse en bas :
- Angle Prouvé ✅ (≥2 Hero+)
- Angle Saturé ⚠️ (≥5 Winner+)
- White Space 💡 (Prouvé mais <3 concurrents)
- Non validé ✖️

---

## Section 7 — Métriques Revenus et Trafic

Cards par concurrent avec badge de confiance visible.

Pour chaque concurrent significatif :
```
[CONCURRENT CARD]
CA Estimé : X€-Y€/an [CONFIDENCE]
Source : SimilarWeb, accédé YYYY-MM-DD
---
Trafic : Xk visites/mois [CONFIDENCE]
Équipe : X-Y employés [LinkedIn]
Ancienneté : X ans
Levées : X€ (si disponible)
```

Si `[N/A]` : afficher la card avec "Données indisponibles" en rouge/gris et lister les 3 sources consultées avec résultat vide.

Jamais de cellule vide sans explication.

---

## Section 8 — White Spaces

Cards des opportunités identifiées.

Chaque white space :
```
[WHITE SPACE CARD — fond vert sombre]
Angle : {ANGLE}
Sous-utilisé : {X}/{TOTAL_COMPETITORS} concurrents utilisent cet angle
Performance référence : {BEST_COMPETITOR} — {DURATION}j actif
Opportunité : {DESCRIPTION 2-3 phrases}
Recommandation créative : {1 phrase concrète}
```

Si aucun white space identifié : "Marché mature — angles principaux occupés par les leaders. Différenciation par sous-angle ou mécanisme nécessaire."

---

## Section 9 — Angles Recommandés (CONDITIONNEL)

**⚠️ Cette section n'apparaît QUE si ≥1 angle est Prouvé (≥2 concurrents Hero+).**

Si la condition n'est pas remplie : afficher un banner :
```
[BANNER ORANGE]
Données insuffisantes pour des recommandations d'angles.
Aucun angle n'a atteint le seuil de validation (2+ concurrents Hero 60j+).
Recommandation : commencer par tester les angles Transformation et Problème avec 3-5 créas chacun.
```

Si la condition est remplie, pour chaque angle Prouvé :

```
[ANGLE CARD — fond accent]
Angle : {ANGLE} ✅ PROUVÉ
Preuve : {X} concurrents avec ads Hero+ — durée moyenne {Y} jours
Référence : {COMPETITOR_NAME} — actif depuis {DATE} — {URL_PUBLIC si disponible}

Pattern Hook observé :
• "{HOOK_PATTERN_1}" (vu chez {COMPETITOR_A})
• "{HOOK_PATTERN_2}" (vu chez {COMPETITOR_B})

Format dominant : {FORMAT} | Plateforme principale : {PLATFORM}
CTA récurrent : {CTA}

⚠️ Ne pas copier. Ces patterns sont une inspiration structurelle — créer un message original.
```

---

## Section 10 — Sources & Méthodologie

Liste complète de toutes les sources utilisées.

```
[META ADS LIBRARY]
• facebook.com/ads/library — {COMPETITOR_1} — accédé {DATE} — Mode: {MODE}
• ...

[TIKTOK CREATIVE CENTER]
• ads.tiktok.com/business/creativecenter/ — accédé {DATE} — Mode: {MODE}
• ...

[MÉTRIQUES BUSINESS]
• similarweb.com/{domain} — accédé {DATE} — Trafic: {VALUE}
• crunchbase.com/{slug} — accédé {DATE}
• linkedin.com/company/{slug} — accédé {DATE}
• ...

[TENDANCES MARCHÉ]
• trends.google.com — {KEYWORD} — période {RANGE} — accédé {DATE}
• ...

[LIMITES DE L'ANALYSE]
• {Limitation 1}
• {Limitation 2}

[MÉTHODOLOGIE]
Extraction : {MODE UTILISÉ}
Scoring : voir references/performance-scoring.md
Angles : voir references/angle-framework.md
```

---

## Règles de génération

1. **Jamais de section vide** : si données manquantes → card explicative avec sources consultées.
2. **Jamais de métrique sans source** : chaque chiffre a une citation `[Source, Date]`.
3. **Jamais de recommandation sans preuve** : un angle sans 2+ Hero = pas de recommandation.
4. **Le fichier doit s'ouvrir offline** : CSS inline, aucune font Google externe, Chart.js via CDN uniquement (acceptable).
5. **Nom du fichier** : `rapport-{product-slug}-{YYYY-MM-DD}.html`
6. **Responsive** : lisible sur mobile (breakpoint 768px).
