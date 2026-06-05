# Performance Scoring — Alan Competitive Intel

Méthodologie pour scorer et comparer les concurrents avec des données sourcées.

---

## Score Ads (0–100)

Mesure l'agressivité et la performance publicitaire d'un concurrent.

### Calcul

```
Score Ads = (Nb ads actifs × 2) + (Nb Winner+ × 5) + (Nb Hero+ × 10) + (Nb Evergreen × 20)
Plafonné à 100.
```

Interprétation :
- 0-15 : annonceur test — exclure de l'analyse principale
- 16-35 : annonceur actif — à surveiller
- 36-60 : annonceur fort — analyse détaillée requise
- 61-80 : annonceur dominant — concurrent clé
- 81-100 : market leader — référence absolue

### Données requises
- Nombre d'ads actifs actuellement visibles dans Meta Ads Library
- Nombre d'ads avec durée 22j+ (Winner)
- Nombre d'ads avec durée 60j+ (Hero)
- Nombre d'ads avec durée 180j+ (Evergreen)

Si la date est masquée pour certains ads : compter uniquement les ads avec date visible et noter le nombre d'ads à date masquée séparément.

---

## Score Revenue (estimé, sourcé)

Estimation de la taille business du concurrent. Toujours accompagné de la source et du niveau de confiance.

### Méthode de triangulation

**Niveau 1 — Source directe [HIGH]**
- Chiffre d'affaires publié dans la presse, rapport annuel, interview fondateur
- Levée de fonds avec valorisation divulguée (Crunchbase)
- Données SEC / registre du commerce publiques

Formule : utiliser la donnée directe.

**Niveau 2 — Estimation SimilarWeb [MEDIUM]**
Si trafic SimilarWeb disponible (sites >100k visites/mois uniquement) :

```
CA estimé = Trafic mensuel × Taux conversion e-com moyen (2-3%) × Panier moyen public
```

Fourchette conservatrice : utiliser 1.5% de conversion et le prix le plus bas du catalogue.

Exemple : 200 000 visites/mois × 1.5% × 49€ = ~147 000€/mois (~1.76M€/an)
Toujours donner une fourchette (bas-haut) et indiquer `[MEDIUM]`.

**Niveau 3 — Triangulation indirecte [LOW]**
Si SimilarWeb non disponible ou site <50k visites :
- Taille équipe LinkedIn × revenus moyens par employé dans l'industrie
- Nombre d'avis × panier moyen × taux d'achat d'avis estimé

Formule taille équipe (e-com DTC) :
```
CA estimé = Nb employés × 150 000€ (revenus moyens/employé DTC)
```
Marge d'erreur élevée — indiquer `[LOW]`.

**Niveau 0 — Aucune donnée [N/A]**
Si aucune source n'est disponible : marquer `[N/A]` et lister les sources consultées.
Ne jamais inventer ou extrapoler sans base factuelle.

---

## Score Agressivité Ads (0–10)

Mesure la fréquence de lancement de nouvelles créas — indicateur de budget et d'optimisation active.

```
Score Agressivité = (Nb nouvelles créas lancées sur 30 derniers jours) / 3
Plafonné à 10.
```

Proxy si date non disponible : regarder la diversité des formats et angles. Un concurrent avec 10+ formats différents actifs = score ≥6.

Interprétation :
- 0-2 : annonceur passif (budget faible ou en pause)
- 3-5 : actif en optimisation
- 6-8 : fort spend + testing continu
- 9-10 : hyper-aggressif — concurrent principal à surveiller de près

---

## Score Global Concurrent (0–100)

```
Score Global = (Score Ads × 0.5) + (Score Revenue normalisé × 0.35) + (Score Agressivité × 10 × 0.15)
```

Score Revenue normalisé :
- <100k€/an → 10
- 100k-500k€/an → 25
- 500k€-2M€/an → 50
- 2M€-10M€/an → 75
- >10M€/an → 100

---

## Signaux de Viralité Produit

Indicateurs que le produit a un potentiel organique fort sur TikTok/Reels (réduit le coût ads).

**Signaux positifs :**
- Produit démonstratif : le fonctionnement se voit en video (score +20)
- Transformation visible et rapide : before/after clair (score +20)
- "Wow factor" : réaction émotionnelle immédiate (score +15)
- Problème universel et connu de l'audience cible (score +15)
- Prix impulse (<80€) : achat décision rapide (score +10)
- UGC naturel déjà existant : chercher sur TikTok/Instagram sans hashtag de marque (score +20)

**Signaux négatifs :**
- Produit technique nécessitant explication longue (-15)
- Produit non-visuel (ex: supplément en gélules sans effet visible rapide) (-10)
- Prix >200€ → cycle d'achat long (-20)
- Marché très régulé (santé, médicaments) → contraintes créatives (-15)

Score viral maximal : 100. Seuil recommandé pour TikTok : ≥50.

---

## Tableau de Synthèse Concurrent

Format de données à collecter pour chaque concurrent avant de générer le HTML :

```json
{
  "name": "Nom Marque",
  "domain": "site.com",
  "meta_page": "URL ou null",
  "tiktok_handle": "@handle ou null",
  "price_range": "39-79€",
  "meta_ads": {
    "total_active": 12,
    "winner_plus": 5,
    "hero_plus": 3,
    "evergreen": 1,
    "dominant_angle": "Transformation",
    "score_ads": 78,
    "score_agressivite": 6,
    "extraction_mode": "direct_library"
  },
  "tiktok_ads": {
    "total_observed": 4,
    "dominant_format": "UGC",
    "dominant_angle": "Preuve Sociale",
    "extraction_mode": "creative_center"
  },
  "revenue": {
    "estimate": "1.2M-2.4M€/an",
    "confidence": "MEDIUM",
    "source": "SimilarWeb 2024-12, 180k visites/mois",
    "method": "trafic_x_conversion"
  },
  "traffic_monthly": {
    "value": 180000,
    "confidence": "MEDIUM",
    "source": "SimilarWeb, accédé 2024-12-01"
  },
  "team_size": {
    "value": "11-50",
    "source": "LinkedIn, 2024-12-01"
  },
  "score_global": 72,
  "score_viral": 65,
  "notes": "Leader de la niche. Evergreen sur angle Transformation depuis 8 mois."
}
```
