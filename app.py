"""Kassa POC - Flask backend.

Start: python app.py  (of start.bat)
Kassa:   http://localhost:5050/
Beheer:  http://localhost:5050/admin
"""
import random
import string
from datetime import datetime

from flask import Flask, abort, jsonify, render_template, request

from kassa.db import get_db, init_schema, is_seeded
from kassa.seed import seed

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

STORE_ID = 1  # POC: 1 winkel. Datamodel is al multi-store (store_id op sales).


# --------------------------------------------------------------------------- helpers
def rows(cur):
    return [dict(r) for r in cur.fetchall()]


def btw_breakdown(lines):
    """Per btw-tarief: bruto (incl.), netto, btw. Statiegeld valt buiten de btw."""
    per_rate = {}
    for ln in lines:
        gross = ln["qty"] * ln["unit_price_cents"]
        per_rate[ln["btw_pct"]] = per_rate.get(ln["btw_pct"], 0) + gross
    out = []
    for pct in sorted(per_rate):
        gross = per_rate[pct]
        net = round(gross / (1 + pct / 100))
        out.append({"pct": pct, "gross_cents": gross, "net_cents": net, "btw_cents": gross - net})
    return out


def build_receipt(conn, sale_id):
    sale = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if not sale:
        return None
    store = dict(conn.execute("SELECT * FROM stores WHERE id = ?", (sale["store_id"],)).fetchone())
    lines = rows(conn.execute("SELECT * FROM sale_lines WHERE sale_id = ? ORDER BY id", (sale_id,)))
    goods = sum(l["qty"] * l["unit_price_cents"] for l in lines)
    statiegeld = sum(l["qty"] * l["statiegeld_cents"] for l in lines)
    return {
        "sale": dict(sale),
        "store": store,
        "lines": lines,
        "goods_cents": goods,
        "statiegeld_cents": statiegeld,
        "total_cents": goods + statiegeld,
        "btw": btw_breakdown(lines),
    }


# --------------------------------------------------------------------------- pagina's
@app.route("/")
def kassa_page():
    return render_template("kassa.html")


@app.route("/admin")
def admin_page():
    with get_db() as conn:
        store = dict(conn.execute("SELECT * FROM stores WHERE id = ?", (STORE_ID,)).fetchone())
        sales = rows(conn.execute(
            """SELECT s.*, COUNT(l.id) AS line_count, COALESCE(SUM(l.qty), 0) AS item_count
               FROM sales s LEFT JOIN sale_lines l ON l.sale_id = s.id
               WHERE s.store_id = ?
               GROUP BY s.id ORDER BY s.id DESC LIMIT 100""", (STORE_ID,)))
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = dict(conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(total_cents),0) AS total FROM sales WHERE store_id = ? AND ts LIKE ?",
            (STORE_ID, today + "%")).fetchone())
        products = rows(conn.execute(
            """SELECT p.*, sub.name AS sub_name, top.name AS cat_name
               FROM products p
               LEFT JOIN categories sub ON sub.id = p.category_id
               LEFT JOIN categories top ON top.id = sub.parent_id
               ORDER BY top.sort, sub.sort, p.name"""))
        top_sellers = rows(conn.execute(
            """SELECT l.name, SUM(l.qty) AS qty, SUM(l.qty * (l.unit_price_cents + l.statiegeld_cents)) AS revenue
               FROM sale_lines l JOIN sales s ON s.id = l.sale_id
               WHERE s.store_id = ? GROUP BY l.name ORDER BY qty DESC LIMIT 10""", (STORE_ID,)))
    return render_template("admin.html", store=store, sales=sales, products=products,
                           today=today_stats, top_sellers=top_sellers)


@app.route("/admin/sales/<int:sale_id>")
def admin_receipt(sale_id):
    with get_db() as conn:
        receipt = build_receipt(conn, sale_id)
    if not receipt:
        abort(404)
    return render_template("receipt.html", r=receipt)


