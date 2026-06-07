# alan-competitive-intel

Skill d'analyse concurrentielle e-commerce pour Alan — Meta Ads + TikTok, métriques sourcées, angles prouvés, rapport HTML.

**Principe absolu : aucun contenu sans métrique. Aucun angle sans preuve de 60+ jours actifs.**

---

## Plug & Play — Aucune configuration requise

| Source | Données | Auth requise |
|---|---|---|
| TikTok Creative Center | Hashtags, topics, sons tendance | ❌ Aucune |
| Google Trends | Courbe 12 mois, requêtes associées | ❌ Aucune |
| Meta Ads Library | Ads actives, durée, angles | ❌ Aucune |
| SimilarWeb public | Trafic estimé | ❌ Aucune |
| TikTok OEmbed | Métadonnées vidéos | ❌ Aucune |

---

## Ce que ce skill produit

- Identification automatique des concurrents d'un produit e-commerce physique
- Analyse Meta Ads Library : ads actives, durée, angles, patterns gagnants
- Analyse TikTok Creative Center : hashtags tendance, topics, sons (sans auth)
- Google Trends : courbe d'intérêt 12 mois + requêtes associées en hausse
- Métriques business sourcées : trafic estimé, CA estimé, taille équipe
- Rapport HTML esthétique et autonome (dark mode, graphiques Chart.js)
- Mode découverte : trouver un produit rentable sans idée de départ

## Ce qui est exclu

- Aucune API payante
- Aucune donnée derrière login
- Aucun angle recommandé sans 2+ concurrents Hero (60j+)
- Aucun revenu inventé — "N/A" si source insuffisante

---

## Installation

```bash
# 1. Copier le skill dans Claude Code
cp -R skills/alan-competitive-intel ~/.claude/plugins/alan-competitive-intel/

# 2. Installer les dépendances Python
cd ~/.claude/plugins/alan-competitive-intel
pip install -r requirements.txt

# 3. (Optionnel) Lightpanda pour un meilleur scraping Meta Ads Library
docker run -d --name lightpanda -p 127.0.0.1:9222:9222 lightpanda/browser:nightly
# ou: brew install lightpanda-io/browser/lightpanda && lightpanda serve --port 9222
```

Sans Lightpanda, le skill utilise automatiquement WebSearch en fallback pour Meta Ads.

---

## Utilisation

### Mode Analyse Produit

```
Utilise alan-competitive-intel pour analyser les concurrents de [nom du produit]
```

### Mode Découverte (pas d'idée de produit)

```
Utilise alan-competitive-intel pour trouver un produit e-commerce rentable à lancer
```

---

## Structure du skill

```
skills/alan-competitive-intel/
  SKILL.md                          ← Document principal du skill
  requirements.txt                  ← pip install -r requirements.txt
  references/
    research-prompts.md             ← Prompts de recherche structurés
    angle-framework.md              ← Classification des 8 angles e-com + Winner Rules
    performance-scoring.md          ← Méthodologie de scoring des concurrents
    html-report-guide.md            ← Spécifications du rapport HTML
    discovery-mode.md               ← Sources et scoring pour le mode découverte
    lightpanda-guide.md             ← Guide Lightpanda (optionnel)
  agents/
    openai.yaml                     ← Configuration agent
  scripts/
    generate_report.py              ← Génère le HTML depuis un JSON de données
    scrape_meta_ads.py              ← Scraping Meta Ads Library (Lightpanda/fallback)
    scrape_tiktok.py                ← TikTok Creative Center endpoints publics (no auth)
    scrape_google_trends.py         ← Google Trends via pytrends (no auth)
```

---

## Rapport HTML

Le rapport généré contient :

1. **Header** — produit, date, score de confiance global, 5 bullets exécutifs
2. **Signal Marché** — saturation, tendance, volume recherche
3. **Matrice Concurrents** — tableau trié par score avec métriques sourcées
4. **Heatmap Angles** — croisement Angle × Concurrent avec labels Winner/Hero/Evergreen
5. **TikTok Tendances** — hashtags + topics + sons tendance (données publiques)
6. **Google Trends** — courbe 12 mois Chart.js + requêtes associées en hausse
7. **White Spaces** — opportunités sous-exploitées
8. **Angles Recommandés** — UNIQUEMENT si ≥2 concurrents Hero (60j+) prouvés
9. **Sources & Méthodologie** — toutes les sources citées avec date d'accès

---

## Génération manuelle du rapport HTML

```bash
python3 skills/alan-competitive-intel/scripts/generate_report.py \
  --data mes-donnees.json \
  --output rapport-produit-2024-12-01.html
```

---

## Auteur

Skill créé par Alan — inspiré de la méthodologie [LeadFactory de Gauthier Thiry](https://www.leadfactory.my).
