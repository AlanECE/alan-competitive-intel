#!/usr/bin/env python3
"""
scrape_google_trends.py - Alan Competitive Intel
Courbes de tendance Google pour corréler avec la viralité TikTok et l'intérêt marché.

Aucune API key, aucun compte requis.
Nécessite: pip install pytrends

Usage:
  python3 scrape_google_trends.py --keyword "mascara" --country FR
  python3 scrape_google_trends.py --keyword "mascara" --compare "rouge a levres,fond de teint" --country FR
  python3 scrape_google_trends.py --trending --country FR
  python3 scrape_google_trends.py --keyword "mascara" --country FR --output trends.json
"""

import argparse
import json
import sys
from datetime import datetime

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

# Mapping pays -> nom pytrends pour trending_searches
COUNTRY_MAP = {
    "FR": "france",
    "US": "united_states",
    "GB": "united_kingdom",
    "DE": "germany",
    "ES": "spain",
    "IT": "italy",
    "BE": "belgium",
    "CA": "canada",
}


def _build_pt(country: str) -> "TrendReq":
    lang = "fr" if country in ("FR", "BE") else "en"
    return TrendReq(hl=f"{lang}-{country}", tz=60, timeout=(10, 30), retries=2, backoff_factor=0.5)


def fetch_trend_curve(keyword: str, country: str = "FR", timeframe: str = "today 12-m") -> dict:
    """
    Courbe de tendance sur 12 mois pour un mot-clé.
    Valeurs normalisées 0-100 (intérêt relatif, pas volume absolu).
    Aucune auth requise.
    """
    if not PYTRENDS_AVAILABLE:
        return _no_pytrends(keyword)

    try:
        pt = _build_pt(country)
        pt.build_payload([keyword], cat=0, timeframe=timeframe, geo=country)
        df = pt.interest_over_time()

        if df.empty:
            return {
                "keyword": keyword,
                "country": country,
                "trend_curve": [],
                "mode": "pytrends_empty",
                "note": "Aucune donnée — mot-clé inconnu ou trop peu de recherches dans ce pays.",
                "fallback_url": f"https://trends.google.com/trends/explore?q={keyword}&geo={country}",
            }

        curve = [
            {"date": str(idx.date()), "interest": int(row[keyword])}
            for idx, row in df.iterrows()
            if not row.get("isPartial", False)
        ]

        interests = [p["interest"] for p in curve]
        recent_avg = sum(p["interest"] for p in curve[-4:]) / max(len(curve[-4:]), 1)
        earlier_avg = sum(p["interest"] for p in curve[:4]) / max(len(curve[:4]), 1)

        if earlier_avg == 0:
            direction, direction_label = "stable", "Stable"
        elif recent_avg > earlier_avg * 1.2:
            direction, direction_label = "up", "En hausse"
        elif recent_avg < earlier_avg * 0.8:
            direction, direction_label = "down", "En baisse"
        else:
            direction, direction_label = "stable", "Stable"

        return {
            "keyword": keyword,
            "country": country,
            "timeframe": timeframe,
            "trend_curve": curve,
            "peak_interest": max(interests, default=0),
            "current_interest": curve[-1]["interest"] if curve else 0,
            "avg_interest": round(sum(interests) / len(interests), 1) if interests else 0,
            "direction": direction,
            "direction_label": direction_label,
            "mode": "pytrends",
            "source_url": f"https://trends.google.com/trends/explore?q={keyword}&geo={country}",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

    except Exception as e:
        return {
            "keyword": keyword,
            "mode": "pytrends_error",
            "error": str(e),
            "fallback_url": f"https://trends.google.com/trends/explore?q={keyword}&geo={country}",
        }


def fetch_related_queries(keyword: str, country: str = "FR") -> dict:
    """
    Requêtes associées en hausse (rising) = angles émergents sous-exploités.
    Aucune auth requise.
    """
    if not PYTRENDS_AVAILABLE:
        return _no_pytrends(keyword)

    try:
        pt = _build_pt(country)
        pt.build_payload([keyword], cat=0, timeframe="today 12-m", geo=country)
        related = pt.related_queries()

        rising, top = [], []

        if keyword in related:
            rising_df = related[keyword].get("rising")
            top_df = related[keyword].get("top")

            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.head(10).iterrows():
                    val = row["value"]
                    rising.append({
                        "query": str(row["query"]),
                        "value": str(val),
                    })

            if top_df is not None and not top_df.empty:
                for _, row in top_df.head(10).iterrows():
                    top.append({
                        "query": str(row["query"]),
                        "value": int(row["value"]) if isinstance(row["value"], (int, float)) else str(row["value"]),
                    })

        return {
            "keyword": keyword,
            "country": country,
            "rising_queries": rising,
            "top_queries": top,
            "mode": "pytrends",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

    except Exception as e:
        return {"keyword": keyword, "mode": "pytrends_error", "error": str(e)}


def compare_keywords(keywords: list, country: str = "FR") -> dict:
    """
    Comparaison relative d'intérêt entre mots-clés (concurrents ou angles).
    Max 5 mots-clés simultanément.
    Aucune auth requise.
    """
    if not PYTRENDS_AVAILABLE:
        return _no_pytrends(str(keywords))

    keywords = [k for k in keywords if k][:5]

    try:
        pt = _build_pt(country)
        pt.build_payload(keywords, cat=0, timeframe="today 12-m", geo=country)
        df = pt.interest_over_time()

        if df.empty:
            return {"keywords": keywords, "mode": "pytrends_empty", "comparison": []}

        comparison = {}
        for kw in keywords:
            if kw in df.columns:
                vals = [int(v) for v in df[kw] if v >= 0]
                comparison[kw] = {
                    "avg_interest": round(sum(vals) / len(vals), 1) if vals else 0,
                    "peak_interest": max(vals, default=0),
                    "current_interest": int(df[kw].iloc[-1]) if not df.empty else 0,
                }

        ranked = sorted(comparison.items(), key=lambda x: x[1]["avg_interest"], reverse=True)

        return {
            "keywords": keywords,
            "country": country,
            "comparison": [{"keyword": k, **v} for k, v in ranked],
            "mode": "pytrends",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

    except Exception as e:
        return {"keywords": keywords, "mode": "pytrends_error", "error": str(e)}


def fetch_trending_searches(country: str = "FR") -> dict:
    """
    Tendances du jour dans le pays donné.
    Signal de viralité immédiate.
    Aucune auth requise.
    """
    if not PYTRENDS_AVAILABLE:
        return _no_pytrends(country)

    pn = COUNTRY_MAP.get(country.upper(), country.lower())

    try:
        pt = _build_pt(country)
        df = pt.trending_searches(pn=pn)
        trends = [str(t) for t in df[0].tolist()[:20]] if not df.empty else []

        return {
            "country": country,
            "trending_today": trends,
            "mode": "pytrends",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        }

    except Exception as e:
        return {"country": country, "mode": "pytrends_error", "error": str(e), "trending_today": []}


def _no_pytrends(context: str = "") -> dict:
    return {
        "mode": "pytrends_unavailable",
        "context": context,
        "install_command": "pip install pytrends",
        "note": "pytrends non installe. Lancer: pip install pytrends",
        "fallback_url": f"https://trends.google.com/",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Google Trends sans API key - pytrends"
    )
    parser.add_argument("--keyword", help="Mot-cle a analyser")
    parser.add_argument("--compare", help="Mots-cles a comparer, separes par virgule")
    parser.add_argument("--trending", action="store_true", help="Tendances du jour")
    parser.add_argument("--country", default="FR")
    parser.add_argument("--timeframe", default="today 12-m",
                        help="Periode (defaut: 12 mois). Exemples: today 3-m, today 5-y")
    parser.add_argument("--output", help="Fichier JSON de sortie")
    args = parser.parse_args()

    if not PYTRENDS_AVAILABLE:
        print("ERREUR: pytrends non installe. Lancer: pip install pytrends", file=sys.stderr)
        sys.exit(1)

    if not any([args.keyword, args.compare, args.trending]):
        parser.print_help()
        sys.exit(0)

    print(f"Google Trends (no-key) - [{args.country}]")

    results = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "country": args.country,
        "data": {},
        "available_without_auth": [
            "trend_curve_12m (interet 0-100, normalise)",
            "direction (up/stable/down)",
            "related_queries_rising (angles emergents)",
            "related_queries_top",
            "trending_searches_today",
            "keyword_comparison (max 5 mots-cles)",
        ],
    }

    if args.trending:
        results["data"]["trending_today"] = fetch_trending_searches(args.country)

    if args.keyword:
        results["data"]["trend_curve"] = fetch_trend_curve(args.keyword, args.country, args.timeframe)
        results["data"]["related_queries"] = fetch_related_queries(args.keyword, args.country)

    if args.compare:
        kws = [k.strip() for k in args.compare.split(",") if k.strip()]
        if args.keyword:
            kws = [args.keyword] + [k for k in kws if k != args.keyword]
        results["data"]["comparison"] = compare_keywords(kws[:5], args.country)

    output_str = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"  Sauvegarde: {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
