import io
import csv
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func, extract

from app import db
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.investment import Investment
from app.models.liability import Liability
from app.services.financial_service import FinancialService
from app.services.portfolio_service import PortfolioService

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


class ReportService:
    """Service layer for financial reporting, CSV export, and PDF generation."""

    @staticmethod
    def get_report_data(user_id, report_type, start_date=None, end_date=None, year=None, month=None):
        """Fetch structured report data based on report type and filters."""
        today = date.today()
        if not start_date:
            start_date = date(today.year, 1, 1)
        if not end_date:
            end_date = today

        if report_type == "daily_summary":
            target_date = end_date
            transactions = Transaction.query.filter_by(
                user_id=user_id,
                transaction_date=target_date
            ).order_by(Transaction.created_at.desc()).all()

            income_total = sum((t.decimal_amount for t in transactions if t.is_income), Decimal("0.00"))
            expense_total = sum((t.decimal_amount for t in transactions if t.is_expense), Decimal("0.00"))

            return {
                "title": f"Daily Financial Summary - {target_date.strftime('%d %B %Y')}",
                "report_type": report_type,
                "target_date": target_date,
                "income_total": income_total,
                "expense_total": expense_total,
                "net_total": income_total - expense_total,
                "transactions": transactions,
                "count": len(transactions)
            }

        elif report_type == "monthly_income":
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "income",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).order_by(Transaction.transaction_date.desc()).all()

            cat_summary = db.session.query(
                Transaction.category,
                func.sum(Transaction.amount).label("total")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "income",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).group_by(Transaction.category).all()

            total_income = sum((t.decimal_amount for t in transactions), Decimal("0.00"))

            return {
                "title": f"Income Report ({start_date} to {end_date})",
                "report_type": report_type,
                "transactions": transactions,
                "categories": [{"category": c, "total": Decimal(str(tot))} for c, tot in cat_summary],
                "total_income": total_income,
                "count": len(transactions)
            }

        elif report_type == "monthly_expense":
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).order_by(Transaction.transaction_date.desc()).all()

            total_expense = sum((t.decimal_amount for t in transactions), Decimal("0.00"))

            return {
                "title": f"Expense Report ({start_date} to {end_date})",
                "report_type": report_type,
                "transactions": transactions,
                "total_expense": total_expense,
                "count": len(transactions)
            }

        elif report_type == "category_expense":
            cat_summary = db.session.query(
                Transaction.category,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

            total_expense = sum((Decimal(str(tot)) for _, _, tot in cat_summary), Decimal("0.00"))

            categories = []
            for cat, cnt, tot in cat_summary:
                tot_dec = Decimal(str(tot))
                pct = ((tot_dec / total_expense) * Decimal("100.00")).quantize(Decimal("0.1")) if total_expense > 0 else Decimal("0.0")
                categories.append({
                    "category": cat,
                    "count": cnt,
                    "total": tot_dec,
                    "percentage": float(pct)
                })

            return {
                "title": f"Category-wise Expense Breakdown ({start_date} to {end_date})",
                "report_type": report_type,
                "categories": categories,
                "total_expense": total_expense
            }

        elif report_type == "annual_summary":
            target_year = year or today.year
            monthly_data = []
            annual_income = Decimal("0.00")
            annual_expense = Decimal("0.00")

            for m in range(1, 13):
                m_str = f"{target_year}-{m:02d}"
                inc = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "income",
                    extract("year", Transaction.transaction_date) == target_year,
                    extract("month", Transaction.transaction_date) == m
                ).scalar()

                exp = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "expense",
                    extract("year", Transaction.transaction_date) == target_year,
                    extract("month", Transaction.transaction_date) == m
                ).scalar()

                inc_dec = Decimal(str(inc)).quantize(Decimal("0.01"))
                exp_dec = Decimal(str(exp)).quantize(Decimal("0.01"))
                savings_dec = inc_dec - exp_dec

                annual_income += inc_dec
                annual_expense += exp_dec

                monthly_data.append({
                    "month": datetime(target_year, m, 1).strftime("%B"),
                    "month_code": m_str,
                    "income": inc_dec,
                    "expense": exp_dec,
                    "savings": savings_dec
                })

            return {
                "title": f"Annual Financial Summary - {target_year}",
                "report_type": report_type,
                "year": target_year,
                "monthly_data": monthly_data,
                "annual_income": annual_income,
                "annual_expense": annual_expense,
                "annual_savings": annual_income - annual_expense
            }

        elif report_type == "investment_performance":
            portfolio = PortfolioService.get_portfolio_summary(user_id)
            return {
                "title": "Investment Portfolio Performance Report",
                "report_type": report_type,
                "portfolio": portfolio
            }

        elif report_type == "net_worth":
            net_worth_data = FinancialService.get_net_worth(user_id)
            liabilities = Liability.query.filter_by(user_id=user_id).all()
            return {
                "title": f"Net Worth Statement - As of {today.strftime('%d %B %Y')}",
                "report_type": report_type,
                "net_worth": net_worth_data,
                "liabilities": liabilities
            }

        elif report_type == "budget_utilization":
            m_code = f"{year or today.year}-{month or today.month:02d}"
            budget_data = FinancialService.get_budget_utilization(user_id, m_code)
            return {
                "title": f"Budget Utilization Report - {m_code}",
                "report_type": report_type,
                "budget_data": budget_data
            }

        else:
            # Default to all transactions summary
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            ).order_by(Transaction.transaction_date.desc()).all()
            return {
                "title": f"Transaction Report ({start_date} to {end_date})",
                "report_type": "transactions",
                "transactions": transactions,
                "count": len(transactions)
            }

    @staticmethod
    def generate_csv(report_data):
        """Generate a formatted CSV file in memory from report data."""
        output = io.StringIO()
        writer = csv.writer(output)

        rep_type = report_data.get("report_type")

        if rep_type in ["monthly_income", "monthly_expense", "transactions", "daily_summary"]:
            writer.writerow(["Transaction ID", "Date", "Type", "Category", "Description", "Payment Method", "Amount", "Notes"])
            for t in report_data.get("transactions", []):
                writer.writerow([
                    t.id,
                    t.transaction_date.strftime("%Y-%m-%d"),
                    t.transaction_type.title(),
                    t.category,
                    t.description,
                    t.payment_method,
                    f"{t.decimal_amount:.2f}",
                    t.notes or ""
                ])

        elif rep_type == "category_expense":
            writer.writerow(["Category", "Transaction Count", "Total Spent", "Share (%)"])
            for c in report_data.get("categories", []):
                writer.writerow([
                    c["category"],
                    c["count"],
                    f"{c['total']:.2f}",
                    f"{c['percentage']}%"
                ])

        elif rep_type == "annual_summary":
            writer.writerow(["Month", "Total Income", "Total Expense", "Net Savings"])
            for m in report_data.get("monthly_data", []):
                writer.writerow([
                    m["month"],
                    f"{m['income']:.2f}",
                    f"{m['expense']:.2f}",
                    f"{m['savings']:.2f}"
                ])
            writer.writerow([])
            writer.writerow(["ANNUAL TOTAL", f"{report_data['annual_income']:.2f}", f"{report_data['annual_expense']:.2f}", f"{report_data['annual_savings']:.2f}"])

        elif rep_type == "investment_performance":
            p = report_data.get("portfolio", {})
            writer.writerow(["Name", "Type", "Quantity", "Purchase Price", "Current Price", "Invested Value", "Current Value", "Profit/Loss", "Return %", "Platform"])
            for h in p.get("holdings", []):
                writer.writerow([
                    h["name"],
                    h["type_display"],
                    f"{h['quantity']:.4f}",
                    f"{h['purchase_price']:.2f}",
                    f"{h['current_price']:.2f}",
                    f"{h['invested_value']:.2f}",
                    f"{h['current_value']:.2f}",
                    f"{h['profit_loss']:.2f}",
                    f"{h['return_percentage']:.2f}%",
                    h["institution"]
                ])
            writer.writerow([])
            writer.writerow(["TOTAL PORTFOLIO", "", "", "", "", f"{p.get('total_invested', 0):.2f}", f"{p.get('total_current', 0):.2f}", f"{p.get('total_profit_loss', 0):.2f}", f"{p.get('total_return_percentage', 0):.2f}%", ""])

        elif rep_type == "budget_utilization":
            b = report_data.get("budget_data", {})
            writer.writerow(["Category", "Budgeted Amount", "Actual Spent", "Remaining", "Utilization (%)", "Status"])
            for item in b.get("items", []):
                writer.writerow([
                    item["category"],
                    f"{item['budgeted']:.2f}",
                    f"{item['spent']:.2f}",
                    f"{item['remaining']:.2f}",
                    f"{item['utilization']}%",
                    item["alert_level"].upper()
                ])

        elif rep_type == "net_worth":
            nw = report_data.get("net_worth", {})
            writer.writerow(["Asset / Liability Item", "Category", "Amount"])
            writer.writerow(["Cash Balance (Net Incomes - Expenses)", "Asset", f"{nw.get('cash_balance', 0):.2f}"])
            writer.writerow(["Stocks Holdings", "Asset", f"{nw.get('stocks_value', 0):.2f}"])
            writer.writerow(["Mutual Funds", "Asset", f"{nw.get('mutual_funds_value', 0):.2f}"])
            writer.writerow(["Fixed Deposits", "Asset", f"{nw.get('fixed_deposits_value', 0):.2f}"])
            writer.writerow(["Gold Holdings", "Asset", f"{nw.get('gold_value', 0):.2f}"])
            writer.writerow(["TOTAL ASSETS", "Total Assets", f"{nw.get('total_assets', 0):.2f}"])
            writer.writerow(["TOTAL LIABILITIES", "Total Liabilities", f"{nw.get('total_liabilities', 0):.2f}"])
            writer.writerow(["NET WORTH", "Net Worth (Assets - Liabilities)", f"{nw.get('net_worth', 0):.2f}"])

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_pdf(report_data, currency_symbol="₹"):
        """Generate a professionally designed PDF report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom Palette & Styles
        navy = colors.HexColor("#0f172a")
        teal = colors.HexColor("#0284c7")
        green = colors.HexColor("#10b981")
        red = colors.HexColor("#ef4444")
        gray = colors.HexColor("#64748b")
        light_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=navy,
            fontName="Helvetica-Bold",
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=gray,
            spaceAfter=12
        )

        header_text = f"Personal Finance Portfolio Tracker"
        elements.append(Paragraph(header_text, title_style))
        elements.append(Paragraph(f"{report_data.get('title', 'Financial Report')} | Generated on {datetime.now().strftime('%d %b %Y %H:%M')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=4, spaceAfter=14))

        rep_type = report_data.get("report_type")

        if rep_type in ["monthly_income", "monthly_expense", "transactions", "daily_summary"]:
            table_data = [["Date", "Type", "Category", "Description", "Method", "Amount"]]
            for t in report_data.get("transactions", []):
                amt_str = f"{currency_symbol}{t.decimal_amount:,.2f}"
                table_data.append([
                    t.transaction_date.strftime("%Y-%m-%d"),
                    t.transaction_type.title(),
                    t.category,
                    t.description[:30],
                    t.payment_method,
                    amt_str
                ])

            t_table = Table(table_data, colWidths=[65, 55, 80, 160, 75, 85])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (5, 0), (5, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elif rep_type == "category_expense":
            table_data = [["Category", "Transaction Count", "Total Spent", "Share"]]
            for c in report_data.get("categories", []):
                table_data.append([
                    c["category"],
                    str(c["count"]),
                    f"{currency_symbol}{c['total']:,.2f}",
                    f"{c['percentage']}%"
                ])
            table_data.append([
                "TOTAL EXPENSES",
                "",
                f"{currency_symbol}{report_data.get('total_expense', 0):,.2f}",
                "100%"
            ])

            t_table = Table(table_data, colWidths=[150, 100, 130, 100])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (3, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elif rep_type == "investment_performance":
            p = report_data.get("portfolio", {})
            table_data = [["Investment Name", "Type", "Qty", "Buy Price", "Cur Price", "Invested", "Current", "P&L", "Return"]]
            for h in p.get("holdings", []):
                pl_str = f"{currency_symbol}{h['profit_loss']:,.2f}"
                table_data.append([
                    h["name"][:20],
                    h["type_display"],
                    f"{h['quantity']:.2f}",
                    f"{currency_symbol}{h['purchase_price']:,.2f}",
                    f"{currency_symbol}{h['current_price']:,.2f}",
                    f"{currency_symbol}{h['invested_value']:,.2f}",
                    f"{currency_symbol}{h['current_value']:,.2f}",
                    pl_str,
                    f"{h['return_percentage']:.2f}%"
                ])

            t_table = Table(table_data, colWidths=[90, 65, 40, 55, 55, 65, 65, 55, 45])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elif rep_type == "budget_utilization":
            b = report_data.get("budget_data", {})
            table_data = [["Category", "Budgeted", "Actual Spent", "Remaining", "Utilization", "Status"]]
            for item in b.get("items", []):
                table_data.append([
                    item["category"],
                    f"{currency_symbol}{item['budgeted']:,.2f}",
                    f"{currency_symbol}{item['spent']:,.2f}",
                    f"{currency_symbol}{item['remaining']:,.2f}",
                    f"{item['utilization']}%",
                    item["alert_level"].upper()
                ])

            t_table = Table(table_data, colWidths=[120, 80, 80, 80, 70, 70])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (4, -1), "RIGHT"),
                ("ALIGN", (5, 0), (5, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elif rep_type == "annual_summary":
            table_data = [["Month", "Total Income", "Total Expense", "Net Savings"]]
            for m in report_data.get("monthly_data", []):
                table_data.append([
                    m["month"],
                    f"{currency_symbol}{m['income']:,.2f}",
                    f"{currency_symbol}{m['expense']:,.2f}",
                    f"{currency_symbol}{m['savings']:,.2f}"
                ])
            table_data.append([
                "ANNUAL TOTAL",
                f"{currency_symbol}{report_data['annual_income']:,.2f}",
                f"{currency_symbol}{report_data['annual_expense']:,.2f}",
                f"{currency_symbol}{report_data['annual_savings']:,.2f}"
            ])

            t_table = Table(table_data, colWidths=[130, 110, 110, 110])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elif rep_type == "net_worth":
            nw = report_data.get("net_worth", {})
            table_data = [
                ["Asset / Liability Item", "Classification", "Amount"],
                ["Cash & Bank Balance", "Liquid Asset", f"{currency_symbol}{nw.get('cash_balance', 0):,.2f}"],
                ["Stocks Holdings", "Equity Asset", f"{currency_symbol}{nw.get('stocks_value', 0):,.2f}"],
                ["Mutual Funds", "Equity/Hybrid Asset", f"{currency_symbol}{nw.get('mutual_funds_value', 0):,.2f}"],
                ["Fixed Deposits", "Fixed Income Asset", f"{currency_symbol}{nw.get('fixed_deposits_value', 0):,.2f}"],
                ["Gold Holdings", "Precious Metal Asset", f"{currency_symbol}{nw.get('gold_value', 0):,.2f}"],
                ["TOTAL ASSETS", "Sum of Assets", f"{currency_symbol}{nw.get('total_assets', 0):,.2f}"],
                ["TOTAL LIABILITIES", "Sum of Debts", f"-{currency_symbol}{nw.get('total_liabilities', 0):,.2f}"],
                ["NET WORTH", "Total Assets - Liabilities", f"{currency_symbol}{nw.get('net_worth', 0):,.2f}"]
            ]

            t_table = Table(table_data, colWidths=[200, 140, 140])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 6), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#e0f2fe")),
                ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#fee2e2")),
                ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#dcfce7")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, 5), [colors.white, light_bg])
            ]))
            elements.append(t_table)

        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Confidential Financial Report • Generated by Personal Finance Portfolio Tracker", ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=gray,
            alignment=1
        )))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
