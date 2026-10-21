# InventoryPro - Enterprise Inventory Management System

**InventoryPro** is a secure, responsive, modular web-based inventory management application engineered for small and medium businesses. Built strictly following clean architecture principles, application factory pattern, and double-entry stock audit ledgers.

---

## Key Features

- **Double-Entry Stock Audit Ledger**: Every inventory change (Stock-In, Stock-Out, Adjustment) updates on-hand balances atomically within a database transaction and records an immutable chronological ledger record in `stock_movements`.
- **Role-Based Access Control (RBAC)**: Fine-grained authorization dividing users into `ADMIN`, `MANAGER`, and `STAFF` roles with route-level security decorators.
- **Dynamic Multi-Item Transactions**: Fast, responsive Vanilla JavaScript dynamic line-item interfaces for Stock-In (Receipts) and Stock-Out (Issues) with real-time browser-side stock limit checks.
- **Real-Time Financial Analytics**: Interactive Chart.js visualizations tracking 7-day movement velocity, stock volume distribution across categories, and full inventory valuation at cost basis vs. retail pricing.
- **PKR Default Currency**: Fully configured and formatted for Pakistani Rupees (`PKR 1,500.00`) with dynamic configuration via system settings.
- **Enterprise Security Hardening**:
  - Global CSRF protection on all mutating HTTP methods via Flask-WTF.
  - Hardened session cookies (`HttpOnly`, `SameSite=Lax`, secure cookie flags).
  - Werkzeug scrypt/pbkdf2 password hashing.
  - Parameterized ORM queries eliminating SQL injection.
  - Centralized error handlers for 400, 403, 404, and 500.
  - Rotating file and console logging.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.0.3, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- **Database**: SQLite (Development) / PostgreSQL-compatible schema
- **Frontend**: HTML5, CSS3 Custom Properties, Vanilla JavaScript (ES6+), Jinja2 Templates, Chart.js
- **Testing**: `pytest`, `pytest-flask`

---

## Directory Structure

```
InventoryPro/
├── app/
│   ├── blueprints/           # Modular route controllers & forms
│   │   ├── auth/             # Authentication & user profile
│   │   ├── dashboard/        # KPI metrics & Chart.js API
│   │   ├── products/         # Products, categories, suppliers
│   │   ├── inventory/        # Stock-In, Stock-Out, History, Alerts
│   │   ├── reports/          # Financial valuation & CSV exports
│   │   ├── users/            # User RBAC administration
│   │   └── settings/         # Dynamic system settings
│   ├── models/               # SQLAlchemy ORM models with constraints
│   ├── services/             # Pure Python domain logic & transactions
│   ├── static/               # CSS tokens, layout, and vanilla JS
│   ├── templates/            # Semantic Jinja2 responsive templates
│   └── utils/                # Security decorators, logging, exceptions
├── config.py                 # Multi-environment configurations
├── run.py                    # Application runner & CLI seed commands
├── requirements.txt          # Pinned Python package dependencies
├── .env.example              # Sanitized environment template
└── tests/                    # Unit, integration, and functional tests
```

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Virtual Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd InventoryPro

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and ensure SECRET_KEY is set
```

### 5. Seed Sample Data (Optional)
Populates sample categories, vendors, and products priced in PKR:
```bash
flask --app run.py seed-sample
```

### 6. Run Development Server
```bash
python run.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`
--

## Running the Automated Test Suite

Run the full automated test suite (unit, integration, and functional RBAC tests):
```bash
pytest -v
```
