from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import Order
from app.models.purchase_order import PurchaseOrder
from app.models.warehouse import Warehouse
from app.models.branch import Branch
from app.schemas.base import ResponseModel
from pydantic import BaseModel

class SearchResultItem(BaseModel):
    category: str  # product, customer, supplier, order, purchase_order, warehouse, branch
    id: str
    title: str
    subtitle: Optional[str] = None
    badge: Optional[str] = None
    url: str

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=ResponseModel[SearchResponse])
def universal_search(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(5, ge=1, le=20, description="Max results per entity category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    search_term = f"%{q.strip()}%"
    results: List[SearchResultItem] = []
    biz_id = current_user.business_id

    # 1. Products
    products = db.query(Product).filter(
        Product.business_id == biz_id,
        or_(
            Product.name.ilike(search_term),
            Product.sku.ilike(search_term),
            Product.barcode.ilike(search_term)
        )
    ).limit(limit).all()
    for p in products:
        results.append(SearchResultItem(
            category="product",
            id=p.id,
            title=p.name,
            subtitle=f"SKU: {p.sku} | ${float(p.selling_price or 0):.2f}",
            badge="Product",
            url=f"/products"
        ))

    # 2. Customers
    customers = db.query(Customer).filter(
        Customer.business_id == biz_id,
        or_(
            Customer.name.ilike(search_term),
            Customer.email.ilike(search_term),
            Customer.phone.ilike(search_term)
        )
    ).limit(limit).all()
    for c in customers:
        results.append(SearchResultItem(
            category="customer",
            id=c.id,
            title=c.name,
            subtitle=c.email or c.phone or "Customer",
            badge="Customer",
            url=f"/customers"
        ))

    # 3. Suppliers
    suppliers = db.query(Supplier).filter(
        Supplier.business_id == biz_id,
        or_(
            Supplier.name.ilike(search_term),
            Supplier.company_name.ilike(search_term),
            Supplier.email.ilike(search_term)
        )
    ).limit(limit).all()
    for s in suppliers:
        results.append(SearchResultItem(
            category="supplier",
            id=s.id,
            title=s.name,
            subtitle=s.company_name or s.email or "Supplier",
            badge="Supplier",
            url=f"/suppliers"
        ))

    # 4. Orders
    orders = db.query(Order).filter(
        Order.business_id == biz_id,
        Order.order_number.ilike(search_term)
    ).limit(limit).all()
    for o in orders:
        results.append(SearchResultItem(
            category="order",
            id=o.id,
            title=o.order_number,
            subtitle=f"${float(o.total_amount or 0):.2f}",
            badge=o.status,
            url=f"/orders"
        ))

    # 5. Purchase Orders
    pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.business_id == biz_id,
        PurchaseOrder.purchase_order_number.ilike(search_term)
    ).limit(limit).all()
    for po in pos:
        results.append(SearchResultItem(
            category="purchase_order",
            id=po.id,
            title=po.purchase_order_number,
            subtitle=f"${float(po.total or 0):.2f}",
            badge=po.status,
            url=f"/purchase-orders"
        ))

    # 6. Warehouses
    warehouses = db.query(Warehouse).filter(
        Warehouse.business_id == biz_id,
        or_(
            Warehouse.name.ilike(search_term),
            Warehouse.code.ilike(search_term)
        )
    ).limit(limit).all()
    for w in warehouses:
        results.append(SearchResultItem(
            category="warehouse",
            id=w.id,
            title=w.name,
            subtitle=f"Code: {w.code}",
            badge="Warehouse",
            url=f"/inventory"
        ))

    # 7. Branches
    branches = db.query(Branch).filter(
        Branch.business_id == biz_id,
        or_(
            Branch.name.ilike(search_term),
            Branch.code.ilike(search_term)
        )
    ).limit(limit).all()
    for b in branches:
        results.append(SearchResultItem(
            category="branch",
            id=b.id,
            title=b.name,
            subtitle=f"Code: {b.code}",
            badge="Branch",
            url=f"/branches"
        ))

    return {
        "data": {
            "query": q,
            "total_results": len(results),
            "results": results
        }
    }
