# -*- coding: utf-8 -*-
"""Staattisen sivuston generaattori – St1 Joppari (joppari.fi), St1 Pello.

    python3 build.py                    -> site/ NordicHostiin (Node, server.js) + ../joppari-nordichost.zip
    HOSTING=netlify python3 build.py    -> Netlify-demo (+ ../joppari-netlify.zip)
    HOSTING=netlify python3 build.py --preview --artifact -> esikatselu Claude-artifaktina (preview/)

Ilme noudattaa St1:n HelmiSimpukka-maailmaa (vihreä #00463c, kerma #f3f1d1, Nunito Sans) – asemalla toimii HelmiSimpukka Express ja Driver's.
Lounaslista: Päivi päivittää sen osoitteessa /hallinta/ → server.js tallentaa DATA_DIR/lounas.json → sivut lukevat /api/lounas.
Tekstit ja listat: content.py. Tyylit: src/style.css. Toiminnot: src/app.js. Vaatii Pillow-kirjaston.
"""
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import date, timedelta

from PIL import Image, ImageDraw, ImageFont, ImageOps

from content import (
    BREAKFAST_ONLY, BREAKFAST_TIMES, BUFFET_HOURS, COMPANY, DOG_FEE, DOORS, EXTRA_BED, GARLIC_PRICE, HOURS, HOURS_JS, HOURS_SCHEMA,
    HS_PELLO, LUNCH_HOURS, LUNCH_PIZZA, NAV, PAN_PIZZAS, PIZZA_TAGS, PIZZAS, REDIRECTS, ROOM_FEATURES, ROOM_GALLERY, ROOM_PRICES,
    TOPPING_PRICE, TOPPINGS, TOPPINGS_SV,
)
os.environ.setdefault("HOSTING", "nordichost")
from hosting import HOSTING, form_attrs, hidden_fields, write_host_files

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
SRC = os.path.join(ROOT, "src")
KUVAT = os.path.join(SRC, "kuvat")
IMG_OUT = os.path.join(SITE, "img")
BASE_URL = f"https://{COMPANY['domain']}"
DEMO = HOSTING == "netlify"
TEL = f"tel:{COMPANY['phone_intl']}"
MAPS = "https://www.google.com/maps/search/?api=1&query=St1+Pello+Pellontie+31+95700+Pello"
MAP_EMBED = "https://maps.google.com/maps?q=Pellontie+31,+95700+Pello&z=15&output=embed"
SITEMAP = []
VERSION = "1"
WIDTHS = [480, 800, 1200, 1600, 2000]
IMG_DIMS, IMG_WS = {}, {}
YEAR = 2026
TODAY = "2026-10-04"
NAME = COMPANY["name"]          # "St1 Joppari" – nimeä ei erotella St1:stä
STATION = COMPANY["station"]    # virallinen aseman nimi "St1 Pello"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


