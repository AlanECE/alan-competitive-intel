---
name: alan-competitive-intel
description: Analyse concurrentielle e-commerce pour Alan — Meta Ads + TikTok, métriques sourcées, angles prouvés, rapport HTML. Use when the user wants competitive intelligence on a physical e-commerce product, wants to find winning ad angles backed by performance data, wants to discover trending profitable products, or needs a sourced HTML report on competitor landscape before launching Meta/TikTok ads.
---

# Alan Competitive Intel

Skill d'analyse concurrentielle e-commerce avec une posture d'expert ROAS.

## Plug & Play — Aucune configuration requise

Installation en 2 commandes :

```bash
cp -R skills/alan-competitive-intel ~/.claude/plugins/alan-competitive-intel/
cd ~/.claude/plugins/alan-competitive-intel && pip install -r requirements.txt
```

Toutes les sources de données sont **publiques et gratuites** :

| Source | Données | Auth requise |
|---|---|---|
| TikTok Creative Center | Hashtags, topics, sons tendance | ❌ Aucune |
| Google Trends (pytrends) | Courbe 12 mois, requêtes associées | ❌ Aucune |
| Meta Ads Library | Ads actives, durée, angles | ❌ Aucune (Lightpanda optionnel) |
| SimilarWeb public | Trafic estimé, canaux | ❌ Aucune |
| TikTok OEmbed | Métadonnées vidéos | ❌ Aucune |
| Crunchbase / LinkedIn / Presse | Signaux business | ❌ Aucune |

**Principe absolu : aucun contenu sans métrique. Aucun angle sans preuve de 60+ jours actifs sur au moins 2 concurrents.**

Ce skill produit un rapport HTML autonome contenant :
- Matrice des concurrents avec métriques sourcées
- Analyse Meta Ads Library + TikTok Creative Center
- Carte des angles par performance (Hero/Evergreen uniquement)
- Signaux de revenus et trafic (sources publiques citées)
- White spaces exploitables
- Hooks recommandés UNIQUEMENT si pattern récurrent prouvé

---

## Non-négociables

- Ne jamais inventer de métriques. Si la donnée n'est pas disponible publiquement, afficher "Données indisponibles" avec la source consultée.
- Ne jamais recommander un angle sans preuve : 2+ concurrents avec ads actifs 60+ jours sur cet angle.
- Ne jamais copier les textes publicitaires de concurrents. Extraire les patterns, pas les verbatims.
- Toujours citer URL + date d'accès pour chaque donnée factuelle.
- Ne pas inventer de revenus, trafic, ou ROAS. Utiliser uniquement SimilarWeb public, Crunchbase, LinkedIn, presse, rapports publics.
- L'output est toujours un fichier HTML autonome (CSS inline + JS embarqué).

---

## Modes d'exécution

### Mode A — Analyse Produit (input fourni)

Déclenché quand l'utilisateur fournit un produit, une URL, ou une liste de produits.

Collecte les champs suivants avant de démarrer :
- `product_name` : nom ou URL du produit (obligatoire)
- `market` : niche + géographie (défaut : France)
- `competitors` : optionnel — si absent, le skill les trouve automatiquement via web search
- `price_range` : fourchette de prix public si connu

Si un champ critique manque, poser **une seule question groupée** et continuer avec des valeurs par défaut.

### Mode B — Découverte (aucun produit/niche)

Déclenché quand l'utilisateur n'a pas d'idée de produit ou de niche.

Rechercher automatiquement les produits e-commerce physiques rentables via :
- TikTok Creative Center → trending products e-commerce
- Meta Ads Library → niches avec >5 annonceurs actifs avec ads 30+ jours
- Google Trends → tendances ascendantes (12 derniers mois)
- Amazon Best Sellers + Movers & Shakers (publics)
- Signaux AliExpress / DSers trending (publics)

Critères de sélection pour retenir un produit :
- ≥3 annonceurs actifs avec ads ≥30 jours
- Marge brute estimée >40% (prix vente public vs prix fournisseur public estimé)
- Potentiel viral : contenu démonstratif, before/after, transformation visible
- Pas de marché saturé (>20 annonceurs Evergreen = rouge)

Présenter 3-5 opportunités classées avant de lancer l'analyse complète.

---

## Workflow d'exécution

### Étape 1 — Détection du mode et collecte des inputs

Identifier le mode (A ou B) à partir du message utilisateur. Si Mode A, vérifier les champs requis. Si Mode B, passer directement à la découverte.

### Étape 2 — Scraping et recherche (lancer en parallèle si subagents disponibles)

Lire `references/lightpanda-guide.md` pour choisir la méthode de scraping optimale.

**Tâche 2a — Identification des concurrents (Mode A)**

Lire `references/research-prompts.md` → Section "Trouver les concurrents".

Utiliser web search public pour trouver 5-10 concurrents directs. Critères :
- Vendent le même produit ou un produit équivalent
- Présents sur Meta Ads ou TikTok Ads
- Marché géographique compatible

**Tâche 2b — Meta Ads Library**

Lire `references/research-prompts.md` → Section "Meta Ads Library".

Pour chaque concurrent identifié :
1. Rechercher la page dans `https://www.facebook.com/ads/library/`
2. Extraire les ads publics visibles (max 30 par concurrent)
3. Pour chaque ad : format, texte d'accroche, CTA, date début, durée estimée, URL destination
4. Classer l'angle selon `references/angle-framework.md`
5. Appliquer les Winner Rules