# --------------------------------------------------------------------------- API
@app.route("/api/catalog")
def api_catalog():
    """Alles wat de kassa nodig heeft in 1 call (later: lokaal cachen voor offline gebruik)."""
    with get_db() as conn:
        store = dict(conn.execute("SELECT * FROM stores WHERE id = ?", (STORE_ID,)).fetchone())
        cats = rows(conn.execute("SELECT * FROM categories ORDER BY sort, name"))
        tops = [c for c in cats if c["parent_id"] is None]
        for t in tops:
            t["subcategories"] = [c for c in cats if c["parent_id"] == t["id"]]
        parent_of = {c["id"]: c["parent_id"] for c in cats}
        products = rows(conn.execute(
            "SELECT * FROM products WHERE category_id IS NOT NULL ORDER BY name"))
        for p in products:
            # Product hangt aan een subcategorie of direct aan een hoofdcategorie
            parent = parent_of.get(p["category_id"])
            p["top_category_id"] = parent if parent is not None else p["category_id"]
    return jsonify({"store": store, "categories": tops, "products": products})


@app.route("/api/products/by-ean/<ean>")
def api_product_by_ean(ean):
    with get_db() as conn:
        p = conn.execute("SELECT * FROM products WHERE ean = ?", (ean.strip(),)).fetchone()
    if not p:
        return jsonify({"error": "Onbekende barcode"}), 404
    return jsonify(dict(p))


@app.route("/api/payments/pin", methods=["POST"])
def api_pin_payment():
    """GESIMULEERDE pinbetaling. Later: Mollie/Adyen Terminal API.

    Levert een fake transactiereferentie; de kassa doet zelf de 'wacht op kaart'-animatie.
    """
    body = request.get_json(force=True) or {}
    amount = int(body.get("amount_cents", 0))
    if amount <= 0:
        return jsonify({"status": "declined", "error": "Ongeldig bedrag"}), 400
    ref = "SIM-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + "".join(random.choices(string.digits, k=4))
    return jsonify({
        "status": "approved",
        "ref": ref,
        "terminal_id": "SIM-TERM-01",
        "brand": random.choice(["Maestro", "V PAY", "Mastercard", "Visa"]),
        "card_masked": "**** **** **** " + "".join(random.choices(string.digits, k=4)),
        "amount_cents": amount,
    })


@app.route("/api/sales", methods=["POST"])
def api_create_sale():
    """Slaat een verkoop op. Prijzen komen uit de database, niet van de client."""
    body = request.get_json(force=True) or {}
    items = body.get("lines") or []
    payment = body.get("payment") or {}
    if not items:
        return jsonify({"error": "Lege bon"}), 400

    with get_db() as conn:
        lines = []
        for it in items:
            p = conn.execute("SELECT * FROM products WHERE id = ?", (int(it["product_id"]),)).fetchone()
            qty = int(it.get("qty", 1))
            if not p or qty <= 0:
                return jsonify({"error": f"Ongeldige regel: {it}"}), 400
            lines.append({
                "product_id": p["id"], "name": p["name"], "qty": qty,
                "unit_price_cents": p["price_cents"], "btw_pct": p["btw_pct"],
                "statiegeld_cents": p["statiegeld_cents"],
            })
        goods = sum(l["qty"] * l["unit_price_cents"] for l in lines)
        statiegeld = sum(l["qty"] * l["statiegeld_cents"] for l in lines)
        total = goods + statiegeld

        cur = conn.execute(
            "INSERT INTO sales (store_id, total_cents, statiegeld_cents, payment_method, payment_ref) VALUES (?, ?, ?, ?, ?)",
            (STORE_ID, total, statiegeld, payment.get("method", "pin"), payment.get("ref")))
        sale_id = cur.lastrowid
        for l in lines:
            conn.execute(
                """INSERT INTO sale_lines (sale_id, product_id, name, qty, unit_price_cents, btw_pct, statiegeld_cents)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sale_id, l["product_id"], l["name"], l["qty"], l["unit_price_cents"], l["btw_pct"], l["statiegeld_cents"]))
            conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (l["qty"], l["product_id"]))
        receipt = build_receipt(conn, sale_id)
    return jsonify(receipt), 201


@app.route("/api/sales/<int:sale_id>")
def api_sale(sale_id):
    with get_db() as conn:
        receipt = build_receipt(conn, sale_id)
    if not receipt:
        abort(404)
    return jsonify(receipt)


# --------------------------------------------------------------------------- start
init_schema()
if not is_seeded():
    seed()
    print("Demodata geladen.")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