ICONS = {
    "phone": '<path d="M4 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L14 13l5 2v4a2 2 0 0 1-2 2C9.5 21 3 14.5 3 6a2 2 0 0 1 1-2Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "pin": '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9" r="2.6"/><path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M15 20c0-2.6 1.6-4.6 4-5"/>',
    "bus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 18v3M16 18v3"/><circle cx="8" cy="14.5" r=".8"/><circle cx="16" cy="14.5" r=".8"/>',
    "pizza": '<path d="M12 21 3.5 6.5a15 15 0 0 1 17 0z"/><path d="M5.3 9.5a12 12 0 0 1 13.4 0"/><circle cx="10" cy="12" r="1"/><circle cx="14" cy="13.5" r="1"/><circle cx="12" cy="17" r=".9"/>',
    "plate": '<circle cx="12" cy="13" r="7"/><circle cx="12" cy="13" r="3.8"/><path d="M3 4v5a1.5 1.5 0 0 0 3 0V4M4.5 9v11M20.5 4c-1.5 1-2 3-2 5.5 0 1.3.7 2 2 2V20"/>',
    "salad": '<path d="M3 12h18a9 9 0 0 1-18 0z"/><path d="M8 12c0-3 2-5 4-5M12 12c0-4 3-6 6-5-1 2-2 4-4 5M7 9c-1-1-3-1-4 0 1 1 2 2 4 3"/>',
    "coffee": '<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 10.5h1.5a2.5 2.5 0 0 1 0 5H17M8 3v3M12 3v3"/>',
    "bed": '<path d="M3 19V6M3 15h18v4M21 15v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11" r="2"/>',
    "sauna": '<path d="M4 20h16M6 20V11l6-5 6 5v9"/><path d="M9.5 14c0-1 1-1.2 1-2.2M12.5 14c0-1 1-1.2 1-2.2"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "kitchen": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M4 9h16M8 6h.01M11 6h.01"/><circle cx="12" cy="15" r="3"/>',
    "fridge": '<rect x="6" y="2.5" width="12" height="19" rx="2"/><path d="M6 10h12M9 6v2M9 13v3"/>',
    "paw": '<circle cx="7" cy="10" r="1.8"/><circle cx="17" cy="10" r="1.8"/><circle cx="10" cy="6" r="1.8"/><circle cx="14" cy="6" r="1.8"/><path d="M12 12c-3 0-5 3.5-5 5.5 0 2 2 2.5 5 1.5 3 1 5 .5 5-1.5S15 12 12 12z"/>',
    "iron": '<path d="M3 17h17v-3a6 6 0 0 0-6-6H8"/><path d="M3 17c0-4 3-6 7-6M8 8V6"/>',
    "door": '<path d="M5 21V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v17M3 21h18"/><circle cx="15.5" cy="12.5" r=".9"/>',
    "fuel": '<path d="M4 21V5a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16M3 21h13M4 10h11"/><path d="M15 8h2l2 2v8a1.5 1.5 0 0 0 3 0v-7l-3-3"/>',
    "app": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
    "wheat": '<path d="M12 21V8"/><path d="M12 12c-2.5 0-4-1.5-4-4 2.5 0 4 1.5 4 4zM12 12c2.5 0 4-1.5 4-4-2.5 0-4 1.5-4 4zM12 16c-2.5 0-4-1.5-4-4 2.5 0 4 1.5 4 4zM12 16c2.5 0 4-1.5 4-4-2.5 0-4 1.5-4 4zM12 8c-1.5-1-1.5-3 0-5 1.5 2 1.5 4 0 5z"/>',
    "flame": '<path d="M12 21a6 6 0 0 0 6-6c0-4-3-6-4-10-2 2-2.5 4-2 6-1-.5-2-2-2-3.5C7.5 9.5 6 12 6 15a6 6 0 0 0 6 6z"/>',
    "leaf": '<path d="M5 19c0-9 5-14 15-15-1 10-6 15-15 15z"/><path d="M5 19 13 11"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
    "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8.5a.5.5 0 0 1 .5-.5z"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "left": '<path d="m15 5-7 7 7 7"/>',
    "right": '<path d="m9 5 7 7-7 7"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "bag": '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "lock": '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13 7 4 4"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def logo(cls="brand"):
    """St1 + Joppari yhtenä lukitusmerkkinä – nimeä ei erotella."""
    return (f'<a class="{cls}" href="/" aria-label="{NAME}, etusivu"><img class="st1" src="/img/st1-logo.png" alt="St1" width="574" height="262">'
            f'<span class="wm"><b>Joppari</b><small>{STATION} · Kahvila-ravintola</small></span></a>')


# ---------------------------------------------------------------------------
# Kuvat
# ---------------------------------------------------------------------------

IMG_SRC = {os.path.splitext(f)[0]: os.path.join(KUVAT, f) for f in sorted(os.listdir(KUVAT))
           if f.lower().endswith((".jpg", ".jpeg", ".png"))}


def _resize_set(name, path, widths):
    meta = os.path.join(IMG_OUT, f".{name}.json")
    if os.path.exists(meta) and os.path.getmtime(meta) > os.path.getmtime(path):
        d = json.load(open(meta))
        IMG_DIMS[name], IMG_WS[name] = tuple(d["dims"]), d["ws"]
        if all(os.path.exists(os.path.join(IMG_OUT, f"{name}-{w}.webp")) for w in d["ws"]):
            return
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    IMG_DIMS[name] = im.size
    ws = [w for w in widths if w < im.width] + ([im.width] if im.width < widths[-1] else [widths[-1]])
    IMG_WS[name] = ws
    for w in ws:
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(os.path.join(IMG_OUT, f"{name}-{w}.webp"), "WEBP", quality=80, method=5)
    json.dump({"dims": im.size, "ws": ws}, open(meta, "w"))


def build_images():
    os.makedirs(IMG_OUT, exist_ok=True)
    for name, path in IMG_SRC.items():
        _resize_set(name, path, WIDTHS)
    for f, h in (("st1-logo.png", 120), ("helmisimpukka-express-logo.png", 160)):
        im = Image.open(os.path.join(SRC, f)).convert("RGBA")
        im.thumbnail((1000, h), Image.LANCZOS)
        im.save(os.path.join(IMG_OUT, f), optimize=True)


def img(name, alt, sizes="100vw", cls="", eager=False, style=""):
    w0, h0 = IMG_DIMS[name]
    ws = IMG_WS[name]
    srcset = ", ".join(f"/img/{name}-{w}.webp {w}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    return (f'<img{c} src="/img/{name}-{ws[min(1, len(ws) - 1)]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w0}" height="{h0}" alt="{esc(alt)}" {load}{st}>')


def src_of(name, i=-1):
    return f"/img/{name}-{IMG_WS[name][i if i >= 0 else len(IMG_WS[name]) + i]}.webp"


AI_NOTE = '<span class="ai-note">Havainnekuva</span>'


# ---------------------------------------------------------------------------
# Yhteiset palat
# ---------------------------------------------------------------------------

def btn(label, href, cls="btn btn-primary", ic="arrow"):
    ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return f'<a class="{cls}" href="{href}"{ext}>{label}{icon(ic) if ic else ""}</a>'


def btn_call(label=None, cls="btn btn-cream"):
    return f'<a class="{cls}" href="{TEL}">{icon("phone")}<span>{label or COMPANY["phone"]}</span></a>'


def open_badge(cls="open"):
    """Auki nyt / suljettu – JS päivittää; ilman JS:ää näkyy aukiolo."""
    return f'<span class="{cls}" data-open=\'{json.dumps(HOURS_JS)}\'><i></i><span>Ma–pe 7–20 · la–su 9–20</span></span>'


def header(current):
    links = "".join(f'<a href="{u}"{" aria-current=page" if current == u else ""}>{t}</a>' for t, u in NAV)
    mlinks = "".join(f'<a href="{u}">{t}{icon("arrow")}</a>' for t, u in [("Etusivu", "/")] + NAV)
    return f'''<header class="hdr">
  <div class="hdr-in">
    {logo()}
    <nav class="nav" aria-label="Päävalikko">{links}</nav>
    <div class="hdr-cta">{open_badge("open hdr-open")}<a class="btn btn-cream btn-sm" href="{TEL}">{icon("phone")}<span>{COMPANY["phone"]}</span></a></div>
    <button class="burger" aria-label="Valikko" aria-expanded="false"><span></span><span></span></button>
  </div>
  <nav class="mnav" aria-label="Mobiilivalikko">{mlinks}
    <div class="mnav-foot">{open_badge()}<p>{STATION}, {COMPANY["street"]}</p>{btn_call(cls="btn btn-primary")}</div></nav>
</header>'''


def hours_list(cls="hours"):
    rows = "".join(f'<li><span>{d}</span><b>{a}–{b}</b></li>' for d, a, b in HOURS)
    return f'<ul class="{cls}">{rows}</ul>'


def footer():
    demo = ('<p class="demo-note">Sivustoehdotus: Äijä Group. Tämä on esikatseluversio. '
            '<a href="/hallinta/">Kokeile lounaslistan hallintaa →</a></p>') if DEMO else ""
    return f'''<footer class="ftr">
  <div class="wrap">
    <div class="ftr-logos"><img src="/img/st1-logo.png" alt="St1" width="263" height="120" loading="lazy">
      <img src="/img/helmisimpukka-express-logo.png" alt="HelmiSimpukka Express" width="306" height="160" loading="lazy"></div>
    <div class="ftr-grid">
      <div class="ftr-brand"><h3>{NAME}</h3>
        <p>Kahvila-ravintola, pizzeria ja majoitus {STATION} -asemalla. Asemalla myös HelmiSimpukka Express ja Driver's. 55 asiakaspaikkaa.</p>
        <div class="some"><a href="{COMPANY["facebook"]}" target="_blank" rel="noopener" aria-label="Facebook">{icon("fb")}</a></div>
      </div>
      <div><h3>Aukioloajat</h3>{hours_list()}<p class="ftr-small">Lounasbuffet joka päivä {BUFFET_HOURS}</p></div>
      <div><h3>Ruoka ja majoitus</h3><ul><li><a href="/lounas/">Lounas</a></li><li><a href="/pizzat/">Pizzat</a></li>
        <li><a href="/majoitus/">Majoitus</a></li><li><a href="{HS_PELLO}" target="_blank" rel="noopener">Driver's-ruokalista</a></li><li><a href="/#asema">Asema ja palvelut</a></li></ul></div>
      <div><h3>Yhteystiedot</h3><ul>
        <li><a href="{MAPS}" target="_blank" rel="noopener">{STATION}<br>{COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}</a></li>
        <li><a href="{TEL}">{COMPANY["phone"]}</a></li>
        <li><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></li>
        <li><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a></li>
      </ul></div>
    </div>
    <div class="ftr-bottom"><span>© {YEAR} {NAME} · {STATION}, {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}</span>
      <span><a href="/tietosuojaseloste/">Tietosuojaseloste</a> · <a href="{COMPANY["travelpello"]}" target="_blank" rel="noopener">Travel Pello</a></span></div>
    {demo}
  </div>
</footer>
<div class="mbar" aria-label="Pikayhteys">{btn_call("Soita", "btn btn-line")}{btn("Päivän lounas", "/lounas/", "btn btn-primary", "plate")}</div>
<div class="lb" hidden><button class="lb-x" aria-label="Sulje">{icon("x")}</button><button class="lb-p" aria-label="Edellinen">{icon("left")}</button>
<figure><img alt=""><figcaption></figcaption></figure><button class="lb-n" aria-label="Seuraava">{icon("right")}</button></div>'''


def org_schema():
    return {
        "@context": "https://schema.org", "@type": ["Restaurant", "CafeOrCoffeeShop"], "@id": BASE_URL + "/#yritys",
        "name": NAME, "alternateName": [STATION, "Joppari"], "url": BASE_URL + "/",
        "telephone": COMPANY["phone_intl"], "email": COMPANY["email"], "image": BASE_URL + "/img/og.jpg",
        "description": f"{NAME} ({STATION}): kotiruoka- ja salaattibuffet joka päivä {BUFFET_HOURS}, pizzat, kahvila, Driver's-pikaruoka ja majoitus Pellossa.",
        "servesCuisine": ["Kotiruoka", "Pizza"], "priceRange": "€", "acceptsReservations": True,
        "hasMenu": BASE_URL + "/pizzat/",
        "address": {"@type": "PostalAddress", "streetAddress": COMPANY["street"], "postalCode": COMPANY["zip"],
                    "addressLocality": COMPANY["city"], "addressRegion": COMPANY["region"], "addressCountry": "FI"},
        "geo": {"@type": "GeoCoordinates", "latitude": COMPANY["geo"][0], "longitude": COMPANY["geo"][1]},
        "hasMap": MAPS, "sameAs": [COMPANY["facebook"], HS_PELLO],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]}
                                      for h in HOURS_SCHEMA],
    }


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE_URL + u} for i, (n, u) in enumerate(items)]}


