from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import pandas as pd

# Import our fraud detection modules
from data_generator import get_sample_data
from fraud_detection import FraudDetectionAnalyzer
from sql_queries import SQLQueriesShowcase

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Banking Fraud Detection API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize data - Generate sample data on startup
customers_df, transactions_df = get_sample_data()
fraud_analyzer = FraudDetectionAnalyzer(transactions_df, customers_df)

logging.info(f"Loaded {len(customers_df)} customers and {len(transactions_df)} transactions")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class FraudStats(BaseModel):
    total_transactions: int
    fraud_transactions: int
    legitimate_transactions: int
    fraud_rate: float
    total_amount: float
    fraud_amount: float
    legitimate_amount: float

# ==================== FRAUD DETECTION ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {
        "message": "Banking Fraud Detection API",
        "version": "1.0.0",
        "description": "API for analyzing banking transactions and detecting fraud patterns"
    }

@api_router.get("/fraud/statistics", response_model=Dict[str, Any])
async def get_fraud_statistics():
    """Get overall fraud statistics"""
    try:
        stats = fraud_analyzer.get_fraud_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logging.error(f"Error getting fraud statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/trends", response_model=Dict[str, Any])
async def get_fraud_trends():
    """Get fraud trends over time"""
    try:
        trends = fraud_analyzer.get_fraud_trends_by_day()
        return {"success": True, "data": trends}
    except Exception as e:
        logging.error(f"Error getting fraud trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/high-risk-customers", response_model=Dict[str, Any])
async def get_high_risk_customers(limit: int = 20):
    """Get high-risk customers with fraud history"""
    try:
        customers = fraud_analyzer.get_high_risk_customers(top_n=limit)
        return {"success": True, "data": customers}
    except Exception as e:
        logging.error(f"Error getting high-risk customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/by-location", response_model=Dict[str, Any])
async def get_fraud_by_location():
    """Get fraud analysis by location"""
    try:
        locations = fraud_analyzer.get_fraud_by_location()
        return {"success": True, "data": locations}
    except Exception as e:
        logging.error(f"Error getting fraud by location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/by-merchant", response_model=Dict[str, Any])
async def get_fraud_by_merchant():
    """Get fraud analysis by merchant"""
    try:
        merchants = fraud_analyzer.get_merchant_fraud_analysis()
        return {"success": True, "data": merchants}
    except Exception as e:
        logging.error(f"Error getting fraud by merchant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/by-amount-range", response_model=Dict[str, Any])
async def get_fraud_by_amount_range():
    """Get fraud analysis by transaction amount ranges"""
    try:
        ranges = fraud_analyzer.get_amount_range_analysis()
        return {"success": True, "data": ranges}
    except Exception as e:
        logging.error(f"Error getting fraud by amount range: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/fraud/velocity-analysis", response_model=Dict[str, Any])
async def get_velocity_analysis():
    """Get transaction velocity analysis (rapid successive transactions)"""
    try:
        velocity = fraud_analyzer.get_transaction_velocity_analysis()
        return {"success": True, "data": velocity}
    except Exception as e:
        logging.error(f"Error getting velocity analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/transactions/recent", response_model=Dict[str, Any])
async def get_recent_transactions(limit: int = 100):
    """Get recent transactions with customer details"""
    try:
        transactions = fraud_analyzer.get_recent_transactions(limit=limit)
        return {"success": True, "data": transactions}
    except Exception as e:
        logging.error(f"Error getting recent transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DATA GOVERNANCE ENDPOINTS ====================

@api_router.get("/governance/data-quality", response_model=Dict[str, Any])
async def get_data_quality_metrics():
    """Get data quality metrics for governance"""
    try:
        metrics = fraud_analyzer.get_data_quality_metrics()
        return {"success": True, "data": metrics}
    except Exception as e:
        logging.error(f"Error getting data quality metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/governance/dataset-info", response_model=Dict[str, Any])
async def get_dataset_info():
    """Get information about the datasets"""
    try:
        info = {
            "customers": {
                "total_records": len(customers_df),
                "columns": list(customers_df.columns),
                "sample_record": customers_df.head(1).to_dict('records')[0] if len(customers_df) > 0 else {}
            },
            "transactions": {
                "total_records": len(transactions_df),
                "columns": list(transactions_df.columns),
                "date_range": {
                    "start": str(transactions_df['transaction_date'].min()),
                    "end": str(transactions_df['transaction_date'].max())
                },
                "sample_record": transactions_df.head(1).to_dict('records')[0] if len(transactions_df) > 0 else {}
            }
        }
        return {"success": True, "data": info}
    except Exception as e:
        logging.error(f"Error getting dataset info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SQL QUERIES SHOWCASE ENDPOINTS ====================

@api_router.get("/sql/queries", response_model=Dict[str, Any])
async def get_sql_queries():
    """Get all SQL query examples"""
    try:
        queries = SQLQueriesShowcase.get_all_queries()
        return {"success": True, "data": queries}
    except Exception as e:
        logging.error(f"Error getting SQL queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sql/queries/{query_id}", response_model=Dict[str, Any])
async def get_sql_query_by_id(query_id: str):
    """Get a specific SQL query by ID"""
    try:
        query = SQLQueriesShowcase.get_query_by_id(query_id)
        if query is None:
            raise HTTPException(status_code=404, detail="Query not found")
        return {"success": True, "data": query}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting SQL query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LEGACY ENDPOINTS ====================

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
