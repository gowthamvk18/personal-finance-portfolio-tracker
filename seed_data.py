import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User, UserSettings
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.savings import SavingsGoal, SavingsContribution
from app.models.investment import Investment
from app.models.liability import Liability


def seed_demo_data():
    """Seeds rich, realistic financial records for the demo user."""
    app = create_app("development")
    with app.app_context():
        # Create database tables if not exist
        db.create_all()

        demo_email = "demo@example.com"
        demo_user = User.query.filter_by(email=demo_email).first()

        if demo_user:
            print(f"Cleaning up existing demo user records for: {demo_email}")
            db.session.delete(demo_user)
            db.session.commit()

        print(f"Creating fresh demo account: {demo_email}")
        user = User(
            name="Adarsh Sharma",
            email=demo_email
        )
        user.set_password("Password123!")
        db.session.add(user)
        db.session.flush()

        # User settings
        settings = UserSettings(
            user_id=user.id,
            currency="INR",
            currency_symbol="₹",
            date_format="YYYY-MM-DD",
            budget_alert_threshold=80
        )
        db.session.add(settings)

        today = date.today()
        # Seed 6 months of historical transactions to populate charts beautifully
        print("Seeding 6 months of realistic transactions...")
        
        # Monthly base salary & recurring bills
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1

            # 1. Salary on the 1st
            t_salary = Transaction(
                user_id=user.id,
                transaction_type="income",
                amount=Decimal("125000.00"),
                category="Salary",
                description="Monthly Software Engineering Salary",
                transaction_date=date(y, m, 1),
                payment_method="Bank Transfer",
                notes="Net monthly credit after tax deduction"
            )
            db.session.add(t_salary)

            # 2. Freelance Consulting on the 15th
            if i in [0, 1, 3, 4]:
                t_freelance = Transaction(
                    user_id=user.id,
                    transaction_type="income",
                    amount=Decimal("35000.00"),
                    category="Freelancing",
                    description="Cloud Architecture Advisory Milestone",
                    transaction_date=date(y, m, 15),
                    payment_method="UPI",
                    notes="Direct client milestone payment"
                )
                db.session.add(t_freelance)

            # 3. Monthly Rent
            t_rent = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("32000.00"),
                category="Rent",
                description="Apartment Monthly Lease Payment",
                transaction_date=date(y, m, 2),
                payment_method="Bank Transfer",
                notes="Residential rent for 2BHK"
            )
            db.session.add(t_rent)

            # 4. Utilities & Bills
            t_bills = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("6200.00"),
                category="Bills",
                description="Electricity, High-Speed Broadband & Gas",
                transaction_date=date(y, m, 5),
                payment_method="UPI",
                notes="Utility bill clearances"
            )
            db.session.add(t_bills)

            # 5. Food & Groceries
            t_food1 = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("9400.00"),
                category="Food",
                description="Monthly Supermarket Grocery Haul",
                transaction_date=date(y, m, 8),
                payment_method="Debit Card",
                notes="Organic staples and household items"
            )
            t_food2 = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("4600.00"),
                category="Food",
                description="Weekend Dining & Cafes",
                transaction_date=date(y, m, 18),
                payment_method="Credit Card",
                notes="Restaurant dining with team"
            )
            db.session.add_all([t_food1, t_food2])

            # 6. Transport & Fuel
            t_trans = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("5200.00"),
                category="Transport",
                description="Fuel Refill & Metro Passes",
                transaction_date=date(y, m, 12),
                payment_method="Credit Card",
                notes="Daily commute transportation"
            )
            db.session.add(t_trans)

            # 7. Entertainment & Subscriptions
            t_ent = Transaction(
                user_id=user.id,
                transaction_type="expense",
                amount=Decimal("2800.00"),
                category="Entertainment",
                description="Streaming Services & Cinema Tickets",
                transaction_date=date(y, m, 20),
                payment_method="Credit Card",
                notes="Netflix, Spotify & weekend movie"
            )
            db.session.add(t_ent)

            # 8. Shopping / Tech
            if i in [0, 2, 4]:
                t_shop = Transaction(
                    user_id=user.id,
                    transaction_type="expense",
                    amount=Decimal("11500.00"),
                    category="Shopping",
                    description="Electronics Accessories & Apparel",
                    transaction_date=date(y, m, 24),
                    payment_method="Credit Card",
                    notes="Ergonomic keyboard and clothes"
                )
                db.session.add(t_shop)

        # Additional current month transactions
        cur_month_str = today.strftime("%Y-%m")
        t_cur_interest = Transaction(
            user_id=user.id,
            transaction_type="income",
            amount=Decimal("3850.00"),
            category="Interest",
            description="Quarterly Savings Bank & FD Interest Credit",
            transaction_date=date(today.year, today.month, 10),
            payment_method="Bank Transfer",
            notes="Direct interest disbursement"
        )
        db.session.add(t_cur_interest)

        print("Seeding monthly budgets with realistic warning/critical thresholds...")
        # Monthly Budgets for current month
        budgets_data = [
            ("Food", Decimal("18000.00"), "Groceries and restaurant budget"),
            ("Rent", Decimal("35000.00"), "House rent ceiling"),
            ("Transport", Decimal("6000.00"), "Fuel, cabs and metro fares"),
            ("Shopping", Decimal("12000.00"), "Personal and home shopping limit"),
            ("Bills", Decimal("7000.00"), "Electricity, water, gas, internet"),
            ("Entertainment", Decimal("4000.00"), "Movies, subscriptions, recreation")
        ]

        for cat, amt, note in budgets_data:
            b = Budget(
                user_id=user.id,
                category=cat,
                amount=amt,
                month_year=cur_month_str,
                notes=note
            )
            db.session.add(b)

        print("Seeding savings goals & historical contributions...")
        # Savings Goals
        g1 = SavingsGoal(
            user_id=user.id,
            name="Emergency Fund (6 Months Expenses)",
            target_amount=Decimal("300000.00"),
            current_amount=Decimal("240000.00"),
            target_date=today + timedelta(days=90),
            status="in_progress",
            notes="Liquid high-interest savings emergency buffer"
        )
        g2 = SavingsGoal(
            user_id=user.id,
            name="MacBook Pro M3 Max",
            target_amount=Decimal("250000.00"),
            current_amount=Decimal("250000.00"),
            target_date=today - timedelta(days=10),
            status="completed",
            notes="High performance developer workstation"
        )
        g3 = SavingsGoal(
            user_id=user.id,
            name="Higher Education / AI Specialization",
            target_amount=Decimal("150000.00"),
            current_amount=Decimal("85000.00"),
            target_date=today + timedelta(days=180),
            status="in_progress",
            notes="Professional certifications & graduate coursework"
        )
        g4 = SavingsGoal(
            user_id=user.id,
            name="International Vacation to Japan",
            target_amount=Decimal("200000.00"),
            current_amount=Decimal("110000.00"),
            target_date=today + timedelta(days=240),
            status="in_progress",
            notes="Tokyo & Kyoto autumn tour fund"
        )
        db.session.add_all([g1, g2, g3, g4])
        db.session.flush()

        # Contributions
        c1 = SavingsContribution(
            goal_id=g1.id,
            amount=Decimal("40000.00"),
            contribution_date=today - timedelta(days=25),
            notes="Monthly savings allocation"
        )
        c2 = SavingsContribution(
            goal_id=g3.id,
            amount=Decimal("20000.00"),
            contribution_date=today - timedelta(days=15),
            notes="Freelance income surplus"
        )
        db.session.add_all([c1, c2])

        print("Seeding investment holdings across Stocks, Mutual Funds, FDs, and Gold...")
        # 1. Stocks
        inv_stock1 = Investment(
            user_id=user.id,
            name="Tata Consultancy Services (TCS)",
            investment_type="stocks",
            quantity=Decimal("45.0000"),
            purchase_price=Decimal("3650.00"),
            current_price=Decimal("4120.00"),
            purchase_date=today - timedelta(days=320),
            institution="Zerodha",
            notes="Blue-chip Indian IT bellwether"
        )
        inv_stock2 = Investment(
            user_id=user.id,
            name="HDFC Bank Ltd",
            investment_type="stocks",
            quantity=Decimal("120.0000"),
            purchase_price=Decimal("1520.00"),
            current_price=Decimal("1745.00"),
            purchase_date=today - timedelta(days=210),
            institution="Zerodha",
            notes="Core banking and financial services leader"
        )
        inv_stock3 = Investment(
            user_id=user.id,
            name="Reliance Industries Ltd",
            investment_type="stocks",
            quantity=Decimal("60.0000"),
            purchase_price=Decimal("2780.00"),
            current_price=Decimal("2960.00"),
            purchase_date=today - timedelta(days=150),
            institution="Groww",
            notes="Energy, telecom, and retail conglomerate"
        )

        # 2. Mutual Funds
        inv_mf1 = Investment(
            user_id=user.id,
            name="Parag Parikh Flexi Cap Fund",
            investment_type="mutual_funds",
            quantity=Decimal("2450.5000"),
            purchase_price=Decimal("62.40"),
            current_price=Decimal("78.10"),
            purchase_date=today - timedelta(days=400),
            institution="Groww",
            notes="Diversified equity with international exposure"
        )
        inv_mf2 = Investment(
            user_id=user.id,
            name="Mirae Asset Large Cap Fund",
            investment_type="mutual_funds",
            quantity=Decimal("1800.0000"),
            purchase_price=Decimal("94.20"),
            current_price=Decimal("112.50"),
            purchase_date=today - timedelta(days=280),
            institution="Groww",
            notes="Top 100 Indian enterprise equity fund"
        )

        # 3. Fixed Deposits
        inv_fd1 = Investment(
            user_id=user.id,
            name="SBI 1-Year Special Term Deposit",
            investment_type="fixed_deposits",
            quantity=Decimal("1.0000"),
            purchase_price=Decimal("200000.00"),
            current_price=Decimal("214200.00"),
            purchase_date=today - timedelta(days=220),
            institution="State Bank of India",
            interest_rate=Decimal("7.10"),
            maturity_date=today + timedelta(days=145),
            notes="Guaranteed capital preservation with compounding interest"
        )

        # 4. Gold
        inv_gold1 = Investment(
            user_id=user.id,
            name="24K Sovereign Gold Bond (SGB)",
            investment_type="gold",
            quantity=Decimal("25.0000"),  # 25 grams
            purchase_price=Decimal("6100.00"),  # buy price per gram
            current_price=Decimal("7350.00"),  # current price per gram
            purchase_date=today - timedelta(days=360),
            institution="Reserve Bank of India (RBI)",
            notes="25 grams sovereign digital gold tranche with 2.5% semi-annual interest"
        )

        db.session.add_all([inv_stock1, inv_stock2, inv_stock3, inv_mf1, inv_mf2, inv_fd1, inv_gold1])

        print("Seeding sample liabilities...")
        # Liabilities (Vehicle loan)
        liab1 = Liability(
            user_id=user.id,
            name="Electric Vehicle Loan (Tata Nexon EV)",
            liability_type="vehicle_loan",
            total_amount=Decimal("600000.00"),
            remaining_amount=Decimal("280000.00"),
            interest_rate=Decimal("8.65"),
            due_date=today + timedelta(days=500),
            institution="HDFC Bank",
            notes="Monthly EMI of 14,800 auto-debited"
        )
        db.session.add(liab1)

        db.session.commit()
        print("Demo data seeded successfully!")
        print("-" * 50)
        print("Demo Account Credentials:")
        print(f"Email:    {demo_email}")
        print("Password: Password123!")
        print("-" * 50)


if __name__ == "__main__":
    seed_demo_data()