def page(path, title, description, body, current="", schema=None, noindex=False, og="og.jpg", cls="", preload=None, extra_head=""):
    if not noindex and path != "/404.html":
        SITEMAP.append((path, TODAY))
    robots = '<meta name="robots" content="noindex">' if (noindex or DEMO) else '<meta name="robots" content="max-image-preview:large">'
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
                 for s in [org_schema()] + (schema or []))
    pre = ""
    if preload:
        ws = IMG_WS[preload]
        pre = (f'<link rel="preload" as="image" imagesrcset="{", ".join(f"/img/{preload}-{w}.webp {w}w" for w in ws)}" '
               f'imagesizes="(max-width:900px) 100vw, 60vw" fetchpriority="high">')
    html = f'''<!doctype html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{BASE_URL}{path if path != '/404.html' else '/'}">
{robots}
<meta name="theme-color" content="#00463c">
<meta property="og:type" content="website">
<meta property="og:locale" content="fi_FI">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{BASE_URL}{path}">
<meta property="og:image" content="{BASE_URL}/img/{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,opsz,wght@0,6..12,400..1000;1,6..12,700..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={VERSION}">
<script>document.documentElement.classList.add("js")</script>
{pre}{extra_head}
{ld}
</head>
<body class="{cls}">
<a class="skip" href="#main">Siirry sisältöön</a>
{header(current)}
<div class="notice" data-notice hidden><div class="wrap"><span data-notice-text></span></div></div>
<main id="main">
{body}
</main>
{footer()}
{demo_script()}<script src="/app.js?v={VERSION}" defer></script>
</body>
</html>
'''
    out = os.path.join(SITE, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(SITE, path.strip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)


def demo_script():
    """Demossa (Netlify/artifakti) ei ole palvelinta: lounaslista = esimerkkiviikko + selaimen localStorage."""
    if not DEMO:
        return ""
    return f'<script>window.JOPPARI_PREVIEW=1;window.JOPPARI_SAMPLE={json.dumps(sample_week(), ensure_ascii=False)};</script>\n'


def crumbs_html(items):
    parts = []
    for i, (n, u) in enumerate(items):
        if i:
            parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{u}">{esc(n)}</a>' if i < len(items) - 1 else f'<span>{esc(n)}</span>')
    return f'<nav class="crumbs" aria-label="Murupolku">{"".join(parts)}</nav>'


def page_hero(eyebrow, h1, lead, image, crumbs, alt="", ctas="", pos="center", ai=False):
    """HelmiSimpukka-tyylinen hero: pyöristetty kuvakortti, teksti kuvan päällä."""
    note = AI_NOTE if ai else ""
    return f'''<section class="phero"><div class="wrap">
  {crumbs_html(crumbs)}
  <div class="hcard">
    <div class="hcard-media">{img(image, alt, "(max-width:1300px) 100vw, 1240px", eager=True, style=f"object-position:{pos}")}</div>{note}
    <div class="hcard-txt">
      <span class="kicker">{esc(eyebrow)}</span>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      {ctas}
    </div>
  </div>
</div></section>'''


def sec_head(eyebrow, title, text="", center=False):
    right = f'<p>{text}</p>' if text else ""
    return f'<div class="sec-head{" center" if center else ""}"><div><span class="kicker">{eyebrow}</span><h2>{title}</h2></div>{right}</div>'


def lunch_card(cls="lunch-card", title_tag="h2"):
    """Päivän lounas – JS täyttää /api/lounas-datasta. Ilman dataa näkyy buffetin perustiedot."""
    return f'''<div class="{cls}" data-lunch="today">
  <span class="kicker" data-lunch-date>Joka päivä {BUFFET_HOURS}</span>
  <{title_tag}>Päivän lounas</{title_tag}>
  <p class="lc-sub">Kotiruoka- ja salaattibuffet <b>{BUFFET_HOURS}</b></p>
  <ul class="lc-list" data-lunch-list><li class="lc-empty">Päivän lounaslista päivitetään tähän. Kysy päivän ruoat puhelimitse: <a href="{TEL}">{COMPANY["phone"]}</a></li></ul>
  <div class="lc-foot"><span class="lc-price" data-lunch-price></span><a class="link" href="/lounas/">Koko viikon lista{icon("arrow")}</a></div>
  <p class="lc-demo" data-lunch-demo hidden>Esimerkkilista. Päivi päivittää oikean listan hallintasivulta.</p>
</div>'''


def visit_block():
    return f'''<section class="sec visit" id="kaynti"><div class="wrap visit-grid">
  <div class="visit-info rv">
    <span class="kicker">Tule käymään</span><h2>{STATION}, Pellontie 31</h2>
    <p class="muted">Kahvila-ravintola, pizzeria ja majoitus samalla pihalla asemalla, joten pysähtyminen matkan varrella on helppoa.</p>
    <div class="visit-cards">
      <div class="vcard">{icon("clock")}<div><small>Aukioloajat</small>{hours_list()}{open_badge()}</div></div>
      <div class="vcard">{icon("plate")}<div><small>Lounasbuffet</small><p><b>Joka päivä {BUFFET_HOURS}</b><br>Kotiruoka ja salaattipöytä</p></div></div>
      <div class="vcard">{icon("pin")}<div><small>Osoite</small><p><b>{COMPANY["street"]}</b><br>{COMPANY["zip"]} {COMPANY["city"]}</p>
        <a class="link" href="{MAPS}" target="_blank" rel="noopener">Reittiohjeet{icon("arrow")}</a></div></div>
      <div class="vcard">{icon("phone")}<div><small>Puhelin</small><p><a href="{TEL}"><b>{COMPANY["phone"]}</b></a><br><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></p></div></div>
    </div>
  </div>
  <div class="map rv"><iframe title="St1 Joppari kartalla" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <a class="map-fallback" href="{MAPS}" target="_blank" rel="noopener">{icon("pin")}Avaa kartta</a></div>
</div></section>'''


def contact_form(title="Lähetä viesti", sub="Kysy majoitustilannetta, ryhmävarausta tai mitä tahansa, niin vastaamme mahdollisimman pian.", aihe="",
                 room=False):
    aiheet = ["Majoitus", "Ryhmävaraus", "Muu asia"]
    opts = "".join(f'<option{" selected" if a == aihe else ""}>{a}</option>' for a in aiheet)
    fid = "m" if room else "y"
    room_fields = f'''<label class="f">Saapuminen<input name="saapuminen" type="date" id="{fid}-in"></label>
      <label class="f">Lähtö<input name="lahto" type="date" id="{fid}-out"></label>
      <label class="f">Henkilömäärä<select name="henkilot" id="{fid}-hlo"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>5</option><option>6–9 (molemmat huoneet)</option></select></label>
      <label class="f">Koira mukana?<select name="lemmikki" id="{fid}-dog"><option>Ei</option><option>Kyllä (siivousmaksu {DOG_FEE} €)</option></select></label>''' if room else ""
    lomake = "majoitus" if room else "yhteydenotto"
    aihe_field = "" if room else f'<label class="f">Aihe<select name="aihe" id="{fid}-aihe">{opts}</select></label>'
    return f'''<form class="panel form rv" name="{lomake}" method="POST" {form_attrs()} novalidate>
    {hidden_fields(lomake)}<input type="hidden" name="lomake" value="{lomake}">
    <h2>{title}</h2><p class="muted">{sub}</p>
    <p class="err" data-err>Täytä nimi ja joko puhelin tai sähköposti.</p>
    <div class="fgrid">
      <label class="f">Nimi *<input name="nimi" required autocomplete="name" id="{fid}-nimi"></label>
      {aihe_field}
      <label class="f">Puhelin<input name="puhelin" type="tel" autocomplete="tel" id="{fid}-tel"></label>
      <label class="f">Sähköposti<input name="email" type="email" autocomplete="email" id="{fid}-mail"></label>
      {room_fields}
      <label class="f full">Viesti<textarea name="viesti" rows="4" id="{fid}-msg" placeholder="{"Esim. lisävuode, aamiainen ryhmälle, saapumisaika" if room else "Kirjoita viestisi"}"></textarea></label>
    </div>
    <p class="check"><input type="checkbox" id="ts-{fid}" required><label for="ts-{fid}">Hyväksyn tietojeni käsittelyn <a class="link" href="/tietosuojaseloste/">tietosuojaselosteen</a> mukaisesti.</label></p>
    <button class="btn btn-primary" type="submit">Lähetä{icon("arrow")}</button>
  </form>'''


def gallery(items, cls="gal"):
    out = []
    for i, (name, cap) in enumerate(items):
        out.append(f'<a class="gi{" big" if i == 0 else ""}" href="{src_of(name)}" data-lb="{esc(cap)}">'
                   f'{img(name, cap, "(max-width:700px) 50vw, 33vw")}<span>{esc(cap)}</span></a>')
    return f'<div class="{cls}">{"".join(out)}</div>'


STATION_SERVICES = [
    ("fuel", "Polttoaineet", "1st 95 E10, Star 98 E5, 1st Diesel ja MPÖ Plus"),
    ("app", "St1 Way -mobiilitankkaus", "Tankkaa ja maksa sovelluksella, sovelluksessa myös edut"),
    ("coffee", "HelmiSimpukka Express", "Kahvit, leivonnaiset ja välipalat"),
    ("pizza", "Driver's", "Driver's-pikaruoka ja Driver's Burger"),
    ("drop", "Nestekaasu", "Nestekaasupullot asemalta"),
    ("paw", "Koirat tervetulleita", "Myös majoitukseen"),
]


# ---------------------------------------------------------------------------
# Sivut
# ---------------------------------------------------------------------------

def build_home():
    tiles = [
        ("ai-buffet", "Lounasbuffet", f"Kotiruoka- ja salaattibuffet joka päivä {BUFFET_HOURS}.", "/lounas/", "plate", True),
        ("ai-poropizza", "Pizzat", "18 pizzaa, pannupizzat ja talon oma poropizza. Myös gluteenittomana.", "/pizzat/", "pizza", True),
        ("huone-parvi", "Majoitus", "Kaksi huonetta 1–5 hengelle, oma sauna, aamiainen. Alkaen 80 €.", "/majoitus/", "bed", False),
    ]
    tiles_html = "".join(f'''<a class="tile rv" href="{u}" style="--d:{i * 90}ms">
      <div class="tile-img">{img(im, "", "(max-width:900px) 100vw, 33vw")}{AI_NOTE if ai else ""}</div>
      <div class="tile-b"><div><h3>{t}</h3><p>{d}</p></div><span class="go">{icon("arrow")}</span></div></a>'''
                         for i, (im, t, d, u, ic, ai) in enumerate(tiles))
    services = "".join(f'<li>{icon(ic)}<div><b>{t}</b><span>{d}</span></div></li>' for ic, t, d in STATION_SERVICES)
    jp = next(p for p in PIZZAS if p[1] == "Jopparin pizza")
    body = f'''
<section class="home-hero"><div class="wrap hh-grid">
  <div class="hcard hh-main">
    <div class="hcard-media">{img("asema-ilmakuva", f"{STATION} ja St1 Joppari ilmasta kuvattuna, taustalla Tornionjoen suvanto", "(max-width:900px) 100vw, 62vw", eager=True, style="object-position:42% 62%")}</div>
    <div class="hcard-txt">
      <span class="kicker">{STATION} · Kahvila · Ravintola · Majoitus</span>
      <h1>Parasta kotiruokaa, lämmöllä tarjottuna.</h1>
      <p class="lead">Kotiruoka- ja salaattibuffet joka päivä {BUFFET_HOURS}, Jopparin pizzat, kahvila ja Driver's. Yöksi kaksi huonetta omalla saunalla.</p>
      <div class="btns">{btn("Päivän lounas", "/lounas/", "btn btn-cream")}{btn("Pizzalista", "/pizzat/", "btn btn-ghost", "")}</div>
    </div>
  </div>
  {lunch_card("lunch-card hh-lunch", "h2")}
</div></section>

<section class="strip"><div class="wrap"><div class="strip-in">
  <div>{icon("clock")}{open_badge("open on-dark")}</div>
  <div>{icon("plate")}<span>Lounasbuffet joka päivä <b>{BUFFET_HOURS}</b></span></div>
  <div>{icon("phone")}<a href="{TEL}"><b>{COMPANY["phone"]}</b></a></div>
  <div>{icon("pin")}<a href="{MAPS}" target="_blank" rel="noopener">{COMPANY["street"]}, {COMPANY["city"]}</a></div>
</div></div></section>

<section class="sec"><div class="wrap">
  {sec_head("Meiltä", "Lounas, pizzat ja yöpyminen", f"55 asiakaspaikkaa, joten kerralla mahtuu vaikka linja-autollinen.")}
  <div class="tiles">{tiles_html}</div>
</div></section>

<section class="sec cream welcome"><div class="wrap welcome-grid">
  <figure class="welcome-img rv">{img("paivi", "Päivi esittelee juuri koottua pizzaa Jopparin keittiössä", "(max-width:900px) 90vw, 460px")}
    <figcaption><b>Päivi</b> ja päivän ensimmäinen pizza</figcaption></figure>
  <div class="welcome-txt rv">
    <span class="kicker">Tervetuloa St1 Joppariin</span>
    <h2>Pysähdy syömään kuin kotona</h2>
    <p class="big">Joka päivä tarjolla maittava kotiruoka- ja salaattibuffet klo 11–16. Ruoka tehdään laadukkaista ja tuoreista raaka-aineista, ja sen tuntee maussa.</p>
    <p>Pizzan voit koota itse ja saat sen myös gluteenittomana. Kiireessä? Soita ja tilaa pizza etukäteen, niin nouto käy samantien.
       Asemalta saat myös HelmiSimpukka Expressin kahvilatuotteet ja Driver's-pikaruoat.</p>
    <ul class="ticks">
      <li>{icon("salad")}<span><b>Kotiruoka- ja salaattibuffet</b> joka päivä {BUFFET_HOURS}</span></li>
      <li>{icon("users")}<span><b>{COMPANY["seats"]} asiakaspaikkaa</b>, ryhmät ja linja-autot tervetulleita</span></li>
      <li>{icon("bag")}<span><b>Pizzat noutona:</b> <a class="link" href="{TEL}">{COMPANY["phone"]}</a></span></li>
    </ul>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="feature rv">
    <div class="feature-media">{img("ai-poropizza", "Jopparin pizza: savuporoa, kananmunaa ja aurajuustoa", "(max-width:900px) 100vw, 55vw")}{AI_NOTE}</div>
    <div class="feature-txt">
      <span class="kicker">Talon oma</span>
      <h2>Jopparin pizza</h2>
      <p class="lead">Savuporoa, kananmunaa ja aurajuustoa. Lapin makuja pizzapohjalla.</p>
      <div class="price-row"><div><small>Normaali</small><b>{jp[4]} €</b></div><div><small>Perhe</small><b>{jp[5]} €</b></div></div>
      <div class="btns">{btn("Koko pizzalista", "/pizzat/", "btn btn-cream")}{btn_call("Tilaa noutoon", "btn btn-ghost")}</div>
    </div>
  </div>
</div></section>

<section class="sec cream" id="asema"><div class="wrap station">
  <div class="station-txt rv">
    <span class="kicker">{STATION}</span>
    <h2>Asema, kahvila ja ravintola samassa paikassa</h2>
    <p>St1 Joppari on {STATION} -aseman kahvila-ravintola. Asemalla toimivat myös <b>HelmiSimpukka Express</b> ja <b>Driver's</b>, joten kahvit, välipalat ja
       Driver's-pikaruoat saat samalla pysähdyksellä. Tankkaa ja maksa kätevästi St1 Way -sovelluksella.</p>
    <div class="btns">{btn("Driver's-ruokalista ja edut", HS_PELLO, "btn btn-red")}{btn("St1 Way ja kortit", "https://www.st1.fi/kortit", "btn btn-line", "")}</div>
    <img class="hs-logo" src="/img/helmisimpukka-express-logo.png" alt="HelmiSimpukka Express" width="306" height="160" loading="lazy">
  </div>
  <ul class="services rv">{services}</ul>
</div></section>

<section class="sec"><div class="wrap stay-grid">
  <div class="stay-imgs rv">
    <a class="si si1" href="/majoitus/">{img("huone-parvi", "Jopparin majoitushuone parvineen", "(max-width:900px) 70vw, 420px")}</a>
    <a class="si si2" href="/majoitus/">{img("sauna", "Huoneen oma sauna", "(max-width:900px) 40vw, 260px")}</a>
    <a class="si si3" href="/majoitus/">{img("huone-oleskelu", "Oleskelunurkkaus", "(max-width:900px) 40vw, 260px")}</a>
  </div>
  <div class="rv">
    <span class="kicker">Majoitus Pellossa</span>
    <h2>Jopparin majoitus</h2>
    <p>Kaksi tilavaa ja viihtyisää huonetta, neljän ja viiden hengen, yhteensä yhdeksälle, ja lisävuoteita saa tarvittaessa.
       Huoneissa on oma sauna, suihku, WC ja minikeittiö. Hintaan sisältyy aamiainen. Koirat ovat tervetulleita.</p>
    <div class="stay-price"><small>Huone alkaen</small><b>80 €</b><span>/ yö, aamiainen sisältyy</span></div>
    <div class="btns">{btn("Huoneet ja hinnat", "/majoitus/")}{btn("Kysy vapaita huoneita", "/majoitus/#tiedustelu", "btn btn-line", "")}</div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="groups rv">
    <div class="groups-media">{img("ai-tornionjoki", "Talvinen Tornionjokilaakso ja revontulet", "100vw", style="object-position:60% 50%")}</div>{AI_NOTE}
    <div class="groups-in">
      <span class="kicker">{icon("bus")}Ryhmät ja linja-autot</span>
      <h2>{COMPANY["seats"]} paikkaa, koko bussi syö kerralla</h2>
      <p class="lead">Matkaryhmä, joukkue tai työporukka? Sovi ryhmän ruokailu etukäteen puhelimitse.</p>
      <div class="btns">{btn_call("Soita ja sovi")}{btn("Lähetä ryhmävaraus", "/yhteystiedot/?aihe=Ryhmävaraus#viesti", "btn btn-ghost", "")}</div>
    </div>
  </div>
  <div class="en-card rv" id="english" lang="en">
    <div><span class="kicker">{icon("globe")}In English · På svenska</span>
    <h3>Welcome to St1 Joppari!</h3></div>
    <p>Café, restaurant, pizzeria and rooms at the St1 Pello station in Lapland. Home-style lunch and salad buffet every day 11–16, 18 pizzas including our
       reindeer pizza, and two rooms with private sauna, breakfast included. <span lang="sv"><b>Välkommen!</b> Pizzalistan finns även på svenska.</span></p>
    <a class="link" href="/pizzat/">Pizza menu / Pizzalista{icon("arrow")}</a>
  </div>
</div></section>

{visit_block()}
'''
    page("/", f"{NAME}: lounas, pizzat ja majoitus | {STATION}",
         f"{NAME} ({STATION}): kotiruoka- ja salaattibuffet joka päivä {BUFFET_HOURS}, Jopparin pizzat, HelmiSimpukka Express, Driver's ja majoitus omalla saunalla. Pellontie 31, Pello.",
         body, current="/", cls="home", preload="asema-ilmakuva")


def pizza_card(p):
    n, name, fi, sv, norm, fam = p
    tags = PIZZA_TAGS.get(name, [])
    star = '<span class="badge">Talon oma</span>' if "talon" in tags else ""
    veg = '<span class="tag veg">Kasvis</span>' if name == "Vegetariana" else ""
    hot = f'<span class="tag hot">{icon("flame")}Tulinen</span>' if "tulinen" in tags else ""
    return f'''<li class="pz{" pz-star" if "talon" in tags else ""}" data-tags="{" ".join(tags)}">
  <span class="pz-n">{n}</span>
  <div class="pz-b"><h3>{esc(name)}{star}{veg}{hot}</h3><p>{esc(fi)}</p><p class="sv" lang="sv">{esc(sv)}</p></div>
  <div class="pz-p"><span><small>norm.</small>{norm} €</span><span><small>perhe</small>{fam} €</span></div>
</li>'''


def build_pizzat():
    filters = [("kaikki", "Kaikki"), ("talon", "Talon oma"), ("liha", "Liha"), ("kala", "Kala & äyriäiset"), ("kasvis", "Kasvis"), ("tulinen", "Tulinen")]
    fbtns = "".join(f'<button type="button" data-f="{k}"{" class=on" if k == "kaikki" else ""}>{t}</button>' for k, t in filters)
    cards = "".join(pizza_card(p) for p in PIZZAS)
    pans = "".join(f'<li><div><b>{esc(fi)}</b><span lang="sv">{esc(sv)}</span></div><em>{pr} €</em></li>' for fi, sv, pr in PAN_PIZZAS)
    lunch = "".join(f'<li><div><b>{esc(fi)}</b><span lang="sv">{esc(sv)}</span></div><em>{pr} €</em></li>' for fi, sv, pr in LUNCH_PIZZA)
    ctas = f'<div class="btns">{btn_call("Tilaa: " + COMPANY["phone"])}{btn("Lounaspizza", "#lounas", "btn btn-ghost", "")}</div>'
    body = f'''
{page_hero("Jopparin pizza · Pizzor", "Pizzat tuoreista raaka-aineista", "Valitse listalta tai kokoa oma. Saat pizzan myös <b>gluteenittomana</b>. Soita ja tilaa etukäteen, niin voit noutaa sen samantien.",
           "ai-poropizza", [("Etusivu", "/"), ("Pizzat", "/pizzat/")], "Jopparin poropizza", ctas, "50% 60%", ai=True)}

<section class="sec menu-sec"><div class="wrap menu-grid">
  <div class="menu-main">
    <div class="menu-top">
      <h2>Pizzat <span lang="sv">/ Pizzor</span></h2>
      <div class="filters" role="group" aria-label="Suodata pizzoja">{fbtns}</div>
      <label class="sv-toggle"><input type="checkbox" data-sv checked id="sv-toggle"> Näytä ruotsiksi / på svenska</label>
    </div>
    <ul class="pizzas" data-pizzas>{cards}</ul>
    <p class="empty" data-empty hidden>Ei pizzoja tällä valinnalla.</p>
  </div>
  <aside class="menu-side">
    <div class="side-card lunch" id="lounas">
      <span class="kicker">Lounas · Lunch</span>
      <h3>Lounastarjous {LUNCH_HOURS}</h3>
      <p class="muted" lang="sv">Lunch vardagar kl. 11–14</p>
      <ul class="plist">{lunch}</ul>
    </div>
    <div class="side-card">
      <span class="kicker">Lisätäytteet · Extra fyllning</span>
      <p>{esc(TOPPINGS)}.</p><p class="sv muted" lang="sv">{esc(TOPPINGS_SV)}.</p>
      <ul class="plist"><li><div><b>Lisätäyte</b></div><em>{TOPPING_PRICE[0]} / {TOPPING_PRICE[1]} €</em></li>
        <li><div><b>Valkosipuli</b><span lang="sv">Vitlök</span></div><em>{GARLIC_PRICE[0]} / {GARLIC_PRICE[1]} €</em></li></ul>
      <p class="note">norm. / perhe · familje</p>
    </div>
    <div class="side-card">
      <span class="kicker">Pannupizzat · Pannpizzor</span>
      <ul class="plist">{pans}</ul>
    </div>
    <div class="side-card gf">{icon("wheat")}<div><b>Gluteeniton pohja</b><p>Pizzat saa myös gluteenittomana, kun kerrot siitä tilatessa.</p></div></div>
  </aside>
</div></section>

<section class="sec cream"><div class="wrap order-band rv">
  <figure>{img("paivi", "Päivi ja valmis pizza", "(max-width:900px) 60vw, 320px", style="object-position:50% 30%")}</figure>
  <div><span class="kicker">Nouto</span><h2>Soita ja tilaa, niin pizza odottaa valmiina</h2>
  <p class="muted">Tilaa puhelimitse etukäteen, niin voit noutaa pizzan samantien. Isommat ryhmätilaukset kannattaa sopia hyvissä ajoin.</p>
  <div class="btns">{btn_call(cls="btn btn-primary")}{btn("Yhteystiedot", "/yhteystiedot/", "btn btn-line", "")}</div></div>
</div></section>
'''
    menu_schema = {"@context": "https://schema.org", "@type": "Menu", "name": "Jopparin pizzalista", "url": BASE_URL + "/pizzat/",
                   "hasMenuSection": [{"@type": "MenuSection", "name": "Pizzat", "hasMenuItem": [
                       {"@type": "MenuItem", "name": p[1], "description": p[2],
                        "offers": [{"@type": "Offer", "price": p[4].replace(",", "."), "priceCurrency": "EUR", "name": "Normaali"},
                                   {"@type": "Offer", "price": p[5].replace(",", "."), "priceCurrency": "EUR", "name": "Perhe"}]} for p in PIZZAS]}]}
    page("/pizzat/", f"Pizzat: Jopparin pizzalista | {NAME}",
         "Jopparin pizzalista: 18 pizzaa, pannupizzat ja talon oma poropizza. Myös gluteenittomana. Lounaspizza arkisin 11–14. Tilaa noutoon: 016 512 771.",
         body, current="/pizzat/", schema=[menu_schema, breadcrumb([("Etusivu", "/"), ("Pizzat", "/pizzat/")])], preload="ai-poropizza")


def build_lounas():
    ctas = f'<div class="btns">{btn("Viikon lista", "#viikko", "btn btn-cream")}{btn_call(cls="btn btn-ghost")}</div>'
    body = f'''
{page_hero("Lounas joka päivä", f"Kotiruoka- ja salaattibuffet {BUFFET_HOURS}", "Maittava kotiruoka ja raikas salaattipöytä joka päivä, myös viikonloppuisin.",
           "ai-buffet", [("Etusivu", "/"), ("Lounas", "/lounas/")], "Kotiruokabuffet: lihapullat, perunat ja laatikkoruoka", ctas, "50% 60%", ai=True)}

<section class="sec" id="viikko"><div class="wrap week-grid">
  <div class="week rv" data-lunch="week">
    <div class="week-head"><div><span class="kicker" data-week-label>Viikon lounaslista</span><h2>Lounaslista</h2></div>
      <p class="lc-price big" data-lunch-price></p></div>
    <div class="week-tabs" data-week-tabs role="tablist" aria-label="Viikonpäivät"></div>
    <div class="week-days" data-week-days>
      <p class="lc-empty">Viikon lounaslista päivitetään tähän. Buffet on tarjolla joka päivä {BUFFET_HOURS}. Kysy päivän ruoat: <a href="{TEL}">{COMPANY["phone"]}</a></p>
    </div>
    <p class="lc-note" data-lunch-note hidden></p>
    <p class="lc-demo" data-lunch-demo hidden>Esimerkkilista. Päivi päivittää oikean listan hallintasivulta.</p>
  </div>
  <aside class="week-side">
    <div class="side-card buffet-card rv">{img("ai-salaatti", "Salaattipöytä", "(max-width:900px) 100vw, 380px")}{AI_NOTE}
      <div><h3>Buffetissa aina</h3><ul class="checks"><li>{icon("check")}Lämmin kotiruoka</li><li>{icon("check")}Salaattipöytä</li>
        <li>{icon("check")}Joka päivä {BUFFET_HOURS}</li></ul></div></div>
    <div class="side-card lunch rv"><span class="kicker">Lounaspizza</span><h3>{LUNCH_HOURS.capitalize()}</h3>
      <p>Normaalipizza 2–4 täytteellä ja 0,4 l juoma.</p>
      <div class="price-row dark"><div><small>2 täyt.</small><b>{LUNCH_PIZZA[0][2]} €</b></div><div><small>3 täyt.</small><b>{LUNCH_PIZZA[1][2]} €</b></div><div><small>4 täyt.</small><b>{LUNCH_PIZZA[2][2]} €</b></div></div>
      <a class="link" href="/pizzat/">Pizzalista{icon("arrow")}</a></div>
  </aside>
</div></section>

<section class="sec cream"><div class="wrap">
  {sec_head("Asemalla myös", "Kahvila ja Driver's", "HelmiSimpukka Express ja Driver's toimivat samassa pihassa nopeaa pysähdystä varten.")}
  <div class="duo">
    <article class="duo-card rv">{img("ai-kahvi", "Kahvi ja pulla ikkunapöydässä", "(max-width:900px) 100vw, 50vw")}{AI_NOTE}
      <div><h3>HelmiSimpukka Express</h3><p>Kahvit, leivonnaiset ja välipalat arkisin jo kello seitsemästä, viikonloppuisin yhdeksästä.</p></div></article>
    <article class="duo-card drivers rv"><div class="drv-mark" aria-hidden="true">Driver's</div>
      <div><h3>Driver's-pikaruoka</h3><p>Hot dogit, lihikset ja Driver's Burger. Ruokalista ja ajankohtaiset edut HelmiSimpukan sivuilla.</p>
      {btn("Driver's-ruokalista", HS_PELLO, "btn btn-red btn-sm")}</div></article>
  </div>
</div></section>
{visit_block()}
'''
    page("/lounas/", f"Lounas: kotiruoka- ja salaattibuffet {BUFFET_HOURS} | {NAME}",
         f"{NAME}, {STATION}: kotiruoka- ja salaattibuffet joka päivä {BUFFET_HOURS}. Viikon lounaslista, lounaspizza arkisin 11–14, HelmiSimpukka Express ja Driver's.",
         body, current="/lounas/", schema=[breadcrumb([("Etusivu", "/"), ("Lounas", "/lounas/")])], preload="ai-buffet")


def build_majoitus():
    rows = "".join(f'<li><span>{n} {"henkilö" if n == 1 else "henkilöä"}</span><b>{p} €</b></li>' for n, p in ROOM_PRICES)
    feats = "".join(f'<li>{icon(ic)}<span>{t}</span></li>' for ic, t in ROOM_FEATURES)
    bft = "".join(f'<li><span>{d}</span><b>{t}</b></li>' for d, t in BREAKFAST_TIMES)
    doors = "".join(f'<li><span>{d}</span><b>{w}</b></li>' for d, w in DOORS)
    ctas = f'<div class="btns">{btn("Kysy vapaita huoneita", "#tiedustelu", "btn btn-cream")}{btn_call(cls="btn btn-ghost")}</div>'
    body = f'''
{page_hero("Majoitus Pellossa", "Jopparin majoitus", "Kaksi tilavaa ja viihtyisää huonetta omalla saunalla, ja aamiainen sisältyy hintaan. Koirat ovat myös tervetulleita.",
           "huone-parvi", [("Etusivu", "/"), ("Majoitus", "/majoitus/")], "Majoitushuone parvineen", ctas, "50% 55%")}

<section class="sec"><div class="wrap rooms-grid">
  <div class="rv">
    <span class="kicker">Huoneet</span>
    <h2>Tilaa yhdeksälle tai kahdelle</h2>
    <p class="big">Meiltä löytyy kaksi huonetta: toinen neljän ja toinen viiden hengen. Huoneita saa vuokrata myös 1–3 hengelle, ja lisävuoteita saa tarvittaessa.</p>
    <p>Kummassakin huoneessa on oma sauna, suihku ja WC sekä minikeittiö astioineen, joten ne sopivat niin työmatkalaiselle, perheelle kuin
       Lapin-reissun väliyöhön. Aamiainen sisältyy huonehintaan.</p>
    <ul class="feats">{feats}</ul>
    <div class="info-grid">
      <div class="info-card">{icon("coffee")}<div><h3>Aamiainen</h3><ul class="kv">{bft}</ul></div></div>
      <div class="info-card">{icon("door")}<div><h3>Ovien leveydet</h3><ul class="kv">{doors}</ul></div></div>
    </div>
  </div>
  <div class="price-card rv">
    <span class="kicker">Hinnat 2026</span>
    <h3>Huone / yö</h3>
    <ul class="prices">{rows}</ul>
    <ul class="prices small"><li><span>Lisävuode</span><b>{EXTRA_BED} €</b></li><li><span>Aamupala erikseen</span><b>{BREAKFAST_ONLY} €</b></li>
      <li><span>Koirista siivousmaksu</span><b>{DOG_FEE} €</b></li></ul>
    <p class="incl">{icon("check")}Hinnat sisältävät aamiaisen.</p>
    {btn("Kysy vapaita huoneita", "#tiedustelu", "btn btn-cream")}
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  {sec_head("Kuvia huoneista", "Katso, millaista meillä on", "Klikkaa kuvaa suurentaaksesi.")}
  {gallery(ROOM_GALLERY)}
</div></section>

<section class="sec" id="tiedustelu"><div class="wrap contact-grid">
  <div class="rv">
    <span class="kicker">Majoitustiedustelu</span>
    <h2>Kysy vapaita huoneita</h2>
    <p class="muted">Lähetä päivämäärät ja henkilömäärä, niin kerromme majoitustilanteen. Nopeimmin tavoitat meidät puhelimitse.</p>
    <div class="call-card">{icon("phone")}<div><small>Soita</small><a href="{TEL}">{COMPANY["phone"]}</a><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></div></div>
    <div class="call-card">{icon("clock")}<div><small>Ravintola auki</small>{hours_list()}</div></div>
  </div>
  {contact_form("Majoitustiedustelu", "Täytä tiedot, niin vastaamme sähköpostilla tai puhelimitse.", room=True)}
</div></section>
'''
    lodging = {"@context": "https://schema.org", "@type": "LodgingBusiness", "name": "Jopparin majoitus, St1 Joppari", "url": BASE_URL + "/majoitus/",
               "telephone": COMPANY["phone_intl"], "image": BASE_URL + src_of("huone-parvi"),
               "address": {"@type": "PostalAddress", "streetAddress": COMPANY["street"], "postalCode": COMPANY["zip"], "addressLocality": COMPANY["city"], "addressCountry": "FI"},
               "priceRange": "80–185 €", "petsAllowed": True,
               "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": t, "value": True} for _, t in ROOM_FEATURES]}
    page("/majoitus/", f"Majoitus Pellossa: huoneet omalla saunalla | {NAME}",
         "Majoitus Pellossa: kaksi huonetta 1–5 hengelle (yht. 9 + lisävuoteet), oma sauna, minikeittiö ja aamiainen. Alkaen 80 €/yö. Koirat tervetulleita.",
         body, current="/majoitus/", schema=[lodging, breadcrumb([("Etusivu", "/"), ("Majoitus", "/majoitus/")])], preload="huone-parvi")


