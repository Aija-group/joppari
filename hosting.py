"""Äijä Group – hosting-kytkin generaattoriin.

Kopioi tämä tiedosto asiakasprojektin juureen ja lisää build.py:hyn:

    from hosting import HOSTING, form_attrs, hidden_fields, write_host_files

Aja:
    python3 build.py                 -> webhotelli (oletus, PHP-lomake + .htaccess)
    HOSTING=netlify python3 build.py -> Netlify (data-netlify, _redirects)
    HOSTING=nordichost python3 build.py -> NordicHost cPanel "AI App Hosting" (Node: server.js tarjoilee site/, lomake /lahetys)

Lomakkeen muutos build.py:ssä (contact_form-funktio):

    return f'''<form class="form" id="{id_}" name="yhteydenotto" method="POST" {form_attrs()}>
    {hidden_fields()}
    ...kentät...
    </form>'''

Ja build()-funktion loppuun, zipin luonnin edelle:

    write_host_files(OUT, vastaanottaja="info@asiakas.fi", domain="asiakas.fi",
                     sivusto="Asiakas Oy")
"""
import os, re, time

HOSTING = os.environ.get("HOSTING", "webhotelli").lower()
KIT = os.path.dirname(os.path.abspath(__file__))


def form_attrs(action_netlify="/kiitos/", action_php="/lahetys.php"):
    """Lomake-elementin hosting-kohtaiset attribuutit."""
    if HOSTING == "netlify":
        return f'action="{action_netlify}" data-netlify="true" netlify-honeypot="bot-field"'
    if HOSTING == "nordichost":
        return 'action="/lahetys"'
    return f'action="{action_php}"'


def hidden_fields(form_name="yhteydenotto"):
    """Piilokentät: Netlifyn form-name tai PHP:n honeypot + aikaleima."""
    hp = ('<p style="display:none" aria-hidden="true">'
          '<label>Älä täytä tätä kenttää: <input name="bot-field" tabindex="-1" autocomplete="off">'
          '</label></p>')
    if HOSTING == "netlify":
        return f'<input type="hidden" name="form-name" value="{form_name}">{hp}'
    return (f'{hp}<input type="hidden" name="ts" value="{int(time.time())}">'
            f'<input type="hidden" name="sivu" value="">'
            f'<script>document.currentScript.previousElementSibling.value=location.pathname;</script>')


def write_host_files(out_dir, vastaanottaja, domain, sivusto,
                     lahettaja=None, redirects=None, www_to_apex=True):
    """Kirjoittaa .htaccess + lahetys.php (webhotelli) tai _redirects (Netlify)."""
    if HOSTING == "nordichost":
        # Node-palvelin (server.js) hoitaa ohjaukset, 404:n ja lomakkeen – ei .htaccessia eikä PHP:tä.
        return "nordichost"
    if HOSTING == "netlify":
        if redirects:
            with open(os.path.join(out_dir, "_redirects"), "w") as f:
                for src, dst in redirects.items():
                    f.write(f"{src} {dst} 301\n")
        return "netlify"

    # --- .htaccess ---
    ht = open(os.path.join(KIT, "htaccess.txt"), encoding="utf-8").read()
    if not www_to_apex:
        ht = ht.replace("RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]\nRewriteRule ^(.*)$ https://%1/$1 [R=301,L]",
                        "RewriteCond %{HTTP_HOST} !^www\\. [NC]\n"
                        "RewriteRule ^(.*)$ https://www.%{HTTP_HOST}/$1 [R=301,L]")
    if redirects:
        rules = "\n".join(f"Redirect 301 {src} {dst}" for src, dst in redirects.items())
        ht = ht.replace("# Redirect 301 /vanha-sivu.html /palvelut/uusi/", rules)
    with open(os.path.join(out_dir, ".htaccess"), "w", encoding="utf-8") as f:
        f.write(ht)

    # --- lahetys.php ---
    php = open(os.path.join(KIT, "lahetys.php"), encoding="utf-8").read()
    php = php.replace("$VASTAANOTTAJA = 'info@asiakas.fi';",
                      f"$VASTAANOTTAJA = '{vastaanottaja}';")
    php = php.replace("$LAHETTAJA     = 'no-reply@asiakas.fi';",
                      f"$LAHETTAJA     = '{lahettaja or 'no-reply@' + domain}';")
    php = php.replace("$SIVUSTO       = 'Asiakas Oy';", f"$SIVUSTO       = '{sivusto}';")
    with open(os.path.join(out_dir, "lahetys.php"), "w", encoding="utf-8") as f:
        f.write(php)
    return "webhotelli"
