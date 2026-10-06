import os

schemas_dir = 'app/schemas'
os.makedirs(schemas_dir, exist_ok=True)

schemas = {
    'business.py': '''from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .base import BaseORMModel

class BusinessBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    currency: str = "USD"
    timezone: str = "UTC"

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None

class BusinessResponse(BusinessBase, BaseORMModel):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
''',
    
    'product.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class ProductBase(BaseModel):
    category_id: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Decimal = Field(default=0.0, ge=0)
    selling_price: Decimal = Field(default=0.0, ge=0)
    tax_rate: Decimal = Field(default=0.0, ge=0)
    reorder_level: Decimal = Field(default=0.0, ge=0)
    reorder_quantity: Decimal = Field(default=0.0, ge=0)
    expiry_tracking_enabled: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    category_id: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    expiry_tracking_enabled: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase, BaseORMModel):
    id: str
    business_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
''',
    
    'order.py': '''from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: Decimal = Field(..., gt=0)
    discount: Decimal = Field(default=0.0, ge=0)

class OrderCreate(BaseModel):
    customer_id: Optional[str] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel, BaseORMModel):
    id: str
    product_id: str
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal

class OrderResponse(BaseModel, BaseORMModel):
    id: str
    business_id: str
    customer_id: Optional[str] = None
    employee_id: Optional[str] = None
    order_number: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    payment_status: str
    order_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []
''',

    'purchase_order.py': '''from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class PurchaseOrderItemCreate(BaseModel):
    product_id: str
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)

class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    warehouse_id: str
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderReceive(BaseModel):
    items: dict[str, Decimal] # product_id -> quantity to receive (must be > 0 and <= outstanding)
    notes: Optional[str] = None

class PurchaseOrderItemResponse(BaseModel, BaseORMModel):
    id: str
    product_id: str
    quantity_ordered: Decimal
    quantity_received: Decimal
    unit_cost: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal

class PurchaseOrderResponse(BaseModel, BaseORMModel):
    id: str
    business_id: str
    supplier_id: str
    warehouse_id: str
    purchase_order_number: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    expected_date: Optional[datetime] = None
    order_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    purchase_items: List[PurchaseOrderItemResponse] = []
''',

    'inventory.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class InventoryAdjust(BaseModel):
    product_id: str
    warehouse_id: str
    quantity_change: Decimal # Negative for deduction, Positive for addition
    movement_type: str
    notes: Optional[str] = None

class InventoryResponse(BaseModel, BaseORMModel):
    id: str
    product_id: str
    warehouse_id: str
    quantity: Decimal
    reserved_quantity: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    last_stock_update: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
''',

    'stock_movement.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class StockMovementResponse(BaseModel, BaseORMModel):
    id: str
    business_id: str
    product_id: str
    warehouse_id: str
    movement_type: str
    quantity: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    previous_quantity: Optional[Decimal] = None
    resulting_quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
''',
    
    'customer.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    customer_type: Optional[str] = None
    credit_limit: Decimal = Decimal('0.0')
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    customer_type: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase, BaseORMModel):
    id: str
    business_id: str
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
''',

    'supplier.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseORMModel

class SupplierBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    tax_identifier: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class SupplierResponse(SupplierBase, BaseORMModel):
    id: str
    business_id: str
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
''',
    
    'payment.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class PaymentCreate(BaseModel):
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    payment_method: str
    amount: Decimal = Field(..., gt=0)
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(BaseModel, BaseORMModel):
    id: str
    business_id: str
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    payment_method: Optional[str] = None
    amount: Decimal
    transaction_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
''',
    
    'expense.py': '''from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseORMModel

class ExpenseCreate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExpenseResponse(BaseModel, BaseORMModel):
    id: str
    business_id: str
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal
    payment_method: Optional[str] = None
    expense_date: Optional[datetime] = None
    employee_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
'''
}

for filename, content in schemas.items():
    with open(os.path.join(schemas_dir, filename), 'w') as f:
        f.write(content)
