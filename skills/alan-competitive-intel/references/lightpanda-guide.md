# Lightpanda Guide — Alan Competitive Intel

Guide d'utilisation de Lightpanda pour le scraping de pages JS-heavy (Meta Ads Library, TikTok Creative Center, SimilarWeb).

---

## Qu'est-ce que Lightpanda

Navigateur headless haute performance (Rust/Zig), compatible Chrome DevTools Protocol (CDP). ~16× moins de RAM que Chrome headless, ~9× plus rapide. Supporte JavaScript, DOM, AJAX, cookies, proxy.

Repo officiel : `https://github.com/lightpanda-io/browser`

---

## Détection de la Disponibilité

Avant d'utiliser Lightpanda, vérifier sa disponibilité :

```bash
lightpanda --version 2>/dev/null && echo "AVAILABLE" || echo "NOT_FOUND"
```

Si non disponible : utiliser le fallback WebFetch + WebSearch (voir section Fallback).

---

## Installation

### Option A — Docker (recommandé, no install)
```bash
docker run -d --name lightpanda -p 127.0.0.1:9222:9222 lightpanda/browser:nightly
```

Vérifier : `curl -s http://127.0.0.1:9222/json/version | python3 -m json.tool`

### Option B — Homebrew (macOS)
```bash
brew install lightpanda-io/browser/lightpanda
lightpanda serve --host 127.0.0.1 --port 9222
```

### Option C — Binaire direct (Linux/macOS)
Télécharger depuis `https://github.com/lightpanda-io/browser/releases/tag/nightly`
```bash
chmod +x lightpanda
./lightpanda serve --host 127.0.0.1 --port 9222
```

---

## Usage CLI (sans serveur)

### Dump HTML d'une page
```bash
lightpanda fetch --dump html https://www.facebook.com/ads/library/?q=exemple --wait-until networkidle --wait-ms 3000
```

### Dump Markdown
```bash
lightpanda fetch --dump markdown https://trends.google.com/trends/explore?q=produit&geo=FR
```

Flags utiles :
- `--wait-until networkidle` : attendre que le réseau soit calme (pages JS-heavy)
- `--wait-ms 2000` : attendre N millisecondes supplémentaires
- `--wait-selector ".adLibraryGrid"` : attendre qu'un sélecteur CSS soit présent
- `--obey-robots` : respecter robots.txt

---

## Usage CDP avec Python (via Playwright)

```python
from playwright.sync_api import sync_playwright

def scrape_with_lightpanda(url: str, wait_selector: str = None) -> str:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("ws://127.0.0.1:9222")
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=15000)
        content = page.content()
        browser.close()
        return content
```

Prérequis : `pip install playwright`

---

## Stratégie de Scraping par Source

### Meta Ads Library

