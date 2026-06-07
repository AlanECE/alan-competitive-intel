#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrape_tiktok_ads.py — Métriques publicitaires TikTok RÉELLES via la TikTok Ads Library.

PLUG & PLAY OPT-IN : ce script n'active des métriques réelles QUE si un token Apify
est fourni au runtime via la variable d'environnement APIFY_TOKEN. Aucun token n'est
jamais stocké dans ce fichier ni dans le repo. Sans token, le script se rabat
proprement sur un mode "no_token" avec un lien manuel — le skill reste plug-and-play.

  export APIFY_TOKEN="apify_api_..."   # le token de l'utilisateur, fourni au runtime
  python3 scrape_tiktok_ads.py --advertisers "CeraVe,The Ordinary,NuFACE" --region all

Actor utilisé : silva95gustavo/tiktok-ads-scraper (https://apify.com/silva95gustavo/tiktok-ads-scraper)
Source des données : TikTok Commercial Content Library (https://library.tiktok.com/ads)

⚠️ PÉRIMÈTRE = UE/EEE (transparence DSA), PAS USA. Les impressions sont européennes →
   à lire comme signal de STRATÉGIE CRÉATIVE, pas comme volume US.
⚠️ LONGÉVITÉ : firstShown/lastShown sont des fenêtres de reporting DSA courtes (≈ jours),
   PAS la durée de campagne. NE PAS appliquer les Winner Rules Hero/Evergreen ici
   (celles-ci sont conçues pour la Meta Ads Library).
"""
import os, sys, json, time, re, argparse, urllib.request, urllib.parse
from collections import Counter
from datetime import datetime

ACTOR = "silva95gustavo~tiktok-ads-scraper"
LIBRARY_BASE = "https://library.tiktok.com/ads"


def _no_token():
    return {
        "mode": "no_token",
        "message": ("APIFY_TOKEN non défini. Pour activer les métriques réelles, "
                    "fournir un token Apify au runtime : export APIFY_TOKEN=apify_api_..."),
        "actor": "silva95gustavo/tiktok-ads-scraper",
        "fallback_url": "https://library.tiktok.com/ads",
        "caveats": _caveats(),
    }


def _caveats():
    return {
        "scope": "UE/EEE uniquement (transparence DSA) — impressions européennes, pas USA.",
        "longevity": ("firstShown/lastShown = fenêtres de reporting DSA courtes, "
                      "pas la durée de campagne. Ne pas appliquer Hero/Evergreen ici "
                      "(réservé à la Meta Ads Library)."),
        "signal": ("Métriques fiables : intensité publicitaire, reach, régions, "
                   "démographie, et part créateurs/affiliés (preuve de monétisation)."),
    }


def build_url(adv_name, region="all", start_time=None, end_time=None):
    # défaut : fenêtre ~8 mois glissants
    if start_time is None:
        start_time = 1759276800000  # ~2025-10-01
    if end_time is None:
        end_time = int(time.time() * 1000)
    params = {
        "region": region, "start_time": start_time, "end_time": end_time,
        "query_type": 1, "sort_type": "create_time,desc", "adv_name": adv_name,
    }
    return LIBRARY_BASE + "?" + urllib.parse.urlencode(params)


def _run_actor(url, limit, token):
    body = {
        "startUrls": [{"url": url}],
        "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": []},
        "skipDetails": False, "shouldDownloadVideos": False, "resultsLimit": limit,
    }
    api = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={token}&timeout=290&memory=1024")
    req = urllib.request.Request(api, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def _is_business(name):
    if not name:
        return False
    n = name.strip()
    return bool(re.search(r"\b(INC|LTD|LLC|GMBH|EUROPE|OFFICIAL|CO|SIRKETI|COMPANY|SHOP|TECHNOLOGY)\b",
                          n, re.I)) or n.isupper()


def _mid(b):
    return (b.get("lowerBound", 0) + b.get("upperBound", 0)) / 2 if b else 0


def _fmt(n):
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.0f}K"
    return str(n)


def analyze(items, query):
    regions, ages, genders = Counter(), Counter(), Counter()
    advs = Counter()
    biz = crtr = impr = 0
    aud = []
    for it in items:
        adv = (it.get("advertiserName") or it.get("adName") or "").strip()
        advs[adv] += 1
        impr += _mid(it.get("impressions"))
        for rs in (it.get("regionStats") or []):
            regions[rs.get("regionCode", "?")] += rs.get("impressions", 0) or 0
        tg = it.get("targeting") or {}
        if tg.get("audienceSize"):
            aud.append(_mid(tg["audienceSize"]))
        for reg in (tg.get("regions") or []):
            for a in (reg.get("ageRanges") or []):
                ages[a] += 1
            for g in (reg.get("genders") or []):
                genders[g] += 1
        if _is_business(adv):
            biz += 1
        else:
            crtr += 1
    n = len(items)
    return {
        "query": query,
        "adCount": n,
        "distinctAdvertisers": len(advs),
        "topAdvertisers": advs.most_common(3),
        "businessAds": biz,
        "creatorAds": crtr,
        "creatorSharePct": round(100 * crtr / n) if n else 0,
        "imprSampleMid": int(impr),
        "imprSampleFmt": _fmt(impr),
        "topRegions": [(r, _fmt(v)) for r, v in regions.most_common(5) if v > 0],
        "topAges": ages.most_common(3),
        "genders": dict(genders),
        "avgAudience": _fmt(sum(aud) / len(aud)) if aud else "N/A",
    }


def main():
    ap = argparse.ArgumentParser(description="Métriques TikTok Ads réelles via Apify (opt-in token).")
    ap.add_argument("--advertisers", required=True,
                    help="Noms d'annonceurs/marques séparés par des virgules")
    ap.add_argument("--region", default="all", help="Région EEE (ex: all, FR, ES) — défaut: all")
    ap.add_argument("--limit", type=int, default=25, help="Annonces max par marque (défaut 25)")
    ap.add_argument("--output", help="Chemin de sortie JSON (sinon stdout)")
    args = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        out = _no_token()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
        return

    brands = [b.strip() for b in args.advertisers.split(",") if b.strip()]
    results = []
    for b in brands:
        try:
            items = _run_actor(build_url(b, args.region), args.limit, token)
            results.append(analyze(items, b))
            print(f"[OK] {b}: {len(items)} annonces", file=sys.stderr)
        except Exception as e:
            results.append({"query": b, "mode": "api_error", "error": str(e)})
            print(f"[ERR] {b}: {e}", file=sys.stderr)
        time.sleep(1)

    out = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "source": ("TikTok Commercial Content Library (DSA/UE) via Apify "
                   "silva95gustavo/tiktok-ads-scraper"),
        "mode": "ok",
        "region": args.region,
        "caveats": _caveats(),
        "advertisers": results,
    }
    payload = json.dumps(out, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Sauvegardé → {args.output}", file=sys.stderr)
    else:
        print(payload)


if __name__ == "__main__":
    main()