**Tâche 2c — TikTok Creative Center**

Lire `references/research-prompts.md` → Section "TikTok Creative Center".

Lancer `scripts/scrape_tiktok.py --trending --country {country} --industry {industry}` si Python disponible.

Données accessibles sans auth : hashtags tendance, topics, sons (post_count, view_count, trend_direction).
Données non disponibles sans compte TikTok Ads : CTR des Top Ads, impressions, budget → afficher "Données indisponibles — compte TikTok Ads requis".

Interpréter les hashtags tendance comme proxy d'angles : hashtag en hausse = angle émergent à investiguer.
**Tâche 2d — Métriques revenus et trafic**

Lire `references/performance-scoring.md`.

Pour chaque concurrent :
- SimilarWeb public : trafic mensuel estimé, canaux d'acquisition
- LinkedIn : taille équipe, croissance (signaux de rentabilité)
- Crunchbase : levées de fonds, date création
- Presse publique : interviews, communiqués, CA si divulgué
- App Store / Play Store : reviews, classements si applicable

Marquer chaque donnée avec son niveau de confiance : `[HIGH]` `[MEDIUM]` `[LOW]`

**Tâche 2e — Signaux de viralité et tendances**

Lancer `scripts/scrape_google_trends.py --keyword {product_name} --country {country}` si Python disponible (pytrends requis).

Données disponibles sans auth :
- Courbe d'intérêt sur 12 mois (0-100, normalisé)
- Direction : hausse / stable / baisse
- Requêtes associées en hausse = angles émergents à investiguer

Croiser avec les hashtags TikTok (Tâche 2c) :
- Hashtag TikTok "increase" + Google Trends "hausse" → signal fort, angle prioritaire
- Google Trends "baisse" → signal précurseur de saturation ou fin de cycle

Compléments :
- Reddit / forums publics : verbatims utilisateurs, objections récurrentes
- Volume recherche Google Keyword Planner public si accessible

### Étape 3 — Analyse et scoring

Lire `references/angle-framework.md` et `references/performance-scoring.md`.

Pour chaque concurrent :
1. Calculer le Score Ads (voir performance-scoring.md)
2. Calculer le Score Revenue (estimé, sourcé)
3. Identifier l'angle dominant
4. Lister les ads Hero (60+ jours) et Evergreen (180+ jours)

Pour chaque angle :
1. Compter le nombre de concurrents avec ads Hero+ sur cet angle
2. Si ≥2 concurrents → angle "Prouvé"
3. Si ≥1 Evergreen (180j+) → angle "Dominant"
4. Si 0 Winner → angle "Non validé" (ne pas recommander)

### Étape 4 — Génération du rapport HTML

Lire `references/html-report-guide.md` pour le template et les règles visuelles.

Utiliser le script `scripts/generate_report.py` si Python est disponible, sinon générer le HTML directement.

Sauvegarder le fichier : `rapport-{product_slug}-{YYYY-MM-DD}.html`

Sur le Desktop de l'utilisateur par défaut, ou dans le dossier courant si le Desktop n'est pas accessible.

### Étape 5 — Réponse finale

Retourner :
- Chemin du fichier HTML généré
- Résumé en 5 bullets : concurrent dominant, angle prouvé n°1, meilleur white space, signal de revenu le plus fiable, recommandation d'action immédiate
- Mode d'extraction utilisé (Lightpanda / WebFetch / WebSearch)
- Limites identifiées (données manquantes, accès restreints)

---

## Règles de qualité strictes

**Concurrent "significatif"** : ≥5 ads actifs OU ≥1 ad Winner+ (22j+). En dessous : noter comme "annonceur test" et exclure de l'analyse principale.

**Angle "Prouvé"** : ≥2 concurrents significatifs avec ads Hero (60j+) sur cet angle.

**Hook recommandé** : uniquement pour un angle Prouvé, extrait des patterns observés sur les ads Hero/Evergreen. Jamais inventé. Toujours accompagné de la preuve : "Vu sur [concurrent] pendant [durée]".

**Revenu "estimable"** : uniquement si source publique datée disponible. Sinon → "Non estimable — source insuffisante."

**Confiance des données** :
- `[HIGH]` : source directe datée (SimilarWeb, press release, Crunchbase)
- `[MEDIUM]` : triangulation de 2+ sources indirectes
- `[LOW]` : signal unique non corroboré
- `[N/A]` : donnée absente — afficher explicitement

---

## Sources autorisées (no-key, public only)

- Meta Ads Library : `https://www.facebook.com/ads/library/`
- TikTok Creative Center : `https://ads.tiktok.com/business/creativecenter/`
- Google Trends : `https://trends.google.com/`
- SimilarWeb (données publiques non-auth) : `https://www.similarweb.com/`
- Crunchbase public : `https://www.crunchbase.com/`
- LinkedIn public profiles
- Amazon Best Sellers : `https://www.amazon.fr/gp/bestsellers/`
- Reddit / forums publics
- Presse publique (Google News)
- App Store / Play Store public listings

- TikTok Creative Center API publique (no-auth) : `https://ads.tiktok.com/business/creativecenter/api/public/trend/`
- TikTok OEmbed : `https://www.tiktok.com/oembed`

Sources interdites : données derrière login, APIs payantes, scraping avec bypass de rate limits.