def build_contact():
    body = f'''
<section class="sec top"><div class="wrap contact-grid">
  <div class="rv">
    {crumbs_html([("Etusivu", "/"), ("Yhteystiedot", "/yhteystiedot/")])}
    <span class="kicker">Yhteystiedot</span>
    <h1 class="h1-sm">{NAME}</h1>
    <p class="muted">{STATION}, {COMPANY["street"]}. Ryhmävaraukset, pizzatilaukset noutoon ja majoitus hoituvat nopeimmin puhelimitse.</p>
    <div class="call-card">{icon("phone")}<div><small>Puhelin</small><a href="{TEL}">{COMPANY["phone"]}</a><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></div></div>
    <div class="call-card">{icon("mail")}<div><small>Sähköposti</small><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a></div></div>
    <div class="call-card">{icon("pin")}<div><small>Osoite</small><a href="{MAPS}" target="_blank" rel="noopener">{STATION}<br>{COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}</a></div></div>
    <div class="call-card">{icon("clock")}<div><small>Aukioloajat</small>{hours_list()}{open_badge()}<p class="note">Lounasbuffet joka päivä {BUFFET_HOURS}</p></div></div>
  </div>
  <div id="viesti">{contact_form()}</div>
</div></section>
<section class="map-wide"><iframe title="St1 Joppari kartalla" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
  <a class="map-fallback" href="{MAPS}" target="_blank" rel="noopener">{icon("pin")}Avaa kartta</a></section>
'''
    page("/yhteystiedot/", f"Yhteystiedot ja aukioloajat | {NAME}",
         f"{NAME}, {STATION}, Pellontie 31, 95700 Pello. Puh. 016 512 771. Avoinna ma–pe 7–20, la–su 9–20. Lounasbuffet {BUFFET_HOURS}.",
         body, current="/yhteystiedot/", schema=[breadcrumb([("Etusivu", "/"), ("Yhteystiedot", "/yhteystiedot/")])])


