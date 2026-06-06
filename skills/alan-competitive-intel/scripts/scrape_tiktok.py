#!/usr/bin/env python3
"""
scrape_tiktok.py - Alan Competitive Intel
Metriques TikTok sans API key ni authentification.

Sources:
  1. TikTok Creative Center JSON endpoints publics (hashtags, topics, sons tendance)
     Endpoints /api/public/trend/{type}/v2/ : pas d auth requise.
  2. TikTok OEmbed API : metadonnees de videos publiques (totalement public).

Disponible sans auth:
  - Hashtags tendance (post count, views, trend direction)
  - Topics tendance par industrie
  - Sons tendance
  - Metadonnees de videos publiques (OEmbed: titre + auteur)

Non disponible sans compte TikTok Ads:
  - CTR et impressions des Top Ads
  - Details creatifs des ads concurrents
  - Budget estime des annonceurs
  => Afficher "Donnees indisponibles - compte TikTok Ads requis"

Usage:
  python3 scrape_tiktok.py --trending --country FR
  python3 scrape_tiktok.py --industry beauty --country FR --period 7
  python3 scrape_tiktok.py --video "https://www.tiktok.com/@brand/video/123"
  python3 scrape_tiktok.py --trending --country FR --output data.json
"""

import argparse
import gzip
import json
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Optional

# Headers navigateur standard - aucun token d auth
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en",
    "Origin": "https://ads.tiktok.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

_CC_BASE = "https://ads.tiktok.com/business/creativecenter/api/public"

INDUSTRY_IDS = {
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


def _get(url: str, params: dict = None) -> Optional[dict]:
    # HTTP GET avec headers navigateur, retourne JSON ou None
    if params:
        cleaned = {k: v for k, v in params.items() if v is not None}
        url += "?" + urllib.parse.urlencode(cleaned)

    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] HTTP GET failed ({url[:70]}): {e}", file=sys.stderr)
        return None


def _extract_list(data: dict) -> list:
    # Extrait la liste depuis differentes structures JSON TikTok
    if not isinstance(data, dict):
        return []
    return (
        (data.get("data") or {}).get("list")
        or (data.get("data") or {}).get("items")
        or data.get("list")
        or []
    )


def fetch_hashtag_trends(country: str = "FR", period: int = 7, limit: int = 20) -> dict:
    # Hashtags tendance via /api/public/trend/hashtag/v2/ (pas d auth requise)
    url = f"{_CC_BASE}/trend/hashtag/v2/"
    raw = _get(url, {"period": period, "region": country, "limit": limit, "page": 1})

    if raw is None:
        return _failed(
            "hashtag_trends", country, period, url,
            f"https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en?region={country}"
        )

    items = _extract_list(raw)
    hashtags = [
        {
            "hashtag": it.get("hashtag_name") or it.get("tag") or "",
            "post_count": it.get("post_num") or it.get("count") or 0,
            "view_count": it.get("video_views") or it.get("views") or 0,
            "trend_direction": it.get("trend") or "",
            "rank": it.get("rank") or 0,
        }
        for it in items[:limit]
    ]

    return {
        "type": "hashtag_trends",
        "country": country,
        "period_days": period,
        "hashtags": hashtags,
        "total": len(hashtags),
        "mode": "tiktok_cc_public_api",
        "source_url": url,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    }


def fetch_topic_trends(country: str = "FR", industry: str = "beauty", period: int = 7) -> dict:
    # Topics tendance par industrie via /api/public/trend/topic/list/v2/ (pas d auth requise)
    url = f"{_CC_BASE}/trend/topic/list/v2/"
    raw = _get(url, {
        "period": period,
        "region": country,
        "limit": 20,
        "page": 1,
        "industry": INDUSTRY_IDS.get(industry.lower()),
    })

    if raw is None:
        return _failed("topic_trends", country, period, url)

    items = _extract_list(raw)
    topics = [
        {
            "topic": it.get("topic_name") or it.get("name") or "",
            "industry": it.get("industry_name") or industry,
            "post_count": it.get("post_num") or 0,
            "view_count": it.get("video_views") or 0,
            "trend_direction": it.get("trend") or "",
        }
        for it in items[:20]
    ]

    return {
        "type": "topic_trends",
        "country": country,
        "industry": industry,
        "period_days": period,
        "topics": topics,
        "total": len(topics),
        "mode": "tiktok_cc_public_api",
        "source_url": url,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    }


