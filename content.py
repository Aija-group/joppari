# -*- coding: utf-8 -*-
"""St1 Joppari (joppari.fi), St1 Pello – sivuston tekstit ja listat.

Lähteet: vanha joppari.fi (haettu 28.9.2026), Travel Pello, helmisimpukka.fi/asemat/pello sekä asiakkaan palaute 29.9.2026
(pizzahinnasto 2026 ja majoitushinnat 2026 kuvina, lounasbuffet 11–16 joka päivä, à la carte ja grillilista poistettu).
Nimi on aina "St1 Joppari" – St1:tä ja Jopparia ei eroteta. Aseman virallinen nimi on St1 Pello.
"""

COMPANY = {
    "name": "St1 Joppari",
    "station": "St1 Pello",
    "short": "Joppari",
    "domain": "joppari.fi",
    "street": "Pellontie 31",
    "zip": "95700",
    "city": "Pello",
    "region": "Lappi",
    "phone": "016 512 771",
    "phone_intl": "+35816512771",
    "phone2": "040 706 5450",
    "phone2_intl": "+358407065450",
    "email": "paivi@joppari.fi",
    "facebook": "https://www.facebook.com/joppari.fi/",
    "travelpello": "https://travelpello.fi/fi/",
    "geo": (66.776188, 23.965948),
    "seats": 55,
    "founded": "2012",
}

