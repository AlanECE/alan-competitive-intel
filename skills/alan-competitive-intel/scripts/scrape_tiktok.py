#!/usr/bin/env python3
"""
scrape_tiktok.py — Alan Competitive Intel
Scrape TikTok Creative Center (Top Ads + Trending Products) via Lightpanda.
Retourne les données ads TikTok en JSON normalisé.

Usage:
  python3 scrape_tiktok.py --industry beauty --country FR --period 30
  python3 scrape_tiktok.py --brand "NomMarque" --country FR
  python3 scrape_tiktok.py --trending --country FR
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

TIKTOK_INDUSTRY_IDS = {
    "beauty": "27101",
    "home": "27201",
    "sports": "27301",
    "health": "27401",
    "fashion": "27501",
    "food": "27601",
    "pets": "27701",
    "electronics": "27801",
    "baby": "27901",
    "automotive": "28001",
}

TIKTOK_TOP_ADS_BASE = "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en"
TIKTOK_TRENDING_BASE = "https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en"


def check_lightpanda_server_running() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{LIGHTPANDA_PORT}/json/version", timeout=3)
        return True
    except Exception:
        return False


def check_lightpanda_available() -> bool:
    try:
        result = subprocess.run(["lightpanda", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def build_top_ads_url(industry_id: str, country: str, period: int) -> str:
    return f"{TIKTOK_TOP_ADS_BASE}?period={period}&industry={industry_id}&region={country}"


def parse_tiktok_ads(html_content: str, source_label: str) -> list:
    """
    Parse les données ads TikTok depuis le HTML.
    TikTok Creative Center charge les données via XHR/JSON embedded.
    """
    import re

    ads = []

    # Chercher les données JSON embarquées (TikTok injecte souvent __STORE__ ou window.__data__)
    json_patterns = [
        r'window\.__INITIAL_STATE__\s*=\s*({.+?});\s*</script>',
        r'"topAdsData"\s*:\s*(\[.+?\])',
        r'"adCreativeList"\s*:\s*(\[.+?\])',
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        for match in matches[:1]:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    for item in data[:20]:
                        ad = {
                            "platform": "tiktok",
                            "source_mode": source_label,
                            "brand": item.get("brandName", item.get("brand", "")),
                            "industry": item.get("industryName", ""),
                            "format": "Video",
                            "duration_seconds": item.get("videoDuration", item.get("duration", 0)),
                            "ctr": item.get("ctr", item.get("clickRate", None)),
                            "hook": item.get("videoTitle", item.get("adTitle", ""))[:200],
                            "like_count": item.get("likeCount", item.get("likes", 0)),
                            "comment_count": item.get("commentCount", item.get("comments", 0)),
                            "angle": "",
                            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                            "notes": "Extraction JSON embarqué"
                        }
                        ads.append(ad)
                    break
            except (json.JSONDecodeError, KeyError):
                continue

    return ads


def scrape_top_ads_cdp(industry: str, country: str, period: int) -> dict:
    """Scrape TikTok Creative Center Top Ads via CDP."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "playwright non installé", "ads": [], "mode": "cdp_failed"}

    industry_id = TIKTOK_INDUSTRY_IDS.get(industry.lower(), "27101")
    url = build_top_ads_url(industry_id, country, period)
    print(f"  TikTok Top Ads CDP → {url}")

    ads = []
    api_data = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(LIGHTPANDA_WS)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = context.new_page()

            # Intercepter les requêtes API TikTok
            def handle_response(response):
                if "creativeCenter" in response.url and response.status == 200:
                    try:
                        body = response.json()
                        if isinstance(body, dict) and body.get("data"):
                            api_data.append(body["data"])
                    except Exception:
                        pass

            page.on("response", handle_response)
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(4)

            # Essayer d'extraire depuis les réponses API interceptées
            if api_data:
                for data_block in api_data:
                    if isinstance(data_block, dict) and "list" in data_block:
                        for item in data_block["list"][:20]:
                            ads.append({
                                "platform": "tiktok",
                                "source_mode": "lightpanda_cdp_api_intercept",
                                "brand": item.get("advertiserName", ""),
                                "ad_id": item.get("adId", ""),
                                "format": "Video",
                                "hook": item.get("materialTitle", "")[:200],
                                "ctr": item.get("ctr", None),
                                "duration_seconds": item.get("videoDuration", 0),
                                "angle": "",
                                "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                                "notes": "Interception API XHR"
                            })

            # Fallback : parse le HTML si pas de données API
            if not ads:
                html_content = page.content()
                ads = parse_tiktok_ads(html_content, "lightpanda_cdp_html")

            browser.close()

    except Exception as e:
        return {"error": str(e), "ads": [], "mode": "cdp_failed"}

    return {
        "industry": industry,
        "country": country,
        "period_days": period,
        "ads": ads,
        "total_extracted": len(ads),
        "mode": "lightpanda_cdp",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "source_url": url
    }


