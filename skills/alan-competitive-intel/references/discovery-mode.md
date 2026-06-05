# Discovery Mode — Alan Competitive Intel

Guide pour le Mode B : trouver des produits e-commerce physiques rentables sans idée de départ.

---

## Objectif

Identifier 3-5 opportunités de produits e-com physiques avec :
- Marché prouvé (annonceurs actifs ≥30 jours)
- Potentiel de marge (>40% estimé)
- Potentiel créatif fort (contenu démonstratif ou transformationnel)
- Pas encore saturé (pas de leader inarrêtable)

---

## Sources de Découverte (par ordre de fiabilité)

### 1. TikTok Creative Center — Trending Products

URL : `https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en`

Filtres à appliquer :
- Région : France (ou région cible)
- Industrie : E-commerce → Consumer Goods, Beauty, Home, Health, Fashion
- Période : 7 derniers jours + 30 derniers jours

Ce qu'on cherche :
- Produits avec croissance de volume d'ads (signal d'adoption annonceurs)
- CTR moyen élevé (>1.5% si visible)
- Formats vidéo courts avec démonstration produit

Signal fort : un produit avec des ads de 10+ annonceurs différents actifs sur 21+ jours.

### 2. Meta Ads Library — Recherche par Catégorie

URL : `https://www.facebook.com/ads/library/`

Technique :
- Rechercher des termes génériques : "maison", "cuisine", "beauté", "sport", "douleur", "sommeil", "poils", "cheveux"
- Filtrer : Tous les annonceurs + Actifs + France
- Observer : nombre d'annonceurs visibles, présence d'ads longue durée

Signal fort : 5-15 annonceurs actifs avec des ads de 30+ jours sur la même catégorie produit = niche viable.
Signal faible : 0-2 annonceurs = marché inexistant ou non-adressé.
Signal danger : 20+ annonceurs Evergreen = saturation.

### 3. Amazon France — Best Sellers & Movers

URL Best Sellers : `https://www.amazon.fr/gp/bestsellers/`
URL Movers & Shakers : `https://www.amazon.fr/gp/movers-and-shakers/`

Catégories cibles :
- Beauté et Parfum → Soins du visage, Corps, Cheveux
- Sport et Plein Air → Fitness, Récupération, Accessoires
- Maison et Cuisine → Organisation, Nettoyage, Cuisine
- Santé → Bien-être, Sommeil, Posture
- Animalerie → Accessoires chien/chat

Signaux positifs :
- Produit dans le Top 100 Movers & Shakers (croissance forte récente)
- Nombre d'avis élevé (>500) avec note >4.2 = demande prouvée
- Plusieurs marques différentes sur le même produit = catégorie ouverte

### 4. Google Trends

URL : `https://trends.google.com/trends/explore?geo=FR&date=today%2012-m`

Chercher les termes des produits identifiés via TikTok/Amazon.

Signal positif :
- Tendance ascendante régulière sur 12 mois (pas un spike unique)
- Volume relatif ≥30/100 (pas marginal)
- Intérêt régional : régions françaises qui recherchent

Signal d'alerte :
- Pic unique suivi d'une chute brutale = tendance éphémère
- Tendance plate à <10/100 = marché minimal

### 5. Spy Tools Publics (sans login)

- Pipiads public : chercher des annonceurs TikTok par catégorie (données limitées sans compte)
- BigSpy public : même logique pour Meta
- PowerAdSpy démo public

Ces outils en mode public donnent des signaux limités mais utiles pour confirmer une catégorie active.

---

## Scoring des Opportunités

Pour chaque produit découvert, appliquer ce scoring :

| Critère | Points | Comment évaluer |
|---|---|---|
| ≥5 annonceurs actifs 30j+ | 20 | Meta Ads Library + TikTok |
| ≥1 Evergreen (180j+) mais <5 | 15 | Marché prouvé, pas saturé |
| Marge estimée >50% | 20 | (Prix vente public - Prix AliExpress) / Prix vente |
| Marge estimée 40-50% | 10 | Idem |
| Score Viral ≥60 | 20 | Voir performance-scoring.md |
| Score Viral 40-59 | 10 | Idem |
| Tendance Google ascendante | 15 | Tendance sur 12 mois |
| Top 100 Amazon Movers | 10 | Movers & Shakers |
| Marché FR non-saturé (<10 Hero+) | 10 | Abs de domination |
| **TOTAL MAX** | **110** | Minimum recommandé : 50 |

Seuil d'inclusion dans le rapport : **Score ≥50**.

---

## Estimation de Marge

Méthode publique sans API :

1. Trouver le prix de vente public du produit chez les annonceurs actifs (scraper leur landing page)
2. Chercher le produit équivalent sur AliExpress / DSers (recherche publique)
3. Calculer :
   ```
   Marge brute estimée = (Prix vente - Prix fournisseur estimé) / Prix vente × 100
   ```
4. Déduire les frais ads estimés (CPM France Meta = 8-12€, CPC = 0.40-0.80€ en moyenne)
5. Estimer le CPA viable :
   ```
   CPA max = Prix vente × Marge brute % × 0.5 (règle 50% du profit pour ads)
   ```

Exemple :
- Prix vente : 49€
- Prix AliExpress équivalent : 8€
- Marge brute : (49-8)/49 = 83%
- CPA max viable : 49 × 0.83 × 0.5 = 20.30€
- Avec CPM Meta 10€ et CTR 1% → CPC ~1€ → besoin de 1/20 = 5% de conversion sur landing

Si conversion landing estimée <2% → produit fragile. Si >3% → viable.

---

## Format de Sortie Mode Découverte

Avant de lancer l'analyse complète, présenter les 3-5 opportunités :

```
🔍 DÉCOUVERTE — 5 OPPORTUNITÉS IDENTIFIÉES

1. {PRODUCT_NAME}
   Niche : {NICHE} | Marché : {MARKET}
   Score : {SCORE}/100
   Signal : {X} annonceurs actifs, meilleur durée {Y}j
   Marge estimée : ~{Z}%
   Source : TikTok Creative Center + Meta Ads Library, accédé {DATE}

2. ...

Recommandation : analyser {TOP_PRODUCT} en priorité (score le plus élevé + marge la plus forte).
Voulez-vous lancer l'analyse complète sur ce produit ou un autre ?
```

Attendre confirmation avant de lancer l'analyse complète Mode A sur le produit sélectionné.
