# -*- coding: utf-8 -*-
"""Staattisen sivuston generaattori – Kahvila-Ravintola St1 Joppari (joppari.fi), Pello.

    python3 build.py                    -> site/ NordicHostiin (Node, server.js) + ../joppari-nordichost.zip
    HOSTING=webhotelli python3 build.py -> tavallinen webhotelli (PHP-lomake + .htaccess)
    HOSTING=netlify python3 build.py --preview --artifact -> esikatselu Claude-artifaktina (preview/)

Tekstit ja listat: content.py. Tyylit: src/style.css. Toiminnot: src/app.js. Vaatii Pillow-kirjaston.
"""
import json
import os
import re
import shutil
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageOps

from content import (
    COMPANY, EXTRA_BED, GARLIC_PRICE, GRILL, HOURS, HOURS_JS, HOURS_SCHEMA, LUNCH_HOURS, LUNCH_PIZZA, NAV, PAN_PIZZAS, PIZZA_TAGS,
    PIZZAS, REDIRECTS, ROOM_FEATURES, ROOM_GALLERY, ROOM_PRICES, TOPPING_PRICE, TOPPINGS, TOPPINGS_SV,
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
MAPS = "https://www.google.com/maps/search/?api=1&query=Joppari+Pellontie+31+95700+Pello"
MAP_EMBED = "https://maps.google.com/maps?q=Pellontie+31,+95700+Pello&z=15&output=embed"
SITEMAP = []
VERSION = "1"
WIDTHS = [480, 800, 1200, 1600, 2000]
IMG_DIMS, IMG_WS = {}, {}
YEAR = 2026
TODAY = "2026-09-28"


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
    "burger": '<path d="M4 11a8 6 0 0 1 16 0z"/><path d="M3 14h18M5 17h14a2 2 0 0 1-2 3H7a2 2 0 0 1-2-3z"/>',
    "coffee": '<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 10.5h1.5a2.5 2.5 0 0 1 0 5H17M8 3v3M12 3v3"/>',
    "bed": '<path d="M3 19V6M3 15h18v4M21 15v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11" r="2"/>',
    "sauna": '<path d="M4 20h16M6 20V11l6-5 6 5v9"/><path d="M9.5 14c0-1 1-1.2 1-2.2M12.5 14c0-1 1-1.2 1-2.2"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "kitchen": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M4 9h16M8 6h.01M11 6h.01"/><circle cx="12" cy="15" r="3"/>',
    "fridge": '<rect x="6" y="2.5" width="12" height="19" rx="2"/><path d="M6 10h12M9 6v2M9 13v3"/>',
    "paw": '<circle cx="7" cy="10" r="1.8"/><circle cx="17" cy="10" r="1.8"/><circle cx="10" cy="6" r="1.8"/><circle cx="14" cy="6" r="1.8"/><path d="M12 12c-3 0-5 3.5-5 5.5 0 2 2 2.5 5 1.5 3 1 5 .5 5-1.5S15 12 12 12z"/>',
    "iron": '<path d="M3 17h17v-3a6 6 0 0 0-6-6H8"/><path d="M3 17c0-4 3-6 7-6M8 8V6"/>',
    "fuel": '<path d="M4 21V5a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16M3 21h13M4 10h11"/><path d="M15 8h2l2 2v8a1.5 1.5 0 0 0 3 0v-7l-3-3"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/>',
    "leaf": '<path d="M5 19c0-9 5-14 15-15-1 10-6 15-15 15z"/><path d="M5 19 13 11"/>',
    "wheat": '<path d="M12 21V8"/><path d="M12 12c-2.5 0-4-1.5-4-4 2.5 0 4 1.5 4 4zM12 12c2.5 0 4-1.5 4-4-2.5 0-4 1.5-4 4zM12 16c-2.5 0-4-1.5-4-4 2.5 0 4 1.5 4 4zM12 16c2.5 0 4-1.5 4-4-2.5 0-4 1.5-4 4zM12 8c-1.5-1-1.5-3 0-5 1.5 2 1.5 4 0 5z"/>',
    "fish": '<path d="M3 12c3-4 8-5 12-3l4-3v12l-4-3c-4 2-9 1-12-3z"/><circle cx="8" cy="11" r=".8"/>',
    "flame": '<path d="M12 21a6 6 0 0 0 6-6c0-4-3-6-4-10-2 2-2.5 4-2 6-1-.5-2-2-2-3.5C7.5 9.5 6 12 6 15a6 6 0 0 0 6 6z"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
    "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8.5a.5.5 0 0 1 .5-.5z"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "left": '<path d="m15 5-7 7 7 7"/>',
    "right": '<path d="m9 5 7 7-7 7"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "bag": '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# Logo: timantti-ikoni (haarukka + veitsi, vanhan logon aihe) + sanamerkki
MARK = ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><rect x="8.2" y="8.2" width="23.6" height="23.6" rx="6" transform="rotate(45 20 20)"/>'
        '<path d="M16 12.5v6.2a2 2 0 0 0 4 0v-6.2M18 12.5v15" /><path d="M24.2 27.5v-15c-1.8 1.2-2.6 3.6-2.6 6.4 0 1.6.9 2.4 2.6 2.4"/></svg>')


def logo(cls="brand"):
    return (f'<a class="{cls}" href="/" aria-label="{COMPANY["name"]}, etusivu">{MARK}'
            f'<span class="wm"><b>Joppari</b><small>Kahvila-ravintola · Pello</small></span></a>')


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
    return f'<a class="{cls}" href="{href}">{label}{icon(ic) if ic else ""}</a>'


def btn_call(label=None, cls="btn btn-ghost"):
    return f'<a class="{cls}" href="{TEL}">{icon("phone")}<span>{label or COMPANY["phone"]}</span></a>'


def open_badge(cls="open"):
    """Auki nyt / suljettu – JS päivittää; ilman JS:ää näkyy tämän päivän aukiolo."""
    return f'<span class="{cls}" data-open=\'{json.dumps(HOURS_JS)}\'><i></i><span>Ma–pe 7–20 · la–su 9–20</span></span>'


