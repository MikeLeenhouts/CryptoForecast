#!/usr/bin/env python3
"""
Utility script to list and summarize LocalStack EventBridge schedules
"""

import boto3
import json
from datetime import datetime
from typing import List, Dict, Any

def list_localstack_schedules(endpoint_url: str = 'http://localhost:4566', group_name: str = 'crypto-forecast-schedules') -> Dict[str, Any]:
    """
    List all EventBridge schedules in LocalStack
    
    Args:
        endpoint_url: LocalStack endpoint URL
        group_name: Schedule group name to filter by (optional)
        
    Returns:
        Dictionary containing schedule summary and details
    """
    try:
        # Initialize LocalStack EventBridge Scheduler client
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # List all schedule groups
        print("📋 Listing Schedule Groups...")
        groups_response = scheduler.list_schedule_groups()
        groups = groups_response.get('ScheduleGroups', [])
        
        print(f"Found {len(groups)} schedule groups:")
        for group in groups:
            print(f"  - {group['Name']}: {group.get('Description', 'No description')}")
        
        # List schedules in the specified group
        print(f"\n📅 Listing Schedules in Group: {group_name}")
        try:
            schedules_response = scheduler.list_schedules(GroupName=group_name)
            schedules = schedules_response.get('Schedules', [])
        except scheduler.exceptions.ResourceNotFoundException:
            print(f"❌ Schedule group '{group_name}' not found")
            return {
                "status": "error",
                "error": f"Schedule group '{group_name}' not found",
                "groups": groups,
                "schedules": []
            }
        
        print(f"Found {len(schedules)} schedules in group '{group_name}':")
        
        # Get detailed information for each schedule
        detailed_schedules = []
        survey_summary = {}
        
        for schedule in schedules:
            try:
                # Get detailed schedule information
                detail_response = scheduler.get_schedule(
                    Name=schedule['Name'],
                    GroupName=group_name
                )
                
                schedule_detail = {
                    "name": schedule['Name'],
                    "arn": schedule.get('Arn', 'N/A'),
                    "state": schedule.get('State', 'UNKNOWN'),
                    "schedule_expression": detail_response.get('ScheduleExpression', 'N/A'),
                    "description": detail_response.get('Description', 'No description'),
                    "creation_date": detail_response.get('CreationDate', 'N/A'),
                    "last_modification_date": detail_response.get('LastModificationDate', 'N/A'),
                    "target": detail_response.get('Target', {}),
                }
                
                # Parse the input payload if available
                target_input = schedule_detail['target'].get('Input')
                if target_input:
                    try:
                        payload = json.loads(target_input)
                        schedule_detail['payload'] = payload
                        
                        # Extract survey information for summary
                        survey_id = payload.get('survey_id')
                        asset_name = payload.get('asset_name', 'Unknown')
                        query_type = payload.get('query_type_name', 'Unknown')
                        
                        if survey_id:
                            if survey_id not in survey_summary:
                                survey_summary[survey_id] = {
                                    'asset_name': asset_name,
                                    'schedules': []
                                }
                            survey_summary[survey_id]['schedules'].append({
                                'name': schedule['Name'],
                                'query_type': query_type,
                                'scheduled_for': payload.get('scheduled_for_utc', 'N/A')
                            })
                    except json.JSONDecodeError:
                        schedule_detail['payload'] = "Invalid JSON"
                
                detailed_schedules.append(schedule_detail)
                
                # Print summary line
                print(f"  ✅ {schedule['Name']} - {schedule.get('State', 'UNKNOWN')}")
                
            except Exception as e:
                print(f"  ❌ Error getting details for {schedule['Name']}: {e}")
        
        # Print survey summary
        print(f"\n📊 Survey Summary:")
        for survey_id, info in survey_summary.items():
            print(f"  Survey {survey_id} ({info['asset_name']}): {len(info['schedules'])} schedules")
            for sched in info['schedules'][:3]:  # Show first 3 schedules
                print(f"    - {sched['query_type']} at {sched['scheduled_for']}")
            if len(info['schedules']) > 3:
                print(f"    ... and {len(info['schedules']) - 3} more")
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_groups": len(groups),
                "total_schedules": len(schedules),
                "active_schedules": len([s for s in schedules if s.get('State') == 'ENABLED']),
                "surveys_count": len(survey_summary)
            },
            "groups": groups,
            "schedules": detailed_schedules,
            "survey_summary": survey_summary
        }
        
    except Exception as e:
        print(f"❌ Error listing LocalStack schedules: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def delete_all_schedules(endpoint_url: str = 'http://localhost:4566', group_name: str = 'crypto-forecast-schedules') -> Dict[str, Any]:
    """
    Delete all schedules in a specific group (useful for cleanup)
    
    Args:
        endpoint_url: LocalStack endpoint URL
        group_name: Schedule group name
        
    Returns:
        Dictionary containing deletion results
    """
    try:
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        # List schedules in the group
        schedules_response = scheduler.list_schedules(GroupName=group_name)
        schedules = schedules_response.get('Schedules', [])
        
        print(f"🗑️  Deleting {len(schedules)} schedules from group '{group_name}'...")
        
        deleted_count = 0
        errors = []
        
        for schedule in schedules:
            try:
                scheduler.delete_schedule(
                    Name=schedule['Name'],
                    GroupName=group_name
                )
                print(f"  ✅ Deleted: {schedule['Name']}")
                deleted_count += 1
            except Exception as e:
                error_msg = f"Failed to delete {schedule['Name']}: {e}"
                print(f"  ❌ {error_msg}")
                errors.append(error_msg)
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "total_schedules": len(schedules),
            "errors": errors
        }
        
    except Exception as e:
        print(f"❌ Error deleting schedules: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_schedule_details(schedule_name: str, endpoint_url: str = 'http://localhost:4566', group_name: str = 'crypto-forecast-schedules') -> Dict[str, Any]:
    """
    Get detailed information about a specific schedule
    
    Args:
        schedule_name: Name of the schedule
        endpoint_url: LocalStack endpoint URL
        group_name: Schedule group name
        
    Returns:
        Dictionary containing schedule details
    """
    try:
        scheduler = boto3.client('scheduler', endpoint_url=endpoint_url)
        
        response = scheduler.get_schedule(
            Name=schedule_name,
            GroupName=group_name
        )
        
        # Parse the payload if available
        target_input = response.get('Target', {}).get('Input')
        payload = None
        if target_input:
            try:
                payload = json.loads(target_input)
            except json.JSONDecodeError:
                payload = "Invalid JSON"
        
        return {
            "status": "success",
            "schedule": {
                "name": response.get('Name'),
                "arn": response.get('Arn'),
                "state": response.get('State'),
                "schedule_expression": response.get('ScheduleExpression'),
                "description": response.get('Description'),
                "creation_date": response.get('CreationDate'),
                "last_modification_date": response.get('LastModificationDate'),
                "target": response.get('Target'),
                "payload": payload
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            # List all schedules
            result = list_localstack_schedules()
            print(f"\n📋 Final Summary:")
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                summary = result['summary']
                print(f"Total Groups: {summary['total_groups']}")
                print(f"Total Schedules: {summary['total_schedules']}")
                print(f"Active Schedules: {summary['active_schedules']}")
                print(f"Surveys: {summary['surveys_count']}")
        
        elif command == "delete":
            # Delete all schedules
            result = delete_all_schedules()
            print(f"\n🗑️  Deletion Summary:")
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Deleted: {result['deleted_count']}/{result['total_schedules']} schedules")
                if result['errors']:
                    print(f"Errors: {len(result['errors'])}")
        
        elif command == "detail" and len(sys.argv) > 2:
            # Get details for specific schedule
            schedule_name = sys.argv[2]
            result = get_schedule_details(schedule_name)
            print(f"\n📅 Schedule Details for '{schedule_name}':")
            if result['status'] == 'success':
                schedule = result['schedule']
                print(f"State: {schedule['state']}")
                print(f"Expression: {schedule['schedule_expression']}")
                print(f"Description: {schedule['description']}")
                if schedule['payload']:
                    print(f"Payload: {json.dumps(schedule['payload'], indent=2)}")
            else:
                print(f"Error: {result['error']}")
        
        else:
            print("Usage:")
            print("  python list_localstack_schedules.py list")
            print("  python list_localstack_schedules.py delete")
            print("  python list_localstack_schedules.py detail <schedule_name>")
    
    else:
        # Default: list schedules
        result = list_localstack_schedules()
        print(f"\n📋 Summary: {result['summary']['total_schedules']} schedules found")
