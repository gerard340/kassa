"""Demodata voor de Kassa POC: 1 winkel, 8 categorieen met subcategorieen, ~60 producten.

Genereert per product een SVG-'afbeelding' (gekleurd vlak + emoji) in static/img/products/.
"""
import os
import random

from .db import get_db

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img", "products")

STORE = ("Buurtsuper De Hoek", "Dorpsstraat 12, 4691 AB Tholen", "12345678", "NL001234567B01")

# (naam, icon, kleur, [subcategorieen])
CATEGORIES = [
    ("Groente & Fruit", "🥦", "#4caf50", ["Groente", "Fruit"]),
    ("Zuivel & Eieren", "🥛", "#5c9ded", ["Melk", "Kaas", "Yoghurt", "Eieren"]),
    ("Brood & Bakkerij", "🍞", "#c98a3a", ["Brood", "Gebak"]),
    ("Vlees & Vis", "🥩", "#d9534f", ["Vlees", "Vis", "Vegetarisch"]),
    ("Dranken", "🧃", "#26a69a", ["Frisdrank", "Sap", "Bier & Wijn", "Water"]),
    ("Snacks & Snoep", "🍫", "#8e5bd1", ["Chips", "Chocolade", "Koek"]),
    ("Voorraadkast", "🍝", "#e0a030", ["Pasta & Rijst", "Conserven", "Ontbijt"]),
    ("Huishouden", "🧻", "#607d8b", ["Schoonmaak", "Papier", "Verzorging"]),
]

# (naam, subcategorie, prijs, btw%, statiegeld, leeftijd, emoji, eenheid)
PRODUCTS = [
    ("Komkommer", "Groente", 0.89, 9, 0, 0, "🥒", "stuk"),
    ("Broccoli 500 g", "Groente", 1.49, 9, 0, 0, "🥦", "stuk"),
    ("Trostomaten 500 g", "Groente", 1.99, 9, 0, 0, "🍅", "stuk"),
    ("Paprika mix 3 st", "Groente", 2.49, 9, 0, 0, "🫑", "stuk"),
    ("Uien 1 kg", "Groente", 1.29, 9, 0, 0, "🧅", "zak"),
    ("Wortelen 1 kg", "Groente", 1.19, 9, 0, 0, "🥕", "zak"),
    ("Bananen 1 kg", "Fruit", 1.79, 9, 0, 0, "🍌", "kg"),
    ("Appels Elstar 1 kg", "Fruit", 2.29, 9, 0, 0, "🍎", "zak"),
    ("Sinaasappels net 2 kg", "Fruit", 2.99, 9, 0, 0, "🍊", "net"),
    ("Aardbeien 400 g", "Fruit", 3.49, 9, 0, 0, "🍓", "bakje"),
    ("Citroen", "Fruit", 0.45, 9, 0, 0, "🍋", "stuk"),
    ("Druiven wit 500 g", "Fruit", 2.79, 9, 0, 0, "🍇", "bakje"),
    ("Halfvolle melk 1 L", "Melk", 1.09, 9, 0, 0, "🥛", "pak"),
    ("Volle melk 1 L", "Melk", 1.19, 9, 0, 0, "🥛", "pak"),
    ("Karnemelk 1 L", "Melk", 1.05, 9, 0, 0, "🥛", "pak"),
    ("Jong belegen kaas 500 g", "Kaas", 5.99, 9, 0, 0, "🧀", "stuk"),
    ("Geraspte kaas 200 g", "Kaas", 2.49, 9, 0, 0, "🧀", "zak"),
    ("Volle yoghurt 1 L", "Yoghurt", 1.39, 9, 0, 0, "🥣", "pak"),
    ("Griekse yoghurt 500 g", "Yoghurt", 2.19, 9, 0, 0, "🥣", "beker"),
    ("Scharreleieren 10 st", "Eieren", 2.79, 9, 0, 0, "🥚", "doos"),
    ("Volkoren brood", "Brood", 2.19, 9, 0, 0, "🍞", "stuk"),
    ("Wit brood", "Brood", 1.99, 9, 0, 0, "🍞", "stuk"),
    ("Croissants 4 st", "Brood", 2.29, 9, 0, 0, "🥐", "zak"),
    ("Appeltaart", "Gebak", 5.99, 9, 0, 0, "🥧", "stuk"),
    ("Gevulde koeken 4 st", "Gebak", 2.49, 9, 0, 0, "🍪", "zak"),
    ("Kipfilet 500 g", "Vlees", 5.49, 9, 0, 0, "🍗", "pak"),
    ("Rundergehakt 500 g", "Vlees", 4.99, 9, 0, 0, "🥩", "pak"),
    ("Zalmfilet 250 g", "Vis", 5.99, 9, 0, 0, "🐟", "pak"),
    ("Vegaburgers 2 st", "Vegetarisch", 3.29, 9, 0, 0, "🍔", "pak"),
    ("Cola 1,5 L", "Frisdrank", 2.19, 9, 0.25, 0, "🥤", "fles"),
    ("Cola blik 33 cl", "Frisdrank", 0.89, 9, 0.15, 0, "🥫", "blik"),
    ("Sinas 1,5 L", "Frisdrank", 1.89, 9, 0.25, 0, "🥤", "fles"),
    ("Sinaasappelsap 1 L", "Sap", 2.49, 9, 0, 0, "🧃", "pak"),
    ("Appelsap 1 L", "Sap", 1.79, 9, 0, 0, "🧃", "pak"),
    ("Pils 6 x 33 cl", "Bier & Wijn", 5.49, 21, 0.90, 1, "🍺", "pak"),
    ("Rode wijn 75 cl", "Bier & Wijn", 6.99, 21, 0, 1, "🍷", "fles"),
    ("Witte wijn 75 cl", "Bier & Wijn", 6.49, 21, 0, 1, "🍷", "fles"),
    ("Bronwater 1,5 L", "Water", 0.79, 9, 0.25, 0, "💧", "fles"),
    ("Spa rood 6 x 50 cl", "Water", 4.49, 9, 0.90, 0, "💧", "pak"),
    ("Paprika chips", "Chips", 1.89, 9, 0, 0, "🍟", "zak"),
    ("Naturel chips", "Chips", 1.89, 9, 0, 0, "🍟", "zak"),
    ("Melkchocolade reep", "Chocolade", 1.49, 9, 0, 0, "🍫", "stuk"),
    ("Hazelnoot chocolade", "Chocolade", 1.49, 9, 0, 0, "🍫", "stuk"),
    ("Stroopwafels", "Koek", 2.29, 9, 0, 0, "🧇", "pak"),
    ("Speculaas", "Koek", 1.99, 9, 0, 0, "🍪", "pak"),
    ("Spaghetti 500 g", "Pasta & Rijst", 1.29, 9, 0, 0, "🍝", "pak"),
    ("Penne 500 g", "Pasta & Rijst", 1.29, 9, 0, 0, "🍝", "pak"),
    ("Basmati rijst 1 kg", "Pasta & Rijst", 2.99, 9, 0, 0, "🍚", "pak"),
    ("Tomatenblokjes", "Conserven", 0.89, 9, 0, 0, "🥫", "blik"),
    ("Kikkererwten", "Conserven", 0.99, 9, 0, 0, "🥫", "blik"),
    ("Tonijn in olie", "Conserven", 1.79, 9, 0, 0, "🐟", "blik"),
    ("Hagelslag melk", "Ontbijt", 2.49, 9, 0, 0, "🍫", "pak"),
    ("Pindakaas", "Ontbijt", 2.99, 9, 0, 0, "🥜", "pot"),
    ("Cornflakes", "Ontbijt", 2.79, 9, 0, 0, "🥣", "pak"),
    ("Afwasmiddel", "Schoonmaak", 1.79, 21, 0, 0, "🧴", "fles"),
    ("Allesreiniger", "Schoonmaak", 2.49, 21, 0, 0, "🧴", "fles"),
    ("Vuilniszakken 20 st", "Schoonmaak", 2.19, 21, 0, 0, "🗑️", "rol"),
    ("Toiletpapier 8 rol", "Papier", 4.49, 21, 0, 0, "🧻", "pak"),
    ("Keukenrol 4 rol", "Papier", 2.99, 21, 0, 0, "🧻", "pak"),
    ("Tandpasta", "Verzorging", 2.49, 21, 0, 0, "🪥", "tube"),
    ("Shampoo", "Verzorging", 3.49, 21, 0, 0, "🧴", "fles"),
    # Bewust zonder categorie: mag NIET zichtbaar zijn in de kassa (wel scanbaar)
    ("Cadeaubon 10 euro", None, 10.00, 0, 0, 0, "🎁", "stuk"),
]


