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
| **Apify TikTok Ads** (optionnel) | Impressions, reach, régions, ciblage, % créateurs — données réelles UE/DSA | ⚙️ Token Apify fourni au runtime |

> **Lightpanda reste la méthode privilégiée** pour les pages JS-lourdes (Meta Ads Library, SimilarWeb) : ~16× moins de RAM et ~9× plus rapide que Chrome headless. Voir `references/lightpanda-guide.md`. Aucune installation obligatoire — fallback WebFetch/WebSearch automatique.

### Option avancée — Métriques publicitaires TikTok RÉELLES (Apify, opt-in)

Le skill sait exploiter l'actor Apify **`silva95gustavo/tiktok-ads-scraper`** pour récupérer de vraies données de la [TikTok Commercial Content Library](https://library.tiktok.com/ads) (impressions, reach, régions, ciblage démographique, part créateurs/affiliés).

**Plug & play piloté par l'utilisateur :**
- Si l'utilisateur **mentionne ou fournit un token Apify** (dans son message, ou via `APIFY_TOKEN` dans l'environnement), le skill l'utilise automatiquement en lançant `scripts/scrape_tiktok_ads.py`.
- **Aucun token n'est jamais stocké dans ce repo.** Le token est lu au runtime depuis `APIFY_TOKEN` — fourni par l'utilisateur, jamais codé en dur, jamais commité (repo public).
- Sans token → le script se rabat proprement sur un mode `no_token` avec lien manuel. Le skill reste 100 % plug-and-play et gratuit par défaut.

⚠️ **Périmètre = UE/EEE (transparence DSA), pas USA** → lire les impressions comme un signal de stratégie créative, pas un volume US.
⚠️ **Ne pas appliquer les Winner Rules ici** : `firstShown`/`lastShown` sont des fenêtres de reporting DSA courtes, pas une durée de campagne. Les Winner Rules Hero/Evergreen sont réservées à la Meta Ads Library.

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

## Deux modes selon l'environnement (détection automatique)

Le skill fonctionne dans deux contextes et s'adapte **tout seul**. Détecter l'environnement au démarrage : un terminal / outil Bash est-il disponible ?

### Mode Terminal (complet) — dès que Bash/Docker/Python sont accessibles

C'est le mode préféré. Quand le terminal est disponible, l'utiliser et lancer les outils lourds :
- **Lightpanda via Docker** pour les pages JS-lourdes (Meta Ads Library, SimilarWeb, Amazon). Le démarrer dès que possible :
  `docker run -d --name lightpanda -p 127.0.0.1:9222:9222 lightpanda/browser:nightly`
- **Scripts Python** : `scrape_tiktok.py`, `scrape_google_trends.py`, et `scrape_tiktok_ads.py` (si un token Apify est fourni au runtime).
- **WebSearch** pour la recherche large.
- Récupération des liens/prix Amazon réels via Lightpanda (`fetch --dump html`).

### Mode Web App (restreint) — pas de terminal ni de Docker (ex. application web Claude)

Quand il n'y a ni terminal, ni Docker, ni scripts exécutables :
- **Pas de Lightpanda, pas de scripts Python.** Ne pas tenter de lancer Docker.
- Utiliser **WebFetch** pour charger directement les pages publiques : Meta Ads Library, TikTok Creative Center, Amazon (liens produits + prix), SimilarWeb, Google Trends, presse.
- Si WebSearch est disponible, l'utiliser ; sinon s'appuyer sur WebFetch + les URLs fournies par l'utilisateur.
- Si une page JS-lourde ne rend rien via WebFetch, demander à l'utilisateur de coller le contenu visible (mode `user_provided`).

| Besoin | Mode Terminal | Mode Web App |
|---|---|---|
| Pages JS-lourdes (Meta Ads, SimilarWeb) | Lightpanda (Docker) | WebFetch, sinon collage utilisateur |
| Liens / prix Amazon | Lightpanda `fetch` | WebFetch sur `amazon.com/s?k=...` |
| TikTok hashtags/sons | `scrape_tiktok.py` | WebFetch endpoints publics |
| Google Trends | `scrape_google_trends.py` | WebFetch `trends.google.com` |
| TikTok Ads réelles (si token Apify) | `scrape_tiktok_ads.py` | API Apify via WebFetch si possible, sinon ignorer |
| Recherche large | WebSearch | WebSearch si dispo, sinon WebFetch ciblé |

