from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.return_order import Return, ReturnItem
from app.models.expense import Expense

from app.services.analytics_service import AnalyticsService
from app.schemas.insights import (
    InsightItem,
    InsightSeverity,
    InsightCategory,
    InsightsSummary,
    InsightsPeriodInfo,
    InsightsData,
)

class InsightThresholds(BaseModel):
    """
    Centralized, deterministic configuration for business insight rules.
    All thresholds are explicit, documented, and configurable.
    """
    # --- Inventory Thresholds ---
    slow_moving_velocity: float = 0.05            # Sales velocity below 0.05 units/day is slow-moving
    slow_moving_min_value: float = 100.0          # Minimum capital ($100) tied up in slow-moving stock to warn
    inventory_concentration_share: float = 0.35   # Single product with >= 35% of total inventory value
    inventory_concentration_min_products: int = 3 # Minimum product catalog size to evaluate concentration

    # --- Sales Thresholds ---
    revenue_concentration_top_pct: float = 0.20   # Top 20% of products
    revenue_concentration_share: float = 0.70     # Accounting for >= 70% of period revenue
    revenue_concentration_min_products: int = 5   # Require at least 5 selling products to trigger rule
    return_rate_threshold: float = 0.10           # Return/refund amount exceeding 10% of revenue
    return_rate_min_refund: float = 20.0          # Minimum refund dollar amount to avoid noise

    # --- Financial Thresholds ---
    low_gross_margin_pct: float = 25.0            # Gross margin % below 25.0%
    low_net_margin_pct: float = 10.0              # Net profit margin % below 10.0%
    receivables_risk_ratio: float = 0.40          # Receivables exceeding 40% of period sales
    receivables_risk_min_amount: float = 500.0    # Minimum receivables ($500) to flag ratio
    payables_pressure_ratio: float = 0.50         # Outstanding payables exceeding 50% of purchases
    payables_pressure_min_amount: float = 500.0   # Minimum payables ($500) to flag pressure

    # --- Customer Thresholds ---
    customer_concentration_share: float = 0.40    # Top customer generating >= 40% of sales
    customer_concentration_min_customers: int = 2 # Minimum active customers to evaluate concentration
    customer_high_receivable_min: float = 500.0   # Individual customer debt >= $500
    customer_high_receivable_share: float = 0.30  # Individual customer debt >= 30% of total receivables
    inactive_customer_min_spend: float = 500.0    # Minimum historical spend to flag account inactivity

    # --- Supplier Thresholds ---
    supplier_concentration_share: float = 0.60    # Top supplier receiving >= 60% of purchase spend
    supplier_concentration_min_suppliers: int = 2 # Minimum active suppliers to evaluate concentration
    supplier_high_payable_min: float = 1000.0     # Unpaid supplier balance >= $1000
    supplier_high_payable_share: float = 0.40     # Unpaid supplier balance >= 40% of total payables
    pending_pos_warning_count: int = 5            # >= 5 pending purchase orders accumulated

    # --- Data Quality Thresholds ---
    cost_coverage_warning_pct: float = 85.0        # Warning if cost coverage is below 85%

DEFAULT_THRESHOLDS = InsightThresholds()