URL de base :
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=FR&q={PAGE_NAME}&search_type=page
```

Sélecteurs CSS à observer (peuvent changer) :
- Container d'ads : `div[data-testid="ad-archive-renderer"]` ou classes dynamiques
- Texte d'accroche : premier paragraphe dans le container
- Date : span contenant "Début le" ou "Started running"
- CTA : bouton ou lien avec classe de CTA

**Important** : Meta génère des classes CSS aléatoires. Préférer la recherche par attributs `data-testid` ou le contenu textuel plutôt que par classes CSS.

Fallback si accès bloqué :
1. Essayer avec `--wait-ms 5000` (lazy loading)
2. Chercher `site:facebook.com/ads/library {PAGE_NAME}` sur Google
3. Utiliser les URLs partagées par l'utilisateur
4. Mode `screenshot_or_paste_fallback` : demander à l'utilisateur de copier le texte visible

### TikTok Creative Center

URL Top Ads :
```
https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?period=7&industry={INDUSTRY_ID}
```

Industries principales :
- Beauty & Personal Care : `27101`
- Home & Garden : `27201`  
- Sports & Outdoor : `27301`
- Health & Wellness : `27401`
- Fashion & Clothing : `27501`

Sélecteurs : chercher les cards `.creative-card` ou équivalent.

### SimilarWeb

URL :
```
https://www.similarweb.com/website/{DOMAIN}/
```

Sélecteurs des métriques publiques :
- Trafic total : `.engagement-list__item--total-visits .engagement-list__item-value`
- Trafic organique / payant dans le breakdown
- Top countries dans la section géographique

**Note** : SimilarWeb affiche des données limitées sans compte. Les estimations sont approximatives pour les sites <1M visites/mois.

---

## Fallback sans Lightpanda

Si Lightpanda n'est pas disponible, utiliser dans cet ordre :

1. **WebFetch direct** : tenter de charger la page (fonctionne pour certaines pages non-JS)
2. **WebSearch ciblé** : `site:facebook.com/ads/library {PAGE_NAME}` pour Meta, `site:ads.tiktok.com {BRAND}` pour TikTok
3. **WebSearch général** : `"{BRAND}" Meta Ads actives 2024` ou `"{BRAND}" TikTok publicité`
4. **Extraction manuelle assistée** : demander à l'utilisateur de copier/coller le contenu visible depuis son navigateur

Toujours indiquer le mode d'extraction dans le rapport :
- `lightpanda_cdp` : Lightpanda connecté via CDP
- `lightpanda_cli` : Lightpanda en mode CLI fetch
- `webfetch_direct` : WebFetch sans JS
- `websearch_fallback` : recherche Google comme proxy
- `user_provided` : données fournies par l'utilisateur

---

## Limites et Éthique

- Respecter `robots.txt` avec le flag `--obey-robots`
- Ne pas surcharger les serveurs : pause de 2-3 secondes entre les requêtes (voir scripts Python)
- Ne pas bypasser les protections anti-scraping intentionnelles (login requis = données privées)
- Ne pas distribuer les médias téléchargés (images, vidéos d'ads)
- Données utilisées uniquement pour analyse concurrentielle privée

---

## Dépannage

**Lightpanda ne démarre pas (Docker)**
```bash
docker ps # vérifier si le container tourne
docker logs lightpanda # voir les erreurs
docker restart lightpanda
```

**Timeout sur pages lentes**
Augmenter `--wait-ms` à 8000-10000 pour Meta Ads Library qui charge lentement.

**Page vide (JS non exécuté)**
Utiliser `--wait-until networkidle` plutôt que `load`. Si toujours vide, la page requiert une interaction (scroll, click) → passer en mode CDP Python.

**Rate limit Meta**
Espacer les requêtes : 5-10 secondes entre chaque page. Si bloqué : passer en mode `websearch_fallback` et le noter dans le rapport.
---

## TikTok Creative Center — Endpoints Publics (sans auth, sans Lightpanda)

Certains endpoints du Creative Center retournent du JSON **sans authentification**.
Ces endpoints sont appeles par le frontend quand on charge la page Popular Trends.
Aucun cookie de session ni token TikTok Ads requis.

### Endpoints publics confirmes

```
GET https://ads.tiktok.com/business/creativecenter/api/public/trend/hashtag/v2/
  ?period=7&region=FR&limit=20&page=1

GET https://ads.tiktok.com/business/creativecenter/api/public/trend/topic/list/v2/
  ?period=7&region=FR&limit=20&page=1&industry=27101

GET https://ads.tiktok.com/business/creativecenter/api/public/trend/sound/v2/
  ?period=7&region=FR&limit=15&page=1