def ean13(seq: int) -> str:
    base = f"8712345{seq:05d}"
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    return base + str((10 - total % 10) % 10)


def write_svg(path: str, emoji: str, color: str) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{color}" stop-opacity="0.35"/>
    <stop offset="1" stop-color="{color}" stop-opacity="0.85"/>
  </linearGradient></defs>
  <rect width="200" height="200" rx="24" fill="url(#g)"/>
  <text x="100" y="118" font-size="96" text-anchor="middle"
        font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, sans-serif">{emoji}</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)


def seed():
    os.makedirs(IMG_DIR, exist_ok=True)
    random.seed(42)
    with get_db() as conn:
        conn.execute("INSERT INTO stores (id, name, address, kvk, btw_nummer) VALUES (1, ?, ?, ?, ?)", STORE)

        sub_ids = {}
        sub_color = {}
        for sort, (name, icon, color, subs) in enumerate(CATEGORIES):
            cur = conn.execute(
                "INSERT INTO categories (name, parent_id, icon, color, sort) VALUES (?, NULL, ?, ?, ?)",
                (name, icon, color, sort),
            )
            cat_id = cur.lastrowid
            for s_sort, sub in enumerate(subs):
                cur = conn.execute(
                    "INSERT INTO categories (name, parent_id, icon, color, sort) VALUES (?, ?, NULL, ?, ?)",
                    (sub, cat_id, color, s_sort),
                )
                sub_ids[sub] = cur.lastrowid
                sub_color[sub] = color

        for seq, (name, sub, price, btw, statiegeld, age, emoji, unit) in enumerate(PRODUCTS, start=1):
            ean = ean13(seq)
            color = sub_color.get(sub, "#9e9e9e")
            filename = f"{ean}.svg"
            write_svg(os.path.join(IMG_DIR, filename), emoji, color)
            conn.execute(
                """INSERT INTO products
                   (ean, name, category_id, price_cents, btw_pct, statiegeld_cents, age_restricted, unit, image_url, stock, min_stock)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ean, name, sub_ids.get(sub), round(price * 100), btw, round(statiegeld * 100), age, unit,
                    f"/static/img/products/{filename}", random.randint(3, 60), 5,
                ),
            )


if __name__ == "__main__":
    from .db import init_schema
    init_schema()
    seed()
    print("Seed klaar.")
