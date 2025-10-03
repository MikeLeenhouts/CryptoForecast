import boto3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def create_one_time_schedule(
    schedule_name: str,
    execution_time: str,
    payload: Dict[str, Any],
    description: Optional[str] = None,
    endpoint_url: str = 'http://localhost:4566'
) -> Dict[str, Any]:
    """
    Create a one-time EventBridge schedule in LocalStack for crypto forecast queries.
    
    This function performs template substitution on the prompt_text field in the payload,
    replacing placeholders like {target_llm_name}, {asset_name}, {delay_hours} with 
    actual values from the payload attributes.
    
    Args:
        schedule_name: Unique name for the schedule
        execution_time: ISO format datetime string (e.g., '2025-09-27T14:00:00')
        payload: Complete payload dictionary with all required attributes
        description: Optional description for the schedule
        endpoint_url: LocalStack endpoint URL
        
    Returns:
        Dict containing the created schedule details
        
    Raises:
        Exception: If schedule creation fails
    """
    try:
        # Initialize LocalStack EventBridge Scheduler client
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # Create a copy of the payload to avoid modifying the original
        processed_payload = payload.copy()
        
        # Perform template substitution on prompt_text if it exists
        if 'prompt_text' in processed_payload and processed_payload['prompt_text']:
            original_prompt_text = processed_payload['prompt_text']
            
            try:
                # Perform template substitution using payload attributes
                # This replaces placeholders like {target_llm_name}, {asset_name}, etc.
                substituted_prompt_text = original_prompt_text.format(**processed_payload)
                processed_payload['prompt_text'] = substituted_prompt_text
                
                logger.info(f"Template substitution completed for schedule: {schedule_name}")
                logger.debug(f"Original prompt: {original_prompt_text[:100]}...")
                logger.debug(f"Substituted prompt: {substituted_prompt_text[:100]}...")
                
            except KeyError as e:
                # Handle missing template variables gracefully
                logger.warning(f"Template substitution failed for {schedule_name}: Missing key {e}")
                logger.warning(f"Using original prompt text without substitution")
                # Keep the original prompt_text if substitution fails
                
            except Exception as e:
                # Handle other template substitution errors
                logger.warning(f"Template substitution error for {schedule_name}: {str(e)}")
                logger.warning(f"Using original prompt text without substitution")
                # Keep the original prompt_text if substitution fails
        
        # Create the schedule with the processed payload
        response = scheduler.create_schedule(
            Name=schedule_name,
            ScheduleExpression=f"at({execution_time})",
            GroupName="crypto-forecast-schedules",
            Target={
                'Arn': 'arn:aws:lambda:us-east-1:000000000000:function:forecast-worker',
                'RoleArn': 'arn:aws:iam::000000000000:role/lambda-role',
                'Input': json.dumps(processed_payload)
            },
            FlexibleTimeWindow={'Mode': 'OFF'},
            Description=description or f"Crypto forecast schedule for survey {payload.get('survey_id', 'unknown')}"
        )
        
        logger.info(f"Successfully created EventBridge schedule: {schedule_name}")
        
        # Return schedule details
        return {
            "ScheduleArn": f"arn:aws:scheduler:us-east-1:000000000000:schedule/crypto-forecast-schedules/{schedule_name}",
            "Name": schedule_name,
            "State": "ENABLED",
            "CreationDate": datetime.utcnow().isoformat(),
            "ScheduleExpression": f"at({execution_time})",
            "Target": response.get('Target', {}),
            "Description": description
        }
        
    except Exception as e:
        logger.error(f"Failed to create EventBridge schedule {schedule_name}: {str(e)}")
        raise Exception(f"EventBridge schedule creation failed: {str(e)}")

def create_schedule_group_if_not_exists(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localhost:4566'
) -> bool:
    """
    Create the schedule group if it doesn't exist.
    
    Args:
        group_name: Name of the schedule group
        endpoint_url: LocalStack endpoint URL
        
    Returns:
        True if group exists or was created successfully
    """
    try:
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # Try to create the group (will fail if it already exists, which is fine)
        try:
            scheduler.create_schedule_group(Name=group_name)
            logger.info(f"Created schedule group: {group_name}")
        except scheduler.exceptions.ConflictException:
            logger.info(f"Schedule group {group_name} already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create/verify schedule group {group_name}: {str(e)}")
        return False

