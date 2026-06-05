# Research Prompts — Alan Competitive Intel

Utiliser ces prompts comme base de travail pour les recherches. Remplacer les placeholders par les données du projet. Output en français par défaut.

---

## Trouver les Concurrents

Recherche les 5-10 principaux concurrents de `{product_name}` sur le marché `{market}`.

Pour chaque concurrent potentiel, vérifier :
1. Vend-il le même produit ou un produit fonctionnellement équivalent ?
2. Est-il présent sur Meta Ads ou TikTok Ads (chercher sur les Ads Libraries publiques) ?
3. Son marché géographique principal est-il compatible avec `{market}` ?
4. A-t-il un site e-commerce actif avec des ventes réelles (pas juste une landing) ?

Sources à consulter dans l'ordre :
- Google : `"{product_name}" site:facebook.com/ads/library` + `"{product_name}" acheter OR buy OR shop`
- Meta Ads Library : chercher le nom du produit / catégorie
- TikTok Creative Center : chercher les top ads par catégorie
- Amazon : Best Sellers dans la catégorie correspondante
- Google Shopping : top annonceurs visibles

Retourner pour chaque concurrent :
- Nom de la marque / page
- URL du site
- URL de leur page Meta Ads Library (si trouvée)
- Produit exact vendu + fourchette de prix public
- Estimation de présence ads (actif / inactif / inconnu)

---

## Meta Ads Library

Analyser les publicités publiques de `{competitor_page}` dans Meta Ads Library.

URL : `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q={competitor_page}&search_type=page`

Pour chaque ad visible :
1. **Format** : Static / Video / Carousel / UGC / FaceCam / LeadForm
2. **Accroche (hook)** : premiers mots ou première image décrite
3. **Texte principal** : résumer en 1-2 phrases
4. **Titre / Headline**
5. **CTA** : Shop Now / En savoir plus / Acheter / etc.
6. **Date de début** : si visible
7. **Durée estimée** : calculer depuis la date de début jusqu'à aujourd'hui
8. **Plateformes** : Facebook / Instagram / Audience Network / Messenger
9. **URL de destination** : landing page ou product page
10. **Angle** : classifier selon `angle-framework.md`
11. **Winner status** : appliquer les Winner Rules de `angle-framework.md`

Si l'accès direct n'est pas possible (rate limit, JS requis) :
- Tenter avec Lightpanda (voir `lightpanda-guide.md`)
- Fallback : recherche Google `site:facebook.com/ads/library {competitor_page}` + screenshots utilisateur si disponibles
- Toujours indiquer le mode utilisé : `direct_library` / `lightpanda` / `search_fallback` / `user_provided`

Ne jamais inventer d'ads. Si aucune donnée accessible : noter "0 ads observés — accès restreint" et continuer.

---

## TikTok Creative Center

Analyser les tendances publicitaires pour `{product_category}` sur TikTok.

URL principale : `https://ads.tiktok.com/business/creativecenter/inspiration/topads/`

Chercher :
1. Top Ads par industrie (Beauty / Health / Home / Fashion / Electronics selon le produit)
2. Trending Products dans la catégorie correspondante
3. Ads de `{competitor_page}` si présents

Pour chaque ad TikTok analysé :
- Format : In-feed / TopView / Spark Ads / UGC
- Durée de la vidéo
- Hook des 3 premières secondes
- Type de créatif : founder-led / UGC / animation / démonstration produit
- CTA visible
- Durée d'activité estimée (si disponible)
- Industrie / Catégorie

Si Lightpanda disponible, scraper `scripts/scrape_tiktok.py`.
Sinon, utiliser WebFetch sur les URLs TikTok Creative Center public.

---

## Métriques Revenus et Trafic

Estimer les performances business de `{competitor_name}` avec des sources publiques uniquement.

### SimilarWeb (public)
URL : `https://www.similarweb.com/website/{competitor_domain}/`
Extraire si disponible :
- Trafic mensuel estimé
- Répartition des sources (direct / SEO / paid / social)
- Top pays
- Durée moyenne de visite
- Taux de rebond estimé
- Catégorie et classement

### LinkedIn
Chercher : `{competitor_name}` sur LinkedIn public
Extraire :
- Taille de l'équipe (fourchette LinkedIn)
- Croissance des effectifs (signe de santé)
- Ancienneté de l'entreprise
- Pays d'implantation

### Crunchbase Public
URL : `https://www.crunchbase.com/organization/{competitor_slug}`
Extraire si disponible :
- Levées de fonds (montant, date, investisseurs)
- Date de création
- Catégorie

### Presse et Signaux Publics
Google News : `"{competitor_name}" chiffre d'affaires OR revenue OR levée OR funding`
Chercher : interviews fondateur, communiqués de presse, articles Forbes/TechCrunch, etc.

### Scoring de confiance
- `[HIGH]` : donnée directe, source datée, univoque
- `[MEDIUM]` : triangulation 2+ sources ou estimation SimilarWeb avec trafic confirmé
- `[LOW]` : signal unique, estimation indirecte
- `[N/A]` : aucune donnée trouvée — toujours indiquer la source consultée

---

## Mode Découverte — Trouver des Produits Rentables

Rechercher des produits e-commerce physiques avec fort potentiel Meta/TikTok Ads en `{market}`.

### Sources à analyser en parallèle

**TikTok Creative Center — Trending Products**
URL : `https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/`
Filtrer par : pays `{market}`, industrie = Shopping / Consumer Goods
Identifier : produits avec >10 ads actifs, engagement fort, durée >21 jours

**Meta Ads Library — Catégories actives**
Rechercher des termes génériques par catégorie : "acné", "posture", "cheveux", "maison", "sport", "cuisine"
Identifier les niches avec 5-15 annonceurs actifs (pas saturées, pas vides)

**Amazon Best Sellers et Movers & Shakers**
URL : `https://www.amazon.fr/gp/bestsellers/` + `https://www.amazon.fr/gp/movers-and-shakers/`
Catégories cibles : Beauté, Sport, Maison, Cuisine, Animalerie, Santé

**Google Trends**
URL : `https://trends.google.com/trends/explore`
Chercher des tendances ascendantes sur 12 mois en France
Signal positif : croissance régulière, pas de spike unique (durable vs viral one-shot)

### Critères de sélection d'un produit

Retenir uniquement si :
- ≥3 annonceurs actifs avec ads ≥30 jours (marché prouvé)
- Marge brute estimée >40% (prix de vente public visible vs prix fournisseur public estimé AliExpress/DSers)
- Potentiel créatif fort : démonstration possible, transformation visible, problème universel
- Pas de barrière réglementaire évidente (médicaments, armes, alcool à exclure)
- Volume de recherche minimal existant (Google Trends signal présent)

Signal négatif (exclure) :
- >20 annonceurs Evergreen (180j+) → marché saturé
- 0 annonceurs actifs → marché inexistant ou trop niché
- Prix <15€ → marge insuffisante pour ads
- Produit saisonnier avec courbe en spike sans base

Retourner les 3-5 meilleures opportunités avec score et justification sourcée avant de lancer l'analyse complète.
