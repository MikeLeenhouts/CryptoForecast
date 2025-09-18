#!/usr/bin/env python3
"""
Test script for forecast_planning function

This script tests the forecast_planning function locally.
Run from the project root directory.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions.planning.forecast_planning import forecast_planning

async def test_forecast_planning():
    """Test the forecast_planning function"""
    print("Testing forecast_planning function...")
    print("=" * 50)
    
    try:
        # Test the function
        result = await forecast_planning()
        
        print("Forecast Planning Test Results:")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            stats = result.get('statistics', {})
            print(f"Active Surveys: {stats.get('active_surveys', 0)}")
            print(f"Total Assets: {stats.get('total_assets', 0)}")
            print(f"Total Schedules: {stats.get('total_schedules', 0)}")
            print(f"Total Query Types: {stats.get('total_query_types', 0)}")
            print(f"Total Prompts: {stats.get('total_prompts', 0)}")
            print(f"Total LLMs: {stats.get('total_llms', 0)}")
            print(f"Schedules Created: {stats.get('schedules_created', 0)}")
            
            print("\nSurvey Summary:")
            for survey in result.get('survey_summary', []):
                print(f"  Survey {survey['survey_id']}: {survey['asset_symbol']} - {survey['schedule_name']} ({survey['query_count']} queries)")
                
            print(f"\nCreated {len(result.get('created_schedules', []))} EventBridge schedules")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_forecast_planning())