def header(current):
    links = "".join(f'<a href="{u}"{" aria-current=page" if current == u else ""}>{t}</a>' for t, u in NAV)
    mlinks = "".join(f'<a href="{u}">{t}{icon("arrow")}</a>' for t, u in [("Etusivu", "/")] + NAV)
    return f'''<header class="hdr">
  <div class="hdr-in">
    {logo()}
    <nav class="nav" aria-label="Päävalikko">{links}</nav>
    <div class="hdr-cta">{open_badge("open hdr-open")}<a class="btn btn-primary btn-sm hdr-tel" href="{TEL}">{icon("phone")}<span>{COMPANY["phone"]}</span></a></div>
    <button class="burger" aria-label="Valikko" aria-expanded="false"><span></span><span></span></button>
  </div>
  <nav class="mnav" aria-label="Mobiilivalikko">{mlinks}
    <div class="mnav-foot">{open_badge()}<p>{COMPANY["street"]}, {COMPANY["city"]}</p>{btn_call(cls="btn btn-primary")}</div></nav>
</header>'''


def hours_list(cls="hours"):
    rows = "".join(f'<li><span>{d}</span><b>{a}–{b}</b></li>' for d, a, b in HOURS)
    return f'<ul class="{cls}">{rows}</ul>'


def footer():
    demo = '<p class="demo-note">Sivustoehdotus – Äijä Group. Tämä on esikatseluversio.</p>' if DEMO else ""
    return f'''<footer class="ftr">
  <div class="wrap">
    <div class="ftr-top">
      <p class="ftr-big">Tervetuloa <em>Joppariin.</em></p>
      <div class="btns">{btn("Katso pizzalista", "/pizzat/")}{btn_call()}</div>
    </div>
    <div class="ftr-grid">
      <div class="ftr-brand">{logo("brand brand-ftr")}
        <p>Kahvila, ravintola, pizzeria ja majoitus St1-aseman yhteydessä Pellossa. 55 asiakaspaikkaa – kerralla mahtuu vaikka linja-autollinen.</p>
        <div class="some"><a href="{COMPANY["facebook"]}" target="_blank" rel="noopener" aria-label="Facebook">{icon("fb")}</a></div>
      </div>
      <div><h3>Aukioloajat</h3>{hours_list()}</div>
      <div><h3>Sivut</h3><ul><li><a href="/pizzat/">Pizzat</a></li><li><a href="/la-carte/">Grilli &amp; lounas</a></li>
        <li><a href="/majoitus/">Majoitus</a></li><li><a href="/yhteystiedot/">Yhteystiedot</a></li><li><a href="/#st1">St1-asema</a></li></ul></div>
      <div><h3>Yhteystiedot</h3><ul>
        <li><a href="{MAPS}" target="_blank" rel="noopener">{COMPANY["street"]}<br>{COMPANY["zip"]} {COMPANY["city"]}</a></li>
        <li><a href="{TEL}">{COMPANY["phone"]}</a></li>
        <li><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></li>
        <li><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a></li>
      </ul></div>
    </div>
    <div class="ftr-bottom"><span>© {YEAR} {COMPANY["name"]} · {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}</span>
      <span><a href="/tietosuojaseloste/">Tietosuojaseloste</a> · <a href="{COMPANY["travelpello"]}" target="_blank" rel="noopener">Travel Pello</a></span></div>
    {demo}
  </div>
</footer>
<div class="mbar" aria-label="Pikayhteys">{btn_call("Soita", "btn btn-line")}{btn("Pizzat", "/pizzat/", "btn btn-primary", "pizza")}</div>
<div class="lb" hidden><button class="lb-x" aria-label="Sulje">{icon("x")}</button><button class="lb-p" aria-label="Edellinen">{icon("left")}</button>
<figure><img alt=""><figcaption></figcaption></figure><button class="lb-n" aria-label="Seuraava">{icon("right")}</button></div>'''


def org_schema():
    return {
        "@context": "https://schema.org", "@type": ["Restaurant", "CafeOrCoffeeShop"], "@id": BASE_URL + "/#yritys",
        "name": COMPANY["name"], "alternateName": ["Joppari", "Kahvila-Ravintola Joppari"], "url": BASE_URL + "/",
        "telephone": COMPANY["phone_intl"], "email": COMPANY["email"], "image": BASE_URL + "/img/og.jpg",
        "logo": BASE_URL + "/img/logo-512.png",
        "description": "Kahvila-ravintola, pizzeria ja majoitus St1-aseman yhteydessä Pellossa. Lounas, pizzat, grilliruoat ja 55 asiakaspaikkaa.",
        "servesCuisine": ["Kotiruoka", "Pizza", "Hampurilaiset"], "priceRange": "€", "acceptsReservations": True,
        "hasMenu": BASE_URL + "/pizzat/", "foundingDate": COMPANY["founded"],
        "address": {"@type": "PostalAddress", "streetAddress": COMPANY["street"], "postalCode": COMPANY["zip"],
                    "addressLocality": COMPANY["city"], "addressRegion": COMPANY["region"], "addressCountry": "FI"},
        "geo": {"@type": "GeoCoordinates", "latitude": COMPANY["geo"][0], "longitude": COMPANY["geo"][1]},
        "hasMap": MAPS, "sameAs": [COMPANY["facebook"]],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]}
                                      for h in HOURS_SCHEMA],
    }


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE_URL + u} for i, (n, u) in enumerate(items)]}