class InsightsService:
    """
    Deterministic Smart Business Insights Engine.
    Evaluates operational conditions across inventory, sales, finance, customer,
    supplier, and data quality metrics without external LLMs or black-box models.
    """

    @classmethod
    def generate_insights(
        cls,
        db: Session,
        business_id: str,
        period: str = "last_30_days",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        thresholds: InsightThresholds = DEFAULT_THRESHOLDS
    ) -> InsightsData:
        # Resolve date boundaries consistently with AnalyticsService
        start_dt, end_dt, days = AnalyticsService.get_date_bounds(period, start_date, end_date)

        # 1. Fetch analytics KPIs using existing SQL aggregations
        sales_kpis = AnalyticsService.get_sales_kpis(db, business_id, start_dt, end_dt)
        inv_kpis = AnalyticsService.get_inventory_kpis(db, business_id)
        cust_kpis = AnalyticsService.get_customer_kpis(db, business_id, start_dt, end_dt)
        supp_kpis = AnalyticsService.get_supplier_kpis(db, business_id)
        purch_kpis = AnalyticsService.get_purchasing_kpis(db, business_id, start_dt, end_dt)
        ret_kpis = AnalyticsService.get_return_kpis(db, business_id, start_dt, end_dt)
        fin_kpis = AnalyticsService.get_financial_kpis(db, business_id, start_dt, end_dt)
        prod_resp = AnalyticsService.get_product_analytics(db, business_id, start_dt, end_dt, days_count=days, limit=50)
        cust_resp = AnalyticsService.get_customer_analytics(db, business_id, start_dt, end_dt, limit=10)
        purch_resp = AnalyticsService.get_purchasing_analytics(db, business_id, start_dt, end_dt)

        insights: List[InsightItem] = []

        # =========================================================================
        # INVENTORY INSIGHTS
        # =========================================================================
        cls._evaluate_inventory_insights(db, business_id, inv_kpis, prod_resp, thresholds, insights)

        # =========================================================================
        # SALES INSIGHTS
        # =========================================================================
        cls._evaluate_sales_insights(sales_kpis, prod_resp, ret_kpis, thresholds, insights)

        # =========================================================================
        # FINANCIAL INSIGHTS
        # =========================================================================
        cls._evaluate_financial_insights(fin_kpis, thresholds, insights)

        # =========================================================================
        # CUSTOMER INSIGHTS
        # =========================================================================
        cls._evaluate_customer_insights(db, business_id, start_dt, end_dt, sales_kpis, cust_kpis, cust_resp, thresholds, insights)

        # =========================================================================
        # SUPPLIER INSIGHTS
        # =========================================================================
        cls._evaluate_supplier_insights(db, business_id, purch_kpis, supp_kpis, purch_resp, thresholds, insights)

        # =========================================================================
        # DATA QUALITY INSIGHTS
        # =========================================================================
        cls._evaluate_data_quality_insights(sales_kpis, fin_kpis, thresholds, insights)

        # =========================================================================
        # PRIORITIZATION & SUMMARY
        # =========================================================================
        # Priority: critical (1) -> warning (2) -> info (3)
        severity_rank = {
            InsightSeverity.CRITICAL: 1,
            InsightSeverity.WARNING: 2,
            InsightSeverity.INFO: 3
        }
        insights.sort(key=lambda item: severity_rank.get(item.severity, 99))

        crit_count = sum(1 for x in insights if x.severity == InsightSeverity.CRITICAL)
        warn_count = sum(1 for x in insights if x.severity == InsightSeverity.WARNING)
        info_count = sum(1 for x in insights if x.severity == InsightSeverity.INFO)

        period_info = InsightsPeriodInfo(
            period=period,
            start_date=start_dt.strftime("%Y-%m-%d") if start_dt else None,
            end_date=end_dt.strftime("%Y-%m-%d") if end_dt else None,
            days=days
        )

        return InsightsData(
            generated_at=datetime.utcnow(),
            period=period_info,
            summary=InsightsSummary(
                total=len(insights),
                critical=crit_count,
                warning=warn_count,
                info=info_count
            ),
            insights=insights
        )

    # -------------------------------------------------------------------------
    # INVENTORY EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_inventory_insights(
        cls,
        db: Session,
        business_id: str,
        inv_kpis: Any,
        prod_resp: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        if inv_kpis.total_products == 0:
            return

        # A. Out of Stock (CRITICAL)
        oos_items = [p for p in prod_resp.low_stock if p.status == "Out of Stock"]
        if len(oos_items) == 1:
            item = oos_items[0]
            insights.append(
                InsightItem(
                    id=f"inv_oos_{item.product_id}",
                    category=InsightCategory.INVENTORY,
                    severity=InsightSeverity.CRITICAL,
                    title=f"Out of Stock: {item.name}",
                    message=f"Product '{item.name}' (SKU: {item.sku}) has zero available inventory across all warehouses.",
                    metric="current_stock",
                    current_value=0.0,
                    threshold=0.0,
                    recommendation="Review replenishment requirements and place a purchase order immediately to avoid stockout disruption.",
                    evidence={"product_id": item.product_id, "sku": item.sku, "reorder_level": item.reorder_level}
                )
            )
        elif len(oos_items) > 1:
            insights.append(
                InsightItem(
                    id="inv_oos_aggregate",
                    category=InsightCategory.INVENTORY,
                    severity=InsightSeverity.CRITICAL,
                    title=f"Critical Out-of-Stock: {len(oos_items)} Products Depleted",
                    message=f"{len(oos_items)} products currently have zero available stock, creating immediate fulfillment risk.",
                    metric="out_of_stock_count",
                    current_value=len(oos_items),
                    threshold=0,
                    recommendation="Generate purchase orders immediately for depleted items to restore catalog availability.",
                    evidence={
                        "out_of_stock_count": len(oos_items),
                        "products": [{"id": p.product_id, "name": p.name, "sku": p.sku} for p in oos_items[:10]]
                    }
                )
            )

        # B. Low Stock (WARNING)
        low_items = [p for p in prod_resp.low_stock if p.status == "Low Stock"]
        if len(low_items) == 1:
            item = low_items[0]
            insights.append(
                InsightItem(
                    id=f"inv_low_{item.product_id}",
                    category=InsightCategory.INVENTORY,
                    severity=InsightSeverity.WARNING,
                    title=f"Low Stock Warning: {item.name}",
                    message=f"Product '{item.name}' stock ({item.current_stock}) has dropped to or below its reorder level ({item.reorder_level}).",
                    metric="current_stock",
                    current_value=item.current_stock,
                    threshold=item.reorder_level,
                    recommendation="Submit purchase orders to restore safety stock buffer before an out-of-stock event occurs.",
                    evidence={"product_id": item.product_id, "sku": item.sku, "current_stock": item.current_stock, "reorder_level": item.reorder_level}
                )
            )
        elif len(low_items) > 1:
            insights.append(
                InsightItem(
                    id="inv_low_aggregate",
                    category=InsightCategory.INVENTORY,
                    severity=InsightSeverity.WARNING,
                    title=f"Low Stock Alert: {len(low_items)} Products Below Safety Level",
                    message=f"{len(low_items)} active products are at or below their configured safety reorder thresholds.",
                    metric="low_stock_count",
                    current_value=len(low_items),
                    threshold=0,
                    recommendation="Review reorder quantities and schedule stock replenishment with suppliers.",
                    evidence={
                        "low_stock_count": len(low_items),
                        "products": [{"id": p.product_id, "name": p.name, "sku": p.sku, "stock": p.current_stock, "reorder": p.reorder_level} for p in low_items[:10]]
                    }
                )
            )

        # C. Slow-Moving Inventory (WARNING)
        slow_with_capital = []
        total_tied_up = 0.0
        for p in prod_resp.slow_moving:
            item_val = p.current_stock * (p.cost_price or p.selling_price or 0.0)
            if item_val >= thresholds.slow_moving_min_value:
                slow_with_capital.append((p, item_val))
                total_tied_up += item_val

        if slow_with_capital:
            if len(slow_with_capital) == 1:
                p, val = slow_with_capital[0]
                insights.append(
                    InsightItem(
                        id=f"inv_slow_{p.product_id}",
                        category=InsightCategory.INVENTORY,
                        severity=InsightSeverity.WARNING,
                        title=f"Stagnant Capital: {p.name}",
                        message=f"Product '{p.name}' shows sluggish velocity ({p.velocity_per_day} units/day) with ${round(val, 2):,.2f} tied up in {p.current_stock} unsold units.",
                        metric="velocity_per_day",
                        current_value=p.velocity_per_day,
                        threshold=thresholds.slow_moving_velocity,
                        recommendation="Consider running a promotional discount, bundling with high-velocity items, or tapering future procurement.",
                        evidence={"product_id": p.product_id, "sku": p.sku, "stock": p.current_stock, "tied_up_capital": round(val, 2), "velocity": p.velocity_per_day}
                    )
                )
            else:
                insights.append(
                    InsightItem(
                        id="inv_slow_aggregate",
                        category=InsightCategory.INVENTORY,
                        severity=InsightSeverity.WARNING,
                        title=f"Slow-Moving Inventory: ${round(total_tied_up, 2):,.2f} Tied Up in {len(slow_with_capital)} Products",
                        message=f"{len(slow_with_capital)} products exhibit sales velocity below {thresholds.slow_moving_velocity} units/day, locking up ${round(total_tied_up, 2):,.2f} in working capital.",
                        metric="tied_up_capital",
                        current_value=round(total_tied_up, 2),
                        threshold=thresholds.slow_moving_min_value,
                        recommendation="Execute promotional sales or product bundles to liquidate slow-moving inventory and free working capital.",
                        evidence={
                            "slow_moving_count": len(slow_with_capital),
                            "total_tied_up_capital": round(total_tied_up, 2),
                            "top_stagnant": [
                                {"name": p.name, "sku": p.sku, "stock": p.current_stock, "tied_up_capital": round(val, 2), "velocity": p.velocity_per_day}
                                for p, val in slow_with_capital[:5]
                            ]
                        }
                    )
                )

        # D. High Stock / Capital Concentration (WARNING / INFO)
        if inv_kpis.total_inventory_value > 0 and inv_kpis.total_products >= thresholds.inventory_concentration_min_products:
            # Find product with highest tied-up value
            highest_item = None
            highest_val = 0.0
            for p in prod_resp.top_by_quantity + prod_resp.slow_moving + prod_resp.low_stock:
                val = p.current_stock * (p.cost_price or p.selling_price or 0.0)
                if val > highest_val:
                    highest_val = val
                    highest_item = p

            if highest_item and inv_kpis.total_inventory_value > 0:
                share = highest_val / inv_kpis.total_inventory_value
                if share >= thresholds.inventory_concentration_share:
                    sev = InsightSeverity.WARNING if share >= 0.50 else InsightSeverity.INFO
                    insights.append(
                        InsightItem(
                            id=f"inv_concentration_{highest_item.product_id}",
                            category=InsightCategory.INVENTORY,
                            severity=sev,
                            title=f"Inventory Capital Concentration: {highest_item.name}",
                            message=f"Product '{highest_item.name}' accounts for {round(share * 100, 1)}% (${round(highest_val, 2):,.2f}) of total inventory valuation (${round(inv_kpis.total_inventory_value, 2):,.2f}).",
                            metric="inventory_value_share",
                            current_value=round(share * 100, 1),
                            threshold=round(thresholds.inventory_concentration_share * 100, 1),
                            recommendation="Monitor inventory holding levels closely to prevent excessive capital exposure in a single SKU line.",
                            evidence={
                                "product_id": highest_item.product_id,
                                "name": highest_item.name,
                                "inventory_value": round(highest_val, 2),
                                "total_inventory_value": round(inv_kpis.total_inventory_value, 2),
                                "share_percentage": round(share * 100, 1)
                            }
                        )
                    )

    # -------------------------------------------------------------------------
    # SALES EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_sales_insights(
        cls,
        sales_kpis: Any,
        prod_resp: Any,
        ret_kpis: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        # A. Low / No Sales Activity
        if sales_kpis.total_orders == 0:
            insights.append(
                InsightItem(
                    id="sales_no_activity",
                    category=InsightCategory.SALES,
                    severity=InsightSeverity.INFO,
                    title="No Sales Activity Recorded",
                    message="Zero customer orders were completed during the selected period.",
                    metric="total_orders",
                    current_value=0,
                    threshold=1,
                    recommendation="Review sales channels, initiate promotional marketing campaigns, or verify offline transactions.",
                    evidence={"total_orders": 0, "total_revenue": 0.0}
                )
            )
            return

        # B. Revenue Concentration
        selling_products = [p for p in prod_resp.top_by_revenue if p.revenue > 0]
        if len(selling_products) >= thresholds.revenue_concentration_min_products and sales_kpis.total_revenue > 0:
            top_n = max(1, int(len(selling_products) * thresholds.revenue_concentration_top_pct))
            top_revenue = sum(p.revenue for p in selling_products[:top_n])
            share = top_revenue / sales_kpis.total_revenue
            if share >= thresholds.revenue_concentration_share:
                insights.append(
                    InsightItem(
                        id="sales_revenue_concentration",
                        category=InsightCategory.SALES,
                        severity=InsightSeverity.WARNING,
                        title="High Revenue Concentration",
                        message=f"Top {top_n} product(s) ({round(top_n / len(selling_products) * 100)}% of catalog) drive {round(share * 100, 1)}% (${round(top_revenue, 2):,.2f}) of total revenue.",
                        metric="revenue_concentration_share",
                        current_value=round(share * 100, 1),
                        threshold=round(thresholds.revenue_concentration_share * 100, 1),
                        recommendation="Diversify revenue across broader product categories to diminish dependency on a small number of top sellers.",
                        evidence={
                            "top_products_count": top_n,
                            "total_selling_products": len(selling_products),
                            "top_revenue": round(top_revenue, 2),
                            "total_revenue": round(sales_kpis.total_revenue, 2),
                            "share_percentage": round(share * 100, 1),
                            "top_products": [p.name for p in selling_products[:top_n]]
                        }
                    )
                )

        # C. Return Rate (WARNING)
        if sales_kpis.total_revenue > 0 and ret_kpis.total_refund_amount >= thresholds.return_rate_min_refund:
            return_rate = ret_kpis.total_refund_amount / sales_kpis.total_revenue
            if return_rate >= thresholds.return_rate_threshold:
                insights.append(
                    InsightItem(
                        id="sales_high_return_rate",
                        category=InsightCategory.SALES,
                        severity=InsightSeverity.WARNING,
                        title="Elevated Product Return Rate",
                        message=f"Customer returns and refunds represent {round(return_rate * 100, 1)}% (${round(ret_kpis.total_refund_amount, 2):,.2f}) of sales revenue (${round(sales_kpis.total_revenue, 2):,.2f}).",
                        metric="return_rate_percentage",
                        current_value=round(return_rate * 100, 1),
                        threshold=round(thresholds.return_rate_threshold * 100, 1),
                        recommendation="Review return reasons, check quality control on delivered items, and review online product descriptions.",
                        evidence={
                            "total_returns": ret_kpis.total_returns,
                            "refund_amount": round(ret_kpis.total_refund_amount, 2),
                            "total_revenue": round(sales_kpis.total_revenue, 2),
                            "return_rate_percentage": round(return_rate * 100, 1)
                        }
                    )
                )

    # -------------------------------------------------------------------------
    # FINANCIAL EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_financial_insights(
        cls,
        fin_kpis: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        # A. Negative Net Profit (CRITICAL)
        if fin_kpis.net_profit < 0 and (fin_kpis.total_sales > 0 or fin_kpis.total_expenses > 0):
            insights.append(
                InsightItem(
                    id="fin_negative_net_profit",
                    category=InsightCategory.FINANCE,
                    severity=InsightSeverity.CRITICAL,
                    title="Operating at a Net Loss",
                    message=f"The business generated a net loss of -${round(abs(fin_kpis.net_profit), 2):,.2f} for the period (Revenue: ${round(fin_kpis.total_sales, 2):,.2f}, COGS: ${round(fin_kpis.cogs, 2):,.2f}, Expenses: ${round(fin_kpis.total_expenses, 2):,.2f}).",
                    metric="net_profit",
                    current_value=round(fin_kpis.net_profit, 2),
                    threshold=0.0,
                    recommendation="Audit operating expenditures immediately and reassess product pricing structure to reverse the negative profit margin.",
                    evidence={
                        "revenue": round(fin_kpis.total_sales, 2),
                        "cogs": round(fin_kpis.cogs, 2),
                        "gross_profit": round(fin_kpis.gross_profit, 2),
                        "expenses": round(fin_kpis.total_expenses, 2),
                        "net_profit": round(fin_kpis.net_profit, 2)
                    }
                )
            )

        # B. Low Gross Margin (WARNING)
        if fin_kpis.total_sales > 0 and fin_kpis.gross_margin_percentage < thresholds.low_gross_margin_pct and fin_kpis.gross_profit >= 0:
            insights.append(
                InsightItem(
                    id="fin_low_gross_margin",
                    category=InsightCategory.FINANCE,
                    severity=InsightSeverity.WARNING,
                    title="Compressed Gross Margin",
                    message=f"Gross margin stands at {fin_kpis.gross_margin_percentage}%, trailing the recommended minimum threshold of {thresholds.low_gross_margin_pct}%.",
                    metric="gross_margin_percentage",
                    current_value=fin_kpis.gross_margin_percentage,
                    threshold=thresholds.low_gross_margin_pct,
                    recommendation="Negotiate volume discounts with vendors or recalibrate retail prices to improve item-level profitability.",
                    evidence={
                        "revenue": round(fin_kpis.total_sales, 2),
                        "cogs": round(fin_kpis.cogs, 2),
                        "gross_profit": round(fin_kpis.gross_profit, 2),
                        "gross_margin_percentage": fin_kpis.gross_margin_percentage
                    }
                )
            )

        # C. Low Net Margin (WARNING)
        if fin_kpis.total_sales > 0 and 0 <= fin_kpis.net_margin_percentage < thresholds.low_net_margin_pct and fin_kpis.net_profit >= 0:
            insights.append(
                InsightItem(
                    id="fin_low_net_margin",
                    category=InsightCategory.FINANCE,
                    severity=InsightSeverity.WARNING,
                    title="Thin Net Profit Margin",
                    message=f"Net profit margin is {fin_kpis.net_margin_percentage}%, leaving minimal margin for error against unforeseen cost increases.",
                    metric="net_margin_percentage",
                    current_value=fin_kpis.net_margin_percentage,
                    threshold=thresholds.low_net_margin_pct,
                    recommendation="Rationalize operational overhead expenses and optimize operational efficiency to improve net conversion.",
                    evidence={
                        "revenue": round(fin_kpis.total_sales, 2),
                        "net_profit": round(fin_kpis.net_profit, 2),
                        "net_margin_percentage": fin_kpis.net_margin_percentage,
                        "expenses": round(fin_kpis.total_expenses, 2)
                    }
                )
            )

        # D. Receivables Risk (WARNING)
        if fin_kpis.outstanding_receivables >= thresholds.receivables_risk_min_amount:
            ratio = fin_kpis.outstanding_receivables / max(fin_kpis.total_sales, 1.0)
            if ratio >= thresholds.receivables_risk_ratio or (fin_kpis.collected_payments > 0 and fin_kpis.outstanding_receivables > fin_kpis.collected_payments):
                insights.append(
                    InsightItem(
                        id="fin_receivables_risk",
                        category=InsightCategory.FINANCE,
                        severity=InsightSeverity.WARNING,
                        title="Elevated Accounts Receivable Risk",
                        message=f"Outstanding customer receivables of ${round(fin_kpis.outstanding_receivables, 2):,.2f} equate to {round(ratio * 100, 1)}% of period sales.",
                        metric="receivables_to_sales_ratio",
                        current_value=round(ratio * 100, 1),
                        threshold=round(thresholds.receivables_risk_ratio * 100, 1),
                        recommendation="Tighten customer credit terms, automate overdue billing reminders, and require advance deposits for substantial orders.",
                        evidence={
                            "outstanding_receivables": round(fin_kpis.outstanding_receivables, 2),
                            "total_sales": round(fin_kpis.total_sales, 2),
                            "collected_payments": round(fin_kpis.collected_payments, 2),
                            "ratio_percentage": round(ratio * 100, 1)
                        }
                    )
                )

        # E. Payables Pressure (WARNING)
        if fin_kpis.outstanding_payables >= thresholds.payables_pressure_min_amount:
            ratio = fin_kpis.outstanding_payables / max(fin_kpis.total_purchases, 1.0)
            if ratio >= thresholds.payables_pressure_ratio or (fin_kpis.total_purchases > 0 and fin_kpis.outstanding_payables > fin_kpis.total_purchases * 0.7):
                insights.append(
                    InsightItem(
                        id="fin_payables_pressure",
                        category=InsightCategory.FINANCE,
                        severity=InsightSeverity.WARNING,
                        title="High Outstanding Supplier Payables",
                        message=f"Outstanding supplier payables stand at ${round(fin_kpis.outstanding_payables, 2):,.2f} relative to ${round(fin_kpis.total_purchases, 2):,.2f} in purchases.",
                        metric="payables_to_purchases_ratio",
                        current_value=round(ratio * 100, 1),
                        threshold=round(thresholds.payables_pressure_ratio * 100, 1),
                        recommendation="Synchronize supplier payments with anticipated cash receipts to preserve good vendor credit standing.",
                        evidence={
                            "outstanding_payables": round(fin_kpis.outstanding_payables, 2),
                            "total_purchases": round(fin_kpis.total_purchases, 2),
                            "ratio_percentage": round(ratio * 100, 1)
                        }
                    )
                )

    # -------------------------------------------------------------------------
    # CUSTOMER EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_customer_insights(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
        sales_kpis: Any,
        cust_kpis: Any,
        cust_resp: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        if cust_kpis.total_customers == 0:
            return

        # A. Customer Concentration (WARNING)
        if len(cust_resp.top_customers) >= thresholds.customer_concentration_min_customers and sales_kpis.total_revenue > 0:
            top_cust = cust_resp.top_customers[0]
            share = top_cust.total_spent / sales_kpis.total_revenue
            if share >= thresholds.customer_concentration_share:
                insights.append(
                    InsightItem(
                        id=f"cust_concentration_{top_cust.customer_id}",
                        category=InsightCategory.CUSTOMER,
                        severity=InsightSeverity.WARNING,
                        title=f"Customer Revenue Concentration: {top_cust.name}",
                        message=f"Customer '{top_cust.name}' accounts for {round(share * 100, 1)}% (${round(top_cust.total_spent, 2):,.2f}) of total sales for the period.",
                        metric="customer_revenue_share",
                        current_value=round(share * 100, 1),
                        threshold=round(thresholds.customer_concentration_share * 100, 1),
                        recommendation="Broaden marketing and sales pipeline to avoid over-reliance on a single client account.",
                        evidence={
                            "customer_id": top_cust.customer_id,
                            "name": top_cust.name,
                            "spent": round(top_cust.total_spent, 2),
                            "total_revenue": round(sales_kpis.total_revenue, 2),
                            "share_percentage": round(share * 100, 1)
                        }
                    )
                )

        # B. High Receivable Customer (WARNING)
        top_debtor = db.query(Customer).filter(
            Customer.business_id == business_id,
            Customer.outstanding_balance >= thresholds.customer_high_receivable_min
        ).order_by(Customer.outstanding_balance.desc()).first()

        if top_debtor:
            debt = float(top_debtor.outstanding_balance or 0.0)
            share_of_debt = debt / max(cust_kpis.total_receivables, 1.0)
            if debt >= thresholds.customer_high_receivable_min or share_of_debt >= thresholds.customer_high_receivable_share:
                insights.append(
                    InsightItem(
                        id=f"cust_high_debt_{top_debtor.id}",
                        category=InsightCategory.CUSTOMER,
                        severity=InsightSeverity.WARNING,
                        title=f"Substantial Unpaid Balance: {top_debtor.name}",
                        message=f"Customer '{top_debtor.name}' owes an unpaid balance of ${round(debt, 2):,.2f}.",
                        metric="customer_outstanding_balance",
                        current_value=round(debt, 2),
                        threshold=thresholds.customer_high_receivable_min,
                        recommendation="Send an account statement and contact the customer to arrange payment or establish an installment plan.",
                        evidence={
                            "customer_id": top_debtor.id,
                            "name": top_debtor.name,
                            "email": top_debtor.email,
                            "outstanding_balance": round(debt, 2)
                        }
                    )
                )

        # C. Inactive High-Value Accounts (INFO)
        # Identify customers with lifetime spend >= min_spend, but who have no order in the selected period
        if start_dt:
            order_date_expr = func.coalesce(Order.order_date, Order.created_at)
            subq_active = db.query(Order.customer_id).filter(
                Order.business_id == business_id,
                Order.status != "Cancelled",
                order_date_expr >= start_dt,
                Order.customer_id.isnot(None)
            )
            if end_dt:
                subq_active = subq_active.filter(order_date_expr <= end_dt)
            active_ids = {r[0] for r in subq_active.all()}

            # Now find high-spending customers who are not in active_ids
            inactive_high_spenders = db.query(
                Customer.id,
                Customer.name,
                Customer.email,
                func.sum(Order.total).label("lifetime_spend")
            ).join(Order, Customer.id == Order.customer_id).filter(
                Customer.business_id == business_id,
                Order.status != "Cancelled"
            ).group_by(Customer.id, Customer.name, Customer.email).having(
                func.sum(Order.total) >= thresholds.inactive_customer_min_spend
            ).all()

            inactive_list = [
                {"id": r.id, "name": r.name, "lifetime_spend": round(float(r.lifetime_spend or 0.0), 2)}
                for r in inactive_high_spenders
                if r.id not in active_ids
            ]

            if inactive_list:
                insights.append(
                    InsightItem(
                        id="cust_inactive_high_value",
                        category=InsightCategory.CUSTOMER,
                        severity=InsightSeverity.INFO,
                        title=f"No Recent Activity: {len(inactive_list)} Key Accounts",
                        message=f"{len(inactive_list)} high-value customers with lifetime spend >= ${thresholds.inactive_customer_min_spend:,.0f} have no recorded purchases in this period.",
                        metric="inactive_customer_count",
                        current_value=len(inactive_list),
                        threshold=0,
                        recommendation="Engage these past buyers with proactive account management, re-engagement emails, or special incentives.",
                        evidence={
                            "inactive_count": len(inactive_list),
                            "accounts": inactive_list[:5]
                        }
                    )
                )

    # -------------------------------------------------------------------------
    # SUPPLIER EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_supplier_insights(
        cls,
        db: Session,
        business_id: str,
        purch_kpis: Any,
        supp_kpis: Any,
        purch_resp: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        if supp_kpis.total_suppliers == 0:
            return

        # A. Supplier Spend Concentration (WARNING)
        if len(purch_resp.top_suppliers) >= thresholds.supplier_concentration_min_suppliers and purch_kpis.total_purchase_spend > 0:
            top_supp = purch_resp.top_suppliers[0]
            spend = top_supp["total_spend"]
            share = spend / purch_kpis.total_purchase_spend
            if share >= thresholds.supplier_concentration_share:
                insights.append(
                    InsightItem(
                        id=f"supp_concentration_{top_supp['supplier_id']}",
                        category=InsightCategory.SUPPLIER,
                        severity=InsightSeverity.WARNING,
                        title=f"Supplier Spend Concentration: {top_supp['name']}",
                        message=f"Supplier '{top_supp['name']}' represents {round(share * 100, 1)}% (${round(spend, 2):,.2f}) of total purchase order expenditure.",
                        metric="supplier_spend_share",
                        current_value=round(share * 100, 1),
                        threshold=round(thresholds.supplier_concentration_share * 100, 1),
                        recommendation="Identify secondary suppliers to mitigate supply disruption or sole-source pricing risks.",
                        evidence={
                            "supplier_id": top_supp["supplier_id"],
                            "name": top_supp["name"],
                            "spend": round(spend, 2),
                            "total_purchases": round(purch_kpis.total_purchase_spend, 2),
                            "share_percentage": round(share * 100, 1)
                        }
                    )
                )

        # B. High Outstanding Payable (WARNING)
        top_payable_supp = db.query(Supplier).filter(
            Supplier.business_id == business_id,
            Supplier.outstanding_balance >= thresholds.supplier_high_payable_min
        ).order_by(Supplier.outstanding_balance.desc()).first()

        if top_payable_supp:
            balance = float(top_payable_supp.outstanding_balance or 0.0)
            share_of_payables = balance / max(supp_kpis.total_payables, 1.0)
            if balance >= thresholds.supplier_high_payable_min or share_of_payables >= thresholds.supplier_high_payable_share:
                insights.append(
                    InsightItem(
                        id=f"supp_high_payable_{top_payable_supp.id}",
                        category=InsightCategory.SUPPLIER,
                        severity=InsightSeverity.WARNING,
                        title=f"Substantial Balance Due to Supplier: {top_payable_supp.name}",
                        message=f"Outstanding balance of ${round(balance, 2):,.2f} is payable to vendor '{top_payable_supp.name}'.",
                        metric="supplier_outstanding_balance",
                        current_value=round(balance, 2),
                        threshold=thresholds.supplier_high_payable_min,
                        recommendation="Review vendor payment schedules to avoid credit suspension or delayed supply deliveries.",
                        evidence={
                            "supplier_id": top_payable_supp.id,
                            "name": top_payable_supp.name,
                            "company_name": top_payable_supp.company_name,
                            "outstanding_balance": round(balance, 2)
                        }
                    )
                )

        # C. Pending Purchase Orders Accumulation (WARNING)
        pending_pos = db.query(
            func.count(PurchaseOrder.id).label("cnt"),
            func.coalesce(func.sum(PurchaseOrder.total), 0).label("tot")
        ).filter(
            PurchaseOrder.business_id == business_id,
            PurchaseOrder.status.in_(["Ordered", "Partially Received", "Draft"])
        ).first()

        cnt = int(pending_pos.cnt or 0)
        tot = float(pending_pos.tot or 0.0)
        if cnt >= thresholds.pending_pos_warning_count:
            insights.append(
                InsightItem(
                    id="supp_pending_pos_accumulation",
                    category=InsightCategory.SUPPLIER,
                    severity=InsightSeverity.WARNING,
                    title=f"Accumulation of Pending Purchase Orders ({cnt} Orders)",
                    message=f"{cnt} purchase orders totaling ${round(tot, 2):,.2f} are awaiting delivery or processing.",
                    metric="pending_purchase_orders_count",
                    current_value=cnt,
                    threshold=thresholds.pending_pos_warning_count,
                    recommendation="Follow up with vendors on expected arrival dates and expedite warehouse receiving.",
                    evidence={"pending_count": cnt, "pending_total": round(tot, 2)}
                )
            )

    # -------------------------------------------------------------------------
    # DATA QUALITY EVALUATOR
    # -------------------------------------------------------------------------
    @classmethod
    def _evaluate_data_quality_insights(
        cls,
        sales_kpis: Any,
        fin_kpis: Any,
        thresholds: InsightThresholds,
        insights: List[InsightItem]
    ):
        # Cost Data Coverage Warning
        if sales_kpis.total_orders > 0 and fin_kpis.cost_data_coverage_percentage < thresholds.cost_coverage_warning_pct:
            insights.append(
                InsightItem(
                    id="data_cost_coverage_warning",
                    category=InsightCategory.DATA_QUALITY,
                    severity=InsightSeverity.WARNING,
                    title="Incomplete Product Cost Data",
                    message=f"Cost data coverage is {fin_kpis.cost_data_coverage_percentage}%. Profitability and COGS metrics may be understated or incomplete.",
                    metric="cost_data_coverage_percentage",
                    current_value=fin_kpis.cost_data_coverage_percentage,
                    threshold=thresholds.cost_coverage_warning_pct,
                    recommendation="Enter missing purchase cost prices in product management to enable 100% accurate gross margin and profit calculations.",
                    evidence={
                        "cost_data_coverage_percentage": fin_kpis.cost_data_coverage_percentage,
                        "note": fin_kpis.note
                    }
                )
            )
