"""CCX Marketplace API"""
import hashlib
import uuid
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from data_models import (PublicCreditListing, TransactionRequest,
                         CreditTransaction)
from database import init_sample_data

# Constants
TAGS_METADATA = [
    {"name": "View Credits", "description": "Access Credit Information"},
    {"name": "Purchase Credits", "description": "Buy Carbon Credits"},
    {"name": "Transaction", "description": "View Transaction History"},
]

DESCRIPTION = (
    "The globally recognized leading registry for the delivery, "
    "trade, and retirement of high-quality, durable carbon credits."
)
BUYER_PERMISSIONS = ["buyer", "admin"]

# FastAPI App Initialization
app = FastAPI(
    title="CCX Marketplace API",
    version="1.0.0",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
)
security = HTTPBearer()

db = init_sample_data()


# Authentication & Authorization
def verify_token(credentials: HTTPAuthorizationCredentials = Security(
    security)) -> dict:
    """Mock token verification for demonstration purposes.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP
            authorization credentials.
    Returns:
        dict: User information including user type and ID.
    Raises:
        HTTPException: If the token is invalid or missing.
    """
    token = credentials.credentials
    if token == "demo_public_token":
        return {"user_type": "public", "user_id": "public_user"}
    elif token == "demo_buyer_token":
        return {"user_type": "buyer", "user_id": "buyer_001"}
    elif token == "demo_admin_token":
        return {"user_type": "admin", "user_id": "admin_001"}
    else:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def create_transaction_hash(transaction_data: dict) -> str:
    """Create immutable hash for transaction integrity.
    Args:
        transaction_data (dict): The transaction data.
    Returns:
        str: The SHA-256 hash of the transaction data.
    """
    hash_input = f"{transaction_data['credit_id']}{transaction_data['buyer_id']}{transaction_data['quantity']}{transaction_data['transaction_date']}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


# API Endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "CCX Marketplace API - Transparent Carbon Trading"}


@app.get("/api/credits/", tags=["View Credits"])
def list_credits() -> list[PublicCreditListing]:
    """List all available carbon credits (public view)"""
    return db.get_credits()


@app.get("/api/credits/available_amount/", tags=["View Credits"])
def total_available_amount() -> Dict[str, int]:
    """Get total available amount of carbon credits"""
    total = db.get_total_available_amount()
    return {"total_available_amount": total}


@app.get("/api/credits/{credit_id}", tags=["View Credits"])
def get_credit_details(credit_id: str, user: dict = Depends(verify_token)):
    """Get detailed information about a specific carbon credit"""
    credit = db.get_credit_by_id(credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")

    if user["user_type"] == "public":
        # Return only public details
        return PublicCreditListing(**credit.dict())
    elif user["user_type"] in ["buyer", "admin"]:
        # Return full details
        return credit
    else:
        raise HTTPException(status_code=403, detail="Access forbidden")


@app.post("/api/purchase", tags=["Purchase Credits"])
def purchase_credits(request: TransactionRequest, user: dict = Depends(verify_token)):
    """Purchase carbon credits (buyer only)"""
    if user["user_type"] not in BUYER_PERMISSIONS:
        raise HTTPException(
            status_code=403, detail="Only buyers or admin can " "make purchases"
        )
    credit = db.get_credit_by_id(request.credit_id)
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    if credit["quantity_available"] < request.quantity:
        raise HTTPException(
            status_code=400, detail="Insufficient quantity " "available"
        )
    # Process the purchase
    transaction = {
        "id": str(uuid.uuid4()),
        "credit_id": request.credit_id,
        "buyer_id": user["user_id"],
        "quantity": request.quantity,
        "price_per_ton": credit["price_per_ton"],
        "transaction_date": datetime.now().isoformat(),
        "status": "completed",
    }
    transaction["transaction_hash"] = create_transaction_hash(transaction)
    credit_transaction = CreditTransaction(**transaction)

    success = db.purchase_credit(credit_transaction)
    if not success:
        raise HTTPException(status_code=500, detail="Transaction failed")
    return {
        "transaction_id": transaction["id"],
        "transaction_hash": transaction["transaction_hash"],
        "total_cost": request.quantity * credit["price_per_ton"],
        "status": "completed",
    }


@app.get("/api/transactions", tags=["Transaction"])
def get_transactions(user: dict = Depends(verify_token)):
    """Get transaction history based on user permissions"""
    if user["user_type"] == "admin":
        transactions = db.get_transactions()
        return transactions
    elif user["user_type"] == "buyer":
        transactions = db.get_transactions(buyer_id=user["user_id"])
        return transactions
    else:
        # Public view - anonymized transactions
        transactions = db.get_transactions()
        credits = db.get_credits()
        credit_lookup = {c["id"]: c for c in credits}

        return [
            {
                "transaction_date": t["transaction_date"],
                "credit_type": credit_lookup.get(t["credit_id"], {}).get(
                    "credit_type", "Unknown"
                ),
                "quantity": t["quantity"],
                "price_per_ton": t["price_per_ton"],
            }
            for t in transactions
        ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5002)
