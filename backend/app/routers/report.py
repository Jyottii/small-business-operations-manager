import csv
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.order import Order
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.models.purchase_order import PurchaseOrder
from app.models.supplier import Supplier
from app.models.expense import Expense
from app.models.customer import Customer
from app.models.payment import Payment
from app.schemas.base import ResponseModel
from app.core.exceptions import BadRequestException

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_ROLES = (UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)

@router.get("/sales")
def get_sales_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES)),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = db.query(Order).filter(Order.business_id == current_user.business_id)
    if start_date:
        query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))

    orders = query.order_by(Order.created_at.desc()).all()
    total_revenue = sum(float(o.total_amount or 0) for o in orders)
    order_count = len(orders)
    avg_order_value = round(total_revenue / order_count, 2) if order_count > 0 else 0.0

    status_counts = {}
    for o in orders:
        status_counts[o.status] = status_counts.get(o.status, 0) + 1

    return {
        "data": {
            "total_revenue": round(total_revenue, 2),
            "order_count": order_count,
            "average_order_value": avg_order_value,
            "status_breakdown": status_counts,
            "orders": [
                {
                    "id": o.id,
                    "order_number": o.order_number,
                    "customer_id": o.customer_id,
                    "status": o.status,
                    "total_amount": float(o.total_amount or 0),
                    "created_at": o.created_at.isoformat() if o.created_at else None
                }
                for o in orders[:50]
            ]
        }
    }

@router.get("/inventory")
def get_inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES))
):
    items = db.query(Inventory, Product, Warehouse).join(
        Product, Inventory.product_id == Product.id
    ).join(
        Warehouse, Inventory.warehouse_id == Warehouse.id
    ).filter(
        Product.business_id == current_user.business_id
    ).all()

    total_stock = 0
    total_valuation = 0.0
    low_stock_items = []
    out_of_stock_items = []

    rows = []
    for inv, prod, wh in items:
        qty = float(inv.quantity or 0)
        cost = float(prod.cost_price or 0)
        selling = float(prod.selling_price or 0)
        reorder = float(inv.reorder_level if inv.reorder_level is not None and inv.reorder_level > 0 else (prod.reorder_level or 0))
        val = qty * cost

        total_stock += int(qty)
        total_valuation += val

        row = {
            "product_id": prod.id,
            "product_name": prod.name,
            "sku": prod.sku,
            "warehouse_name": wh.name,
            "quantity": qty,
            "cost_price": cost,
            "selling_price": selling,
            "valuation": round(val, 2),
            "reorder_level": reorder
        }
        rows.append(row)

        if qty <= 0:
            out_of_stock_items.append(row)
        elif qty <= reorder:
            low_stock_items.append(row)

    return {
        "data": {
            "total_stock": total_stock,
            "total_valuation": round(total_valuation, 2),
            "total_skus": len(items),
            "low_stock_count": len(low_stock_items),
            "out_of_stock_count": len(out_of_stock_items),
            "items": rows[:100]
        }
    }

@router.get("/purchases")
def get_purchases_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES))
):
    pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.business_id == current_user.business_id
    ).order_by(PurchaseOrder.created_at.desc()).all()

    total_spend = sum(float(po.total_amount or 0) for po in pos)
    status_counts = {}
    for po in pos:
        status_counts[po.status] = status_counts.get(po.status, 0) + 1

    return {
        "data": {
            "total_spend": round(total_spend, 2),
            "po_count": len(pos),
            "status_breakdown": status_counts,
            "orders": [
                {
                    "id": po.id,
                    "po_number": po.po_number,
                    "supplier_id": po.supplier_id,
                    "status": po.status,
                    "total_amount": float(po.total_amount or 0),
                    "created_at": po.created_at.isoformat() if po.created_at else None
                }
                for po in pos[:50]
            ]
        }
    }

