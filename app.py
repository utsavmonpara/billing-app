from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

DB_NAME = "billing.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            rate REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/save_invoice", methods=["POST"])
def save_invoice():
    items = request.json.get("items", [])
    total = request.json.get("total", 0)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO invoices (created_at, total) VALUES (?, ?)", (created_at, total))
    invoice_id = cur.lastrowid

    for item in items:
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, product_name, quantity, rate, line_total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            invoice_id,
            item.get("product_name"),
            int(item.get("quantity", 0)),
            float(item.get("rate", 0)),
            float(item.get("line_total", 0)),
        ))

    conn.commit()
    conn.close()

    return {"success": True, "invoice_id": invoice_id}


@app.route("/history")
def history():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, total FROM invoices ORDER BY id DESC")
    invoices = cur.fetchall()
    conn.close()
    return render_template("history.html", invoices=invoices)


@app.route("/invoice/<int:invoice_id>")
def invoice_detail(invoice_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, created_at, total FROM invoices WHERE id = ?", (invoice_id,))
    invoice = cur.fetchone()

    cur.execute("""
        SELECT product_name, quantity, rate, line_total
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,))
    items = cur.fetchall()

    conn.close()
    if not invoice:
        return "Invoice not found", 404

    return render_template("invoice_detail.html", invoice=invoice, items=items)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
