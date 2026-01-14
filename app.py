from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

DB_NAME = "billing.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables_exist():
    """Ensure database tables exist, create if missing"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create invoices table with customer_name and customer_email
        cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_email TEXT,
        created_at TEXT NOT NULL,
        total REAL NOT NULL
        )
        """)
        
        # Create invoice_items table
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
    except Exception as e:
        print(f"Error ensuring tables exist: {str(e)}")

# Ensure tables exist when app starts
ensure_tables_exist()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_invoice", methods=["POST"])
def save_invoice():
    try:
        ensure_tables_exist()  # Ensure tables exist before saving
        data = request.get_json()
        items = data.get("items", [])
        total = data.get("total", 0)
        customer_name = data.get("customer_name", "Unknown Customer")
        customer_email = data.get("customer_email", "")
        
        if not items:
            return jsonify({"success": False, "message": "No items to save"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert invoice with customer information
        cur.execute(
            "INSERT INTO invoices (customer_name, customer_email, created_at, total) VALUES (?, ?, ?, ?)",
            (customer_name, customer_email, created_at, total)
        )
        invoice_id = cur.lastrowid
        
        # Insert invoice items
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
        
        return jsonify({"success": True, "invoice_id": invoice_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/history")
def history():
    try:
        ensure_tables_exist()  # Ensure tables exist before querying
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Select invoices with customer_name
        cur.execute("SELECT id, customer_name, created_at, total FROM invoices ORDER BY id DESC")
        invoices = cur.fetchall()
        conn.close()
        
        return render_template("history.html", invoices=invoices)
    except Exception as e:
        print(f"Error in history: {str(e)}")
        return f"Error loading history: {str(e)}", 500

@app.route("/invoice/<int:invoice_id>")
def invoice_detail(invoice_id):
    try:
        ensure_tables_exist()  # Ensure tables exist before querying
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, customer_name, customer_email, created_at, total FROM invoices WHERE id = ?", (invoice_id,))
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
    except Exception as e:
        print(f"Error in invoice_detail: {str(e)}")
        return f"Error loading invoice: {str(e)}", 500

if __name__ == "__main__":
    ensure_tables_exist()
    app.run(debug=True)
