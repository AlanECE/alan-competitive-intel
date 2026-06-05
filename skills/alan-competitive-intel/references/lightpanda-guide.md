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