# (päivät, auki, kiinni) – schema.org-muodossa myös alla
HOURS = [
    ("Ma–pe", "7.00", "20.00"),
    ("La–su", "9.00", "20.00"),
]
HOURS_SCHEMA = [
    {"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "20:00"},
    {"days": ["Saturday", "Sunday"], "opens": "09:00", "closes": "20:00"},
]
# JS:n "auki nyt" -merkki: viikonpäivä 0=su … 6=la → [auki min, kiinni min]
HOURS_JS = {0: [540, 1200], 1: [420, 1200], 2: [420, 1200], 3: [420, 1200], 4: [420, 1200], 5: [420, 1200], 6: [540, 1200]}

NAV = [
    ("Lounas", "/lounas/"),
    ("Pizzat", "/pizzat/"),
    ("Majoitus", "/majoitus/"),
    ("Yhteystiedot", "/yhteystiedot/"),
]

# ---------------------------------------------------------------------------
# Pizzat (vanha /pizzat/-sivu, hinnat: normaali / perhe)
# ---------------------------------------------------------------------------
PIZZAS = [
    (1, "Opera", "Kinkkua, tonnikalaa", "Skinka, tonfisk", "11,20", "19,40"),
    (2, "Quattro Stagioni", "Kinkkua, herkkusieniä, katkarapuja, tonnikalaa", "Skinka, champinjoner, räkor, tonfisk", "13,20", "23,40"),
    (3, "Bolognese", "Jauhelihakastiketta", "Maletköttsås", "10,80", "18,80"),
    (4, "Francescana", "Kinkkua, herkkusieniä", "Skinka, champinjoner", "11,20", "19,40"),
    (5, "Frutti di Mare", "Tonnikalaa, katkarapuja, simpukoita", "Tonfisk, räkor, musslor", "12,20", "21,40"),
    (6, "Opera Special", "Kinkkua, tonnikalaa, salamia", "Skinka, tonfisk, salami", "12,20", "21,40"),
    (7, "Jopparin pizza", "Savuporoa, kananmunaa, aurajuustoa", "Rökt renkött, färska ägg, blåmögelost", "12,20", "21,40"),
    (8, "Tropicana", "Kinkkua, ananasta", "Skinka, ananas", "11,20", "19,40"),
    (9, "Vegetariana", "Paprikaa, herkkusieniä, oliiveja", "Paprika, champinjoner, oliver", "12,20", "21,40"),
    (10, "Margherita", "Lisäjuustoa", "Extra ost", "10,80", "18,80"),
    (11, "Pepperoni", "Tonnikalaa, pepperonimakkaraa", "Tonfisk, pepperonikorv", "11,20", "19,40"),
    (12, "Mexicana", "Mexicanakastiketta, pariloitua kananpoikaa, ananasta, jalopenoa", "Mexicanasås, grillad kyckling, ananas, jalapeño", "13,20", "23,40"),
    (13, "Mexico", "Mexicanakastiketta, pepperonimakkaraa, ananasta, jalopenoa", "Mexicanasås, pepperonikorv, ananas, jalapeño", "13,20", "23,40"),
    (14, "Chicken", "Pariloitua kananpoikaa, ananasta", "Grillad kyckling, ananas", "11,20", "19,40"),
    (15, "Americana", "Kinkkua, ananasta, aurajuustoa", "Skinka, ananas, blåmögelost", "12,20", "21,40"),
    (16, "Kebabpizza", "Kebablihaa, jalopenoa, sipulia, paprikaa", "Kebabkött, jalapeño, lök, paprika", "13,20", "23,40"),
    (17, "Chicken Hawaii", "Pariloitua kananpoikaa, ananasta, aurajuustoa", "Grillad kyckling, ananas, blåmögelost", "12,20", "21,40"),
    (18, "Fantasia", "Neljä täytettä oman maun mukaan", "Fyra fyllningar enligt eget val", "13,20", "23,40"),
]
# Suodatinmerkit (Kasvis ja Tulinen merkitty myös painettuun hinnastoon)
PIZZA_TAGS = {
    "Jopparin pizza": ["talon", "liha"], "Vegetariana": ["kasvis"], "Margherita": ["kasvis"],
    "Frutti di Mare": ["kala"], "Opera": ["liha", "kala"], "Quattro Stagioni": ["liha", "kala"], "Bolognese": ["liha"],
    "Francescana": ["liha"], "Opera Special": ["liha", "kala"], "Tropicana": ["liha"], "Pepperoni": ["liha", "kala"],
    "Mexicana": ["liha", "tulinen"], "Mexico": ["liha", "tulinen"], "Chicken": ["liha"], "Americana": ["liha"],
    "Kebabpizza": ["liha"], "Chicken Hawaii": ["liha"], "Fantasia": ["oma"],
}
TOPPINGS = ("Ananas, paprika, sipuli, oliivi, jalopeno, mex-kastike, herkkusieni, simpukka, aurajuusto, tonnikala, juusto, "
            "kinkku, salami, jauhelihakastike, katkarapu, pepperoni, kebabliha, pariloitu kanakuutio, kananmuna")
TOPPINGS_SV = ("Ananas, paprika, lök, oliver, jalapeño, mex-sås, champinjoner, musslor, blåmögelost, tonfisk, ost, "
               "skinka, salami, maletköttsås, räkor, pepperoni, kebabkött, grillad kyckling, färska ägg")
TOPPING_PRICE = ("1,60", "3,20")
GARLIC_PRICE = ("1,60", "3,20")
PAN_PIZZAS = [
    ("Pepperonimakkaraa", "Pepperonikorv", "9,70"),
    ("Katkarapuja, tonnikalaa", "Räkor, tonfisk", "10,70"),
    ("Herkkusieniä, paprikaa, oliiveja", "Champinjoner, paprika, oliver", "11,70"),
    ("Kinkkua, sinihomejuustoa", "Skinka, blåmögelost", "10,70"),
    ("Tonnikalaa, kinkkua", "Tonfisk, skinka", "10,70"),
]
LUNCH_PIZZA = [
    ("Normaalipizza kahdella täytteellä + 0,4 l juoma", "Normalstor pizza med två fyllningar + 0,4 l dryck", "11,20"),
    ("Normaalipizza kolmella täytteellä + 0,4 l juoma", "Normalstor pizza med tre fyllningar + 0,4 l dryck", "12,20"),
    ("Normaalipizza neljällä täytteellä + 0,4 l juoma", "Normalstor pizza med fyra fyllningar + 0,4 l dryck", "13,20"),
]
LUNCH_HOURS = "arkisin klo 11–14"

# Lounasbuffet (asiakkaan tieto 29.9.2026): kotiruoka- ja salaattibuffet joka päivä
BUFFET_HOURS = "klo 11–16"
HS_PELLO = "https://helmisimpukka.fi/asemat/pello"

# ---------------------------------------------------------------------------
# Majoitus (vanha /majoitus/-sivu)
# ---------------------------------------------------------------------------
ROOM_PRICES = [(1, "80"), (2, "105"), (3, "130"), (4, "155"), (5, "185")]
EXTRA_BED = "50"
BREAKFAST_ONLY = "10"      # aamupala erikseen
DOG_FEE = "20"             # koirista siivousmaksu
BREAKFAST_TIMES = [("Arkisin", "7.30–9.30"), ("Viikonloppuna", "9.00–10.00")]
DOORS = [("WC-oven leveys", "60 cm"), ("Muut ovet", "80 cm")]
ROOM_FEATURES = [
    ("sauna", "Oma sauna"), ("drop", "Suihku ja WC"), ("kitchen", "Minikeittiö astioineen"), ("fridge", "Jääkaappi ja mikro"),
    ("bed", "Liinavaatteet ja pyyhkeet"), ("coffee", "Aamiainen sisältyy"), ("paw", "Koirat tervetulleita"), ("iron", "Silitysrauta pyydettäessä"),
]
ROOM_GALLERY = [
    ("huone-parvi", "Huone parvineen, parivuode, nojatuoli ja televisio"),
    ("huone-oleskelu", "Oleskelu- ja ruokailunurkkaus"),
    ("huone-2", "Valoisa huone parvisängyllä"),
    ("huone-keittio", "Minikeittiö ja ruokapöytä"),
    ("huone-yla", "Parven vuoteet"),
    ("sauna", "Huoneen oma sauna"),
    ("kylpyhuone", "Suihku ja WC"),
]

# Vanhat osoitteet → uudet (server.js lukee site/redirects.json)
REDIRECTS = {
    "/hankietukortti/": "/#asema",
    "/lounaslista/": "/lounas/",
    "/la-carte/": "/lounas/",
    "/in-english/": "/#english",
    "/etusivu/": "/",
    "/hampurilaiset-suolaiset/": "/lounas/",
    "/fb/": "/",
    "/po-russki/": "/",
}
