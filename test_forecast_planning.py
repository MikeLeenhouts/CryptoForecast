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
            schedules_created = stats.get('schedules_created', 0)
            print(f"Schedules Created: {schedules_created}")
            
            print("\nSurvey Summary:")
            ten_day_surveys = []
            fourteen_day_surveys = []
            
            for survey in result.get('survey_summary', []):
                print(f"  Survey {survey['survey_id']}: {survey['asset_symbol']} - {survey['schedule_name']} ({survey['query_count']} queries)")
                if "10-Day" in survey['schedule_name']:
                    ten_day_surveys.append(survey)
                elif "14-Day" in survey['schedule_name']:
                    fourteen_day_surveys.append(survey)
            
            print(f"\nCreated {len(result.get('created_schedules', []))} EventBridge schedules")
            
            # Calculate expected schedules with paired followups
            print("\n" + "=" * 60)
            print("SCHEDULE CALCULATION BREAKDOWN:")
            print("=" * 60)
            
            print(f"\n10-Day_6-Follow-ups Schedule ({len(ten_day_surveys)} surveys):")
            print("  - Query 1 (Initial Baseline): 1 schedule")
            print("  - Queries 2-7 (Baseline Forecast): 6 schedules (executed at time 0)")
            print("  - Queries 9-14 (Follow-up): 6 schedules (executed at delay_hours)")
            print("  - Per Survey Total: 1 + 6 + 6 = 13 schedules")
            ten_day_total = len(ten_day_surveys) * 13
            print(f"  - {len(ten_day_surveys)} surveys × 13 = {ten_day_total} schedules")
            
            print(f"\n14-Day_7-Follow-ups Schedule ({len(fourteen_day_surveys)} surveys):")
            print("  - Query 16 (Initial Baseline): 1 schedule")
            print("  - Queries 17-23 (Baseline Forecast): 7 schedules (executed at time 0)")
            print("  - Queries 24-30 (Follow-up): 7 schedules (executed at delay_hours)")
            print("  - Per Survey Total: 1 + 7 + 7 = 15 schedules")
            fourteen_day_total = len(fourteen_day_surveys) * 15
            print(f"  - {len(fourteen_day_surveys)} surveys × 15 = {fourteen_day_total} schedules")
            
            expected_total = ten_day_total + fourteen_day_total
            print(f"\nEXPECTED TOTAL: {ten_day_total} + {fourteen_day_total} = {expected_total} schedules")
            print(f"ACTUAL TOTAL: {schedules_created} schedules")
            
            if schedules_created == expected_total:
                print("✅ CALCULATION VERIFIED: Schedule count is correct!")
            else:
                print(f"❌ MISMATCH: Expected {expected_total}, got {schedules_created}")
            
            print("\nNOTE: Paired followups create additional schedules when 'paired_followup_delay_hours' is set.")
            print("This is intentional for comprehensive crypto forecasting with timed followup analysis.")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_forecast_planning())
