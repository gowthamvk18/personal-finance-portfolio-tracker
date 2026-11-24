from decimal import Decimal
from app.models.investment import Investment


class PortfolioService:
    """Service layer for investment analytics and portfolio performance calculations."""

    @staticmethod
    def get_portfolio_summary(user_id):
        """
        Calculates complete portfolio summary with exact Decimal arithmetic:
        - Total Invested Value
        - Total Current Value
        - Overall Profit / Loss
        - Overall Return %
        - Allocation by Asset Type
        - Best & Worst Performing Investments
        """
        investments = Investment.query.filter_by(user_id=user_id).all()

        total_invested = Decimal("0.00")
        total_current = Decimal("0.00")

        # Type aggregation dictionary
        type_summary = {
            "stocks": {"name": "Stocks", "invested": Decimal("0.00"), "current": Decimal("0.00"), "count": 0, "color": "#3b82f6"},
            "mutual_funds": {"name": "Mutual Funds", "invested": Decimal("0.00"), "current": Decimal("0.00"), "count": 0, "color": "#8b5cf6"},
            "fixed_deposits": {"name": "Fixed Deposits", "invested": Decimal("0.00"), "current": Decimal("0.00"), "count": 0, "color": "#10b981"},
            "gold": {"name": "Gold", "invested": Decimal("0.00"), "current": Decimal("0.00"), "count": 0, "color": "#f59e0b"}
        }

        holdings = []
        best_performer = None
        worst_performer = None

        for inv in investments:
            inv_val = inv.invested_value
            cur_val = inv.current_value
            pl = inv.profit_loss
            ret_pct = inv.return_percentage

            total_invested += inv_val
            total_current += cur_val

            itype = inv.investment_type
            if itype in type_summary:
                type_summary[itype]["invested"] += inv_val
                type_summary[itype]["current"] += cur_val
                type_summary[itype]["count"] += 1

            holding_item = {
                "id": inv.id,
                "name": inv.name,
                "type": inv.investment_type,
                "type_display": inv.type_display,
                "quantity": inv.decimal_quantity,
                "purchase_price": inv.decimal_purchase_price,
                "current_price": inv.decimal_current_price,
                "purchase_date": inv.purchase_date,
                "institution": inv.institution or "N/A",
                "invested_value": inv_val,
                "current_value": cur_val,
                "profit_loss": pl,
                "return_percentage": ret_pct,
                "interest_rate": inv.interest_rate,
                "maturity_date": inv.maturity_date,
                "notes": inv.notes
            }
            holdings.append(holding_item)

            # Track best and worst
            if best_performer is None or ret_pct > best_performer["return_percentage"]:
                best_performer = holding_item

            if worst_performer is None or ret_pct < worst_performer["return_percentage"]:
                worst_performer = holding_item

        total_pl = (total_current - total_invested).quantize(Decimal("0.01"))
        total_return_pct = Decimal("0.00")
        if total_invested > Decimal("0.00"):
            total_return_pct = ((total_pl / total_invested) * Decimal("100.00")).quantize(Decimal("0.01"))

        # Calculate allocation percentages
        allocation = []
        for itype, data in type_summary.items():
            alloc_pct = Decimal("0.00")
            if total_current > Decimal("0.00"):
                alloc_pct = ((data["current"] / total_current) * Decimal("100.00")).quantize(Decimal("0.1"))
            
            type_pl = (data["current"] - data["invested"]).quantize(Decimal("0.01"))
            type_ret = Decimal("0.00")
            if data["invested"] > Decimal("0.00"):
                type_ret = ((type_pl / data["invested"]) * Decimal("100.00")).quantize(Decimal("0.1"))

            allocation.append({
                "type": itype,
                "name": data["name"],
                "invested": data["invested"],
                "current": data["current"],
                "profit_loss": type_pl,
                "return_pct": float(type_ret),
                "count": data["count"],
                "percentage": float(alloc_pct),
                "color": data["color"]
            })

        return {
            "total_invested": total_invested.quantize(Decimal("0.01")),
            "total_current": total_current.quantize(Decimal("0.01")),
            "total_profit_loss": total_pl,
            "total_return_percentage": total_return_pct,
            "holdings": holdings,
            "allocation": allocation,
            "best_performer": best_performer,
            "worst_performer": worst_performer,
            "holdings_count": len(holdings)
        }
