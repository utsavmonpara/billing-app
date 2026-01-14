from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, template_folder="templates", static_folder="static")
DB_NAME = "billing.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables_exist():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_email TEXT,
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
            cost_price REAL DEFAULT 0,
            line_total REAL NOT NULL,
            profit REAL DEFAULT 0,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL UNIQUE,
            cost_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            margin_percentage REAL,
            created_at TEXT NOT NULL
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS profit_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            total_selling_price REAL NOT NULL,
            total_cost_price REAL NOT NULL,
            total_profit REAL NOT NULL,
            profit_percentage REAL,
            invoice_date TEXT NOT NULL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
        """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")

ensure_tables_exist()

# PRODUCT MANAGEMENT
@app.route("/products")
def products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY product_name ASC")
        products_list = cur.fetchall()
        conn.close()
        return render_template("products.html", products=products_list)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        data = request.get_json()
        product_name = data.get("product_name", "")
        cost_price = float(data.get("cost_price", 0))
        selling_price = float(data.get("selling_price", 0))
        margin = ((selling_price - cost_price) / selling_price * 100) if selling_price > 0 else 0
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO products (product_name, cost_price, selling_price, margin_percentage, created_at) VALUES (?, ?, ?, ?, ?)",
                (product_name, cost_price, selling_price, margin, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            product_id = cur.lastrowid
            conn.close()
            return jsonify({"success": True, "product_id": product_id})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "message": "Product already exists"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/get_products")
def get_products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        products_list = cur.fetchall()
        conn.close()
        return jsonify([dict(p) for p in products_list])
    except Exception as e:
        return jsonify({"success": False}), 500

# INVOICE ROUTES
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_invoice", methods=["POST"])
def save_invoice():
    try:
        data = request.get_json()
        items = data.get("items", [])
        total = data.get("total", 0)
        customer_name = data.get("customer_name", "Unknown")
        customer_email = data.get("customer_email", "")
        
        conn = get_db_connection()
        cur = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute("INSERT INTO invoices (customer_name, customer_email, created_at, total) VALUES (?, ?, ?, ?)",
            (customer_name, customer_email, created_at, total))
        invoice_id = cur.lastrowid
        
        total_cost = 0
        total_selling = 0
        
        for item in items:
            quantity = int(item.get("quantity", 0))
            rate = float(item.get("rate", 0))
            cost_price = float(item.get("cost_price", 0))
            line_total = rate * quantity
            item_profit = line_total - (cost_price * quantity)
            
            total_cost += cost_price * quantity
            total_selling += line_total
            
            cur.execute("INSERT INTO invoice_items (invoice_id, product_name, quantity, rate, cost_price, line_total, profit) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (invoice_id, item.get("product_name"), quantity, rate, cost_price, line_total, item_profit))
        
        total_profit = total_selling - total_cost
        profit_pct = (total_profit / total_selling * 100) if total_selling > 0 else 0
        
        cur.execute("INSERT INTO profit_summary (invoice_id, total_selling_price, total_cost_price, total_profit, profit_percentage, invoice_date) VALUES (?, ?, ?, ?, ?, ?)",
            (invoice_id, total_selling, total_cost, total_profit, profit_pct, created_at.split()[0]))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "invoice_id": invoice_id, "profit": total_profit})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/history")
def history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT i.id, i.customer_name, i.created_at, i.total, COALESCE(ps.total_profit, 0) as profit FROM invoices i LEFT JOIN profit_summary ps ON i.id = ps.invoice_id ORDER BY i.id DESC")
        invoices = cur.fetchall()
        conn.close()
        return render_template("history.html", invoices=invoices)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/invoice/<int:invoice_id>")
def 187
(invoice_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        invoice = cur.fetchone()
        cur.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        items = cur.fetchall()
        cur.execute("SELECT total_profit, profit_percentage FROM profit_summary WHERE invoice_id = ?", (invoice_id,))
        profit_data = cur.fetchone()
        conn.close()
        return render_template("invoice_detail.html", invoice=tuple(invoice) if invoice else None, items=items, profit_data=profit_data)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/profit_dashboard")
def profit_dashboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        year = datetime.now().strftime("%Y")
        
        cur.execute("SELECT COALESCE(SUM(total_profit), 0) as profit FROM profit_summary WHERE invoice_date = ?", (today,))
        daily_profit = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(SUM(total_profit), 0) as profit FROM profit_summary WHERE invoice_date LIKE ?", (f"{month}%",))
        monthly_profit = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(SUM(total_profit), 0) as profit FROM profit_summary WHERE invoice_date LIKE ?", (f"{year}%",))
        yearly_profit = cur.fetchone()[0]
        
        conn.close()
        return render_template("profit_dashboard.html", daily=daily_profit, monthly=monthly_profit, yearly=yearly_profit)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    ensure_tables_exist()
    app.run(debug=True)
