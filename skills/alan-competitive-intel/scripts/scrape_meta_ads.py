#!/usr/bin/env python3
"""
scrape_meta_ads.py — Alan Competitive Intel
Scrape Meta Ads Library via Lightpanda (CDP) ou CLI.
Retourne les ads publics d'une page en JSON normalisé.

Usage:
  python3 scrape_meta_ads.py --page "NomDeLaPage" --country FR --max 30
  python3 scrape_meta_ads.py --page "NomDeLaPage" --cli  # mode CLI lightpanda
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

LIGHTPANDA_PORT = 9222
LIGHTPANDA_WS = f"ws://127.0.0.1:{LIGHTPANDA_PORT}"


def check_lightpanda_available() -> bool:
    try:
        result = subprocess.run(["lightpanda", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_lightpanda_server_running() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{LIGHTPANDA_PORT}/json/version", timeout=3)
        return True
    except Exception:
        return False


def build_library_url(page_name: str, country: str = "FR") -> str:
    import urllib.parse
    encoded = urllib.parse.quote(page_name)
    return (
        f"https://www.facebook.com/ads/library/"
        f"?active_status=active&ad_type=all&country={country}"
        f"&q={encoded}&search_type=page"
    )


def parse_ads_from_html(html_content: str, page_name: str) -> list:
    """
    Parse les ads depuis le HTML brut de Meta Ads Library.
    Note : Meta utilise des classes CSS aléatoires. Cette extraction est basée
    sur des heuristiques textuelles robustes aux changements de classes.
    """
    from html.parser import HTMLParser

    ads = []
    extraction_note = "html_parse_heuristic"

    # Recherche de patterns textuels dans le HTML
    # Meta Ads Library inclut des data- attributes et des textes clés
    import re

    # Chercher les blocs d'ads (pattern approximatif)
    # En production, adapter selon la structure actuelle de Meta Ads Library
    ad_blocks = re.findall(r'"adArchiveID":"(\d+)".*?"startDate":"(\d+)".*?"endDate":(\d+|null)', html_content, re.DOTALL)

    for block in ad_blocks[:30]:
        ad_id, start_ts, end_ts = block
        try:
            start_date = datetime.fromtimestamp(int(start_ts)).strftime("%Y-%m-%d")
            days_active = (datetime.now() - datetime.fromtimestamp(int(start_ts))).days
        except Exception:
            start_date = "unknown"
            days_active = 0

        winner_label = (
            "Evergreen" if days_active >= 180 else
            "Hero" if days_active >= 60 else
            "Winner" if days_active >= 22 else
            "Validation" if days_active >= 8 else
            "Test"
        )

        ads.append({
            "competitor": page_name,
            "ad_id": ad_id,
            "start_date": start_date,
            "days_active": days_active,
            "winner_label": winner_label,
            "winner": days_active >= 22,
            "format": "unknown",
            "angle": "",
            "hook": "",
            "primary_text": "",
            "headline": "",
            "cta": "",
            "landing_url": "",
            "source_mode": extraction_note,
            "notes": "Extraction heuristique — valider manuellement"
        })

    return ads


def scrape_via_cdp(page_name: str, country: str, max_ads: int) -> dict:
    """Scrape Meta Ads Library via Lightpanda CDP (Playwright)."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "playwright non installé — pip install playwright", "ads": [], "mode": "cdp_failed"}

    url = build_library_url(page_name, country)
    print(f"  Connexion CDP → {url}")

    ads = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(LIGHTPANDA_WS)
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(3)  # lazy loading

            html_content = page.content()
            ads = parse_ads_from_html(html_content, page_name)

            # Tenter d'extraire les textes visibles via DOM
            try:
                ad_texts = page.evaluate("""() => {
                    const results = [];
                    document.querySelectorAll('[data-testid="ad-archive-renderer"]').forEach(el => {
                        results.push({
                            text: el.innerText.substring(0, 500),
                            html: el.innerHTML.substring(0, 1000)
                        });
                    });
                    return results;
                }""")
                for i, ad_text in enumerate(ad_texts[:max_ads]):
                    if i < len(ads):
                        ads[i]["primary_text"] = ad_text.get("text", "")[:200]
                        ads[i]["source_mode"] = "lightpanda_cdp"
                    else:
                        ads.append({
                            "competitor": page_name,
                            "ad_id": f"dom_{i}",
                            "primary_text": ad_text.get("text", "")[:200],
                            "source_mode": "lightpanda_cdp",
                            "winner": False,
                            "winner_label": "Test",
                            "days_active": 0,
                            "notes": "Extraction DOM — date non disponible"
                        })
            except Exception as e:
                print(f"  DOM extraction failed: {e}")

            browser.close()

    except Exception as e:
        return {
            "error": str(e),
            "ads": [],
            "mode": "cdp_failed",
            "fallback_url": url
        }

    return {
        "page_name": page_name,
        "country": country,
        "ads": ads[:max_ads],
        "total_extracted": len(ads),
        "mode": "lightpanda_cdp",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "library_url": url
    }


