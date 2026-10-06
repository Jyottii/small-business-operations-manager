from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.models.purchase_order import PurchaseOrder
from app.models.order import Order
from app.models.goal import BusinessGoal
from app.models.stock_transfer import StockTransfer
from app.schemas.base import ResponseModel
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    id: str
    title: str
    event_type: str  # po_delivery, payment_due, goal_deadline, stock_transfer
    date: str
    status: Optional[str] = None
    entity_type: str
    entity_id: str
    description: Optional[str] = None
    link: str

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/events", response_model=ResponseModel[List[CalendarEvent]])
def get_calendar_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    biz_id = current_user.business_id
    events: List[CalendarEvent] = []

    # 1. Expected PO Deliveries
    po_query = db.query(PurchaseOrder).filter(
        PurchaseOrder.business_id == biz_id,
        PurchaseOrder.status.in_(["ORDERED", "PENDING", "APPROVED"])
    )
    for po in po_query.all():
        date_val = getattr(po, 'expected_delivery_date', None) or po.created_at
        if date_val:
            events.append(CalendarEvent(
                id=f"po-{po.id}",
                title=f"PO Delivery: {po.po_number}",
                event_type="po_delivery",
                date=date_val.strftime("%Y-%m-%d"),
                status=po.status,
                entity_type="purchase_order",
                entity_id=po.id,
                description=f"Expected delivery from supplier. Total: ${float(po.total_amount or 0):.2f}",
                link="/purchase-orders"
            ))

    # 2. Orders with pending payments / fulfillment
    order_query = db.query(Order).filter(
        Order.business_id == biz_id,
        Order.status.in_(["PENDING", "CONFIRMED", "PROCESSING"])
    ).limit(30)
    for o in order_query.all():
        if o.created_at:
            events.append(CalendarEvent(
                id=f"ord-{o.id}",
                title=f"Fulfillment Due: {o.order_number}",
                event_type="order_fulfillment",
                date=o.created_at.strftime("%Y-%m-%d"),
                status=o.status,
                entity_type="order",
                entity_id=o.id,
                description=f"Order awaiting processing/delivery. Total: ${float(o.total_amount or 0):.2f}",
                link="/orders"
            ))

    # 3. Active Goal Deadlines
    goal_query = db.query(BusinessGoal).filter(
        BusinessGoal.business_id == biz_id,
        BusinessGoal.is_active == True,
        BusinessGoal.end_date != None
    )
    for g in goal_query.all():
        if g.end_date:
            events.append(CalendarEvent(
                id=f"goal-{g.id}",
                title=f"Target Deadline: {g.title}",
                event_type="goal_deadline",
                date=g.end_date.strftime("%Y-%m-%d"),
                status="ACTIVE",
                entity_type="goal",
                entity_id=g.id,
                description=f"Target: {g.target_value} ({g.metric})",
                link="/dashboard"
            ))

    # 4. Stock Transfers In Transit
    transfers = db.query(StockTransfer).filter(
        StockTransfer.business_id == biz_id,
        StockTransfer.status.in_(["PENDING", "IN_TRANSIT"])
    ).all()
    for trf in transfers:
        date_val = trf.shipped_at or trf.created_at
        if date_val:
            events.append(CalendarEvent(
                id=f"trf-{trf.id}",
                title=f"Stock Transfer: {trf.transfer_number}",
                event_type="stock_transfer",
                date=date_val.strftime("%Y-%m-%d"),
                status=trf.status,
                entity_type="stock_transfer",
                entity_id=trf.id,
                description=f"Transfer between warehouses ({trf.status})",
                link="/inventory"
            ))

    events.sort(key=lambda x: x.date)
    return {"data": events}
