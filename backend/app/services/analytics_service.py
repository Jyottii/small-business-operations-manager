from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.payment import Payment
from app.models.return_order import Return, ReturnItem
from app.models.expense import Expense
from app.models.warehouse import Warehouse

from app.schemas.analytics import (
    SalesKPIs,
    InventoryKPIs,
    CustomerKPIs,
    SupplierKPIs,
    PurchasingKPIs,
    ReturnKPIs,
    FinancialKPIs,
    TimeSeriesPoint,
    ProductPerformanceItem,
    CustomerPerformanceItem,
    WarehouseStockItem,
    StockMovementSummary,
    AnalyticsSummaryResponse,
    SalesAnalyticsResponse,
    ProductsAnalyticsResponse,
    CustomersAnalyticsResponse,
    InventoryAnalyticsResponse,
    PurchasesAnalyticsResponse,
    ReturnsAnalyticsResponse,
)

class AnalyticsService:

    @staticmethod
    def get_date_bounds(
        period: str = "last_30_days",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[Optional[datetime], Optional[datetime], int]:
        """
        Determines the datetime range [start_dt, end_dt] and number of days in the window.
        Supported periods:
        - today
        - last_7_days
        - last_30_days
        - current_month
        - previous_month
        - all_time
        - custom (uses start_date and end_date)
        """
        now = datetime.utcnow()
        today_midnight = datetime(now.year, now.month, now.day)

        if period == "today":
            start_dt = today_midnight
            end_dt = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            return start_dt, end_dt, 1

        elif period == "last_7_days":
            start_dt = today_midnight - timedelta(days=6)
            end_dt = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            return start_dt, end_dt, 7

        elif period == "last_30_days":
            start_dt = today_midnight - timedelta(days=29)
            end_dt = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            return start_dt, end_dt, 30

        elif period == "current_month":
            start_dt = datetime(now.year, now.month, 1)
            end_dt = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            days = max((end_dt - start_dt).days + 1, 1)
            return start_dt, end_dt, days

        elif period == "previous_month":
            # First day of current month minus 1 day = last day of prev month
            first_curr = datetime(now.year, now.month, 1)
            last_prev = first_curr - timedelta(days=1)
            start_dt = datetime(last_prev.year, last_prev.month, 1)
            end_dt = datetime(last_prev.year, last_prev.month, last_prev.day, 23, 59, 59, 999999)
            days = max((end_dt - start_dt).days + 1, 1)
            return start_dt, end_dt, days

        elif period == "all_time":
            return None, None, 365

        elif period == "custom":
            s = start_date or (today_midnight - timedelta(days=29))
            e = end_date or datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            days = max((e - s).days + 1, 1)
            return s, e, days

        else:
            # Default to last 30 days
            start_dt = today_midnight - timedelta(days=29)
            end_dt = datetime(now.year, now.month, now.day, 23, 59, 59, 999999)
            return start_dt, end_dt, 30

    @classmethod
    def get_sales_kpis(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> SalesKPIs:
        date_expr = func.coalesce(Order.order_date, Order.created_at)
        filters = [Order.business_id == business_id]
        if start_dt:
            filters.append(date_expr >= start_dt)
        if end_dt:
            filters.append(date_expr <= end_dt)

        # Non-cancelled sales query
        sales_q = db.query(
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.count(Order.id).label("total_orders"),
            func.count(case((Order.status == "Completed", 1), else_=None)).label("completed"),
            func.count(case((Order.status == "Pending", 1), else_=None)).label("pending")
        ).filter(and_(*filters, Order.status != "Cancelled")).first()

        # Cancelled orders query
        cancelled_q = db.query(
            func.count(Order.id)
        ).filter(and_(*filters, Order.status == "Cancelled")).scalar() or 0

        # Returned orders query (orders that have an associated Return)
        returned_orders_count = db.query(
            func.count(func.distinct(Return.order_id))
        ).join(Order, Return.order_id == Order.id).filter(
            and_(*filters, Return.business_id == business_id)
        ).scalar() or 0

        revenue = float(sales_q.revenue or 0.0)
        total_orders = int(sales_q.total_orders or 0)
        aov = round(revenue / total_orders, 2) if total_orders > 0 else 0.0

        return SalesKPIs(
            total_revenue=round(revenue, 2),
            total_orders=total_orders,
            average_order_value=aov,
            completed_orders_count=int(sales_q.completed or 0),
            cancelled_orders_count=int(cancelled_q),
            pending_orders_count=int(sales_q.pending or 0),
            returned_orders_count=int(returned_orders_count)
        )

    @classmethod
    def get_inventory_kpis(cls, db: Session, business_id: str) -> InventoryKPIs:
        # Total units and inventory value tied up
        inv_q = db.query(
            func.coalesce(func.sum(Inventory.quantity), 0).label("units"),
            func.coalesce(func.sum(Inventory.quantity * func.coalesce(Product.cost_price, 0)), 0).label("value")
        ).join(Product, Inventory.product_id == Product.id).filter(
            Product.business_id == business_id
        ).first()

        total_units = float(inv_q.units or 0.0)
        total_value = float(inv_q.value or 0.0)

        total_products = db.query(func.count(Product.id)).filter(
            Product.business_id == business_id
        ).scalar() or 0

        # Product-level total stock across warehouses
        prod_stocks = db.query(
            Product.id,
            Product.reorder_level,
            func.coalesce(func.sum(Inventory.quantity), 0).label("stock")
        ).outerjoin(Inventory, Product.id == Inventory.product_id).filter(
            Product.business_id == business_id,
            Product.is_active == True
        ).group_by(Product.id, Product.reorder_level).all()

        low_stock_count = 0
        out_of_stock_count = 0
        for p in prod_stocks:
            stock = float(p.stock or 0.0)
            reorder = float(p.reorder_level or 0.0)
            if stock <= 0:
                out_of_stock_count += 1
            elif reorder > 0 and stock <= reorder:
                low_stock_count += 1

        total_movements = db.query(func.count(StockMovement.id)).filter(
            StockMovement.business_id == business_id
        ).scalar() or 0

        return InventoryKPIs(
            total_inventory_units=round(total_units, 2),
            total_inventory_value=round(total_value, 2),
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            total_products=total_products,
            total_stock_movements=total_movements
        )

    @classmethod
    def get_customer_kpis(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> CustomerKPIs:
        cust_q = db.query(
            func.count(Customer.id).label("total_cust"),
            func.coalesce(func.sum(Customer.outstanding_balance), 0).label("receivables")
        ).filter(Customer.business_id == business_id).first()

        total_customers = int(cust_q.total_cust or 0)
        receivables = float(cust_q.receivables or 0.0)

        order_filters = [Order.business_id == business_id, Order.status != "Cancelled"]
        if start_dt:
            order_filters.append(func.coalesce(Order.order_date, Order.created_at) >= start_dt)
        if end_dt:
            order_filters.append(func.coalesce(Order.order_date, Order.created_at) <= end_dt)

        active_in_period = db.query(func.count(func.distinct(Order.customer_id))).filter(
            and_(*order_filters, Order.customer_id.isnot(None))
        ).scalar() or 0

        return CustomerKPIs(
            total_customers=total_customers,
            total_receivables=round(receivables, 2),
            active_customers_in_period=int(active_in_period)
        )

    @classmethod
    def get_supplier_kpis(cls, db: Session, business_id: str) -> SupplierKPIs:
        supp_q = db.query(
            func.count(Supplier.id).label("total_supp"),
            func.coalesce(func.sum(Supplier.outstanding_balance), 0).label("payables")
        ).filter(Supplier.business_id == business_id).first()

        return SupplierKPIs(
            total_suppliers=int(supp_q.total_supp or 0),
            total_payables=round(float(supp_q.payables or 0.0), 2)
        )

    @classmethod
    def get_purchasing_kpis(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> PurchasingKPIs:
        date_expr = func.coalesce(PurchaseOrder.order_date, PurchaseOrder.created_at)
        filters = [PurchaseOrder.business_id == business_id]
        if start_dt:
            filters.append(date_expr >= start_dt)
        if end_dt:
            filters.append(date_expr <= end_dt)

        po_q = db.query(
            func.coalesce(func.sum(case((PurchaseOrder.status != "Cancelled", PurchaseOrder.total), else_=0)), 0).label("spend"),
            func.count(PurchaseOrder.id).label("total_pos"),
            func.count(case((PurchaseOrder.status == "Received", 1), else_=None)).label("received"),
            func.count(case((PurchaseOrder.status.in_(["Ordered", "Partially Received", "Draft"]), 1), else_=None)).label("pending"),
            func.count(case((PurchaseOrder.status == "Cancelled", 1), else_=None)).label("cancelled")
        ).filter(and_(*filters)).first()

        return PurchasingKPIs(
            total_purchase_spend=round(float(po_q.spend or 0.0), 2),
            total_purchase_orders=int(po_q.total_pos or 0),
            received_purchase_orders=int(po_q.received or 0),
            pending_purchase_orders=int(po_q.pending or 0),
            cancelled_purchase_orders=int(po_q.cancelled or 0)
        )

    @classmethod
    def get_return_kpis(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> ReturnKPIs:
        date_expr = func.coalesce(Return.return_date, Return.created_at)
        filters = [Return.business_id == business_id]
        if start_dt:
            filters.append(date_expr >= start_dt)
        if end_dt:
            filters.append(date_expr <= end_dt)

        ret_q = db.query(
            func.count(func.distinct(Return.id)).label("total_returns"),
            func.coalesce(func.sum(Return.refund_amount), 0).label("refund_amount")
        ).filter(and_(*filters)).first()

        qty_q = db.query(
            func.coalesce(func.sum(ReturnItem.quantity), 0)
        ).join(Return, ReturnItem.return_id == Return.id).filter(
            and_(*filters)
        ).scalar() or 0.0

        return ReturnKPIs(
            total_returns=int(ret_q.total_returns or 0),
            total_returned_quantity=round(float(qty_q or 0.0), 2),
            total_refund_amount=round(float(ret_q.refund_amount or 0.0), 2)
        )

    @classmethod
    def get_financial_kpis(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> FinancialKPIs:
        # Sales & Receivables
        sales_kpi = cls.get_sales_kpis(db, business_id, start_dt, end_dt)
        cust_kpi = cls.get_customer_kpis(db, business_id, start_dt, end_dt)
        purch_kpi = cls.get_purchasing_kpis(db, business_id, start_dt, end_dt)
        supp_kpi = cls.get_supplier_kpis(db, business_id)
        ret_kpi = cls.get_return_kpis(db, business_id, start_dt, end_dt)

        # Collected payments from customer orders
        pay_date_expr = func.coalesce(Payment.payment_date, Payment.created_at)
        pay_filters = [Payment.business_id == business_id]
        if start_dt:
            pay_filters.append(pay_date_expr >= start_dt)
        if end_dt:
            pay_filters.append(pay_date_expr <= end_dt)

        collected_payments = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            and_(*pay_filters, or_(Payment.customer_id.isnot(None), Payment.order_id.isnot(None)))
        ).scalar() or 0.0

        # Expenses
        exp_date_expr = func.coalesce(Expense.expense_date, Expense.created_at)
        exp_filters = [Expense.business_id == business_id]
        if start_dt:
            exp_filters.append(exp_date_expr >= start_dt)
        if end_dt:
            exp_filters.append(exp_date_expr <= end_dt)

        total_expenses = db.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(and_(*exp_filters)).scalar() or 0.0

        # Cost of Goods Sold (COGS) calculation from OrderItems
        order_date_expr = func.coalesce(Order.order_date, Order.created_at)
        cogs_filters = [Order.business_id == business_id, Order.status != "Cancelled"]
        if start_dt:
            cogs_filters.append(order_date_expr >= start_dt)
        if end_dt:
            cogs_filters.append(order_date_expr <= end_dt)

        cogs_stats = db.query(
            func.coalesce(func.sum(OrderItem.quantity * func.coalesce(Product.cost_price, 0)), 0).label("cogs"),
            func.count(OrderItem.id).label("total_items"),
            func.count(case((Product.cost_price.is_(None), 1), else_=None)).label("missing_cost_items")
        ).join(Order, OrderItem.order_id == Order.id).outerjoin(
            Product, OrderItem.product_id == Product.id
        ).filter(and_(*cogs_filters)).first()

        cogs = float(cogs_stats.cogs or 0.0)
        total_items = int(cogs_stats.total_items or 0)
        missing_costs = int(cogs_stats.missing_cost_items or 0)

        coverage = 100.0
        if total_items > 0:
            coverage = round(((total_items - missing_costs) / total_items) * 100, 1)

        total_sales = sales_kpi.total_revenue
        gross_profit = total_sales - cogs
        gross_margin = round((gross_profit / total_sales) * 100, 1) if total_sales > 0 else 0.0

        net_profit = gross_profit - float(total_expenses)
        net_margin = round((net_profit / total_sales) * 100, 1) if total_sales > 0 else 0.0

        note = "COGS calculated from product purchase cost prices on sold items."
        if coverage < 100.0:
            note += f" Warning: {missing_costs} order line items lacked product cost data ({coverage}% coverage)."

        return FinancialKPIs(
            total_sales=round(total_sales, 2),
            collected_payments=round(float(collected_payments), 2),
            outstanding_receivables=cust_kpi.total_receivables,
            total_purchases=purch_kpi.total_purchase_spend,
            outstanding_payables=supp_kpi.total_payables,
            total_expenses=round(float(total_expenses), 2),
            total_refunds=ret_kpi.total_refund_amount,
            cogs=round(cogs, 2),
            gross_profit=round(gross_profit, 2),
            gross_margin_percentage=gross_margin,
            net_profit=round(net_profit, 2),
            net_margin_percentage=net_margin,
            cost_data_coverage_percentage=coverage,
            note=note
        )

    @classmethod
    def get_time_series_timeline(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> List[TimeSeriesPoint]:
        """
        Aggregates daily revenue, order count, purchase spend, payments collected,
        refunds, and expenses into a unified time series.
        """
        date_dict: Dict[str, Dict[str, float]] = {}

        def get_entry(d_str: str) -> Dict[str, float]:
            if d_str not in date_dict:
                date_dict[d_str] = {
                    "revenue": 0.0,
                    "order_count": 0,
                    "purchase_spend": 0.0,
                    "po_count": 0,
                    "payments_collected": 0.0,
                    "refunds": 0.0,
                    "expenses": 0.0,
                }
            return date_dict[d_str]

        # 1. Orders
        order_date_expr = func.coalesce(Order.order_date, Order.created_at)
        order_filters = [Order.business_id == business_id, Order.status != "Cancelled"]
        if start_dt:
            order_filters.append(order_date_expr >= start_dt)
        if end_dt:
            order_filters.append(order_date_expr <= end_dt)

        order_rows = db.query(
            func.date(order_date_expr).label("day"),
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.count(Order.id).label("count")
        ).filter(and_(*order_filters)).group_by(func.date(order_date_expr)).all()

        for r in order_rows:
            if r.day:
                d = str(r.day)
                e = get_entry(d)
                e["revenue"] = float(r.revenue or 0.0)
                e["order_count"] = int(r.count or 0)

        # 2. Purchase Orders
        po_date_expr = func.coalesce(PurchaseOrder.order_date, PurchaseOrder.created_at)
        po_filters = [PurchaseOrder.business_id == business_id, PurchaseOrder.status != "Cancelled"]
        if start_dt:
            po_filters.append(po_date_expr >= start_dt)
        if end_dt:
            po_filters.append(po_date_expr <= end_dt)

        po_rows = db.query(
            func.date(po_date_expr).label("day"),
            func.coalesce(func.sum(PurchaseOrder.total), 0).label("spend"),
            func.count(PurchaseOrder.id).label("count")
        ).filter(and_(*po_filters)).group_by(func.date(po_date_expr)).all()

        for r in po_rows:
            if r.day:
                d = str(r.day)
                e = get_entry(d)
                e["purchase_spend"] = float(r.spend or 0.0)
                e["po_count"] = int(r.count or 0)

        # 3. Payments collected
        pay_date_expr = func.coalesce(Payment.payment_date, Payment.created_at)
        pay_filters = [Payment.business_id == business_id, or_(Payment.customer_id.isnot(None), Payment.order_id.isnot(None))]
        if start_dt:
            pay_filters.append(pay_date_expr >= start_dt)
        if end_dt:
            pay_filters.append(pay_date_expr <= end_dt)

        pay_rows = db.query(
            func.date(pay_date_expr).label("day"),
            func.coalesce(func.sum(Payment.amount), 0).label("collected")
        ).filter(and_(*pay_filters)).group_by(func.date(pay_date_expr)).all()

        for r in pay_rows:
            if r.day:
                d = str(r.day)
                e = get_entry(d)
                e["payments_collected"] = float(r.collected or 0.0)

        # 4. Refunds
        ret_date_expr = func.coalesce(Return.return_date, Return.created_at)
        ret_filters = [Return.business_id == business_id]
        if start_dt:
            ret_filters.append(ret_date_expr >= start_dt)
        if end_dt:
            ret_filters.append(ret_date_expr <= end_dt)

        ret_rows = db.query(
            func.date(ret_date_expr).label("day"),
            func.coalesce(func.sum(Return.refund_amount), 0).label("refunds")
        ).filter(and_(*ret_filters)).group_by(func.date(ret_date_expr)).all()

        for r in ret_rows:
            if r.day:
                d = str(r.day)
                e = get_entry(d)
                e["refunds"] = float(r.refunds or 0.0)

        # 5. Expenses
        exp_date_expr = func.coalesce(Expense.expense_date, Expense.created_at)
        exp_filters = [Expense.business_id == business_id]
        if start_dt:
            exp_filters.append(exp_date_expr >= start_dt)
        if end_dt:
            exp_filters.append(exp_date_expr <= end_dt)

        exp_rows = db.query(
            func.date(exp_date_expr).label("day"),
            func.coalesce(func.sum(Expense.amount), 0).label("expenses")
        ).filter(and_(*exp_filters)).group_by(func.date(exp_date_expr)).all()

        for r in exp_rows:
            if r.day:
                d = str(r.day)
                e = get_entry(d)
                e["expenses"] = float(r.expenses or 0.0)

        sorted_days = sorted(date_dict.keys())
        points = []
        for day in sorted_days:
            data = date_dict[day]
            points.append(
                TimeSeriesPoint(
                    date=day,
                    revenue=round(data["revenue"], 2),
                    order_count=int(data["order_count"]),
                    purchase_spend=round(data["purchase_spend"], 2),
                    po_count=int(data["po_count"]),
                    payments_collected=round(data["payments_collected"], 2),
                    refunds=round(data["refunds"], 2),
                    expenses=round(data["expenses"], 2)
                )
            )

        return points

    @classmethod
    def get_product_analytics(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        days_count: int = 30,
        limit: int = 10
    ) -> ProductsAnalyticsResponse:
        """
        Determines:
        - Top products by revenue
        - Top products by quantity sold
        - Slow-moving / stagnant products
        - Low-stock products

        Fast/Slow Moving Deterministic Rule:
        Velocity V = quantity_sold / max(days_count, 1) (units per day)
        - Fast-Moving: V >= 0.2 units/day and quantity_sold > 0
        - Slow-Moving: Current Stock > 0 and V < 0.05 units/day
        """
        # 1. Product sales in period
        order_date_expr = func.coalesce(Order.order_date, Order.created_at)
        order_filters = [Order.business_id == business_id, Order.status != "Cancelled"]
        if start_dt:
            order_filters.append(order_date_expr >= start_dt)
        if end_dt:
            order_filters.append(order_date_expr <= end_dt)

        sales_subq = db.query(
            OrderItem.product_id,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty_sold"),
            func.coalesce(func.sum(OrderItem.line_total), 0).label("revenue")
        ).join(Order, OrderItem.order_id == Order.id).filter(
            and_(*order_filters)
        ).group_by(OrderItem.product_id).subquery()

        # 2. Current stock per product across warehouses
        stock_subq = db.query(
            Inventory.product_id,
            func.coalesce(func.sum(Inventory.quantity), 0).label("current_stock")
        ).group_by(Inventory.product_id).subquery()

        # 3. Main product query
        rows = db.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.reorder_level,
            Product.cost_price,
            Product.selling_price,
            Product.is_active,
            func.coalesce(sales_subq.c.qty_sold, 0).label("qty_sold"),
            func.coalesce(sales_subq.c.revenue, 0).label("revenue"),
            func.coalesce(stock_subq.c.current_stock, 0).label("current_stock")
        ).outerjoin(sales_subq, Product.id == sales_subq.c.product_id).outerjoin(
            stock_subq, Product.id == stock_subq.c.product_id
        ).filter(
            Product.business_id == business_id
        ).all()

        items: List[ProductPerformanceItem] = []
        for r in rows:
            qty_sold = float(r.qty_sold or 0.0)
            revenue = float(r.revenue or 0.0)
            stock = float(r.current_stock or 0.0)
            reorder = float(r.reorder_level or 0.0)
            cost = float(r.cost_price) if r.cost_price is not None else None
            selling = float(r.selling_price) if r.selling_price is not None else None

            gross_profit = None
            if cost is not None:
                gross_profit = round(revenue - (qty_sold * cost), 2)

            velocity = round(qty_sold / max(days_count, 1), 2)

            # Determine deterministic status
            if stock <= 0:
                status = "Out of Stock"
            elif reorder > 0 and stock <= reorder:
                status = "Low Stock"
            elif velocity >= 0.2 and qty_sold > 0:
                status = "Fast-Moving"
            elif stock > 0 and velocity < 0.05:
                status = "Slow-Moving"
            else:
                status = "Normal"

            items.append(
                ProductPerformanceItem(
                    product_id=r.id,
                    name=r.name,
                    sku=r.sku,
                    quantity_sold=round(qty_sold, 2),
                    revenue=round(revenue, 2),
                    current_stock=round(stock, 2),
                    reorder_level=round(reorder, 2),
                    cost_price=cost,
                    selling_price=selling,
                    gross_profit=gross_profit,
                    velocity_per_day=velocity,
                    status=status
                )
            )

        # Rankings
        top_by_revenue = sorted(items, key=lambda x: x.revenue, reverse=True)[:limit]
        top_by_quantity = sorted(items, key=lambda x: x.quantity_sold, reverse=True)[:limit]
        slow_moving = [x for x in items if x.status == "Slow-Moving"]
        slow_moving.sort(key=lambda x: x.current_stock * (x.cost_price or x.selling_price or 1.0), reverse=True)
        low_stock = [x for x in items if x.status in ("Low Stock", "Out of Stock")]
        low_stock.sort(key=lambda x: x.current_stock)

        return ProductsAnalyticsResponse(
            period=f"{days_count} days",
            top_by_revenue=top_by_revenue,
            top_by_quantity=top_by_quantity,
            slow_moving=slow_moving[:limit],
            low_stock=low_stock[:limit]
        )

    @classmethod
    def get_customer_analytics(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None,
        limit: int = 10
    ) -> CustomersAnalyticsResponse:
        kpis = cls.get_customer_kpis(db, business_id, start_dt, end_dt)

        order_date_expr = func.coalesce(Order.order_date, Order.created_at)
        order_filters = [Order.business_id == business_id, Order.status != "Cancelled"]
        if start_dt:
            order_filters.append(order_date_expr >= start_dt)
        if end_dt:
            order_filters.append(order_date_expr <= end_dt)

        rows = db.query(
            Customer.id,
            Customer.name,
            Customer.email,
            Customer.outstanding_balance,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.total), 0).label("total_spent")
        ).join(Order, Customer.id == Order.customer_id).filter(
            and_(*order_filters)
        ).group_by(
            Customer.id, Customer.name, Customer.email, Customer.outstanding_balance
        ).order_by(
            func.sum(Order.total).desc()
        ).limit(limit).all()

        top_customers = []
        for r in rows:
            orders = int(r.order_count or 0)
            spent = float(r.total_spent or 0.0)
            aov = round(spent / orders, 2) if orders > 0 else 0.0
            top_customers.append(
                CustomerPerformanceItem(
                    customer_id=r.id,
                    name=r.name,
                    email=r.email,
                    order_count=orders,
                    total_spent=round(spent, 2),
                    outstanding_balance=round(float(r.outstanding_balance or 0.0), 2),
                    average_order_value=aov
                )
            )

        return CustomersAnalyticsResponse(
            period="Selected",
            kpis=kpis,
            top_customers=top_customers
        )

    @classmethod
    def get_inventory_analytics(
        cls,
        db: Session,
        business_id: str,
        days_count: int = 30
    ) -> InventoryAnalyticsResponse:
        kpis = cls.get_inventory_kpis(db, business_id)

        # Warehouse breakdown
        wh_rows = db.query(
            Warehouse.id,
            Warehouse.name,
            func.coalesce(func.sum(Inventory.quantity), 0).label("units"),
            func.coalesce(func.sum(Inventory.quantity * func.coalesce(Product.cost_price, 0)), 0).label("val")
        ).join(Inventory, Warehouse.id == Inventory.warehouse_id).join(
            Product, Inventory.product_id == Product.id
        ).filter(
            Warehouse.business_id == business_id
        ).group_by(Warehouse.id, Warehouse.name).all()

        by_wh = [
            WarehouseStockItem(
                warehouse_id=w.id,
                warehouse_name=w.name,
                total_units=round(float(w.units or 0.0), 2),
                total_value=round(float(w.val or 0.0), 2)
            )
            for w in wh_rows
        ]

        # Stock movements breakdown
        mov_rows = db.query(
            StockMovement.movement_type,
            func.coalesce(func.sum(StockMovement.quantity), 0).label("qty"),
            func.count(StockMovement.id).label("cnt")
        ).filter(
            StockMovement.business_id == business_id
        ).group_by(StockMovement.movement_type).all()

        mov_summary = [
            StockMovementSummary(
                movement_type=m.movement_type,
                total_quantity=round(float(m.qty or 0.0), 2),
                movement_count=int(m.cnt or 0)
            )
            for m in mov_rows
        ]

        prod_resp = cls.get_product_analytics(db, business_id, days_count=days_count, limit=20)

        fast_moving = [p for p in prod_resp.top_by_quantity if p.status == "Fast-Moving"]

        return InventoryAnalyticsResponse(
            kpis=kpis,
            by_warehouse=by_wh,
            stock_movement_summary=mov_summary,
            fast_moving_products=fast_moving,
            slow_moving_products=prod_resp.slow_moving,
            low_stock_products=prod_resp.low_stock
        )

    @classmethod
    def get_purchasing_analytics(
        cls,
        db: Session,
        business_id: str,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
    ) -> PurchasesAnalyticsResponse:
        kpis = cls.get_purchasing_kpis(db, business_id, start_dt, end_dt)
        timeline = cls.get_time_series_timeline(db, business_id, start_dt, end_dt)

        date_expr = func.coalesce(PurchaseOrder.order_date, PurchaseOrder.created_at)
        filters = [PurchaseOrder.business_id == business_id, PurchaseOrder.status != "Cancelled"]
        if start_dt:
            filters.append(date_expr >= start_dt)
        if end_dt:
            filters.append(date_expr <= end_dt)

        supp_rows = db.query(
            Supplier.id,
            Supplier.name,
            func.count(PurchaseOrder.id).label("po_count"),
            func.coalesce(func.sum(PurchaseOrder.total), 0).label("spend")
        ).join(PurchaseOrder, Supplier.id == PurchaseOrder.supplier_id).filter(
            and_(*filters)
        ).group_by(Supplier.id, Supplier.name).order_by(
            func.sum(PurchaseOrder.total).desc()
        ).limit(10).all()

        top_suppliers = [
            {
                "supplier_id": s.id,
                "name": s.name,
                "po_count": int(s.po_count or 0),
                "total_spend": round(float(s.spend or 0.0), 2)
            }
            for s in supp_rows
        ]

        return PurchasesAnalyticsResponse(
            period="Selected",
            start_date=start_dt.strftime("%Y-%m-%d") if start_dt else None,
            end_date=end_dt.strftime("%Y-%m-%d") if end_dt else None,
            kpis=kpis,
            timeline=timeline,
            top_suppliers=top_suppliers
        )

    @classmethod
    def get_summary(
        cls,
        db: Session,
        business_id: str,
        period: str = "last_30_days",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsSummaryResponse:
        start_dt, end_dt, days = cls.get_date_bounds(period, start_date, end_date)

        sales = cls.get_sales_kpis(db, business_id, start_dt, end_dt)
        inventory = cls.get_inventory_kpis(db, business_id)
        customers = cls.get_customer_kpis(db, business_id, start_dt, end_dt)
        suppliers = cls.get_supplier_kpis(db, business_id)
        purchasing = cls.get_purchasing_kpis(db, business_id, start_dt, end_dt)
        returns = cls.get_return_kpis(db, business_id, start_dt, end_dt)
        financial = cls.get_financial_kpis(db, business_id, start_dt, end_dt)
        recent_trend = cls.get_time_series_timeline(db, business_id, start_dt, end_dt)

        return AnalyticsSummaryResponse(
            period=period,
            start_date=start_dt.strftime("%Y-%m-%d") if start_dt else None,
            end_date=end_dt.strftime("%Y-%m-%d") if end_dt else None,
            sales=sales,
            inventory=inventory,
            customers=customers,
            suppliers=suppliers,
            purchasing=purchasing,
            returns=returns,
            financial=financial,
            recent_trend=recent_trend
        )