```

Headers requis pour imiter un navigateur :

```python
{
    "User-Agent": "Mozilla/5.0 ... Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en",
    "Origin": "https://ads.tiktok.com",
    "Sec-Fetch-Mode": "cors",
}
```

### OEmbed TikTok (totalement public)

```
GET https://www.tiktok.com/oembed?url={video_url}
```

Retourne : titre, auteur, thumbnail. Aucune auth requise.
Limite : pas de vues, likes, commentaires.

### Ce qui reste derriere login

- **Top Ads CTR / impressions** : `/creative_radar_api/v1/top_ads/v2/list` — requiert cookies TikTok Ads
- **Keyword insights detailles** : requiert connexion compte Creative Center

Utiliser `scripts/scrape_tiktok.py` pour tous les appels publics (Lightpanda non necessaire pour TikTok).
Lightpanda reste **la methode privilegiee et la plus efficace** pour Meta Ads Library et SimilarWeb (pages JS-lourdes) : ~16x moins de RAM et ~9x plus rapide que Chrome headless. A utiliser en premier des qu'il est disponible.

---

## Option avancee — TikTok Ads Library reelle via Apify (opt-in, token utilisateur)

Pour obtenir de **vraies metriques publicitaires TikTok** (impressions, reach, regions, ciblage, part createurs/affilies), le skill peut utiliser l'actor Apify `silva95gustavo/tiktok-ads-scraper` sur la TikTok Commercial Content Library (`https://library.tiktok.com/ads`).

### Activation plug-and-play (pilotee par l'utilisateur)

- Active **uniquement** si l'utilisateur fournit un token Apify (mentionne dans son message, ou via `APIFY_TOKEN` dans l'environnement).
- **Aucun token n'est stocke dans le repo.** Le script `scripts/scrape_tiktok_ads.py` lit `APIFY_TOKEN` au runtime. Repo public => jamais de cle en dur.
- Sans token : mode `no_token` (fallback propre avec lien manuel). Le skill reste gratuit et plug-and-play par defaut.

### Appel

```bash
export APIFY_TOKEN="apify_api_..."   # fourni par l'utilisateur au runtime
python3 scripts/scrape_tiktok_ads.py --advertisers "CeraVe,The Ordinary,NuFACE" --region all --limit 25
```

### Comment ca marche (recherche par nom d'annonceur)

L'actor navigue des URLs de la library. La recherche fiable se fait **par nom d'annonceur** (substring, fuzzy) :

```
https://library.tiktok.com/ads?region=all&start_time={ms}&end_time={ms}&query_type=1&sort_type=create_time,desc&adv_name={MARQUE}
```

- `query_type=1` + `adv_name` = recherche par annonceur. La recherche par mot-cle de contenu (`query=skincare`) ne retourne rien.
- Appel HTTP direct (sans CLI) : `POST https://api.apify.com/v2/acts/silva95gustavo~tiktok-ads-scraper/run-sync-get-dataset-items?token=...` avec `{startUrls, proxyConfiguration, skipDetails:false, shouldDownloadVideos:false, resultsLimit}`.

### Champs reels retournes (par annonce)

`firstShown`, `lastShown`, `impressions{lowerBound,upperBound}`, `reach`, `regionStats[]`, `targeting{audienceSize,ageRanges,genders,interests}`, `advertiserName`, `videos[]`.

### Deux mises en garde critiques

1. ⚠️ **Perimetre = UE/EEE (transparence DSA), pas USA.** Les impressions sont europeennes. A lire comme signal de strategie creative, pas comme volume US.
2. ⚠️ **Longevite != Winner Rules.** `firstShown`/`lastShown` sont des fenetres de reporting DSA courtes (quelques jours), PAS la duree de campagne. Ne JAMAIS appliquer Hero/Evergreen ici — ces regles sont concues pour la Meta Ads Library. Ici, exploiter : intensite publicitaire, reach, regions, demographie, et **part createurs/affilies** (preuve de monetisation affiliee).

### Astuce qualite

La recherche par nom est fuzzy : filtrer les faux-positifs (ex. "CeraVe" peut matcher "ceramiche..."). Verifier `advertiserName` et privilegier les comptes business (INC/LTD/EUROPE/OFFICIAL) ou les marques officielles. Une part elevee de handles minuscules = createurs/affilies (signal recherche).
