from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    TECHNICAL_ISSUE = "Technical issue"
    BILLING_INQUIRY = "Billing inquiry"
    CANCELLATION_REQUEST = "Cancellation request"
    PRODUCT_INQUIRY = "Product inquiry"
    REFUND_REQUEST = "Refund request"


class PredictRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000, description="Texto do ticket de suporte")

    model_config = {"str_strip_whitespace": True}


class PredictResponse(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