def build_admin():
    """Lounaslistan hallinta – Päivi päivittää listan puhelimella tai koneella. Ei hakukoneisiin."""
    body = f'''
<section class="sec top admin"><div class="wrap admin-wrap">
  <div class="admin-login panel" data-admin-login>
    <span class="kicker">{icon("lock")}Hallinta</span>
    <h1 class="h1-sm">Lounaslistan päivitys</h1>
    <p class="muted">Kirjaudu salasanalla. Päivitetty lista näkyy heti etusivulla ja lounassivulla.</p>
    <form data-login-form>
      <label class="f">Salasana<input type="password" id="adm-pw" autocomplete="current-password" required></label>
      <p class="err" data-login-err>Väärä salasana. Yritä uudelleen.</p>
      <button class="btn btn-primary" type="submit">Kirjaudu{icon("arrow")}</button>
    </form>
    <p class="note" data-preview-note hidden>Esikatselu: mikä tahansa salasana käy, ja muutokset tallentuvat vain tähän selaimeen.</p>
  </div>

  <div class="admin-app" data-admin-app hidden>
    <div class="admin-head">
      <div><span class="kicker">{icon("edit")}Lounaslista</span><h1 class="h1-sm">Viikon lounas</h1></div>
      <div class="admin-week">
        <button type="button" class="btn btn-line btn-sm" data-week-prev aria-label="Edellinen viikko">{icon("left")}</button>
        <b data-week-title>Viikko</b>
        <button type="button" class="btn btn-line btn-sm" data-week-next aria-label="Seuraava viikko">{icon("right")}</button>
      </div>
    </div>
    <p class="muted">Kirjoita jokainen ruoka omalle rivilleen. Erikoisruokavaliot voi merkitä perään, esim. <code>Lihamureke ja ruskea kastike (L, G)</code>.
       Tyhjäksi jätetty päivä näyttää sivulla tekstin "kysy päivän ruoat puhelimitse".</p>
    <div class="admin-notice">
      <label class="f">Tiedote koko sivuston yläreunaan (jätä tyhjäksi, jos ei tiedotettavaa)<input id="adm-notice" maxlength="200" placeholder="Esim. Itsenäisyyspäivänä 6.12. avoinna klo 10–18"></label>
    </div>
    <div class="admin-meta">
      <label class="f">Buffetin hinta<input id="adm-price" placeholder="Esim. Lounasbuffet 13,90 €"></label>
      <label class="f">Lisätieto (näkyy listan alla)<input id="adm-note" placeholder="Esim. Hintaan sisältyy salaattipöytä, leipä, juoma ja kahvi"></label>
    </div>
    <div class="admin-days" data-admin-days></div>
    <div class="admin-bar">
      <button type="button" class="btn btn-line btn-sm" data-copy-prev>{icon("copy")}Kopioi edellinen viikko</button>
      <span class="admin-status" data-admin-status></span>
      <button type="button" class="btn btn-primary" data-admin-save>Tallenna ja julkaise{icon("check")}</button>
    </div>
    <p class="note">Tallennus julkaisee listan heti. <a class="link" href="/" target="_blank">Katso etusivu</a> · <button type="button" class="linkbtn" data-logout>Kirjaudu ulos</button></p>
  </div>
</div></section>
'''
    page("/hallinta/", f"Lounaslistan hallinta | {NAME}", "Lounaslistan päivitys.", body, noindex=True, cls="nohero admin-page")