**Toujours indiquer le mode et la méthode d'extraction dans le rapport** (`mode_terminal` / `mode_webapp`, et `lightpanda` / `webfetch` / `user_provided`).

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

Déclenché quand l'utilisateur n'a pas d'idée de produit ou de niche. Dans ce cas, faire l'effort de **trouver la niche soi-même**, puis dérouler le format standard.

**Étape B1 — Top 3 niches.** Classer 3 niches par performance réelle (GMV / croissance, sources publiques : FastMoss, Accio, TikTok Shop stats). **Priorité absolue aux produits physiques** : ils se démontrent en vidéo (avant/après, unboxing, application), là où un logiciel ne se filme pas. Un produit de type logiciel / digital n'est retenu qu'en dernier recours (même si ses commissions sont plus élevées, 30-50 %). Présenter les 3 niches avec leur métrique sourcée et désigner la n°1.

**Étape B2 — Top 3 produits de la niche n°1.** Pour la niche gagnante, sortir le top 3 produits via :
- TikTok Creative Center / TikTok Shop best-sellers → produits tendance
- Meta Ads Library → niches avec >5 annonceurs actifs avec ads 30+ jours
- Google Trends → tendances ascendantes (12 derniers mois)
- Amazon Best Sellers + Movers & Shakers (publics)

Critères de sélection pour retenir un produit :
- ≥3 annonceurs actifs avec ads ≥30 jours (ou forte présence créateurs/affiliés)
- Marge / commission exploitable, prix accessible (forte conversion)
- Potentiel viral : contenu démonstratif, before/after, transformation visible
- Pas de marché saturé (>20 annonceurs Evergreen = rouge)

Chaque produit du top 3 suit le **format standard de fiche produit** (voir Étape 4 et `html-report-guide.md`) : hook, rémunération par plateforme (% × prix = gain), et deux prompts créatifs (photo + vidéo UGC).

---

## Workflow d'exécution

### Étape 1 — Détection du mode et collecte des inputs

Identifier le mode (A ou B) à partir du message utilisateur. Si Mode A, vérifier les champs requis. Si Mode B, passer directement à la découverte.

### Étape 2 — Scraping et recherche (lancer en parallèle si subagents disponibles)

D'abord, **détecter le mode** (voir « Deux modes selon l'environnement »). En Mode Terminal, lire `references/lightpanda-guide.md` : **Lightpanda (via Docker) est la méthode privilégiée et la plus efficace** pour les pages JS-lourdes (Meta Ads Library, SimilarWeb, Amazon), bien plus rapide et léger que Chrome headless. En Mode Web App, remplacer Lightpanda et les scripts par **WebFetch**. Si l'utilisateur a fourni un token Apify (Mode Terminal), ajouter la Tâche 2c-bis pour des métriques TikTok Ads réelles.

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

**Tâche 2c-bis — TikTok Ads Library RÉELLE (Apify, seulement si token fourni)**

Activer cette tâche **uniquement si l'utilisateur a fourni un token Apify** (mentionné dans son message ou présent dans `APIFY_TOKEN`).

Lancer `scripts/scrape_tiktok_ads.py --advertisers "{Concurrent1,Concurrent2,...}" --region all`.

Le script lit `APIFY_TOKEN` au runtime (jamais codé en dur) et retourne, par annonceur :
- `adCount`, `distinctAdvertisers` → intensité concurrentielle
- `creatorSharePct` → part d'annonces tenues par des créateurs/affiliés = **preuve de monétisation affiliée active**
- `imprSampleMid` + `topRegions` → reach réel (UE)
- `topAges`, `genders`, `avgAudience` → ciblage démographique réel

Interprétation :
- Part créateurs élevée (≥90 %) → produit déjà monétisé par des affiliés indépendants → modèle reproductible.
- 1 seul annonceur dominant → faible concurrence (white space) OU marché verrouillé par un acteur.
- ⚠️ Données UE/DSA — signal créatif, pas volume US. Ne pas appliquer Hero/Evergreen (voir lightpanda-guide.md).

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

