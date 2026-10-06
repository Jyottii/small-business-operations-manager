from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    health, business, customer, supplier, product, 
    order, purchase_order, inventory, payment, expense,
    warehouse, audit_log, notification, auth, user, analytics,
    insights, branch, stock_transfer, search, report,
    document, goal, calendar
)

from app.core.config import settings

app = FastAPI(
    title="Small Business Operations Manager API",
    description="API for managing small business operations.",
    version="1.0.0"
)

# CORS configuration - strict origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register base health
app.include_router(health.router)

# Register API v1 routers
api_v1_prefix = "/api/v1"
app.include_router(health.router, prefix=api_v1_prefix)
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(user.router, prefix=api_v1_prefix)
app.include_router(business.router, prefix=api_v1_prefix)
app.include_router(customer.router, prefix=api_v1_prefix)
app.include_router(supplier.router, prefix=api_v1_prefix)
app.include_router(product.router, prefix=api_v1_prefix)
app.include_router(order.router, prefix=api_v1_prefix)
app.include_router(purchase_order.router, prefix=api_v1_prefix)
app.include_router(inventory.router, prefix=api_v1_prefix)
app.include_router(payment.router, prefix=api_v1_prefix)
app.include_router(expense.router, prefix=api_v1_prefix)
app.include_router(warehouse.router, prefix=api_v1_prefix)
app.include_router(audit_log.router, prefix=api_v1_prefix)
app.include_router(notification.router, prefix=api_v1_prefix)
app.include_router(analytics.router, prefix=api_v1_prefix)
app.include_router(insights.router, prefix=api_v1_prefix)
app.include_router(branch.router, prefix=api_v1_prefix)
app.include_router(stock_transfer.router, prefix=api_v1_prefix)
app.include_router(search.router, prefix=api_v1_prefix)
app.include_router(report.router, prefix=api_v1_prefix)
app.include_router(document.router, prefix=api_v1_prefix)
app.include_router(goal.router, prefix=api_v1_prefix)
app.include_router(calendar.router, prefix=api_v1_prefix)