def build_simple():
    tp = f'''<section class="sec top"><div class="wrap prose">{crumbs_html([("Etusivu", "/"), ("Tietosuojaseloste", "/tietosuojaseloste/")])}
<h1 class="h1-sm">Tietosuojaseloste</h1>
<h2>1. Rekisterinpitäjä</h2><p>{NAME} ({STATION}), {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}.</p>
<h2>2. Yhteyshenkilö</h2><p>Päivi, {COMPANY["phone"]}, {COMPANY["email"]}.</p>
<h2>3. Käyttötarkoitus</h2><p>Yhteydenotto- ja majoitustiedustelulomakkeilla lähetettyjä tietoja käytetään tiedusteluihin vastaamiseen sekä varausten hoitamiseen.</p>
<h2>4. Käsiteltävät tiedot</h2><p>Nimi, puhelinnumero, sähköpostiosoite, majoituksen päivämäärät ja henkilömäärä sekä viestin sisältö.</p>
<h2>5. Käsittelyn peruste</h2><p>Varauksen tai sopimuksen valmistelu, oikeutettu etu (asiakassuhde) sekä lakisääteiset velvoitteet (kirjanpito).</p>
<h2>6. Säilytysaika</h2><p>Tietoja säilytetään niin kauan kuin niitä tarvitaan tiedustelun ja varauksen hoitamiseen sekä lain edellyttämän ajan.</p>
<h2>7. Luovutukset</h2><p>Tietoja ei luovuteta kolmansille osapuolille markkinointiin. Sivuston ja sähköpostin palveluntarjoajat käsittelevät tietoja lukuumme.</p>
<h2 id="evasteet">8. Evästeet</h2><p>Sivusto ei käytä seuranta- tai markkinointievästeitä. Kartta ladataan Googlesta.</p>
<h2>9. Rekisteröidyn oikeudet</h2><p>Sinulla on oikeus tarkastaa, korjata ja pyytää poistamaan tietosi sekä vastustaa käsittelyä. Ota yhteyttä yllä olevaan yhteyshenkilöön. Voit myös tehdä valituksen tietosuojavaltuutetulle.</p></div></section>'''
    page("/tietosuojaseloste/", f"Tietosuojaseloste | {NAME}", "St1 Joppari, tietosuojaseloste: lomakkeiden tietojen käsittely, evästeet ja oikeutesi.",
         tp, cls="nohero")
    ok = f'''<section class="sec top"><div class="wrap narrow"><span class="kicker">Kiitos</span><h1 class="h1-sm">Kiitos viestistäsi!</h1>
<p class="big">Viestisi on vastaanotettu. Palaamme asiaan mahdollisimman pian. Kiireellisissä asioissa soita {COMPANY["phone"]}.</p>
<div class="btns">{btn("Päivän lounas", "/lounas/")}{btn_call(cls="btn btn-line")}</div></div></section>'''
    page("/kiitos/", f"Kiitos | {NAME}", "Kiitos yhteydenotostasi.", ok, noindex=True, cls="nohero")
    nf = f'''<section class="sec top"><div class="wrap narrow"><span class="kicker">404</span><h1 class="h1-sm">Sivua ei löytynyt</h1>
<p class="big">Sivusto on uudistunut, ja osa osoitteista on muuttunut.</p>
<div class="btns">{btn("Lounas", "/lounas/")}{btn("Pizzat", "/pizzat/", "btn btn-line", "")}{btn("Majoitus", "/majoitus/", "btn btn-line", "")}</div></div></section>'''
    page("/404.html", f"Sivua ei löytynyt | {NAME}", "Sivua ei löytynyt.", nf, noindex=True, cls="nohero")