def page(path, title, description, body, current="", schema=None, noindex=False, og="og.jpg", cls="", preload=None):
    if not noindex and path != "/404.html":
        SITEMAP.append((path, TODAY))
    robots = '<meta name="robots" content="noindex">' if (noindex or DEMO) else '<meta name="robots" content="max-image-preview:large">'
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
                 for s in [org_schema()] + (schema or []))
    pre = ""
    if preload:
        ws = IMG_WS[preload]
        pre = (f'<link rel="preload" as="image" imagesrcset="{", ".join(f"/img/{preload}-{w}.webp {w}w" for w in ws)}" '
               f'imagesizes="100vw" fetchpriority="high">')
    html = f'''<!doctype html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{BASE_URL}{path if path != '/404.html' else '/'}">
{robots}
<meta name="theme-color" content="#1c1512">
<meta property="og:type" content="website">
<meta property="og:locale" content="fi_FI">
<meta property="og:site_name" content="Joppari">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{BASE_URL}{path}">
<meta property="og:image" content="{BASE_URL}/img/{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500..800;1,9..144,600..800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={VERSION}">
{pre}
{ld}
</head>
<body class="{cls}">
<a class="skip" href="#main">Siirry sisältöön</a>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script src="/app.js?v={VERSION}" defer></script>
</body>
</html>
'''
    out = os.path.join(SITE, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(SITE, path.strip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)


def crumbs_html(items):
    parts = []
    for i, (n, u) in enumerate(items):
        if i:
            parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{u}">{esc(n)}</a>' if i < len(items) - 1 else f'<span>{esc(n)}</span>')
    return f'<nav class="crumbs" aria-label="Murupolku">{"".join(parts)}</nav>'


def page_hero(eyebrow, h1, lead, image, crumbs, alt="", ctas="", pos="center", ai=False):
    note = AI_NOTE if ai else ""
    return f'''<section class="phero">
  <div class="hero-media">{img(image, alt, eager=True, style=f"object-position:{pos}")}</div>{note}
  <div class="wrap">
    {crumbs_html(crumbs)}
    <span class="eyebrow light">{esc(eyebrow)}</span>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {ctas}
  </div>
</section>'''


def sec_head(eyebrow, title, text="", center=False):
    right = f'<p>{text}</p>' if text else ""
    return f'<div class="sec-head{" center" if center else ""}"><div><span class="eyebrow">{eyebrow}</span><h2>{title}</h2></div>{right}</div>'


def visit_block():
    return f'''<section class="sec visit" id="kaynti"><div class="wrap visit-grid">
  <div class="visit-info rv">
    <span class="eyebrow">Tule käymään</span><h2>Pellon keskustassa, St1-aseman yhteydessä</h2>
    <p class="muted">Pellontie 31 – iso piha, helppo pysähtyä matkan varrella.</p>
    <div class="visit-cards">
      <div class="vcard">{icon("clock")}<div><small>Aukioloajat</small>{hours_list()}{open_badge()}</div></div>
      <div class="vcard">{icon("pin")}<div><small>Osoite</small><p><b>{COMPANY["street"]}</b><br>{COMPANY["zip"]} {COMPANY["city"]}</p>
        <a class="link" href="{MAPS}" target="_blank" rel="noopener">Reittiohjeet{icon("arrow")}</a></div></div>
      <div class="vcard">{icon("phone")}<div><small>Puhelin</small><p><a href="{TEL}"><b>{COMPANY["phone"]}</b></a><br><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></p></div></div>
      <div class="vcard">{icon("mail")}<div><small>Sähköposti</small><p><a href="mailto:{COMPANY["email"]}"><b>{COMPANY["email"]}</b></a></p></div></div>
    </div>
  </div>
  <div class="map rv"><iframe title="Jopparin sijainti kartalla" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <a class="map-fallback" href="{MAPS}" target="_blank" rel="noopener">{icon("pin")}Avaa kartta</a></div>
</div></section>'''


def contact_form(title="Lähetä viesti", sub="Kysy majoitustilannetta, ryhmävarausta tai mitä tahansa – vastaamme mahdollisimman pian.", aihe="",
                 room=False):
    aiheet = ["Majoitus", "Ryhmävaraus", "Muu asia"]
    opts = "".join(f'<option{" selected" if a == aihe else ""}>{a}</option>' for a in aiheet)
    fid = "m" if room else "y"
    room_fields = f'''<label class="f">Saapuminen<input name="saapuminen" type="date"></label>
      <label class="f">Lähtö<input name="lahto" type="date"></label>
      <label class="f">Henkilömäärä<select name="henkilot"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>5</option><option>6–9 (molemmat huoneet)</option></select></label>
      <label class="f">Lemmikki mukana?<select name="lemmikki"><option>Ei</option><option>Kyllä</option></select></label>''' if room else ""
    lomake = "majoitus" if room else "yhteydenotto"
    aihe_field = "" if room else f'<label class="f">Aihe<select name="aihe">{opts}</select></label>'
    return f'''<form class="panel form rv" name="{lomake}" method="POST" {form_attrs()} novalidate>
    {hidden_fields(lomake)}<input type="hidden" name="lomake" value="{lomake}">
    <h2>{title}</h2><p class="muted">{sub}</p>
    <p class="err" data-err>Täytä nimi ja joko puhelin tai sähköposti.</p>
    <div class="fgrid">
      <label class="f">Nimi *<input name="nimi" required autocomplete="name"></label>
      {aihe_field}
      <label class="f">Puhelin<input name="puhelin" type="tel" autocomplete="tel"></label>
      <label class="f">Sähköposti<input name="email" type="email" autocomplete="email"></label>
      {room_fields}
      <label class="f full">Viesti<textarea name="viesti" rows="4" placeholder="{"Esim. lisävuode, aamiainen ryhmälle, saapumisaika" if room else "Kirjoita viestisi"}"></textarea></label>
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


# ---------------------------------------------------------------------------
# Sivut
# ---------------------------------------------------------------------------

def build_home():
    tiles = [
        ("ai-poropizza", "Pizzat", "18 klassikkoa, pannupizzat ja talon oma poropizza. Myös gluteenittomana.", "/pizzat/", "pizza", True),
        ("ai-hampurilainen", "Grilli & lounas", "Hampurilaisateriat, lounaspizzat arkisin 11–14, paniinit ja pikkusuolaiset.", "/la-carte/", "burger", True),
        ("huone-parvi", "Majoitus", "Kaksi viihtyisää huonetta 1–5 hengelle, oma sauna ja aamiainen. Alkaen 75 €.", "/majoitus/", "bed", False),
    ]
    tiles_html = "".join(f'''<a class="tile rv" href="{u}" style="--d:{i * 90}ms">
      <div class="tile-img">{img(im, "", "(max-width:900px) 100vw, 33vw")}{AI_NOTE if ai else ""}</div>
      <div class="tile-b"><span class="ti">{icon(ic)}</span><div><h3>{t}</h3><p>{d}</p></div>{icon("arrow", "ic go")}</div></a>'''
                         for i, (im, t, d, u, ic, ai) in enumerate(tiles))
    offers = [
        ("lohi", "À la carte", "Kotiruokaa lautaselta – lämpimästi tarjottuna.", False),
        ("ai-keitto", "Lounas", "Arkipäivän lämmin ateria. Lounaspizzat arkisin klo 11–14.", True),
        ("ai-paniini", "Paniinit & suolaiset", "Nopea välipala matkan varrelle.", True),
        ("ai-kahvi", "Kahvila", "Kupillinen kahvia ja jotain makeaa kaveriksi.", True),
    ]
    offers_html = "".join(f'''<figure class="offer rv" style="--d:{i * 80}ms">{img(im, t, "(max-width:700px) 50vw, 25vw")}{AI_NOTE if ai else ""}
      <figcaption><b>{t}</b><span>{d}</span></figcaption></figure>''' for i, (im, t, d, ai) in enumerate(offers))
    jp = next(p for p in PIZZAS if p[1] == "Jopparin pizza")
    body = f'''
<section class="hero">
  <div class="hero-media">{img("asema-ilmakuva", "Joppari ja St1-asema Pellossa ilmasta kuvattuna, taustalla Tornionjoen suvanto", eager=True, style="object-position:40% 60%")}</div>
  <div class="wrap hero-in">
    <span class="eyebrow light">Kahvila · Ravintola · Pizzeria · Majoitus</span>
    <h1>Parasta kotiruokaa <em>lämmöllä tarjottuna.</em></h1>
    <p class="lead">Lounas, pizzat, grilliruoat ja kahvit Pellon keskustassa St1-aseman yhteydessä – ja yöksi kaksi viihtyisää huonetta omalla saunalla.</p>
    <div class="btns">{btn("Katso pizzalista", "/pizzat/")}{btn_call()}</div>
  </div>
  <div class="hero-card rv">
    {open_badge()}
    {hours_list()}
    <a href="{MAPS}" target="_blank" rel="noopener">{icon("pin")}{COMPANY["street"]}, {COMPANY["city"]}</a>
  </div>
</section>

<section class="tiles-sec"><div class="wrap tiles">{tiles_html}</div></section>

<section class="sec welcome"><div class="wrap welcome-grid">
  <figure class="welcome-img rv">{img("paivi", "Päivi esittelee juuri koottua pizzaa Jopparin keittiössä", "(max-width:900px) 90vw, 480px")}
    <figcaption><b>Päivi</b> ja päivän ensimmäinen pizza</figcaption></figure>
  <div class="welcome-txt rv">
    <span class="eyebrow">Tervetuloa Joppariin</span>
    <h2>Pysähdy syömään kuin kotona</h2>
    <p class="big">Jopparissa ruoka tehdään laadukkaista ja tuoreista raaka-aineista – sen tuntee maussa.</p>
    <p>Meiltä saat à la carte -annokset, lounaan, pizzat, paniinit ja muut pikkusuolaiset. Pizzan voit koota itse ja saat sen myös gluteenittomana.
       Kiireessä? Soita ja tilaa etukäteen, niin nouto käy samantien.</p>
    <ul class="ticks">
      <li>{icon("users")}<span><b>{COMPANY["seats"]} asiakaspaikkaa</b> – kerralla mahtuu vaikka linja-autollinen</span></li>
      <li>{icon("wheat")}<span><b>Gluteeniton pizzapohja</b> saatavana</span></li>
      <li>{icon("bag")}<span><b>Tilaa etukäteen</b> ja nouda heti: <a class="link" href="{TEL}">{COMPANY["phone"]}</a></span></li>
    </ul>
  </div>
</div></section>

<section class="feature"><div class="feature-media">{img("ai-poropizza", "Jopparin pizza: savuporoa, kananmunaa ja aurajuustoa", "(max-width:900px) 100vw, 55vw")}{AI_NOTE}</div>
  <div class="wrap feature-in"><div class="feature-txt rv">
    <span class="eyebrow light">Talon oma</span>
    <h2>Jopparin pizza</h2>
    <p class="lead">Savuporoa, kananmunaa ja aurajuustoa. Jopparin erikoisuus – Lapin makuja pizzapohjalla.</p>
    <div class="price-row"><div><small>Normaali</small><b>{jp[4]} €</b></div><div><small>Perhe</small><b>{jp[5]} €</b></div></div>
    <div class="btns">{btn("Koko pizzalista", "/pizzat/")}{btn_call("Tilaa noudettavaksi")}</div>
  </div></div>
</section>

<section class="sec"><div class="wrap">
  {sec_head("Meiltä voit tilata", "Aamukahvista iltapalaan", "Aukeamme arkisin jo seitsemältä ja olemme auki iltakahdeksaan joka päivä.")}
  <div class="offers">{offers_html}</div>
</div></section>

<section class="sec tint stay"><div class="wrap stay-grid">
  <div class="stay-imgs rv">
    <a class="si si1" href="/majoitus/">{img("huone-parvi", "Jopparin majoitushuone parvineen", "(max-width:900px) 70vw, 420px")}</a>
    <a class="si si2" href="/majoitus/">{img("sauna", "Huoneen oma sauna", "(max-width:900px) 40vw, 260px")}</a>
    <a class="si si3" href="/majoitus/">{img("huone-oleskelu", "Oleskelunurkkaus", "(max-width:900px) 40vw, 260px")}</a>
  </div>
  <div class="rv">
    <span class="eyebrow">Majoitus Pellossa</span>
    <h2>Jopparin makuukammarit</h2>
    <p>Kaksi tilavaa ja viihtyisää huonetta – neljän ja viiden hengen – yhteensä yhdeksälle, ja lisävuoteita saa tarvittaessa.
       Huoneissa on oma sauna, suihku, WC ja minikeittiö. Aamiainen sisältyy hintaan, ja ryhmille aamiaisen saa tilauksesta.</p>
    <div class="stay-price"><small>Huone alkaen</small><b>75 €</b><span>/ yö, aamiainen sisältyy</span></div>
    <div class="chips">{"".join(f'<span>{icon(ic)}{t}</span>' for ic, t in ROOM_FEATURES[:6])}</div>
    <div class="btns">{btn("Huoneet ja hinnat", "/majoitus/")}{btn("Kysy vapaita huoneita", "/majoitus/#tiedustelu", "btn btn-line", "")}</div>
  </div>
</div></section>

<section class="groups"><div class="groups-media">{img("ai-tornionjoki", "Talvinen Tornionjokilaakso ja revontulet", "100vw", style="object-position:60% 50%")}</div>{AI_NOTE}
  <div class="wrap groups-in rv">
    <span class="eyebrow light">{icon("bus")}Ryhmät ja linja-autot</span>
    <h2>{COMPANY["seats"]} paikkaa – koko bussi syö kerralla</h2>
    <p class="lead">Matkaryhmä, joukkue tai työporukka? Sovi ryhmän ruokailu etukäteen puhelimitse – mitoitamme ruoan ja pöydät porukallenne.</p>
    <div class="btns">{btn_call("Soita ja sovi", "btn btn-primary")}{btn("Lähetä ryhmävaraus", "/yhteystiedot/?aihe=Ryhmävaraus#viesti", "btn btn-ghost", "")}</div>
  </div>
</section>

<section class="sec st1" id="st1"><div class="wrap st1-grid">
  <div class="st1-card rv">
    <span class="st1-logo" aria-hidden="true">St1</span>
    <div><span class="eyebrow">Tankkaa samalla</span>
    <h2>St1 Pello – asema ja ravintola samassa pihassa</h2>
    <p>Tankkaa auto ja itsesi yhdellä pysähdyksellä. St1:n kortit käyvät myös Pellon asemalla – tutustu korttivaihtoehtoihin ja etuihin St1:n sivuilla.</p>
    <div class="btns">{btn("St1:n kortit ja edut", "https://www.st1.fi/kortit", "btn btn-line")}</div></div>
  </div>
  <div class="en-card rv" id="english" lang="en">
    <span class="eyebrow">{icon("globe")}In English · På svenska</span>
    <h3>Welcome to Joppari!</h3>
    <p>Café, restaurant, pizzeria and rooms next to the St1 station in Pello, Lapland. Lunch, burgers and 18 pizzas – including our reindeer pizza and gluten-free bases.
       Two rooms with private sauna, breakfast included.</p>
    <p lang="sv"><b>Välkommen!</b> Pizzalistan finns även på svenska.</p>
    <a class="link" href="/pizzat/">Pizza menu / Pizzalista{icon("arrow")}</a>
  </div>
</div></section>

{visit_block()}
'''
    page("/", "Joppari – kahvila-ravintola, pizzeria ja majoitus Pellossa",
         "Kahvila-Ravintola St1 Joppari Pellossa: lounas, pizzat (myös poropizza ja gluteeniton), grilliruoat ja majoitus omalla saunalla. Avoinna ma–pe 7–20, la–su 9–20.",
         body, current="/", cls="home", preload="asema-ilmakuva")


def pizza_card(p):
    n, name, fi, sv, norm, fam = p
    tags = PIZZA_TAGS.get(name, [])
    star = '<span class="badge">Talon oma</span>' if "talon" in tags else ""
    hot = f'<span class="hot" title="Tulinen">{icon("flame")}</span>' if "tulinen" in tags else ""
    return f'''<li class="pz{" pz-star" if "talon" in tags else ""}" data-tags="{" ".join(tags)}">
  <span class="pz-n">{n}</span>
  <div class="pz-b"><h3>{esc(name)}{hot}{star}</h3><p>{esc(fi)}</p><p class="sv" lang="sv">{esc(sv)}</p></div>
  <div class="pz-p"><span><small>norm.</small>{norm} €</span><span><small>perhe</small>{fam} €</span></div>
</li>'''


def build_pizzat():
    filters = [("kaikki", "Kaikki"), ("talon", "Talon oma"), ("liha", "Liha"), ("kala", "Kala & äyriäiset"), ("kasvis", "Kasvis"), ("tulinen", "Tulinen")]
    fbtns = "".join(f'<button type="button" data-f="{k}"{" class=on" if k == "kaikki" else ""}>{t}</button>' for k, t in filters)
    cards = "".join(pizza_card(p) for p in PIZZAS)
    pans = "".join(f'<li><div><b>{esc(fi)}</b><span lang="sv">{esc(sv)}</span></div><em>{pr} €</em></li>' for fi, sv, pr in PAN_PIZZAS)
    lunch = "".join(f'<li><div><b>{esc(fi)}</b><span lang="sv">{esc(sv)}</span></div><em>{pr} €</em></li>' for fi, sv, pr in LUNCH_PIZZA)
    ctas = f'<div class="btns">{btn_call("Tilaa: " + COMPANY["phone"], "btn btn-primary")}{btn("Lounastarjous", "#lounas", "btn btn-ghost", "")}</div>'
    body = f'''
{page_hero("Jopparin pizzalista · Pizzor", "Pizzat tuoreista raaka-aineista", "Valitse listalta tai kokoa oma. Saat pizzan myös <b>gluteenittomana</b>. Soita ja tilaa etukäteen – voit noutaa sen samantien.",
           "ai-poropizza", [("Etusivu", "/"), ("Pizzat", "/pizzat/")], "Jopparin poropizza", ctas, "50% 60%", ai=True)}

<section class="sec menu-sec"><div class="wrap menu-grid">
  <div class="menu-main">
    <div class="menu-top">
      <h2>Pizzat <span lang="sv">/ Pizzor</span></h2>
      <div class="filters" role="group" aria-label="Suodata pizzoja">{fbtns}</div>
      <label class="sv-toggle"><input type="checkbox" data-sv checked> Näytä ruotsiksi / på svenska</label>
    </div>
    <ul class="pizzas" data-pizzas>{cards}</ul>
    <p class="empty" data-empty hidden>Ei pizzoja tällä valinnalla.</p>
  </div>
  <aside class="menu-side">
    <div class="side-card lunch" id="lounas">
      <span class="eyebrow">Lounastarjous · Lunch</span>
      <h3>Lounaspizza {LUNCH_HOURS}</h3>
      <p class="muted" lang="sv">Lunch vardagar kl. 11–14</p>
      <ul class="plist">{lunch}</ul>
    </div>
    <div class="side-card">
      <span class="eyebrow">Lisätäytteet · Extra fyllningar</span>
      <p>{esc(TOPPINGS)}.</p><p class="sv muted" lang="sv">{esc(TOPPINGS_SV)}.</p>
      <ul class="plist"><li><div><b>Lisätäyte</b></div><em>{TOPPING_PRICE[0]} / {TOPPING_PRICE[1]} €</em></li>
        <li><div><b>Valkosipuli</b><span lang="sv">Vitlök</span></div><em>{GARLIC_PRICE[0]} / {GARLIC_PRICE[1]} €</em></li></ul>
      <p class="note">norm. / perhe · familje</p>
    </div>
    <div class="side-card">
      <span class="eyebrow">Pannupizzat · Pannpizzor</span>
      <ul class="plist">{pans}</ul>
    </div>
    <div class="side-card gf">{icon("wheat")}<div><b>Gluteeniton pohja</b><p>Kaikki pizzat saa myös gluteenittomana – kerro tilatessa.</p></div></div>
  </aside>
</div></section>

<section class="sec tint"><div class="wrap order-band rv">
  <figure>{img("paivi", "Päivi ja valmis pizza", "(max-width:900px) 60vw, 320px", style="object-position:50% 30%")}</figure>
  <div><span class="eyebrow">Nouto</span><h2>Soita ja tilaa – pizza odottaa, kun tulet</h2>
  <p class="muted">Tilaa puhelimitse etukäteen, niin voit noutaa pizzan samantien. Isommat ryhmätilaukset kannattaa sopia hyvissä ajoin.</p>
  <div class="btns">{btn_call(cls="btn btn-primary")}{btn("Yhteystiedot", "/yhteystiedot/", "btn btn-line", "")}</div></div>
</div></section>
'''
    menu_schema = {"@context": "https://schema.org", "@type": "Menu", "name": "Jopparin pizzalista", "url": BASE_URL + "/pizzat/",
                   "hasMenuSection": [{"@type": "MenuSection", "name": "Pizzat", "hasMenuItem": [
                       {"@type": "MenuItem", "name": p[1], "description": p[2],
                        "offers": [{"@type": "Offer", "price": p[4].replace(",", "."), "priceCurrency": "EUR", "name": "Normaali"},
                                   {"@type": "Offer", "price": p[5].replace(",", "."), "priceCurrency": "EUR", "name": "Perhe"}]} for p in PIZZAS]}]}
    page("/pizzat/", "Pizzat – Jopparin pizzalista | Joppari Pello",
         "Jopparin pizzalista: 18 pizzaa, pannupizzat ja talon oma poropizza. Myös gluteenittomana. Lounaspizza arkisin 11–14. Tilaa noutoon: 016 512 771.",
         body, current="/pizzat/", schema=[menu_schema, breadcrumb([("Etusivu", "/"), ("Pizzat", "/pizzat/")])], preload="ai-poropizza")


def build_lacarte():
    grill = "".join(f'<li><div><b>{esc(n)}</b>{f"<span>{esc(d)}</span>" if d else ""}</div><i>{a}</i><em>{p} €</em></li>' for n, d, p, a in GRILL)
    ctas = f'<div class="btns">{btn_call(cls="btn btn-primary")}{btn("Pizzat", "/pizzat/", "btn btn-ghost", "")}</div>'
    body = f'''
{page_hero("À la carte · Grilli · Lounas", "Grilli, lounas ja kahvila", "Hampurilaisateriat, arkipäivän lounas, paniinit ja pikkusuolaiset – nopeasti matkan varrelle tai rauhassa pöydän ääressä.",
           "ai-hampurilainen", [("Etusivu", "/"), ("Grilli & lounas", "/la-carte/")], "Hampurilaisateria ranskalaisilla", ctas, "50% 55%", ai=True)}

<section class="sec menu-sec"><div class="wrap lc-grid">
  <div class="rv">
    <span class="eyebrow">{icon("burger")}Grillistä</span>
    <h2>Grilliruoat</h2>
    <ul class="plist big">{grill}</ul>
    <p class="note">L = laktoositon, G = gluteeniton. Kysy allergeeneista henkilökunnalta.</p>
  </div>
  <div class="side-card lunch rv">
    <span class="eyebrow">Lounastarjous</span>
    <h3>Lounaspizza {LUNCH_HOURS}</h3>
    <p>Normaalipizza 2–4 täytteellä ja 0,4 l juoma.</p>
    <div class="price-row dark"><div><small>2 täytettä</small><b>{LUNCH_PIZZA[2][2]} €</b></div><div><small>3 täytettä</small><b>{LUNCH_PIZZA[1][2]} €</b></div><div><small>4 täytettä</small><b>{LUNCH_PIZZA[0][2]} €</b></div></div>
    <a class="link" href="/pizzat/#lounas">Katso pizzalista{icon("arrow")}</a>
  </div>
</div></section>

<section class="sec tint"><div class="wrap">
  {sec_head("Keittiöstä", "Kotiruokaa, suolaista ja makeaa", "Päivän vaihtuvat annokset kannattaa kysyä paikan päältä tai puhelimitse.")}
  <div class="duo">
    <article class="duo-card rv">{img("lohi", "Lohiannos perunoiden, tillin ja sitruunan kera", "(max-width:900px) 100vw, 50vw")}
      <div><h3>À la carte ja lounas</h3><p>Parasta kotiruokaa – lämmöllä tarjottuna. Lämmin ateria pöytään arkena ja viikonloppuna.</p></div></article>
    <article class="duo-card rv">{img("ai-paniini", "Paniinit ja salaatti", "(max-width:900px) 100vw, 50vw")}{AI_NOTE}
      <div><h3>Paniinit ja pikkusuolaiset</h3><p>Lämpimät paniinit ja muut suolaiset mukaan tai paikan päällä syötäväksi.</p></div></article>
    <article class="duo-card rv">{img("ai-kahvi", "Kahvi ja pulla ikkunapöydässä", "(max-width:900px) 100vw, 50vw")}{AI_NOTE}
      <div><h3>Kahvila</h3><p>Aamukahvit arkisin jo kello seitsemästä, viikonloppuisin yhdeksästä.</p></div></article>
    <article class="duo-card rv">{img("ai-keitto", "Lohikeitto ja ruisleipä", "(max-width:900px) 100vw, 50vw")}{AI_NOTE}
      <div><h3>Ryhmille</h3><p>{COMPANY["seats"]} asiakaspaikkaa. Ryhmien ruokailut kannattaa sopia etukäteen puhelimitse.</p></div></article>
  </div>
</div></section>
{visit_block()}
'''
    page("/la-carte/", "Grilli, lounas ja à la carte | Joppari Pello",
         "Jopparin grilliruoat, lounaspizzat arkisin 11–14, à la carte, paniinit ja kahvila Pellossa. Hampurilaisateria 11,50 €. Avoinna joka päivä.",
         body, current="/la-carte/", schema=[breadcrumb([("Etusivu", "/"), ("Grilli & lounas", "/la-carte/")])], preload="ai-hampurilainen")


def build_majoitus():
    rows = "".join(f'<li><span>{n} {"henkilö" if n == 1 else "henkilöä"}</span><b>{p} €</b></li>' for n, p in ROOM_PRICES)
    feats = "".join(f'<li>{icon(ic)}<span>{t}</span></li>' for ic, t in ROOM_FEATURES)
    ctas = f'<div class="btns">{btn("Kysy vapaita huoneita", "#tiedustelu")}{btn_call()}</div>'
    body = f'''
{page_hero("Majoitus Pellossa", "Jopparin makuukammarit", "Kaksi tilavaa ja viihtyisää huonetta omalla saunalla – aamiainen sisältyy. Lemmikit ovat myös tervetulleita.",
           "huone-parvi", [("Etusivu", "/"), ("Majoitus", "/majoitus/")], "Majoitushuone parvineen", ctas, "50% 55%")}

<section class="sec"><div class="wrap rooms-grid">
  <div class="rv">
    <span class="eyebrow">Huoneet</span>
    <h2>Tilaa yhdeksälle – tai kahdelle</h2>
    <p class="big">Meiltä löytyy kaksi huonetta: toinen neljän ja toinen viiden hengen. Huoneita saa vuokrata myös 1–3 hengelle, ja lisävuoteita saa tarvittaessa.</p>
    <p>Huoneet on uusittu vuonna 2013. Kummassakin on oma sauna, suihku ja WC sekä minikeittiö astioineen – sopii niin työmatkalaiselle, perheelle kuin
       Lapin-reissun väliyöhön. Aamiainen sisältyy huonehintaan, ja illallisen saat Jopparin keittiöstä.</p>
    <ul class="feats">{feats}</ul>
  </div>
  <div class="price-card rv">
    <span class="eyebrow">Hinnasto</span>
    <h3>Huone / yö</h3>
    <ul class="prices">{rows}</ul>
    <p class="extra"><span>Lisävuode</span><b>{EXTRA_BED} €</b></p>
    <p class="incl">{icon("coffee")}Aamiainen sisältyy huonehintaan. Ryhmille aamiainen tilauksesta.</p>
    {btn("Kysy vapaita huoneita", "#tiedustelu")}
  </div>
</div></section>

<section class="sec tint"><div class="wrap">
  {sec_head("Kuvia huoneista", "Katso, millaista meillä on", "Klikkaa kuvaa suurentaaksesi.")}
  {gallery(ROOM_GALLERY)}
</div></section>

<section class="sec" id="tiedustelu"><div class="wrap contact-grid">
  <div class="rv">
    <span class="eyebrow">Majoitustiedustelu</span>
    <h2>Kysy vapaita huoneita</h2>
    <p class="muted">Lähetä päivämäärät ja henkilömäärä, niin kerromme majoitustilanteen. Nopeimmin tavoitat meidät puhelimitse.</p>
    <div class="call-card">{icon("phone")}<div><small>Soita</small><a href="{TEL}">{COMPANY["phone"]}</a><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></div></div>
    <div class="call-card">{icon("clock")}<div><small>Ravintola auki</small>{hours_list()}</div></div>
  </div>
  {contact_form("Majoitustiedustelu", "Täytä tiedot – vastaamme sähköpostilla tai puhelimitse.", room=True)}
</div></section>
'''
    lodging = {"@context": "https://schema.org", "@type": "LodgingBusiness", "name": "Jopparin makuukammarit", "url": BASE_URL + "/majoitus/",
               "telephone": COMPANY["phone_intl"], "image": BASE_URL + src_of("huone-parvi"),
               "address": {"@type": "PostalAddress", "streetAddress": COMPANY["street"], "postalCode": COMPANY["zip"], "addressLocality": COMPANY["city"], "addressCountry": "FI"},
               "priceRange": "75–180 €", "petsAllowed": True,
               "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": t, "value": True} for _, t in ROOM_FEATURES]}
    page("/majoitus/", "Majoitus Pellossa – huoneet omalla saunalla | Joppari",
         "Majoitus Pellossa: kaksi huonetta 1–5 hengelle (yht. 9 + lisävuoteet), oma sauna, minikeittiö ja aamiainen. Alkaen 75 €/yö. Lemmikit tervetulleita.",
         body, current="/majoitus/", schema=[lodging, breadcrumb([("Etusivu", "/"), ("Majoitus", "/majoitus/")])], preload="huone-parvi")


def build_contact():
    body = f'''
<section class="sec" style="padding-top:calc(var(--hdr) + 56px)"><div class="wrap contact-grid">
  <div class="rv">
    {crumbs_html([("Etusivu", "/"), ("Yhteystiedot", "/yhteystiedot/")])}
    <span class="eyebrow">Yhteystiedot</span>
    <h1 class="h1-sm">Kahvila-Ravintola <em>St1 Joppari</em></h1>
    <p class="muted">Pöytä- ja ryhmävaraukset, pizzatilaukset noutoon ja majoitus – nopeimmin puhelimitse.</p>
    <div class="call-card">{icon("phone")}<div><small>Puhelin</small><a href="{TEL}">{COMPANY["phone"]}</a><a href="tel:{COMPANY["phone2_intl"]}">{COMPANY["phone2"]}</a></div></div>
    <div class="call-card">{icon("mail")}<div><small>Sähköposti</small><a href="mailto:{COMPANY["email"]}">{COMPANY["email"]}</a></div></div>
    <div class="call-card">{icon("pin")}<div><small>Osoite</small><a href="{MAPS}" target="_blank" rel="noopener">{COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}</a></div></div>
    <div class="call-card">{icon("clock")}<div><small>Aukioloajat</small>{hours_list()}{open_badge()}</div></div>
  </div>
  <div id="viesti">{contact_form()}</div>
</div></section>
<section class="map-wide"><iframe title="Jopparin sijainti kartalla" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
  <a class="map-fallback" href="{MAPS}" target="_blank" rel="noopener">{icon("pin")}Avaa kartta</a></section>
'''
    page("/yhteystiedot/", "Yhteystiedot ja aukioloajat | Joppari Pello",
         "Kahvila-Ravintola St1 Joppari, Pellontie 31, 95700 Pello. Puh. 016 512 771. Avoinna ma–pe 7–20, la–su 9–20. Majoitus- ja ryhmävaraukset.",
         body, current="/yhteystiedot/", cls="nohero", schema=[breadcrumb([("Etusivu", "/"), ("Yhteystiedot", "/yhteystiedot/")])])


def build_simple():
    tp = f'''<section class="sec" style="padding-top:calc(var(--hdr) + 56px)"><div class="wrap prose">{crumbs_html([("Etusivu", "/"), ("Tietosuojaseloste", "/tietosuojaseloste/")])}
<h1 class="h1-sm">Tietosuojaseloste</h1>
<h2>1. Rekisterinpitäjä</h2><p>{COMPANY["name"]}, {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}.</p>
<h2>2. Yhteyshenkilö</h2><p>Päivi, {COMPANY["phone"]}, {COMPANY["email"]}.</p>
<h2>3. Käyttötarkoitus</h2><p>Yhteydenotto- ja majoitustiedustelulomakkeilla lähetettyjä tietoja käytetään tiedusteluihin vastaamiseen sekä varausten hoitamiseen.</p>
<h2>4. Käsiteltävät tiedot</h2><p>Nimi, puhelinnumero, sähköpostiosoite, majoituksen päivämäärät ja henkilömäärä sekä viestin sisältö.</p>
<h2>5. Käsittelyn peruste</h2><p>Varauksen tai sopimuksen valmistelu, oikeutettu etu (asiakassuhde) sekä lakisääteiset velvoitteet (kirjanpito).</p>
<h2>6. Säilytysaika</h2><p>Tietoja säilytetään niin kauan kuin niitä tarvitaan tiedustelun ja varauksen hoitamiseen sekä lain edellyttämän ajan.</p>
<h2>7. Luovutukset</h2><p>Tietoja ei luovuteta kolmansille osapuolille markkinointiin. Sivuston ja sähköpostin palveluntarjoajat käsittelevät tietoja lukuumme.</p>
<h2 id="evasteet">8. Evästeet</h2><p>Sivusto ei käytä seuranta- tai markkinointievästeitä. Yhteystietosivun kartta ladataan Googlesta.</p>
<h2>9. Rekisteröidyn oikeudet</h2><p>Sinulla on oikeus tarkastaa, korjata ja pyytää poistamaan tietosi sekä vastustaa käsittelyä. Ota yhteyttä yllä olevaan yhteyshenkilöön. Voit myös tehdä valituksen tietosuojavaltuutetulle.</p></div></section>'''
    page("/tietosuojaseloste/", "Tietosuojaseloste | Joppari", "Jopparin tietosuojaseloste: lomakkeiden tietojen käsittely, evästeet ja oikeutesi.",
         tp, cls="nohero")
    ok = f'''<section class="phero plain"><div class="wrap"><span class="eyebrow">Kiitos</span><h1>Kiitos viestistäsi!</h1>
<p class="lead">Viestisi on vastaanotettu. Palaamme asiaan mahdollisimman pian – kiireellisissä asioissa soita {COMPANY["phone"]}.</p>
<div class="btns">{btn("Katso pizzalista", "/pizzat/")}{btn_call(cls="btn btn-line")}</div></div></section>'''
    page("/kiitos/", "Kiitos – Joppari", "Kiitos yhteydenotostasi.", ok, noindex=True, cls="nohero")
    nf = f'''<section class="phero plain"><div class="wrap"><span class="eyebrow">404</span><h1>Sivua ei löytynyt</h1>
<p class="lead">Sivusto on uudistunut, ja osa osoitteista on muuttunut.</p>
<div class="btns">{btn("Pizzat", "/pizzat/")}{btn("Majoitus", "/majoitus/", "btn btn-line", "")}</div></div></section>'''
    page("/404.html", "Sivua ei löytynyt – Joppari", "Sivua ei löytynyt.", nf, noindex=True, cls="nohero")


# ---------------------------------------------------------------------------
# OG-kuva, favicon, sitemap
# ---------------------------------------------------------------------------

ORANGE = (232, 106, 36)


def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(SRC, "fonts", name), size)
    if var:
        try:
            f.set_variation_by_axes(var)
        except Exception:
            pass
    return f


def mark_png(size, bg=None):
    s = 4 * size
    im = Image.new("RGBA", (s, s), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = s / 40
    # timantti
    d.regular_polygon((20 * k, 20 * k, 19.6 * k), 4, rotation=0, fill=ORANGE)
    w = int(2.2 * k)
    d.line([(16 * k, 12.5 * k), (16 * k, 18.7 * k)], fill="white", width=w)
    d.line([(20 * k, 12.5 * k), (20 * k, 18.7 * k)], fill="white", width=w)
    d.arc([16 * k, 16.7 * k, 20 * k, 20.7 * k], 0, 180, fill="white", width=w)
    d.line([(18 * k, 12.5 * k), (18 * k, 27.5 * k)], fill="white", width=w)
    d.line([(24.2 * k, 12.5 * k), (24.2 * k, 27.5 * k)], fill="white", width=w)
    d.pieslice([21.6 * k, 12.5 * k, 26.8 * k, 26 * k], 90, 270, fill="white")
    return im.resize((size, size), Image.LANCZOS)


def og_image():
    bg = ImageOps.fit(Image.open(IMG_SRC["asema-ilmakuva"]).convert("RGB"), (1200, 630), Image.LANCZOS, centering=(.45, .6)).convert("RGBA")
    shade = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(1200):
        d.line([(x, 0), (x, 630)], fill=(28, 21, 18, int(235 * max(0.12, 1 - x / 900))))
    bg = Image.alpha_composite(bg, shade)
    bg.alpha_composite(mark_png(92), (70, 70))
    d = ImageDraw.Draw(bg)
    d.text((180, 76), "Joppari", font=font("Fraunces-Italic.ttf", 70, [72, 800, 100, 1]), fill=(255, 255, 255))
    d.text((72, 250), "Parasta kotiruokaa", font=font("Fraunces.ttf", 70, [72, 750, 50, 0]), fill=(255, 255, 255))
    d.text((72, 332), "lämmöllä tarjottuna.", font=font("Fraunces-Italic.ttf", 70, [72, 700, 50, 1]), fill=(255, 170, 110))
    d.rectangle([72, 452, 140, 457], fill=ORANGE)
    d.text((72, 480), f"Kahvila · Pizzeria · Majoitus · Pello · {COMPANY['phone']}", font=font("Inter.ttf", 28), fill=(240, 232, 222))
    bg.convert("RGB").save(os.path.join(IMG_OUT, "og.jpg"), quality=86)


def build_assets():
    og_image()
    mark_png(64).save(os.path.join(SITE, "favicon.png"))
    mark_png(180, (255, 248, 240, 255)).save(os.path.join(SITE, "apple-touch-icon.png"))
    mark_png(512).save(os.path.join(IMG_OUT, "logo-512.png"))
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(SITE, "style.css"))
    shutil.copy(os.path.join(SRC, "app.js"), os.path.join(SITE, "app.js"))
    with open(os.path.join(SITE, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n" if DEMO else f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n")
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
    build_pizzat()
    build_lacarte()
    build_majoitus()
    build_contact()
    build_simple()
    build_assets()
    with open(os.path.join(SITE, "redirects.json"), "w") as f:
        json.dump(REDIRECTS, f, ensure_ascii=False, indent=1)
    target = write_host_files(SITE, vastaanottaja=COMPANY["email"], domain=COMPANY["domain"], sivusto=COMPANY["name"], redirects=REDIRECTS)
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
    """Esikatselu Claude-artifaktina: litteät sivut, suhteelliset polut, lomakkeet eivät lähetä mitään."""
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
        h = re.sub(r'<!doctype html>\s*<html[^>]*>\s*<head>\s*', "", h)
        h = h.replace("</head>", "").replace("</body>", "").replace("</html>", "")
        h = re.sub(r'<body([^>]*)>', lambda m: f'<div id="__b"{m.group(1)}></div><script>document.body.className=document.getElementById("__b").className</script>', h)
        if rel == "index.html":
            h = re.sub(r"<title>[^<]*</title>", "<title>Joppari Pello</title>", h, count=1)
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
