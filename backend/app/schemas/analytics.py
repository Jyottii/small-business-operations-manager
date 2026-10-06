from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class BaseAnalyticsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class SalesKPIs(BaseAnalyticsModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    completed_orders_count: int
    cancelled_orders_count: int
    pending_orders_count: int
    returned_orders_count: int

class InventoryKPIs(BaseAnalyticsModel):
    total_inventory_units: float
    total_inventory_value: float
    low_stock_count: int
    out_of_stock_count: int
    total_products: int
    total_stock_movements: int

class CustomerKPIs(BaseAnalyticsModel):
    total_customers: int
    total_receivables: float
    active_customers_in_period: int

class SupplierKPIs(BaseAnalyticsModel):
    total_suppliers: int
    total_payables: float

class PurchasingKPIs(BaseAnalyticsModel):
    total_purchase_spend: float
    total_purchase_orders: int
    received_purchase_orders: int
    pending_purchase_orders: int
    cancelled_purchase_orders: int

class ReturnKPIs(BaseAnalyticsModel):
    total_returns: int
    total_returned_quantity: float
    total_refund_amount: float

class FinancialKPIs(BaseAnalyticsModel):
    total_sales: float
    collected_payments: float
    outstanding_receivables: float
    total_purchases: float
    outstanding_payables: float
    total_expenses: float
    total_refunds: float
    cogs: float
    gross_profit: float
    gross_margin_percentage: float
    net_profit: float
    net_margin_percentage: float
    cost_data_coverage_percentage: float
    note: Optional[str] = None

class TimeSeriesPoint(BaseAnalyticsModel):
    date: str
    revenue: float = 0.0
    order_count: int = 0
    purchase_spend: float = 0.0
    po_count: int = 0
    payments_collected: float = 0.0
    refunds: float = 0.0
    expenses: float = 0.0

class ProductPerformanceItem(BaseAnalyticsModel):
    product_id: str
    name: str
    sku: str
    quantity_sold: float
    revenue: float
    current_stock: float
    reorder_level: float
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    gross_profit: Optional[float] = None
    velocity_per_day: float
    status: str

class CustomerPerformanceItem(BaseAnalyticsModel):
    customer_id: str
    name: str
    email: Optional[str] = None
    order_count: int
    total_spent: float
    outstanding_balance: float
    average_order_value: float

class WarehouseStockItem(BaseAnalyticsModel):
    warehouse_id: str
    warehouse_name: str
    total_units: float
    total_value: float

class StockMovementSummary(BaseAnalyticsModel):
    movement_type: str
    total_quantity: float
    movement_count: int

class AnalyticsSummaryResponse(BaseAnalyticsModel):
    period: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sales: SalesKPIs
    inventory: InventoryKPIs
    customers: CustomerKPIs
    suppliers: SupplierKPIs
    purchasing: PurchasingKPIs
    returns: ReturnKPIs
    financial: FinancialKPIs
    recent_trend: List[TimeSeriesPoint]

class SalesAnalyticsResponse(BaseAnalyticsModel):
    period: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    kpis: SalesKPIs
    timeline: List[TimeSeriesPoint]
    payment_methods: List[Dict[str, Any]]
    top_products: List[ProductPerformanceItem]

class ProductsAnalyticsResponse(BaseAnalyticsModel):
    period: str
    top_by_revenue: List[ProductPerformanceItem]
    top_by_quantity: List[ProductPerformanceItem]
    slow_moving: List[ProductPerformanceItem]
    low_stock: List[ProductPerformanceItem]

class CustomersAnalyticsResponse(BaseAnalyticsModel):
    period: str
    kpis: CustomerKPIs
    top_customers: List[CustomerPerformanceItem]

class InventoryAnalyticsResponse(BaseAnalyticsModel):
    kpis: InventoryKPIs
    by_warehouse: List[WarehouseStockItem]
    stock_movement_summary: List[StockMovementSummary]
    fast_moving_products: List[ProductPerformanceItem]
    slow_moving_products: List[ProductPerformanceItem]
    low_stock_products: List[ProductPerformanceItem]

class PurchasesAnalyticsResponse(BaseAnalyticsModel):
    period: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    kpis: PurchasingKPIs
    timeline: List[TimeSeriesPoint]
    top_suppliers: List[Dict[str, Any]]

class ReturnsAnalyticsResponse(BaseAnalyticsModel):
    period: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    kpis: ReturnKPIs
    timeline: List[TimeSeriesPoint]