**Format standard : tout rapport a la même structure, quelle que soit la niche.** Ordre imposé : (1) chiffres marché + verdict analyste, (2) Top 3 niches si pas de produit fourni, (3) glossaire, (4) Top 3 produits de la niche n°1, (5) comparatif, (6) données réelles, (7) sources.

**Design : viser simple, clair et beau, lisible par un novice.** Si le skill `impeccable` est installé (`.agents/skills/impeccable`), suivre ses règles (thème clair neutre, pas de bordure latérale colorée, pas de tiret cadratin dans le texte, contraste ≥ 4.5:1, une couleur par catégorie de produit). Règles **obligatoires** (détaillées dans `html-report-guide.md`) :
1. **Glossaire** : expliquer en français simple chaque acronyme utilisé (GMV, YoY, CAGR, DTC...).
2. **Analyse data-analyste** : pour chaque chiffre clé, donner un verdict « bon / à surveiller / mauvais » et pourquoi, en une phrase.
3. **Top 3 niches** (si aucun produit fourni) : niches classées par perf, priorité au physique (cf. Mode B).
4. **Fiche produit standard** pour chacun du Top 3, identique d'une niche à l'autre :
   - **Hook** : accroche des 3 premières secondes (en anglais si cible US, + traduction).
   - **Rémunération par plateforme** : un mini-tableau `Plateforme | Taux % | Gain par vente` où gain = taux × prix réel (ex. TikTok Shop 18 % × 13 $ = 2,34 $), plus une projection « à 100 ventes/mois ≈ X $ ». Toujours sourcer les taux.
   - **Lien TikTok** (hashtag) + **lien Amazon réel** (Lightpanda en Mode Terminal, WebFetch en Mode Web App).
   - **Deux prompts créatifs**, chacun via un **bouton « + »** ouvrant une **popup** (`<textarea>` éditable = modifier + bouton **Copier**). Implémentation : `<dialog>` natif réutilisable, objet JS `PROMPTS` (clé `{produit}-photo` / `{produit}-video`), bouton `.prompt-btn` avec `data-key`.
     - **Prompt photo** : image 9:16 hyper-détaillée (sujet, pose, prise en main du produit label-caméra, regard, lumière, optique), **sans texte ni graphisme**.
     - **Prompt vidéo UGC** : **un seul prompt pour un modèle vidéo IA de 15s max** (Veo 3 / Kling / Higgsfield), une scène continue, déroulé 0-4s / 4-9s / 9-15s avec le dialogue PARLÉ mot à mot, le **regard** (caméra vs produit vs peau) et la **façon de tenir le produit**. **Jamais de texte à l'écran** (`NEGATIVE: no on-screen text`), dialogue parlé OK. Tout détailler car le modèle est payant à la génération.
   - **Sourcer le choix du format** (avant/après pour résultat visible, démonstration + comparaison pour un dupe, GRWM/tutoriel, unboxing, hypermotion + jeux de lumière pour un objet tech) et le citer dans la popup. **Bonus Mode Terminal :** analyser de vraies pubs TikTok (Apify + `ffmpeg` sur `videos[].url`) pour en extraire des patterns réels et personnaliser les prompts. Détails dans `html-report-guide.md`.
5. **Comparatif** des produits (notes 1-5) puis le reste.

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

**Source optionnelle pilotée par token (fourni par l'utilisateur au runtime, jamais commité) :**
- Apify `silva95gustavo/tiktok-ads-scraper` → TikTok Commercial Content Library (`https://library.tiktok.com/ads`). Activée seulement si `APIFY_TOKEN` est fourni. Données UE/DSA réelles (impressions, reach, ciblage). Cette source est une API payante côté Apify mais reste conforme : la clé n'est jamais stockée dans le repo public — l'utilisateur fournit la sienne.

Sources interdites : données derrière login non autorisé, scraping avec bypass de rate limits, et **tout token/clé API codé en dur dans le repo** (le repo est public).
