"""
API endpoints for fetching LocalStack EventBridge scheduled queries
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import boto3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

r = APIRouter(prefix="/scheduled-queries", tags=["scheduled-queries"])

def get_localstack_scheduler_client(endpoint_url: str = 'http://localstack:4566'):
    """Get LocalStack EventBridge Scheduler client"""
    return boto3.client(
        'scheduler', 
        endpoint_url=endpoint_url, 
        region_name='us-east-1',
        aws_access_key_id='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933',
        aws_secret_access_key='ls-reqe8270-Qidi-ViFe-sIku-1863Vode4933'
    )

@r.get("/", response_model=List[Dict[str, Any]])
async def get_scheduled_queries(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localstack:4566'
) -> List[Dict[str, Any]]:
    """
    Fetch all scheduled queries from LocalStack EventBridge Scheduler
    
    Returns a list of scheduled queries with their payload data formatted for the frontend table
    """
    try:
        scheduler = get_localstack_scheduler_client(endpoint_url)
        
        # List all schedules in the group
        try:
            response = scheduler.list_schedules(GroupName=group_name)
            schedules = response.get('Schedules', [])
        except scheduler.exceptions.ResourceNotFoundException:
            logger.warning(f"Schedule group '{group_name}' not found")
            return []
        
        if not schedules:
            logger.info(f"No schedules found in group '{group_name}'")
            return []
        
        # Get detailed information for each schedule
        detailed_schedules = []
        
        for schedule in schedules:
            try:
                # Get detailed schedule information
                detail_response = scheduler.get_schedule(
                    Name=schedule['Name'],
                    GroupName=group_name
                )
                
                # Parse the input payload
                target_input = detail_response.get('Target', {}).get('Input')
                payload = {}
                if target_input:
                    try:
                        payload = json.loads(target_input)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON payload for schedule {schedule['Name']}")
                        payload = {}
                
                # Format the schedule data for the frontend table
                schedule_data = {
                    "schedule_id": schedule['Name'],
                    "survey_init": detail_response.get('CreationDate', '').isoformat() if detail_response.get('CreationDate') else '',
                    "query_schedule": detail_response.get('ScheduleExpression', ''),
                    "schedule_name": payload.get('schedule_name', ''),
                    "query_type": payload.get('query_type_name', ''),
                    "delay_hours": payload.get('delay_hours', 0),
                    "asset": payload.get('asset_name', ''),
                    "llm": payload.get('llm_name', ''),
                    "target_llm": payload.get('target_llm_name', ''),
                    "prompt_type": payload.get('prompt_type', ''),
                    "state": schedule.get('State', 'UNKNOWN'),
                    "description": detail_response.get('Description', ''),
                    "full_payload": payload  # Include full payload for debugging if needed
                }
                
                detailed_schedules.append(schedule_data)
                
            except Exception as e:
                logger.error(f"Error getting details for schedule {schedule['Name']}: {e}")
                # Add a minimal entry for failed schedules
                detailed_schedules.append({
                    "schedule_id": schedule['Name'],
                    "survey_init": "",
                    "query_schedule": "",
                    "schedule_name": "Error loading",
                    "query_type": "Error",
                    "delay_hours": 0,
                    "asset": "Error",
                    "llm": "Error",
                    "target_llm": "Error",
                    "prompt_type": "Error",
                    "state": schedule.get('State', 'ERROR'),
                    "description": f"Error: {str(e)}",
                    "full_payload": {}
                })
        
        logger.info(f"Retrieved {len(detailed_schedules)} scheduled queries")
        return detailed_schedules
        
    except Exception as e:
        logger.error(f"Error fetching scheduled queries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled queries: {str(e)}")

@r.get("/summary")
async def get_scheduled_queries_summary(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localhost:4566'
) -> Dict[str, Any]:
    """
    Get a summary of scheduled queries
    """
    try:
        scheduler = get_localstack_scheduler_client(endpoint_url)
        
        # List schedule groups
        groups_response = scheduler.list_schedule_groups()
        groups = groups_response.get('ScheduleGroups', [])
        
        # List schedules in the specified group
        try:
            schedules_response = scheduler.list_schedules(GroupName=group_name)
            schedules = schedules_response.get('Schedules', [])
        except scheduler.exceptions.ResourceNotFoundException:
            schedules = []
        
        # Count schedules by state
        state_counts = {}
        for schedule in schedules:
            state = schedule.get('State', 'UNKNOWN')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "total_groups": len(groups),
            "total_schedules": len(schedules),
            "state_counts": state_counts,
            "group_name": group_name
        }
        
    except Exception as e:
        logger.error(f"Error fetching scheduled queries summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")

@r.delete("/")
async def delete_all_scheduled_queries(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localhost:4566'
) -> Dict[str, Any]:
    """
    Delete all scheduled queries in the specified group
    """
    try:
        # Import the deletion function
        from functions.planning.create_one_time_schedule import delete_all_schedules
        
        result = delete_all_schedules(group_name, endpoint_url)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except ImportError as e:
        logger.error(f"Failed to import deletion function: {e}")
        raise HTTPException(status_code=500, detail="Deletion function not available")
    except Exception as e:
        logger.error(f"Error deleting scheduled queries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete scheduled queries: {str(e)}")
