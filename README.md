# 💳 Smart Billing Web App

A fully functional, production-ready billing application built with **Python Flask** and **JavaScript**. Create invoices, manage items, track invoice history, and view detailed bills with a clean, modern UI.

## ✨ Features

✅ **Add/Edit/Delete Items** - Dynamically manage products with quantity and rate
✅ **Real-time Calculation** - Automatic line total and grand total updates
✅ **Invoice Management** - Save invoices to SQLite database
✅ **Invoice History** - View all past invoices with date and total
✅ **Detailed Invoice View** - Display complete invoice details with items and totals
✅ **Print Support** - Print invoices directly from the browser
✅ **Modern UI/UX** - Beautiful, responsive design with smooth animations
✅ **SQLite Database** - Persistent storage for all invoices and items

## 🛠️ Tech Stack

- **Backend**: Python Flask 3.0.0
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite3
- **Server**: Gunicorn 21.2.0
- **Deployment**: Render.com

## 📁 Project Structure

```
billing-app/
├── app.py                 # Flask backend with routes
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment configuration
├── templates/
│   ├── index.html        # Main billing form
│   ├── history.html      # Invoice history page
│   └── invoice_detail.html # Individual invoice view
└── static/
    └── css/
        └── style.css     # Application styles
```

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/utsavmonpara/billing-app.git
   cd billing-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://127.0.0.1:5000`

## 📤 Deploy to Render

### Step-by-Step Deployment

1. **Push code to GitHub**
   - Create a repository on GitHub
   - Push your code: `git push origin main`

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub account

3. **Create New Web Service**
   - Click "New" → "Web Service"
   - Select your GitHub repository
   - Choose "billing-app" repository

4. **Configure Deployment Settings**
   - **Name**: billing-app (or any name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free tier (or paid for better performance)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

### Environment Variables (if needed)

No environment variables required for basic setup. The app uses SQLite which stores data locally.

## 💡 How to Use

1. **Create Invoice**
   - Enter Product Name, Quantity, and Rate
   - Click "Add Item"
   - Repeat to add more items
   - Total updates automatically

2. **Manage Items**
   - Click "Delete" to remove any item
   - Click "Clear All" to start fresh

3. **Save Invoice**
   - Click "Save Invoice"
   - Invoice is stored in database
   - You'll get a confirmation with Invoice ID

4. **View History**
   - Click "Invoice History" in top-right
   - See all past invoices
   - Click "View Details" to see complete invoice

5. **Print Invoice**
   - On invoice detail page, click "Print Invoice"
   - Use browser print dialog (Ctrl+P or Cmd+P)

## 🗄️ Database Schema

### invoices table
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    total REAL NOT NULL
)
```

### invoice_items table
```sql
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    rate REAL NOT NULL,
    line_total REAL NOT NULL,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
)
```

## 📝 API Endpoints

- `GET /` - Main billing page
- `POST /save_invoice` - Save invoice to database
- `GET /history` - View all invoices
- `GET /invoice/<id>` - View specific invoice details

## 🎨 UI/UX Features

- Responsive design works on desktop, tablet, mobile
- Smooth animations and transitions
- Color-coded buttons (Primary, Secondary, Success, Danger)
- Real-time calculation with no page refresh
- Confirmation dialogs for destructive actions
- Currency symbol (₹) for Indian Rupees

## 🔒 Security Notes

- SQLite database file (`billing.db`) is local to server
- No sensitive authentication required for demo
- For production: Add user login, HTTPS, input validation

## 🐛 Troubleshooting

**App won't start locally**
- Ensure Python 3.8+ is installed
- Check Flask is installed: `pip install Flask`

**Render deployment fails**
- Verify `requirements.txt` has all dependencies
- Check `Procfile` format (no extra spaces)
- View logs in Render dashboard

**Database errors**
- Delete `billing.db` to reset database
- App will recreate it on next run

## 📦 Future Enhancements

- [ ] User authentication & multi-user support
- [ ] PDF export of invoices
- [ ] Email invoice functionality
- [ ] GST/Tax calculations
- [ ] Customer management
- [ ] Invoice templates
- [ ] Payment tracking

## 📄 License

Open source - feel free to use and modify

## 👨‍💻 Author

Created by **Utsav Monpara**

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

---

**Made with ❤️ for simplifying billing**
