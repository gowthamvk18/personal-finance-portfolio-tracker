# Personal Finance Portfolio Tracker

> **Full-Stack Academic Capstone Project**  
> Built with Python Flask, SQLAlchemy, SQLite/MySQL, Bootstrap 5, Chart.js, and ReportLab.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gowthamvk18/personal-finance-portfolio-tracker)
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/gowthamvk18/personal-finance-portfolio-tracker&branch=master&name=finance-tracker)

![GitHub Repo](https://img.shields.io/badge/GitHub-gowthamvk18%2Fpersonal--finance--portfolio--tracker-blue?logo=github)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![Tests](https://img.shields.io/badge/Tests-31%20Passed-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Quick Permanent Cloud Deployment

Click either button below to deploy this application to the cloud with a **permanent 24/7 live link**:

1. **[Deploy to Render (Permanent Free Hosting)](https://render.com/deploy?repo=https://github.com/gowthamvk18/personal-finance-portfolio-tracker)**
   - Click the button or link above.
   - Sign in with your GitHub account (`gowthamvk18`).
   - Click **Apply Blueprint**.
   - Render automatically builds the dependencies, executes `seed_data.py`, and assigns your permanent 24/7 URL (e.g. `https://personal-finance-tracker-xxxx.onrender.com`).

2. **[Deploy to Koyeb (Global Cloud Serverless)](https://app.koyeb.com/deploy?type=git&repository=github.com/gowthamvk18/personal-finance-portfolio-tracker&branch=master&name=finance-tracker)**
   - Click the link, authenticate with GitHub, and launch.
   - Provides an instant permanent `https://<app-name>.koyeb.app` URL.

---

## 1. Project Overview

The **Personal Finance Portfolio Tracker** is a production-ready, full-stack financial management web application designed for comprehensive personal wealth monitoring. It provides real-time income and expense tracking, categorical monthly budget enforcement with early warning thresholds, milestone-driven savings goals, multi-asset investment tracking (Stocks, Mutual Funds, Fixed Deposits, Gold), dynamic net worth valuation, and downloadable financial audit statements (CSV & PDF).

The application enforces **strict user data isolation**, uses **Python `Decimal` precision** to eliminate floating-point arithmetic errors, and recalculates all metrics on the backend service layer.

---

## 2. Technology Stack

### Frontend
- **HTML5 & CSS3**: Custom responsive styling with dark navy sidebar navigation (`#0f172a`) and light dashboard (`#f8fafc`).
- **Bootstrap 5.3.3**: Grid layout, responsive utilities, modals, form controls, and toasts.
- **Chart.js 4.4.2**: Interactive financial visualizations (Bar, Line, Doughnut, Pie, and Horizontal Bar charts).
- **Font Awesome 6.5.1**: Modern iconography.
- **Vanilla JavaScript (ES6+)**: Dynamic form filtering, responsive drawer toggle, and asynchronous API chart loaders.

### Backend
- **Python 3.12**: Core server runtime.
- **Flask 3.1**: Lightweight, scalable WSGI web application framework utilizing the Application Factory Pattern and Blueprints.
- **Flask-SQLAlchemy 3.1**: Object-Relational Mapping (ORM) and relational database query construction.
- **Flask-Login 0.6.3**: Session management, user authentication, and route guards.
- **Flask-WTF 1.3 & WTForms 3.3**: Form validation, CSRF protection, and input sanitization.
- **Werkzeug 3.1**: Cryptographic password hashing (`scrypt`).
- **Python `Decimal`**: Standard library high-precision decimal calculations.
- **ReportLab 5.1**: Programmatic, enterprise-grade PDF report compilation with custom styling and table grids.

### Database
- **SQLite**: Local development default (zero-configuration file-based storage in `instance/finance_tracker.db`).
- **MySQL / PostgreSQL Ready**: Built strictly with SQLAlchemy ORM abstraction for instant migration to MySQL via environment variables.

---

## 3. Architecture & Directory Structure

```text
personal_finance_tracker/
├── app/
│   ├── __init__.py               # Flask application factory (create_app), extensions, context processors
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py               # User and UserSettings models
│   │   ├── transaction.py        # Transaction model (Income/Expense, Categories, Payment methods)
│   │   ├── budget.py             # Monthly category budget model
│   │   ├── savings.py            # SavingsGoal and SavingsContribution models
│   │   ├── investment.py         # Investment holding model (Stocks, MFs, FDs, Gold)
│   │   └── liability.py          # Liability model (Loans, Credit Cards, Debts)
│   ├── routes/                   # Modular Flask blueprints
│   │   ├── __init__.py
│   │   ├── auth.py               # Registration, login, logout routes
│   │   ├── dashboard.py          # Summary cards, charts, and activity feeds
│   │   ├── transactions.py       # Full CRUD, filtering, search, and pagination
│   │   ├── budgets.py            # Budget creation, utilization tracking, alerts
│   │   ├── savings.py            # Savings goals, target dates, contribution logging
│   │   ├── investments.py        # Holdings CRUD, price updates, market sync simulation
│   │   ├── analytics.py          # Portfolio analytics, performance comparison, allocation
│   │   ├── reports.py            # Report dashboard, CSV export, PDF downloads
│   │   ├── settings.py           # Profile, password, preferences, liabilities
│   │   └── api.py                # REST JSON endpoints for Chart.js
│   ├── services/                 # Pure business logic & calculation services
│   │   ├── __init__.py
│   │   ├── financial_service.py  # Cash balance, budget utilization, Net Worth calculations
│   │   ├── portfolio_service.py  # Portfolio P&L, returns %, asset allocation, rankings
│   │   └── report_service.py     # CSV builder and ReportLab PDF document builder
│   ├── forms/                    # Flask-WTF validation forms
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── transaction_forms.py
│   │   ├── budget_forms.py
│   │   ├── savings_forms.py
│   │   ├── investment_forms.py
│   │   ├── liability_forms.py
│   │   └── settings_forms.py
│   ├── templates/                # Jinja2 template components
│   │   ├── base.html             # Master layout with collapsible sidebar & header
│   │   ├── auth/                 # Sign in and registration
│   │   ├── dashboard/            # Executive summary dashboard
│   │   ├── transactions/         # Ledger, filter controls, form modals
│   │   ├── budgets/              # Budget cards, progress bars, warning badges
│   │   ├── savings/              # Savings goals and contribution modal
│   │   ├── investments/          # Holdings table, price editor modal
│   │   ├── analytics/            # Performance rankings and allocation charts
│   │   ├── reports/              # Interactive reports viewer and download actions
│   │   ├── settings/             # User profile, display settings, liabilities
│   │   └── errors/               # 404, 500, 403 custom error pages
│   └── static/
│       ├── css/style.css         # Modern fintech design styles
│       └── js/
│           ├── main.js           # UI interactions, category switchers, alerts
│           └── charts.js         # Dynamic Chart.js API asynchronous hooks
├── tests/                        # Automated Pytest Suite
│   ├── __init__.py
│   ├── conftest.py               # Test app, client, in-memory DB, auth fixtures
│   ├── test_auth.py              # Authentication and authorization guards
│   ├── test_transactions.py      # Transaction CRUD, amounts, filters
│   ├── test_budgets.py           # Budget calculations and 80%/100% alert thresholds
│   ├── test_savings.py           # Goals, contributions, milestone completions
│   ├── test_investments.py       # P&L, return %, FD & Gold formulas
│   ├── test_isolation.py         # Multi-tenant data partition and security isolation
│   ├── test_net_worth.py         # Assets - Liabilities formula
│   └── test_reports.py           # CSV and PDF exports
├── config.py                     # Development, Testing, and Production configurations
├── requirements.txt              # Pinned Python package dependencies
├── run.py                        # Application entry point and CLI commands
├── seed_data.py                  # Realistic demo data populator
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclusions
└── README.md                     # Comprehensive system documentation
```

---

## 4. Financial Calculation Principles & Formulas

To ensure complete academic and financial rigor, calculations never trust frontend submissions and are executed using Python's `Decimal` module:

### 1. Liquid Cash Balance
$$\text{Cash Balance} = \sum \text{All-Time Incomes} - \sum \text{All-Time Expenses}$$

### 2. Investment Valuation & Returns
- **Invested Value**:
  $$\text{Invested Value} = \text{Quantity} \times \text{Purchase Price}$$
- **Current Value**:
  $$\text{Current Value} = \text{Quantity} \times \text{Current Price}$$
- **Profit / Loss (P&L)**:
  $$\text{Profit/Loss} = \text{Current Value} - \text{Invested Value}$$
- **Return Percentage**:
  $$\text{Return \%} = \left( \frac{\text{Profit/Loss}}{\text{Invested Value}} \right) \times 100$$
- **Gold Valuation**: Supports quantity in exact grams ($g$) and current price per gram.
- **Fixed Deposits**: Tracks principal invested, annual interest rate ($\%$ p.a.), and calculated maturity value.

### 3. Net Worth Calculation
$$\text{Net Worth} = \text{Total Assets} - \text{Total Liabilities}$$
- **Total Assets**:
  $$\text{Total Assets} = \text{Liquid Cash Balance} + \sum \text{Current Value of Investments}$$
  *(Double-counting prevention: Income deposits increase cash balance; investment holdings reflect deployed capital valuation independently).*
- **Total Liabilities**:
  $$\text{Total Liabilities} = \sum \text{Remaining Balances on Active Loans, Credit Cards, and Debts}$$

### 4. Budget Utilization & Warning Thresholds
$$\text{Utilization \%} = \left( \frac{\text{Actual Category Spending}}{\text{Allocated Monthly Budget}} \right) \times 100$$
- **Normal Status**: $\text{Utilization} < 80\%$ (Green progress indicator)
- **Warning Alert**: $80\% \le \text{Utilization} < 100\%$ (Amber caution badge)
- **Critical Alert**: $\text{Utilization} \ge 100\%$ (Red overspending banner with alert notification)

---

## 5. Getting Started & Local Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Git

### Step 1: Clone or Navigate to Project Directory
```bash
cd "c:\Users\ADARS\Downloads\java cps"
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Or Windows Command Prompt (CMD)
.\venv\Scripts\activate.bat

# Or Linux / macOS
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Default SQLite database path will be automatically configured inside the `instance/` folder.

---

## 6. Database Initialization & Demo Data

The project includes an automated demo database seeder that creates realistic financial history across 6 months, populated with salary credits, freelance consulting milestones, categorised bills, monthly budgets, savings goals with contributions, stocks (TCS, HDFC Bank, Reliance), mutual funds, a 7.10% SBI fixed deposit, 24K sovereign gold, and vehicle loan liabilities.

### Run Demo Seeder
```bash
python seed_data.py
```
*(Or via Flask CLI: `flask seed-data`)*

### Demo Account Credentials
- **Email:** `demo@example.com`
- **Password:** `Password123!`

---

## 7. Running the Application

Start the local Flask development server:
```bash
python run.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```
Log in using the demo account credentials or register a new user.

---

## 8. Executing the Automated Test Suite

The application includes a comprehensive test suite covering authentication, authorization, CRUD operations, decimal calculations, budget warning thresholds, savings milestones, investment analytics, Net Worth formulas, user data isolation, and CSV/PDF export.

Run all tests via pytest:
```bash
pytest -v
```

### Test Coverage Summary:
- `tests/test_auth.py`: Registration, duplicate email rejection, password hashing, session login, logout, and protected route access control.
- `tests/test_transactions.py`: Income/expense recording, Decimal accuracy, invalid amount validation, editing, deletion, and category/type filtering.
- `tests/test_budgets.py`: Category budget creation, utilization computation, 80% warning triggers, and 100% critical alerts.
- `tests/test_savings.py`: Goals creation, contribution logging, remaining deficit, and automatic completion status triggers.
- `tests/test_investments.py`: Stock, mutual fund, FD, and Gold holding calculations; P&L and ROI percentage; manual price updates; asset allocation.
- `tests/test_net_worth.py`: Exact Assets vs Liabilities computation and negative cash flow resilience.
- `tests/test_isolation.py`: Cross-tenant security validation proving User A cannot view, mutate, or delete User B's financial records.
- `tests/test_reports.py`: Generation and download validation of CSV files and binary PDF documents.

---

## 9. Migration to MySQL / PostgreSQL

The application is structured using SQLAlchemy ORM so that it can transition to MySQL or PostgreSQL without modifying application source code:

1. Install MySQL driver:
   ```bash
   pip install pymysql cryptography
   ```
2. Update `DATABASE_URL` in your `.env` file:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/finance_portfolio_db
   ```
3. Run initialization:
   ```bash
   python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
   ```

---

## 10. Security & Financial Integrity Highlights

1. **Authentication & Password Protection**: Passwords are encrypted using modern `scrypt` hashing via Werkzeug.
2. **CSRF Defense**: All POST/PUT/DELETE forms and modals are protected using `Flask-WTF` CSRF tokens.
3. **Multi-Tenant Data Isolation**: Every database query filters by `user_id == current_user.id` to guarantee complete privacy.
4. **Backend Recalculation**: Financial totals, savings rates, and portfolio valuations are always recalculated on the backend; client-side values are never trusted.
5. **ReportLab PDF Engine**: High-fidelity PDF generation running directly in Python memory without external C-library dependencies.
