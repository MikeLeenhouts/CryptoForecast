"""
API endpoints for fetching LocalStack Lambda functions
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import boto3
import logging

logger = logging.getLogger(__name__)

r = APIRouter(prefix="/lambda-functions", tags=["lambda-functions"])

def get_localstack_lambda_client(endpoint_url: str = 'http://localstack:4566'):
    """Get LocalStack Lambda client"""
    return boto3.client(
        'lambda', 
        endpoint_url=endpoint_url, 
        region_name='us-east-1',
        aws_access_key_id='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933',
        aws_secret_access_key='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933'
    )

@r.get("/", response_model=List[Dict[str, Any]])
async def get_lambda_functions(
    endpoint_url: str = 'http://localstack:4566'
) -> List[Dict[str, Any]]:
    """
    Fetch all Lambda functions from LocalStack
    
    Returns a list of Lambda functions with their configuration details
    """
    try:
        lambda_client = get_localstack_lambda_client(endpoint_url)
        
        # List all functions
        response = lambda_client.list_functions()
        functions = response.get('Functions', [])
        
        logger.info(f"Retrieved {len(functions)} Lambda functions")
        return functions
        
    except Exception as e:
        logger.error(f"Error fetching Lambda functions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Lambda functions: {str(e)}")

@r.get("/summary")
async def get_lambda_functions_summary(
    endpoint_url: str = 'http://localstack:4566'
) -> Dict[str, Any]:
    """
    Get a summary of Lambda functions
    """
    try:
        lambda_client = get_localstack_lambda_client(endpoint_url)
        
        # List all functions
        response = lambda_client.list_functions()
        functions = response.get('Functions', [])
        
        # Count functions by runtime
        runtime_counts = {}
        for function in functions:
            runtime = function.get('Runtime', 'UNKNOWN')
            runtime_counts[runtime] = runtime_counts.get(runtime, 0) + 1
        
        return {
            "total_functions": len(functions),
            "runtime_counts": runtime_counts
        }
        
    except Exception as e:
        logger.error(f"Error fetching Lambda functions summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")
