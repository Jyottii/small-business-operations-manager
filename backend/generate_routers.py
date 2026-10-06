import os

routers_dir = 'app/routers'
os.makedirs(routers_dir, exist_ok=True)

# Helper function to generate common CRUD routers
def generate_router(name, model_name, schema_name, update_schema_name, extra_imports="", extra_routes="", has_business_id=True):
    var_name = name.lower()
    plural_name = var_name + "s"
    if var_name == "inventory": plural_name = "inventory" # Plural of inventory is inventory here
    
    code = f'''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_business_id
from app.models.{var_name} import {model_name}
from app.schemas.{var_name} import {schema_name}Response, {schema_name}Create, {update_schema_name}
from app.schemas.base import PaginatedResponseModel, ResponseModel, PaginationInfo
from app.core.exceptions import NotFoundException
{extra_imports}

router = APIRouter(prefix="/{plural_name.replace('_', '-')}", tags=["{model_name}s"])

@router.get("", response_model=PaginatedResponseModel[{schema_name}Response])
def get_{plural_name}(
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = db.query({model_name}).filter({model_name}.business_id == business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {{
        "data": items,
        "pagination": {{"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}}
    }}

@router.get("/{{item_id}}", response_model=ResponseModel[{schema_name}Response])
def get_{var_name}(
    item_id: str,
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    item = db.query({model_name}).filter({model_name}.id == item_id, {model_name}.business_id == business_id).first()
    if not item:
        raise NotFoundException()
    return {{"data": item}}

@router.post("", response_model=ResponseModel[{schema_name}Response])
def create_{var_name}(
    data: {schema_name}Create,
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    item_data = data.model_dump()
    item_data["business_id"] = business_id
    item = {model_name}(**item_data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {{"data": item}}

@router.patch("/{{item_id}}", response_model=ResponseModel[{schema_name}Response])
def update_{var_name}(
    item_id: str,
    data: {update_schema_name},
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    item = db.query({model_name}).filter({model_name}.id == item_id, {model_name}.business_id == business_id).first()
    if not item:
        raise NotFoundException()
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    db.commit()
    db.refresh(item)
    return {{"data": item}}
    
{extra_routes}
'''
    with open(os.path.join(routers_dir, f'{var_name}.py'), 'w') as f:
        f.write(code)

# 1. Product Router
extra_product_routes = '''
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryResponse

@router.get("/{item_id}/inventory", response_model=PaginatedResponseModel[InventoryResponse])
def get_product_inventory(
    item_id: str,
    db: Session = Depends(get_db),
    business_id: str = Depends(get_current_business_id)
):
    items = db.query(Inventory).join(Product).filter(Product.id == item_id, Product.business_id == business_id).all()
    return {"data": items, "pagination": {"page": 1, "page_size": len(items), "total": len(items), "total_pages": 1}}
'''
generate_router("Product", "Product", "Product", "ProductUpdate", extra_routes=extra_product_routes)
generate_router("Customer", "Customer", "Customer", "CustomerUpdate")
generate_router("Supplier", "Supplier", "Supplier", "SupplierUpdate")
generate_router("Business", "Business", "Business", "BusinessUpdate")

# Custom for Orders (uses Service)
with open(os.path.join(routers_dir, 'order.py'), 'w') as f:
    f.write('''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_business_id
from app.models.order import Order
from app.schemas.order import OrderResponse, OrderCreate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.order_service import OrderService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=PaginatedResponseModel[OrderResponse])
def get_orders(db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id), page: int = Query(1), page_size: int = Query(20)):
    query = db.query(Order).filter(Order.business_id == business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}}

@router.get("/{item_id}", response_model=ResponseModel[OrderResponse])
def get_order(item_id: str, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    item = db.query(Order).filter(Order.id == item_id, Order.business_id == business_id).first()
    if not item:
        raise NotFoundException()
    return {"data": item}

@router.post("", response_model=ResponseModel[OrderResponse])
def create_order(data: OrderCreate, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    try:
        order = OrderService.create_order(db, business_id, data)
        db.commit()
        db.refresh(order)
        return {"data": order}
    except Exception as e:
        db.rollback()
        raise e
''')

