"""Data models for Carbon Credit Trading Platform"""

from typing import Dict, Optional, Any

from pydantic import BaseModel


class CarbonCredit(BaseModel):
    """A model representing a carbon credit listing."""
    id: str
    project_name: str
    supplier: str
    credit_type: str
    vintage: int
    quantity_available: int
    price_per_ton: float
    location: str
    verification_status: str
    methodology: str
    public_details: Dict[str, Any]
    private_details: Optional[Dict[str, Any]] = None


class PublicCreditListing(BaseModel):
    """A model representing the public view of a carbon credit listing."""
    id: str
    project_name: str
    supplier: str
    credit_type: str
    vintage: int
    quantity_available: int
    price_per_ton: float
    location: str
    verification_status: str
    methodology: str


class TransactionRequest(BaseModel):
    """A model representing a request to purchase carbon credits."""
    credit_id: str
    quantity: int


class TransactionRequest(BaseModel):
    """A model representing a request to purchase carbon credits."""
    credit_id: str
    quantity: int


class CreditTransaction(BaseModel):
    """A model representing a carbon credit transaction."""
    id: str
    credit_id: str
    buyer_id: str
    quantity: int
    price_per_ton: float
    transaction_date: str
    status: str
    transaction_hash: str