def scrape_via_cli(page_name: str, country: str, max_ads: int) -> dict:
    """Scrape Meta Ads Library via Lightpanda CLI (dump HTML)."""
    url = build_library_url(page_name, country)
    print(f"  Lightpanda CLI fetch → {url}")

    try:
        result = subprocess.run(
            ["lightpanda", "fetch", "--dump", "html",
             "--wait-until", "networkidle", "--wait-ms", "4000", url],
            capture_output=True, text=True, timeout=45
        )
        if result.returncode != 0:
            raise RuntimeError(f"Exit {result.returncode}: {result.stderr[:200]}")

        html_content = result.stdout
        ads = parse_ads_from_html(html_content, page_name)
        for ad in ads:
            ad["source_mode"] = "lightpanda_cli"

    except Exception as e:
        return {
            "error": str(e),
            "ads": [],
            "mode": "cli_failed",
            "fallback_url": url
        }

    return {
        "page_name": page_name,
        "country": country,
        "ads": ads[:max_ads],
        "total_extracted": len(ads),
        "mode": "lightpanda_cli",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "library_url": url
    }


def scrape_websearch_fallback(page_name: str) -> dict:
    """
    Fallback si Lightpanda indisponible.
    Retourne des instructions pour extraction manuelle ou via WebSearch dans le skill.
    """
    url = build_library_url(page_name, "FR")
    return {
        "page_name": page_name,
        "ads": [],
        "mode": "websearch_fallback",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "library_url": url,
        "fallback_instructions": (
            f"Lightpanda non disponible. Pour extraire manuellement :\n"
            f"1. Ouvrir : {url}\n"
            f"2. Copier les textes des 10-20 premières ads visibles\n"
            f"3. Ou utiliser WebFetch/WebSearch dans le skill avec l'URL ci-dessus\n"
            f"Recherche alternative : site:facebook.com/ads/library \"{page_name}\""
        ),
        "note": "Mode fallback — aucune donnée extraite automatiquement"
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape Meta Ads Library via Lightpanda")
    parser.add_argument("--page", required=True, help="Nom de la page/marque à analyser")
    parser.add_argument("--country", default="FR", help="Code pays (défaut: FR)")
    parser.add_argument("--max", type=int, default=30, help="Nombre max d'ads (défaut: 30)")
    parser.add_argument("--cli", action="store_true", help="Forcer le mode CLI (pas CDP)")
    parser.add_argument("--output", help="Fichier JSON de sortie (optionnel)")
    args = parser.parse_args()

    print(f"Meta Ads Library — {args.page} [{args.country}]")

    if args.cli:
        if not check_lightpanda_available():
            print("  Lightpanda CLI introuvable — mode fallback", file=sys.stderr)
            result = scrape_websearch_fallback(args.page)
        else:
            result = scrape_via_cli(args.page, args.country, args.max)
    elif check_lightpanda_server_running():
        print("  Lightpanda CDP détecté sur port 9222")
        result = scrape_via_cdp(args.page, args.country, args.max)
    elif check_lightpanda_available():
        print("  Lightpanda CLI disponible — mode CLI")
        result = scrape_via_cli(args.page, args.country, args.max)
    else:
        print("  Lightpanda non disponible — mode fallback WebSearch")
        result = scrape_websearch_fallback(args.page)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"  Résultat sauvegardé : {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