# ---------------------------------------------------------------------------
# Esimerkkiviikko (vain esikatseluun – oikea lista tulee hallinnasta)
# ---------------------------------------------------------------------------

def sample_week():
    mon = date.fromisoformat(TODAY) - timedelta(days=date.fromisoformat(TODAY).weekday())
    menu = [
        ["Lihapullat ja ruskea kastike (L, G)", "Kasvissosekeitto (L, G, VE)", "Keitetyt perunat, puolukka"],
        ["Broileri-kermaperunat (L)", "Kalakeitto (L, G)", "Porkkanaraaste"],
        ["Makaronilaatikko (L)", "Hernekeitto (M, G)", "Punajuurisalaatti"],
        ["Uunilohi ja tillikastike (L, G)", "Lihakeitto (M, G)", "Pannukakku ja hillo"],
        ["Poronkäristys ja perunamuusi (L, G)", "Kanakeitto (L)", "Puolukkasurvos"],
        ["Kinkkukiusaus (L, G)", "Tomaattikeitto (VE)", "Kurkkusalaatti"],
        ["Paistetut muikut ja perunamuusi (L)", "Jauhelihakastike ja pasta (M)", "Mustikkakiisseli"],
    ]
    return {"week_start": mon.isoformat(), "price": "", "note": "",
            "days": {(mon + timedelta(days=i)).isoformat(): m for i, m in enumerate(menu)}, "sample": True}


