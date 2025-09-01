# CCX Marketplace API

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003b57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.5.0-e92063?style=flat-square&logo=pydantic&logoColor=white)](https://pydantic.dev/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.24.0-417294?style=flat-square&logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![API Version](https://img.shields.io/badge/API%20Version-1.0.0-brightgreen?style=flat-square)](http://localhost:5002/docs)

The globally recognized leading registry for the delivery, trade, and retirement of high-quality, durable carbon credits.

## Overview

The CCX Marketplace API is a FastAPI-based carbon credit trading platform that enables transparent buying and selling of verified carbon credits. The platform supports multiple credit types including reforestation, renewable energy, methane capture, and more.

## Features

### Core Functionality
- **Carbon Credit Listings**: Browse and search available carbon credits
- **Multi-tier Access Control**: Public, buyer, and admin access levels
- **Secure Transactions**: Cryptographic transaction hashing for integrity
- **Real-time Inventory**: Live tracking of available credit quantities
- **Transaction History**: Complete audit trail of all purchases

### Authentication & Authorization
- **Public Access**: View public credit information and anonymized transactions
- **Buyer Access**: Full credit details and purchase capabilities
- **Admin Access**: Complete system access including all transactions

## Installation

### Prerequisites
- Python 3.11+
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd ccx
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
cd marketplace_api
python database.py
```

## Usage

### Starting the Server
```bash
cd marketplace_api
python main.py
```

The API will be available at `http://localhost:5002`

### API Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:5002/docs`

## API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with welcome message |
| GET | `/api/credits/` | List all available carbon credits (public view) |
| GET | `/api/credits/available_amount/` | Get total available credit quantity |

### Authenticated Endpoints
| Method | Endpoint | Description | Access Level |
|--------|----------|-------------|--------------|
| GET | `/api/credits/{credit_id}` | Get detailed credit information | Public/Buyer/Admin |
| POST | `/api/purchase` | Purchase carbon credits | Buyer/Admin |
| GET | `/api/transactions` | Get transaction history | Public/Buyer/Admin |

## Authentication

The API uses Bearer token authentication. Use these demo tokens for testing:

- **Public Access**: `demo_public_token`
- **Buyer Access**: `demo_buyer_token`  
- **Admin Access**: `demo_admin_token`

## Database Schema

The application uses SQLite with two main tables:

### carbon_credits
- Stores all carbon credit information
- JSON fields for public/private details
- Automatic timestamp tracking

### transactions
- Records all purchase transactions
- Foreign key relationship to credits
- Cryptographic hash for integrity

## Sample Data

The system includes 12 sample carbon credits covering various project types:
- Amazon Rainforest Restoration (Brazil)
- Solar Farm Development (Kenya)
- Wind Farm Expansion (Texas)
- Mangrove Restoration (Indonesia)
- Direct Air Capture Plant (Canada)
- And more...

## Security Features

- **Bearer Token Authentication**: Secure API access control
- **Transaction Hashing**: SHA-256 cryptographic verification
- **Data Segregation**: Public/private information separation
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: Parameterized queries

## Future Work

### Phase 1: Enhanced Security
- [ ] JWT token implementation with expiration
- [ ] OAuth2 integration for enterprise authentication
- [ ] Rate limiting and API quotas
- [ ] Enhanced input sanitization
- [ ] Audit logging for all operations

### Phase 2: Advanced Features
- [ ] Automated credit retirement system
- [ ] Credit portfolio management
- [ ] Advanced search and filtering
- [ ] Bulk purchase operations

### Phase 3: Integration & Scaling
- [ ] Third-party verification system integration
- [ ] RESTful webhook notifications
- [ ] Microservices architecture
- [ ] Redis caching layer

### Phase 4: Business Intelligence
- [ ] Market analytics dashboard
- [ ] Carbon footprint calculators
- [ ] ESG compliance reporting
- [ ] Market trend analysis

### Phase 5: Ecosystem Expansion
- [ ] Partner API for credit verification
- [ ] IoT integration for real-time monitoring
- [ ] AI-powered fraud detection
- [ ] Automated compliance checking