def delete_all_schedules(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localhost:4566'
) -> Dict[str, Any]:
    """
    Delete all EventBridge schedules in a specific group.
    
    Args:
        group_name: Name of the schedule group
        endpoint_url: LocalStack endpoint URL
        
    Returns:
        Dict containing deletion results with counts and any errors
    """
    try:
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # List all schedules in the group
        try:
            response = scheduler.list_schedules(GroupName=group_name)
            schedules = response.get('Schedules', [])
        except scheduler.exceptions.ResourceNotFoundException:
            logger.warning(f"Schedule group '{group_name}' not found")
            return {
                "status": "success",
                "message": f"Schedule group '{group_name}' not found - nothing to delete",
                "deleted_count": 0,
                "total_schedules": 0,
                "errors": []
            }
        
        if not schedules:
            logger.info(f"No schedules found in group '{group_name}'")
            return {
                "status": "success",
                "message": f"No schedules found in group '{group_name}'",
                "deleted_count": 0,
                "total_schedules": 0,
                "errors": []
            }
        
        logger.info(f"Found {len(schedules)} schedules to delete in group '{group_name}'")
        
        deleted_count = 0
        errors = []
        
        # Delete each schedule
        for schedule in schedules:
            schedule_name = schedule['Name']
            try:
                scheduler.delete_schedule(
                    Name=schedule_name,
                    GroupName=group_name
                )
                logger.info(f"Successfully deleted schedule: {schedule_name}")
                deleted_count += 1
                
            except Exception as e:
                error_msg = f"Failed to delete schedule '{schedule_name}': {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Summary
        success_rate = (deleted_count / len(schedules)) * 100 if schedules else 100
        
        result = {
            "status": "success" if deleted_count == len(schedules) else "partial_success",
            "message": f"Deleted {deleted_count}/{len(schedules)} schedules ({success_rate:.1f}% success rate)",
            "deleted_count": deleted_count,
            "total_schedules": len(schedules),
            "errors": errors
        }
        
        if errors:
            logger.warning(f"Completed with {len(errors)} errors: {result['message']}")
        else:
            logger.info(f"Successfully deleted all schedules: {result['message']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to delete schedules from group '{group_name}': {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "deleted_count": 0,
            "total_schedules": 0,
            "errors": [error_msg]
        }

def delete_schedule_group(
    group_name: str = "crypto-forecast-schedules",
    endpoint_url: str = 'http://localhost:4566',
    force: bool = False
) -> Dict[str, Any]:
    """
    Delete a schedule group (optionally after deleting all schedules in it).
    
    Args:
        group_name: Name of the schedule group to delete
        endpoint_url: LocalStack endpoint URL
        force: If True, delete all schedules in the group first
        
    Returns:
        Dict containing deletion results
    """
    try:
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # If force is True, delete all schedules first
        if force:
            logger.info(f"Force deletion requested - deleting all schedules in group '{group_name}' first")
            delete_result = delete_all_schedules(group_name, endpoint_url)
            
            if delete_result["status"] == "error":
                return {
                    "status": "error",
                    "message": f"Failed to delete schedules before deleting group: {delete_result['message']}",
                    "schedule_deletion": delete_result
                }
        
        # Delete the schedule group
        try:
            scheduler.delete_schedule_group(Name=group_name)
            logger.info(f"Successfully deleted schedule group: {group_name}")
            
            result = {
                "status": "success",
                "message": f"Successfully deleted schedule group '{group_name}'",
                "group_name": group_name
            }
            
            if force:
                result["schedule_deletion"] = delete_result
            
            return result
            
        except scheduler.exceptions.ResourceNotFoundException:
            return {
                "status": "success",
                "message": f"Schedule group '{group_name}' not found - nothing to delete",
                "group_name": group_name
            }
        
    except Exception as e:
        error_msg = f"Failed to delete schedule group '{group_name}': {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "group_name": group_name
        }

# Legacy function for backward compatibility
def create_one_time_schedule_legacy(survey_id, execution_time, query_schedule_id, query_type_id, asset_symbol, asset_name, live_prompt_id, forecast_prompt_id, prompt_id, query_type_name):
    """Legacy function for backward compatibility"""
    payload = {
        'survey_id': survey_id,
        'action': 'run_forecast',
        'query_schedule_id': query_schedule_id,
        'query_type_id': query_type_id,
        'asset_symbol': asset_symbol,
        'asset_name': asset_name,
        'live_prompt_id': live_prompt_id,
        'forecast_prompt_id': forecast_prompt_id,
        'prompt_id': prompt_id,
        'query_type_name': query_type_name
    }
    
    schedule_name = f"crypto-survey-{survey_id}-{query_schedule_id}-one-time"
    description = f"One-time forecast for survey ID {survey_id} with query type {query_type_name}"
    
    return create_one_time_schedule(schedule_name, execution_time, payload, description)

# Example usage
if __name__ == "__main__":
    # Example with comprehensive payload
    sample_payload = {
        'survey_id': 123,
        'asset_id': 1,
        'asset_name': 'Bitcoin',
        'schedule_id': 1,
        'schedule_name': '10-Day_6-Follow-ups',
        'schedule_version': 1,
        'query_schedule_id': 456,
        'delay_hours': 0,
        'paired_followup_delay_hours': 24,
        'query_type_id': 789,
        'query_type_name': 'Initial Baseline',
        'prompt_id': 103,
        'prompt_text': 'Analyze Bitcoin trends',
        'prompt_type': 'live',
        'prompt_version': 1,
        'attribute_1': 'Market Analysis',
        'attribute_2': 'Technical Indicators',
        'attribute_3': 'Risk Assessment',
        'target_llm_id': 1,
        'llm_id': 1,
        'llm_name': 'OpenAI',
        'asset_symbol': 'BTC-USD',
        'live_prompt_id': 101,
        'forecast_prompt_id': 102,
        'scheduled_for_utc': '2025-09-27T14:00:00'
    }
    
    # Create schedule group first
    create_schedule_group_if_not_exists()
    
    # Create the schedule
    result = create_one_time_schedule(
        schedule_name="crypto-forecast-123-456-test",
        execution_time='2025-09-27T14:00:00',
        payload=sample_payload,
        description="Test crypto forecast schedule"
    )
    
    print("Schedule created:", result)