# Custom for PO (uses Service)
with open(os.path.join(routers_dir, 'purchase_order.py'), 'w') as f:
    f.write('''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_business_id
from app.models.purchase_order import PurchaseOrder
from app.schemas.purchase_order import PurchaseOrderResponse, PurchaseOrderCreate, PurchaseOrderReceive
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.purchase_order_service import PurchaseOrderService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get("", response_model=PaginatedResponseModel[PurchaseOrderResponse])
def get_pos(db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id), page: int = Query(1), page_size: int = Query(20)):
    query = db.query(PurchaseOrder).filter(PurchaseOrder.business_id == business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}}

@router.get("/{item_id}", response_model=ResponseModel[PurchaseOrderResponse])
def get_po(item_id: str, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    item = db.query(PurchaseOrder).filter(PurchaseOrder.id == item_id, PurchaseOrder.business_id == business_id).first()
    if not item:
        raise NotFoundException()
    return {"data": item}

@router.post("", response_model=ResponseModel[PurchaseOrderResponse])
def create_po(data: PurchaseOrderCreate, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    try:
        po = PurchaseOrderService.create_po(db, business_id, data)
        db.commit()
        db.refresh(po)
        return {"data": po}
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{item_id}/receive", response_model=ResponseModel[PurchaseOrderResponse])
def receive_po(item_id: str, data: PurchaseOrderReceive, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    try:
        po = PurchaseOrderService.receive_po(db, business_id, item_id, data)
        db.commit()
        db.refresh(po)
        return {"data": po}
    except Exception as e:
        db.rollback()
        raise e
''')

# Custom for Inventory (uses Service)
with open(os.path.join(routers_dir, 'inventory.py'), 'w') as f:
    f.write('''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_business_id
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryResponse, InventoryAdjust
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=PaginatedResponseModel[InventoryResponse])
def get_inventory(db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id), page: int = Query(1), page_size: int = Query(20)):
    query = db.query(Inventory).join(Product).filter(Product.business_id == business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}}

@router.post("/adjust", response_model=ResponseModel[InventoryResponse])
def adjust_inventory(data: InventoryAdjust, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    try:
        inv = InventoryService.adjust_stock(db, business_id, data.product_id, data.warehouse_id, data.quantity_change, data.movement_type, notes=data.notes)
        db.commit()
        db.refresh(inv)
        return {"data": inv}
    except Exception as e:
        db.rollback()
        raise e
''')

# Custom for Payment (uses Service)
with open(os.path.join(routers_dir, 'payment.py'), 'w') as f:
    f.write('''from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_business_id
from app.models.payment import Payment
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.schemas.base import PaginatedResponseModel, ResponseModel
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=PaginatedResponseModel[PaymentResponse])
def get_payments(db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id), page: int = Query(1), page_size: int = Query(20)):
    query = db.query(Payment).filter(Payment.business_id == business_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"data": items, "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}}

@router.post("", response_model=ResponseModel[PaymentResponse])
def create_payment(data: PaymentCreate, db: Session = Depends(get_db), business_id: str = Depends(get_current_business_id)):
    try:
        payment = PaymentService.create_payment(db, business_id, data)
        db.commit()
        db.refresh(payment)
        return {"data": payment}
    except Exception as e:
        db.rollback()
        raise e
''')

# Expense Router
generate_router("Expense", "Expense", "Expense", "ExpenseUpdate")

# Health
with open(os.path.join(routers_dir, 'health.py'), 'w') as f:
    f.write('''from fastapi import APIRouter
from app.schemas.base import ResponseModel

router = APIRouter(tags=["System"])

@router.get("/health")
def health_check():
    return {"status": "ok"}
''')

