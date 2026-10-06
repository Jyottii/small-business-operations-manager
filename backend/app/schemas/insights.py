from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class InsightSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class InsightCategory(str, Enum):
    INVENTORY = "inventory"
    SALES = "sales"
    FINANCE = "finance"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    OPERATIONS = "operations"
    DATA_QUALITY = "data_quality"

class InsightItem(BaseModel):
    id: str = Field(..., description="Unique deterministic identifier for the insight")
    category: InsightCategory = Field(..., description="Business domain category")
    severity: InsightSeverity = Field(..., description="Urgency level: info, warning, critical")
    title: str = Field(..., description="Concise human-readable title")
    message: str = Field(..., description="Clear explanation of the detected business condition")
    metric: str = Field(..., description="Primary metric or KPI name associated with this insight")
    current_value: Optional[Union[float, int, str]] = Field(None, description="Current value of the monitored metric")
    threshold: Optional[Union[float, int, str]] = Field(None, description="Configured rule threshold")
    recommendation: str = Field(..., description="Specific, actionable next step for the business")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting operational data points")

    model_config = ConfigDict(from_attributes=True)

class InsightsSummary(BaseModel):
    total: int = 0
    critical: int = 0
    warning: int = 0
    info: int = 0

class InsightsPeriodInfo(BaseModel):
    period: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: int

class InsightsData(BaseModel):
    generated_at: datetime
    period: InsightsPeriodInfo
    summary: InsightsSummary
    insights: List[InsightItem]

    model_config = ConfigDict(from_attributes=True)
