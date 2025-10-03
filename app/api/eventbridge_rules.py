"""
API endpoints for fetching LocalStack EventBridge rules
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import boto3
import logging

logger = logging.getLogger(__name__)

r = APIRouter(prefix="/eventbridge-rules", tags=["eventbridge-rules"])

def get_localstack_events_client(endpoint_url: str = 'http://localstack:4566'):
    """Get LocalStack EventBridge client"""
    return boto3.client(
        'events', 
        endpoint_url=endpoint_url, 
        region_name='us-east-1',
        aws_access_key_id='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933',
        aws_secret_access_key='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933'
    )

@r.get("/", response_model=List[Dict[str, Any]])
async def get_eventbridge_rules(
    endpoint_url: str = 'http://localstack:4566'
) -> List[Dict[str, Any]]:
    """
    Fetch all EventBridge rules from LocalStack
    
    Returns a list of EventBridge rules with their configuration details
    """
    try:
        events_client = get_localstack_events_client(endpoint_url)
        
        # List all rules
        response = events_client.list_rules()
        rules = response.get('Rules', [])
        
        logger.info(f"Retrieved {len(rules)} EventBridge rules")
        return rules
        
    except Exception as e:
        logger.error(f"Error fetching EventBridge rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch EventBridge rules: {str(e)}")

@r.get("/summary")
async def get_eventbridge_rules_summary(
    endpoint_url: str = 'http://localstack:4566'
) -> Dict[str, Any]:
    """
    Get a summary of EventBridge rules
    """
    try:
        events_client = get_localstack_events_client(endpoint_url)
        
        # List all rules
        response = events_client.list_rules()
        rules = response.get('Rules', [])
        
        # Count rules by state
        state_counts = {}
        for rule in rules:
            state = rule.get('State', 'UNKNOWN')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "total_rules": len(rules),
            "state_counts": state_counts
        }
        
    except Exception as e:
        logger.error(f"Error fetching EventBridge rules summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")