@router.get("/expenses")
def get_expenses_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES))
):
    expenses = db.query(Expense).filter(
        Expense.business_id == current_user.business_id
    ).order_by(Expense.created_at.desc()).all()

    total_expense = sum(float(e.amount or 0) for e in expenses)
    by_category = {}
    for e in expenses:
        cat = e.category or "Uncategorized"
        by_category[cat] = by_category.get(cat, 0.0) + float(e.amount or 0)

    return {
        "data": {
            "total_expense": round(total_expense, 2),
            "expense_count": len(expenses),
            "by_category": {k: round(v, 2) for k, v in by_category.items()},
            "expenses": [
                {
                    "id": e.id,
                    "title": e.title if hasattr(e, 'title') else e.category,
                    "category": e.category,
                    "amount": float(e.amount or 0),
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in expenses[:50]
            ]
        }
    }

@router.get("/customers")
def get_customers_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES))
):
    customers = db.query(Customer).filter(
        Customer.business_id == current_user.business_id
    ).all()

    total_receivables = 0.0
    cust_data = []
    for c in customers:
        # compute customer orders
        orders = db.query(Order).filter(
            Order.customer_id == c.id,
            Order.business_id == current_user.business_id
        ).all()
        spent = sum(float(o.total_amount or 0) for o in orders)
        balance = float(c.current_balance or 0) if hasattr(c, 'current_balance') else 0.0
        total_receivables += balance
        cust_data.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "total_orders": len(orders),
            "total_spent": round(spent, 2),
            "balance": round(balance, 2)
        })

    cust_data.sort(key=lambda x: x["total_spent"], reverse=True)
    return {
        "data": {
            "total_customers": len(customers),
            "total_receivables": round(total_receivables, 2),
            "customers": cust_data[:50]
        }
    }

@router.get("/export")
def export_report_csv(
    report_type: str = Query(..., description="Report type: sales, inventory, purchases, expenses, customers"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REPORT_ROLES))
):
    output = io.StringIO()
    writer = csv.writer(output)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_type}_report_{timestamp}.csv"

    if report_type == "sales":
        orders = db.query(Order).filter(Order.business_id == current_user.business_id).all()
        writer.writerow(["Order Number", "Date", "Status", "Total Amount"])
        for o in orders:
            writer.writerow([
                o.order_number,
                o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
                o.status,
                f"{float(o.total_amount or 0):.2f}"
            ])

    elif report_type == "inventory":
        items = db.query(Inventory, Product, Warehouse).join(
            Product, Inventory.product_id == Product.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).filter(
            Product.business_id == current_user.business_id
        ).all()
        writer.writerow(["Product Name", "SKU", "Warehouse", "Quantity", "Cost Price", "Selling Price", "Valuation"])
        for inv, prod, wh in items:
            qty = float(inv.quantity or 0)
            cost = float(prod.cost_price or 0)
            writer.writerow([
                prod.name,
                prod.sku,
                wh.name,
                qty,
                f"{cost:.2f}",
                f"{float(prod.selling_price or 0):.2f}",
                f"{qty * cost:.2f}"
            ])

    elif report_type == "purchases":
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.business_id == current_user.business_id).all()
        writer.writerow(["PO Number", "Date", "Status", "Total Amount"])
        for po in pos:
            writer.writerow([
                po.po_number,
                po.created_at.strftime("%Y-%m-%d %H:%M") if po.created_at else "",
                po.status,
                f"{float(po.total_amount or 0):.2f}"
            ])

    elif report_type == "expenses":
        expenses = db.query(Expense).filter(Expense.business_id == current_user.business_id).all()
        writer.writerow(["Date", "Category", "Amount", "Description"])
        for e in expenses:
            writer.writerow([
                e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else "",
                e.category,
                f"{float(e.amount or 0):.2f}",
                getattr(e, 'description', '')
            ])

    elif report_type == "customers":
        customers = db.query(Customer).filter(Customer.business_id == current_user.business_id).all()
        writer.writerow(["Name", "Email", "Phone", "Total Orders", "Total Spent"])
        for c in customers:
            orders = db.query(Order).filter(
                Order.customer_id == c.id,
                Order.business_id == current_user.business_id
            ).all()
            spent = sum(float(o.total_amount or 0) for o in orders)
            writer.writerow([
                c.name,
                c.email or "",
                c.phone or "",
                len(orders),
                f"{spent:.2f}"
            ])
    else:
        raise BadRequestException(f"Unsupported report type: '{report_type}'")

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