# ---------------------------------------------------------------------------
# OG-kuva, favicon, sitemap
# ---------------------------------------------------------------------------

GREEN = (0, 70, 60)
CREAM = (243, 241, 209)


def font(size, wght=800):
    f = ImageFont.truetype(os.path.join(SRC, "fonts", "NunitoSans.ttf"), size)
    try:
        axes = f.get_variation_axes()
        vals = []
        for a in axes:
            n = a.get("name", b"")
            n = n.decode() if isinstance(n, bytes) else str(n)
            vals.append(wght if "eight" in n else a.get("default", a["minimum"]))
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def mark_png(size):
    """Favicon: vihreä pyöristetty neliö, kerman värinen J."""
    s = 4 * size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .22), fill=GREEN)
    f = font(int(s * .78), 900)
    bb = d.textbbox((0, 0), "J", font=f)
    d.text(((s - (bb[2] - bb[0])) / 2 - bb[0], (s - (bb[3] - bb[1])) / 2 - bb[1]), "J", font=f, fill=CREAM)
    return im.resize((size, size), Image.LANCZOS)


def og_image():
    bg = ImageOps.fit(Image.open(IMG_SRC["asema-ilmakuva"]).convert("RGB"), (1200, 630), Image.LANCZOS, centering=(.45, .6)).convert("RGBA")
    shade = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(1200):
        d.line([(x, 0), (x, 630)], fill=(0, 50, 43, int(240 * max(0.1, 1 - x / 900))))
    bg = Image.alpha_composite(bg, shade)
    lg = Image.open(os.path.join(SRC, "st1-logo.png")).convert("RGBA")
    lg.thumbnail((170, 80), Image.LANCZOS)
    bg.alpha_composite(lg, (70, 64))
    d = ImageDraw.Draw(bg)
    d.text((70 + lg.width + 18, 66), "Joppari", font=font(66, 900), fill=CREAM)
    d.text((72, 250), "Parasta kotiruokaa,", font=font(64, 900), fill=(255, 255, 255))
    d.text((72, 326), "lämmöllä tarjottuna.", font=font(64, 900), fill=CREAM)
    d.text((72, 470), f"Lounasbuffet joka päivä 11–16 · Pizzat · Majoitus", font=font(30, 700), fill=(255, 255, 255))
    d.text((72, 514), f"{STATION} · Pellontie 31 · {COMPANY['phone']}", font=font(26, 600), fill=(210, 225, 218))
    bg.convert("RGB").save(os.path.join(IMG_OUT, "og.jpg"), quality=86)


def build_assets():
    og_image()
    mark_png(64).save(os.path.join(SITE, "favicon.png"))
    mark_png(180).save(os.path.join(SITE, "apple-touch-icon.png"))
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(SITE, "style.css"))
    shutil.copy(os.path.join(SRC, "app.js"), os.path.join(SITE, "app.js"))
    with open(os.path.join(SITE, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n" if DEMO else f"User-agent: *\nAllow: /\nDisallow: /hallinta/\n\nSitemap: {BASE_URL}/sitemap.xml\n")
    with open(os.path.join(SITE, "sitemap.xml"), "w") as f:
        urls = "".join(f"<url><loc>{BASE_URL}{p}</loc><lastmod>{lm}</lastmod></url>" for p, lm in SITEMAP)
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')


def build():
    global VERSION
    VERSION = str(int(max(os.path.getmtime(os.path.join(SRC, f)) for f in ("style.css", "app.js"))))
    for f in os.listdir(SITE) if os.path.isdir(SITE) else []:
        if f != "img":
            p = os.path.join(SITE, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(SITE, exist_ok=True)
    build_images()
    build_home()
    build_lounas()
    build_pizzat()
    build_majoitus()
    build_contact()
    build_admin()
    build_simple()
    build_assets()
    with open(os.path.join(SITE, "redirects.json"), "w") as f:
        json.dump(REDIRECTS, f, ensure_ascii=False, indent=1)
    target = write_host_files(SITE, vastaanottaja=COMPANY["email"], domain=COMPANY["domain"], sivusto=NAME, redirects=REDIRECTS)
    print(f"Rakennettu {len(SITEMAP)} indeksoitavaa sivua → site/ ({target})")
    if "--preview" not in sys.argv:
        name = os.path.join(ROOT, "..", f"joppari-{target}.zip")
        with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
            for base, _, files in os.walk(SITE):
                for fn in files:
                    if fn.startswith("."):
                        continue
                    full = os.path.join(base, fn)
                    z.write(full, os.path.relpath(full, SITE))
        print("Zip:", os.path.abspath(name))


def build_artifact():
    """Esikatselu Claude-artifaktina: litteät sivut, suhteelliset polut, lomakkeet eivät lähetä mitään.
    Lounaslista: esimerkkiviikko + hallinta tallentaa selaimen localStorageen (ei palvelinta)."""
    pv = os.path.join(ROOT, "preview")
    if os.path.exists(pv):
        shutil.rmtree(pv)
    os.makedirs(os.path.join(pv, "img"))
    for f in ("style.css", "app.js", "favicon.png", "apple-touch-icon.png"):
        shutil.copy(os.path.join(SITE, f), os.path.join(pv, f))

    def flat(path):
        path = path.strip("/")
        return "index.html" if path == "" else path if path.endswith(".html") else path.replace("/", "-") + ".html"

    def fix(m):
        attr, path, frag = m.group(1), m.group(2), m.group(3) or ""
        if path.startswith(("img/", "style.css", "app.js", "favicon", "apple-touch")):
            return f'{attr}="{path}{frag}"'
        q = ""
        if "?" in path:
            path, q = path.split("?", 1)
            q = "?" + q
        return f'{attr}="{flat(path)}{q}{frag}"'

    pages = []
    for dp, _, fs in os.walk(SITE):
        for f in fs:
            if f.endswith(".html"):
                pages.append(os.path.relpath(os.path.join(dp, f), SITE))
    for rel in pages:
        h = open(os.path.join(SITE, rel), encoding="utf-8").read()
        h = re.sub(r'(href|src|srcset|action|imagesrcset)="/([^"#]*)(#[^"]*)?"', fix, h)
        h = re.sub(r'(\s|,)/img/', r'\1img/', h)
        h = re.sub(r'<form ([^>]*?)method="POST"[^>]*>', lambda m: f'<form {m.group(1)}data-preview="1" novalidate>', h)
        if rel == "index.html":  # pääsivu kääritään artifaktin runkoon; alasivut pysyvät täysinä HTML-dokumentteina
            h = re.sub(r'<!doctype html>\s*<html[^>]*>\s*<head>\s*', "", h)
            h = h.replace("</head>", "").replace("</body>", "").replace("</html>", "")
            h = re.sub(r'<body([^>]*)>', lambda m: f'<div id="__b"{m.group(1)}></div><script>document.body.className=document.getElementById("__b").className</script>', h)
        if rel == "index.html":
            h = re.sub(r"<title>[^<]*</title>", "<title>St1 Joppari</title>", h, count=1)
        h = re.sub(r'<img([^>]*?)src="img/([\w.-]+)-(\d+)\.webp"([^>]*?)fetchpriority="high"',
                   lambda m: f'<img{m.group(1)}src="img/{m.group(2)}-{max([w for w in IMG_WS[m.group(2)] if w <= 1600])}.webp"{m.group(4)}fetchpriority="high"', h)
        h = re.sub(r'\s(srcset|imagesrcset|sizes|imagesizes)="[^"]*"', "", h)
        h = re.sub(r'<link rel="preload" as="image"[^>]*>', "", h)
        h = re.sub(r'<iframe[^>]*></iframe>', "", h)  # artifakti ei salli upotuksia → pelkkä karttalinkki
        name = "index.html" if rel == "index.html" else ("404.html" if rel == "404.html" else flat(rel[:-len("index.html")]))
        open(os.path.join(pv, name), "w", encoding="utf-8").write(h)
    used = set()
    for f in os.listdir(pv):
        if f.endswith((".html", ".css", ".js")):
            used |= set(re.findall(r'img/([\w.-]+\.(?:webp|png|jpg))', open(os.path.join(pv, f), encoding="utf-8").read()))
    for u in used:
        if os.path.exists(os.path.join(SITE, "img", u)):
            shutil.copy(os.path.join(SITE, "img", u), os.path.join(pv, "img", u))
    n = sum(len(fs) for _, _, fs in os.walk(pv))
    print(f"ARTIFACT: {len(pages)} sivua, {len(used)} kuvaa, {n} tiedostoa -> {pv}")


if __name__ == "__main__":
    build()
    if "--artifact" in sys.argv:
        build_artifact()