def fetch_sound_trends(country: str = "FR", period: int = 7, limit: int = 15) -> dict:
    # Sons tendance via /api/public/trend/sound/v2/ (pas d auth requise)
    url = f"{_CC_BASE}/trend/sound/v2/"
    raw = _get(url, {"period": period, "region": country, "limit": limit, "page": 1})

    if raw is None:
        return _failed("sound_trends", country, period, url)

    items = _extract_list(raw)
    sounds = [
        {
            "title": it.get("title") or it.get("sound_name") or "",
            "artist": it.get("author_name") or it.get("artist") or "",
            "usage_count": it.get("usage_count") or it.get("video_count") or 0,
            "trend_direction": it.get("trend") or "",
            "rank": it.get("rank") or 0,
        }
        for it in items[:limit]
    ]

    return {
        "type": "sound_trends",
        "country": country,
        "period_days": period,
        "sounds": sounds,
        "total": len(sounds),
        "mode": "tiktok_cc_public_api",
        "source_url": url,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    }


def fetch_video_oembed(video_url: str) -> dict:
    # Metadonnees via OEmbed TikTok (public, aucune auth) - titre + auteur uniquement
    raw = _get("https://www.tiktok.com/oembed", {"url": video_url})

    if raw is None:
        return {
            "type": "video_oembed",
            "url": video_url,
            "mode": "oembed_failed",
            "note": "OEmbed inaccessible - verifier que l URL est une video TikTok publique valide.",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

    return {
        "type": "video_oembed",
        "url": video_url,
        "title": raw.get("title") or "",
        "author_name": raw.get("author_name") or "",
        "author_url": raw.get("author_url") or "",
        "thumbnail_url": raw.get("thumbnail_url") or "",
        "mode": "tiktok_oembed",
        "note": "OEmbed public: titre + auteur uniquement. Vues/likes non disponibles sans auth.",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    }


def _failed(data_type: str, country: str, period: int, url: str, fallback_url: str = None) -> dict:
    return {
        "type": data_type,
        "country": country,
        "period_days": period,
        "mode": "api_failed",
        "source_url": url,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "fallback_url": (
            fallback_url
            or "https://ads.tiktok.com/business/creativecenter/inspiration/popular-trends/pc/en"
        ),
        "note": (
            "API TikTok Creative Center inaccessible (rate limit ou region). "
            "Acceder manuellement a fallback_url et copier les donnees visibles."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Metriques TikTok sans API key - Creative Center public + OEmbed"
    )
    parser.add_argument("--industry", default="beauty", choices=list(INDUSTRY_IDS.keys()))
    parser.add_argument("--country", default="FR")
    parser.add_argument("--period", type=int, default=7, choices=[7, 30, 180])
    parser.add_argument("--trending", action="store_true",
                        help="Extraire hashtags + topics + sons tendance")
    parser.add_argument("--video", help="URL TikTok pour metadata OEmbed")
    parser.add_argument("--output", help="Fichier JSON de sortie")
    args = parser.parse_args()

    print(f"TikTok (no-key) - {args.industry} [{args.country}] {args.period}j")

    results = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "country": args.country,
        "industry": args.industry,
        "period_days": args.period,
        "data": {},
        "available_without_auth": [
            "hashtags_trending (post_count, view_count, trend_direction)",
            "topics_trending (par industrie, post_count, view_count)",
            "sounds_trending (usage_count, trend_direction)",
            "video_oembed (titre + auteur uniquement)",
        ],
        "unavailable_without_tiktok_ads_account": [
            "top_ads_ctr",
            "ad_impressions",
            "advertiser_budget",
            "ad_creative_details",
        ],
    }

    if args.video:
        results["data"]["video_oembed"] = fetch_video_oembed(args.video)

    if args.trending or not args.video:
        results["data"]["hashtag_trends"] = fetch_hashtag_trends(args.country, args.period)
        results["data"]["topic_trends"] = fetch_topic_trends(args.country, args.industry, args.period)
        results["data"]["sound_trends"] = fetch_sound_trends(args.country, args.period)

    output_str = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"  Sauvegarde: {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