def scrape_trending_cli(country: str) -> dict:
    """Scrape TikTok Trending Products via Lightpanda CLI."""
    url = f"{TIKTOK_TRENDING_BASE}?region={country}"
    print(f"  TikTok Trending CLI → {url}")

    try:
        result = subprocess.run(
            ["lightpanda", "fetch", "--dump", "markdown",
             "--wait-until", "networkidle", "--wait-ms", "5000", url],
            capture_output=True, text=True, timeout=45
        )
        if result.returncode != 0:
            raise RuntimeError(f"Exit {result.returncode}")

        content = result.stdout

        # Extraire les tendances du markdown
        import re
        trending = []
        lines = content.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["trending", "product", "shop", "top"]):
                if len(line.strip()) > 10:
                    trending.append({"raw_text": line.strip(), "source_mode": "lightpanda_cli_markdown"})

        return {
            "country": country,
            "trending_items": trending[:30],
            "raw_excerpt": content[:2000],
            "mode": "lightpanda_cli",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "source_url": url
        }

    except Exception as e:
        return {"error": str(e), "trending_items": [], "mode": "cli_failed"}


def build_websearch_fallback(industry: str, country: str, brand: Optional[str] = None) -> dict:
    """Fallback WebSearch si Lightpanda indisponible."""
    cc_url = TIKTOK_TOP_ADS_BASE
    if brand:
        cc_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?keyword={brand}"

    return {
        "industry": industry,
        "country": country,
        "ads": [],
        "mode": "websearch_fallback",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "fallback_instructions": (
            f"Lightpanda non disponible. Instructions extraction manuelle :\n"
            f"1. Ouvrir : {cc_url}\n"
            f"2. Filtrer par région {country} et industrie {industry}\n"
            f"3. Copier les données des 10-20 top ads visibles\n"
            f"Recherche alternative : site:ads.tiktok.com creativecenter {industry} {country}\n"
            f"Ou chercher : TikTok ads {industry} {country} 2024 top performing"
        ),
        "note": "Mode fallback — aucune donnée extraite automatiquement"
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape TikTok Creative Center via Lightpanda")
    parser.add_argument("--industry", default="beauty", choices=list(TIKTOK_INDUSTRY_IDS.keys()),
                        help="Industrie à analyser")
    parser.add_argument("--brand", help="Rechercher une marque spécifique")
    parser.add_argument("--country", default="FR", help="Code pays (défaut: FR)")
    parser.add_argument("--period", type=int, default=30, choices=[7, 30, 180],
                        help="Période en jours (7, 30, 180)")
    parser.add_argument("--trending", action="store_true", help="Mode Trending Products")
    parser.add_argument("--output", help="Fichier JSON de sortie (optionnel)")
    args = parser.parse_args()

    print(f"TikTok Creative Center — {args.industry} [{args.country}] {args.period}j")

    if args.trending:
        if check_lightpanda_available():
            result = scrape_trending_cli(args.country)
        else:
            result = build_websearch_fallback(args.industry, args.country)
    elif check_lightpanda_server_running():
        print("  Lightpanda CDP détecté sur port 9222")
        result = scrape_top_ads_cdp(args.industry, args.country, args.period)
    elif check_lightpanda_available():
        print("  Lightpanda CLI disponible")
        result = scrape_trending_cli(args.country)
    else:
        print("  Lightpanda non disponible — mode fallback")
        result = build_websearch_fallback(args.industry, args.country, args.brand)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"  Résultat sauvegardé : {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
