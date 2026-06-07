#!/usr/bin/env python3
"""
generate_report.py - Alan Competitive Intel
Génère un rapport HTML autonome à partir d'un fichier JSON de données concurrentielles.

Usage:
  python3 generate_report.py --data data.json --output rapport-produit-2024-12-01.html
  python3 generate_report.py --data data.json  # output auto-nommé sur le Desktop
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────────────
# HELPERS — BADGES
# ──────────────────────────────────────────────────────

def confidence_badge(level: str) -> str:
    colors = {"HIGH": "#00c896", "MEDIUM": "#ffd32a", "LOW": "#ff8c42", "N/A": "#ff4757"}
    color = colors.get(level.upper(), "#888")
    return f'<span class="badge-confidence" style="background:{color}20;color:{color};border:1px solid {color}40">{level}</span>'


def winner_badge(label: str) -> str:
    cfg = {
        "Evergreen": ("#00c896", "🌿"),
        "Hero": ("#1877F2", "🏆"),
        "Winner": ("#a855f7", "✅"),
        "Validation": ("#ffd32a", "📊"),
        "Test": ("#888", "🧪"),
    }
    color, icon = cfg.get(label, ("#888", ""))
    return f'<span class="badge-winner" style="background:{color}25;color:{color};border:1px solid {color}50">{icon} {label}</span>'


def angle_badge(angle: str) -> str:
    colors = {
        "Transformation": "#00c896",
        "Problème": "#ff4757",
        "Preuve Sociale": "#1877F2",
        "Contre-intuitif": "#a855f7",
        "Urgence": "#ff8c42",
        "Éducatif": "#ffd32a",
        "Autorité": "#00b4d8",
        "Entertainment": "#ff0050",
    }
    color = colors.get(angle, "#888888")
    return f'<span class="badge-angle" style="background:{color}20;color:{color};border:1px solid {color}40">{angle}</span>'


def trend_arrow(direction: str) -> str:
    arrows = {
        "increase": '<span style="color:#00c896;font-weight:700">↑</span>',
        "up": '<span style="color:#00c896;font-weight:700">↑</span>',
        "decrease": '<span style="color:#ff4757;font-weight:700">↓</span>',
        "down": '<span style="color:#ff4757;font-weight:700">↓</span>',
        "stable": '<span style="color:#ffd32a;font-weight:700">→</span>',
    }
    return arrows.get((direction or "").lower(), '<span style="color:#555">—</span>')


def fmt_count(n) -> str:
    if not n:
        return "—"
    try:
        n = int(n)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.0f}K"
        return str(n)
    except (ValueError, TypeError):
        return str(n)


# ──────────────────────────────────────────────────────
# SECTION — TIKTOK TENDANCES
# ──────────────────────────────────────────────────────

def build_tiktok_trends_section(tiktok_trends: dict) -> str:
    if not tiktok_trends:
        return ""

    hashtags = tiktok_trends.get("hashtags", [])
    topics = tiktok_trends.get("topics", [])
    sounds = tiktok_trends.get("sounds", [])
    country = tiktok_trends.get("country", "")
    period = tiktok_trends.get("period_days", "")
    mode = tiktok_trends.get("mode", "")
    src = tiktok_trends.get("source_url", "")
    date = tiktok_trends.get("extraction_date", "")

    if not any([hashtags, topics, sounds]):
        note = tiktok_trends.get("note", "Données TikTok indisponibles.")
        fallback = tiktok_trends.get("fallback_url", "")
        return (
            '<section class="section">'
            '<div class="section-title">TikTok — Tendances</div>'
            '<div class="no-data-card">' + note +
            (f' <a href="{fallback}" target="_blank" rel="noopener" style="color:#1877F2">Accès manuel →</a>' if fallback else "") +
            "</div></section>"
        )

    # Hashtags table
    hashtag_rows = ""
    for h in hashtags[:15]:
        hashtag_rows += (
            f'<tr>'
            f'<td style="color:#ff0050;font-weight:600">#{h.get("hashtag","").lstrip("#")}</td>'
            f'<td style="color:#e8e8f0">{fmt_count(h.get("post_count"))}</td>'
            f'<td style="color:#a0a0c0">{fmt_count(h.get("view_count"))}</td>'
            f'<td>{trend_arrow(h.get("trend_direction",""))}</td>'
            f'</tr>'
        )

    hashtag_section = ""
    if hashtag_rows:
        hashtag_section = (
            '<div style="flex:1;min-width:280px">'
            '<div style="font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#6666888;margin-bottom:10px;font-weight:600">Hashtags tendance</div>'
            '<div class="table-wrapper"><table>'
            '<thead><tr><th>Hashtag</th><th>Posts</th><th>Vues</th><th>Tendance</th></tr></thead>'
            '<tbody>' + hashtag_rows + '</tbody>'
            '</table></div></div>'
        )

    # Topics table
    topic_rows = ""
    for t in topics[:10]:
        topic_rows += (
            f'<tr>'
            f'<td style="color:#e8e8f0;font-weight:500">{t.get("topic","")}</td>'
            f'<td style="color:#a0a0c0">{fmt_count(t.get("post_count"))}</td>'
            f'<td style="color:#a0a0c0">{fmt_count(t.get("view_count"))}</td>'
            f'<td>{trend_arrow(t.get("trend_direction",""))}</td>'
            f'</tr>'
        )

    topic_section = ""
    if topic_rows:
        topic_section = (
            '<div style="flex:1;min-width:280px">'
            '<div style="font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#6666888;margin-bottom:10px;font-weight:600">Topics tendance</div>'
            '<div class="table-wrapper"><table>'
            '<thead><tr><th>Topic</th><th>Posts</th><th>Vues</th><th>Tendance</th></tr></thead>'
            '<tbody>' + topic_rows + '</tbody>'
            '</table></div></div>'
        )

    # Sounds list
    sound_pills = ""
    for s in sounds[:8]:
        title = s.get("title", "")
        artist = s.get("artist", "")
        usage = fmt_count(s.get("usage_count"))
        arr = trend_arrow(s.get("trend_direction", ""))
        sound_pills += (
            f'<div class="card" style="padding:10px 14px;display:flex;justify-content:space-between;align-items:center;gap:8px">'
            f'<div><span style="color:#e8e8f0;font-size:13px">{title}</span>'
            + (f'<span style="color:#666688;font-size:11px;margin-left:6px">{artist}</span>' if artist else "")
            + f'</div><div style="display:flex;gap:8px;align-items:center;white-space:nowrap">'
            f'<span style="color:#a0a0c0;font-size:12px">{usage} utilisations</span>{arr}</div></div>'
        )

    sound_section = ""
    if sound_pills:
        sound_section = (
            '<div style="margin-top:20px">'
            '<div style="font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#6666888;margin-bottom:10px;font-weight:600">Sons tendance</div>'
            '<div style="display:flex;flex-direction:column;gap:8px">' + sound_pills + '</div></div>'
        )

    meta_badge = ""
    if mode and mode != "api_failed":
        meta_badge = f'<span style="font-size:11px;color:#555577;margin-left:8px">Source: <code>{mode}</code> · {date}</span>'
    if mode == "api_failed":
        meta_badge = '<span style="font-size:11px;color:#ff8c42;margin-left:8px">⚠ API rate-limited — données partielles</span>'

    return (
        '<section class="section">'
        '<div class="section-title">TikTok — Tendances ' + (f'{country} · {period}j' if country else "") + meta_badge + '</div>'
        '<div style="display:flex;flex-wrap:wrap;gap:20px">'
        + hashtag_section + topic_section +
        '</div>'
        + sound_section +
        '</section>'
    )


# ──────────────────────────────────────────────────────
# SECTION — GOOGLE TRENDS
# ──────────────────────────────────────────────────────

def build_google_trends_section(google_trends: dict) -> str:
    if not google_trends:
        return ""

    keyword = google_trends.get("keyword", "")
    country = google_trends.get("country", "")
    curve = google_trends.get("trend_curve", [])
    direction = google_trends.get("direction", "stable")
    direction_label = google_trends.get("direction_label", "Stable")
    peak = google_trends.get("peak_interest", 0)
    current = google_trends.get("current_interest", 0)
    mode = google_trends.get("mode", "")
    src = google_trends.get("source_url", "")
    date = google_trends.get("extraction_date", "")
    related_rising = google_trends.get("related_queries", {}).get("rising_queries", [])

    if mode in ("pytrends_error", "pytrends_unavailable", "pytrends_empty"):
        note = google_trends.get("note", google_trends.get("error", "Données indisponibles."))
        fallback = google_trends.get("fallback_url", src or "")
        return (
            '<section class="section">'
            '<div class="section-title">Google Trends</div>'
            '<div class="no-data-card">' + note +
            (f' <a href="{fallback}" target="_blank" rel="noopener" style="color:#1877F2">Voir sur Google →</a>' if fallback else "") +
            "</div></section>"
        )

    if not curve:
        return ""

    dir_color = {"up": "#00c896", "down": "#ff4757", "stable": "#ffd32a"}.get(direction, "#888")
    dir_icon = {"up": "↑", "down": "↓", "stable": "→"}.get(direction, "→")

    # Build chart data as JSON-safe lists (no f-string escaping needed for JS)
    labels_json = json.dumps([p["date"] for p in curve])
    values_json = json.dumps([p["interest"] for p in curve])

    # Build the chart canvas block as a plain string (avoids f-string/JS brace conflicts)
    chart_id = "gtChart"
    chart_block = (
        '<div class="chart-card" style="margin-top:20px">'
        '<div class="chart-title">Intérêt de recherche — 12 mois (Google Trends, 0-100)</div>'
        '<canvas id="' + chart_id + '" height="80"></canvas>'
        '</div>'
        '<script>'
        '(function(){'
        'var ctx=document.getElementById("' + chart_id + '").getContext("2d");'
        'new Chart(ctx,{'
        'type:"line",'
        'data:{'
        'labels:' + labels_json + ','
        'datasets:[{label:"' + keyword.replace('"', "'") + '",'
        'data:' + values_json + ','
        'borderColor:"#1877F2",backgroundColor:"rgba(24,119,242,0.08)",'
        'borderWidth:2,pointRadius:0,tension:0.3,fill:true}]'
        '},'
        'options:{responsive:true,plugins:{legend:{display:false}},'
        'scales:{x:{display:true,ticks:{maxTicksLimit:6,color:"#555577",font:{size:10}},grid:{color:"#1a1a2e"}},'
        'y:{min:0,max:100,ticks:{color:"#555577",font:{size:10}},grid:{color:"#1a1a2e"}}}}}'
        ');'
        '})();'
        '</script>'
    )

    # Rising queries as tags
    rising_html = ""
    if related_rising:
        tags = "".join(
            f'<span style="background:#1877F215;border:1px solid #1877F230;color:#a0c0f0;padding:4px 10px;border-radius:6px;font-size:12px">'
            f'{r.get("query","")} '
            f'<span style="color:#1877F2;font-size:10px">{r.get("value","")}</span>'
            f'</span>'
            for r in related_rising[:8]
        )
        rising_html = (
            '<div style="margin-top:16px">'
            '<div style="font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#6666888;margin-bottom:8px;font-weight:600">'
            'Requêtes associées en hausse (= angles émergents)</div>'
            '<div style="display:flex;flex-wrap:wrap;gap:8px">' + tags + '</div>'
            '</div>'
        )

    src_link = f'<a href="{src}" target="_blank" rel="noopener" style="color:#1877F2;font-size:11px">Voir sur Google Trends →</a>' if src else ""

    return (
        '<section class="section">'
        '<div class="section-title">Google Trends — ' + keyword + ' · ' + country + '</div>'
        '<div class="cards-grid" style="margin-bottom:16px">'
        f'<div class="card"><div class="metric-value" style="color:{dir_color}">{dir_icon} {direction_label}</div><div class="metric-label">Tendance 12 mois</div></div>'
        f'<div class="card"><div class="metric-value">{peak}</div><div class="metric-label">Pic d\'intérêt (max 100)</div></div>'
        f'<div class="card"><div class="metric-value">{current}</div><div class="metric-label">Intérêt actuel</div></div>'
        '</div>'
        + chart_block
        + rising_html
        + f'<div style="margin-top:8px;color:#555577;font-size:11px">Source: pytrends (Google Trends public) · {date} · {src_link}</div>'
        + '</section>'
    )


# ──────────────────────────────────────────────────────
# SECTION — HTML PRINCIPAL
# ──────────────────────────────────────────────────────

def build_html(data: dict) -> str:
    product = data.get("product_name", "Produit Inconnu")
    market = data.get("market", "France")
    generated_date = datetime.now().strftime("%d/%m/%Y à %Hh%M")
    competitors = data.get("competitors", [])
    global_confidence = data.get("global_confidence", "MEDIUM")
    summary = data.get("summary", {})
    market_signal = data.get("market_signal", {})
    white_spaces = data.get("white_spaces", [])
    proven_angles = data.get("proven_angles", [])
    sources = data.get("sources", [])
    limits = data.get("limits", [])

    nb_ads_total = sum(c.get("meta_ads", {}).get("total_active", 0) for c in competitors)
    nb_hero_total = sum(c.get("meta_ads", {}).get("hero_plus", 0) for c in competitors)

    competitors_sorted = sorted(competitors, key=lambda c: c.get("score_global", 0), reverse=True)

    # Competitor rows
    competitor_rows = ""
    for i, comp in enumerate(competitors_sorted):
        meta = comp.get("meta_ads", {})
        tiktok = comp.get("tiktok_ads", {})
        revenue = comp.get("revenue", {})
        score = comp.get("score_global", 0)
        score_pct = min(score, 100)
        score_color = "#00c896" if score >= 60 else "#ffd32a" if score >= 35 else "#ff8c42"
        initials = "".join(w[0].upper() for w in comp.get("name", "??").split()[:2])
        bg_colors = ["#1877F2", "#ff0050", "#a855f7", "#00c896", "#ff8c42", "#00b4d8", "#ffd32a", "#ff4757"]
        bg = bg_colors[i % len(bg_colors)]

        rev_str = revenue.get("estimate", "N/A")
        rev_conf = revenue.get("confidence", "N/A")
        traffic = comp.get("traffic_monthly", {}).get("value", None)
        traffic_str = f"{traffic:,}" if traffic else "N/A"
        traffic_conf = comp.get("traffic_monthly", {}).get("confidence", "N/A")

        dominant_angle = meta.get("dominant_angle", tiktok.get("dominant_angle", "N/A"))
        winner_plus = meta.get("winner_plus", 0)
        hero_plus = meta.get("hero_plus", 0)
        evergreen = meta.get("evergreen", 0)
        total_active = meta.get("total_active", 0)

        competitor_rows += f"""
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:36px;height:36px;border-radius:8px;background:{bg};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0">{initials}</div>
              <div>
                <div style="font-weight:600;color:#e8e8f0">{comp.get("name","?")}</div>
                <div style="font-size:11px;color:#666688">{comp.get("domain","")}</div>
              </div>
            </div>
          </td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:60px;height:6px;background:#2a2a3e;border-radius:3px;overflow:hidden">
                <div style="width:{score_pct}%;height:100%;background:{score_color};border-radius:3px"></div>
              </div>
              <span style="font-weight:700;color:{score_color}">{score}</span>
            </div>
          </td>
          <td style="color:#e8e8f0;font-weight:600">{total_active}</td>
          <td>{winner_badge("Hero") if hero_plus > 0 else ""} <span style="color:#e8e8f0">{winner_plus}W / {hero_plus}H / {evergreen}E</span></td>
          <td>{angle_badge(dominant_angle) if dominant_angle != "N/A" else "<span style='color:#555'>N/A</span>"}</td>
          <td style="color:#e8e8f0">{comp.get("price_range","N/A")}</td>
          <td><span style="color:#a0a0c0">{traffic_str}</span> {confidence_badge(traffic_conf)}</td>
          <td><span style="color:#a0a0c0">{rev_str}</span> {confidence_badge(rev_conf)}</td>
        </tr>"""

    # Angle heatmap
    all_angles = ["Transformation", "Problème", "Preuve Sociale", "Contre-intuitif", "Urgence", "Éducatif", "Autorité", "Entertainment"]
    heatmap_header = "<tr><th>Angle</th>" + "".join(f"<th>{c.get('name','?')[:12]}</th>" for c in competitors_sorted[:6]) + "<th>Statut</th></tr>"
    heatmap_rows = ""
    angle_stats = data.get("angle_stats", {})

    for angle in all_angles:
        row = f"<tr><td>{angle_badge(angle)}</td>"
        hero_count = 0
        for comp in competitors_sorted[:6]:
            angle_data = comp.get("angles", {}).get(angle, {})
            label = angle_data.get("best_label", "")
            if label:
                if label in ("Evergreen", "Hero"):
                    hero_count += 1
                row += f"<td style='text-align:center'>{winner_badge(label)}</td>"
            else:
                row += "<td style='text-align:center;color:#333'>—</td>"
        stats = angle_stats.get(angle, {})
        hero_c = stats.get("hero_count", hero_count)
        if hero_c >= 2:
            status = f'<span style="color:#00c896;font-weight:700">✅ Prouvé ({hero_c}H+)</span>'
        elif stats.get("winner_count", 0) >= 3:
            status = f'<span style="color:#ffd32a">⚡ Signal ({stats.get("winner_count",0)}W)</span>'
        else:
            status = '<span style="color:#555">✖ Non validé</span>'
        row += f"<td>{status}</td></tr>"
        heatmap_rows += row

    # White spaces
    white_space_cards = ""
    for ws in white_spaces:
        white_space_cards += f"""
        <div class="ws-card">
          <div class="ws-header">{angle_badge(ws.get("angle","?"))} <span class="ws-usage">{ws.get("usage","?")}</span></div>
          <p class="ws-opportunity">{ws.get("opportunity","")}</p>
          <p class="ws-recommendation">💡 {ws.get("recommendation","")}</p>
          <div class="ws-proof">Référence : {ws.get("proof","")}</div>
        </div>"""
    if not white_space_cards:
        white_space_cards = '<div class="no-data-card">Marché mature — angles principaux occupés. Différenciation par sous-angle ou mécanisme nécessaire.</div>'

    # Proven angles
    proven_section = ""
    if proven_angles:
        for pa in proven_angles:
            hooks_html = "".join(
                f'<li class="hook-item"><span class="hook-quote">"{h.get("text","")}"</span> <span class="hook-source">— {h.get("source","")}</span></li>'
                for h in pa.get("hooks", [])
            )
            proven_section += f"""
            <div class="proven-card">
              <div class="proven-header">
                {angle_badge(pa.get("angle","?"))}
                <span class="proven-label">✅ PROUVÉ</span>
              </div>
              <div class="proven-proof"><strong>Preuve :</strong> {pa.get("proof","")}</div>
              <div class="proven-hooks">
                <div class="hooks-title">Patterns hooks observés :</div>
                <ul class="hooks-list">{hooks_html}</ul>
              </div>
              <div class="proven-meta">
                Format dominant : <strong>{pa.get("format","?")}</strong> &nbsp;|&nbsp;
                Plateforme : <strong>{pa.get("platform","?")}</strong> &nbsp;|&nbsp;
                CTA récurrent : <strong>{pa.get("cta","?")}</strong>
              </div>
              <div class="proven-warning">⚠️ Ne pas copier — patterns à réinterpréter avec un message original.</div>
            </div>"""
    else:
        proven_section = """
        <div class="warning-banner">
          <div class="warning-icon">⚠️</div>
          <div>
            <strong>Données insuffisantes pour des recommandations d'angles.</strong><br>
            Aucun angle n'a atteint le seuil de validation (2+ concurrents Hero 60j+).<br>
            <em>Recommandation : tester les angles Transformation et Problème avec 3-5 créas chacun avant de conclure.</em>
          </div>
        </div>"""

    # Sources
    sources_html = "".join(
        f'<li class="source-item"><a href="{s.get("url","#")}" target="_blank" rel="noopener">{s.get("label","")}</a> — accédé le {s.get("date","")} — Mode: <code>{s.get("mode","")}</code></li>'
        for s in sources
    )
    limits_html = "".join(f'<li>{lim}</li>' for lim in limits)

    # Market signal
    trend_icon = {"up": "↗️", "stable": "↔️", "down": "↘️"}.get(market_signal.get("trend_direction", "stable"), "↔️")
    saturation_color = {
        "Émergent": "#00c896", "Actif": "#1877F2", "Mature": "#ffd32a", "Saturé": "#ff4757"
    }.get(market_signal.get("saturation", "Actif"), "#888")

    # New dynamic sections
    tiktok_section_html = build_tiktok_trends_section(data.get("tiktok_trends"))
    google_section_html = build_google_trends_section(data.get("google_trends"))

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analyse Concurrentielle — {product}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0a0a0f; color: #e8e8f0; font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif; line-height: 1.6; min-height: 100vh; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 24px; }}
    .header {{ padding: 48px 0 40px; border-bottom: 1px solid #2a2a3e; margin-bottom: 40px; }}
    .header-meta {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }}
    .badge {{ background: #1877F220; color: #1877F2; border: 1px solid #1877F240; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }}
    .date-label {{ color: #6666888; font-size: 13px; }}
    h1 {{ font-size: clamp(28px, 5vw, 48px); font-weight: 800; background: linear-gradient(135deg, #e8e8f0 0%, #8888c8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 8px; }}
    .subtitle {{ color: #6666888; font-size: 15px; margin-bottom: 24px; }}
    .summary-bullets {{ display: grid; gap: 8px; }}
    .bullet {{ background: #12121a; border: 1px solid #2a2a3e; border-radius: 10px; padding: 12px 16px; font-size: 14px; color: #c0c0d8; }}
    .bullet strong {{ color: #e8e8f0; }}
    .section {{ margin-bottom: 48px; }}
    .section-title {{ font-size: 13px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #6666888; margin-bottom: 20px; padding-bottom: 8px; border-bottom: 1px solid #2a2a3e; }}
    .card {{ background: #12121a; border: 1px solid #2a2a3e; border-radius: 12px; padding: 20px; }}
    .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    .metric-value {{ font-size: 32px; font-weight: 800; color: #e8e8f0; line-height: 1; margin-bottom: 4px; }}
    .metric-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: #6666888; }}
    .table-wrapper {{ overflow-x: auto; border-radius: 12px; border: 1px solid #2a2a3e; }}
    table {{ width: 100%; border-collapse: collapse; background: #12121a; }}
    thead {{ background: #1a1a2e; }}
    th {{ padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #6666888; white-space: nowrap; }}
    td {{ padding: 14px 16px; border-top: 1px solid #1e1e2e; vertical-align: middle; font-size: 13px; }}
    tr:hover td {{ background: #14141e; }}
    .badge-confidence {{ padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
    .badge-winner {{ padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
    .badge-angle {{ padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
    .heatmap-wrapper {{ overflow-x: auto; border-radius: 12px; border: 1px solid #2a2a3e; }}
    .heatmap-wrapper table {{ background: #12121a; }}
    .ws-card {{ background: #0d1f18; border: 1px solid #00c89630; border-radius: 12px; padding: 20px; margin-bottom: 12px; }}
    .ws-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
    .ws-usage {{ color: #6666888; font-size: 13px; }}
    .ws-opportunity {{ color: #c0c0d8; font-size: 14px; margin-bottom: 8px; }}
    .ws-recommendation {{ color: #00c896; font-size: 14px; margin-bottom: 8px; }}
    .ws-proof {{ font-size: 12px; color: #555577; border-top: 1px solid #00c89620; padding-top: 8px; }}
    .proven-card {{ background: #12121a; border: 1px solid #1877F240; border-radius: 12px; padding: 24px; margin-bottom: 16px; }}
    .proven-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
    .proven-label {{ background: #00c89620; color: #00c896; border: 1px solid #00c89640; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; }}
    .proven-proof {{ background: #1877F210; border: 1px solid #1877F220; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #a0c0f0; margin-bottom: 16px; }}
    .hooks-title {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #6666888; margin-bottom: 10px; font-weight: 600; }}
    .hooks-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }}
    .hook-item {{ background: #1a1a2e; border-radius: 8px; padding: 10px 14px; font-size: 13px; }}
    .hook-quote {{ color: #e8e8f0; font-style: italic; }}
    .hook-source {{ color: #6666888; font-size: 12px; }}
    .proven-meta {{ font-size: 13px; color: #888899; background: #0a0a0f; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }}
    .proven-meta strong {{ color: #c0c0d8; }}
    .proven-warning {{ font-size: 12px; color: #ff8c42; }}
    .warning-banner {{ background: #ff8c4210; border: 1px solid #ff8c4240; border-radius: 12px; padding: 20px 24px; display: flex; gap: 16px; align-items: flex-start; }}
    .warning-icon {{ font-size: 24px; flex-shrink: 0; }}
    .source-item {{ padding: 6px 0; font-size: 13px; color: #888899; border-bottom: 1px solid #1a1a2e; }}
    .source-item a {{ color: #1877F2; text-decoration: none; }}
    .source-item a:hover {{ text-decoration: underline; }}
    code {{ background: #1a1a2e; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #a0c0f0; font-family: 'Courier New', monospace; }}
    .no-data-card {{ background: #12121a; border: 1px dashed #2a2a3e; border-radius: 12px; padding: 20px; color: #6666888; font-style: italic; text-align: center; }}
    .chart-card {{ background: #12121a; border: 1px solid #2a2a3e; border-radius: 12px; padding: 20px; }}
    .chart-title {{ font-size: 13px; font-weight: 600; color: #8888a8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.06em; }}
    .footer {{ margin-top: 60px; padding-top: 24px; border-top: 1px solid #2a2a3e; color: #555577; font-size: 12px; text-align: center; }}
  </style>
</head>
<body>
<div class="container">

  <header class="header">
    <div class="header-meta">
      <span class="badge">Analyse Concurrentielle</span>
      <span class="date-label">Généré le {generated_date}</span>
      {confidence_badge(global_confidence)}
    </div>
    <h1>{product}</h1>
    <p class="subtitle">{market} &nbsp;·&nbsp; {len(competitors)} concurrents analysés &nbsp;·&nbsp; {nb_ads_total} ads observées &nbsp;·&nbsp; {nb_hero_total} ads Hero+</p>
    <div class="summary-bullets">
      <div class="bullet">🎯 <strong>Concurrent dominant :</strong> {summary.get("top_competitor","N/A")}</div>
      <div class="bullet">📈 <strong>Angle prouvé n°1 :</strong> {summary.get("top_angle","N/A")}</div>
      <div class="bullet">💡 <strong>Meilleur white space :</strong> {summary.get("white_space","N/A")}</div>
      <div class="bullet">💰 <strong>Signal revenu le plus fiable :</strong> {summary.get("revenue_signal","N/A")}</div>
      <div class="bullet">⚡ <strong>Action recommandée :</strong> {summary.get("action","N/A")}</div>
    </div>
  </header>

  <section class="section">
    <div class="section-title">Signal Marché</div>
    <div class="cards-grid">
      <div class="card">
        <div class="metric-value" style="color:{saturation_color}">{market_signal.get("saturation","N/A")}</div>
        <div class="metric-label">Niveau de saturation</div>
      </div>
      <div class="card">
        <div class="metric-value">{trend_icon} {market_signal.get("trend_label","N/A")}</div>
        <div class="metric-label">Tendance 12 mois</div>
      </div>
      <div class="card">
        <div class="metric-value" style="font-size:20px">{market_signal.get("search_volume","N/A")}</div>
        <div class="metric-label">Volume recherche estimé {confidence_badge(market_signal.get("search_confidence","N/A"))}</div>
        <div style="font-size:11px;color:#555577;margin-top:4px">{market_signal.get("search_source","")}</div>
      </div>
      <div class="card">
        <div class="metric-value" style="font-size:20px">{market_signal.get("active_advertisers","N/A")}</div>
        <div class="metric-label">Annonceurs actifs estimés</div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="section-title">Matrice Concurrents</div>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Marque</th><th>Score Global</th><th>Ads Actives</th>
            <th>Winner / Hero / Evergreen</th><th>Angle Dominant</th>
            <th>Prix</th><th>Trafic/mois</th><th>CA Estimé</th>
          </tr>
        </thead>
        <tbody>{competitor_rows}</tbody>
      </table>
    </div>
  </section>

  <section class="section">
    <div class="section-title">Carte des Angles — Meta + TikTok</div>
    <div class="heatmap-wrapper">
      <table><thead>{heatmap_header}</thead><tbody>{heatmap_rows}</tbody></table>
    </div>
    <div style="margin-top:12px;display:flex;gap:16px;flex-wrap:wrap">
      <span>{winner_badge("Evergreen")} 180j+ actif</span>
      <span>{winner_badge("Hero")} 60-179j actif</span>
      <span>{winner_badge("Winner")} 22-59j actif</span>
      <span>{winner_badge("Validation")} 8-21j actif</span>
    </div>
  </section>

  {tiktok_section_html}

  {google_section_html}

  <section class="section">
    <div class="section-title">White Spaces — Opportunités</div>
    {white_space_cards}
  </section>

  <section class="section">
    <div class="section-title">Angles Recommandés</div>
    {proven_section}
  </section>

  <section class="section">
    <div class="section-title">Sources &amp; Méthodologie</div>
    <div class="card">
      <ul style="list-style:none">{sources_html if sources_html else "<li style='color:#555577'>Aucune source documentée</li>"}</ul>
      {"<div style='margin-top:16px;padding-top:16px;border-top:1px solid #2a2a3e'><div style='font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#6666888;margin-bottom:8px'>Limites de l\\'analyse</div><ul style=\\'list-style:disc;padding-left:20px;color:#888899;font-size:13px\\'>" + limits_html + "</ul></div>" if limits else ""}
    </div>
  </section>

  <footer class="footer">
    <p>Rapport généré par alan-competitive-intel &nbsp;·&nbsp; {generated_date} &nbsp;·&nbsp; Données publiques uniquement — aucune API payante</p>
  </footer>

</div>
</body>
</html>"""


def get_output_path(product_slug: str) -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"rapport-{product_slug}-{date_str}.html"
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop / filename
    return Path.cwd() / filename


def main():
    parser = argparse.ArgumentParser(description="Génère un rapport HTML d'analyse concurrentielle")
    parser.add_argument("--data", required=True, help="Chemin vers le fichier JSON de données")
    parser.add_argument("--output", help="Chemin de sortie du fichier HTML (optionnel)")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Erreur : fichier de données introuvable : {data_path}", file=sys.stderr)
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = build_html(data)

    if args.output:
        output_path = Path(args.output)
    else:
        slug = data.get("product_name", "produit").lower().replace(" ", "-").replace("/", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        output_path = get_output_path(slug)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rapport généré : {output_path}")
    return str(output_path)


if __name__ == "__main__":
    main()
