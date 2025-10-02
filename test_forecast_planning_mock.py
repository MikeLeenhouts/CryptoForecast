#!/usr/bin/env python3
"""
Mock test script for forecast_planning function

This script tests the forecast_planning function with mocked database data,
allowing testing without requiring database connectivity or aiomysql.
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, time, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the database dependencies before importing
sys.modules['aiomysql'] = MagicMock()
sys.modules['app.db.session'] = MagicMock()

# Create mock database models
class MockSurvey:
    def __init__(self, survey_id, asset_id, schedule_id, live_prompt_id, forecast_prompt_id, is_active=True):
        self.survey_id = survey_id
        self.asset_id = asset_id
        self.schedule_id = schedule_id
        self.live_prompt_id = live_prompt_id
        self.forecast_prompt_id = forecast_prompt_id
        self.is_active = is_active

class MockAsset:
    def __init__(self, asset_id, asset_type_id, asset_name, asset_symbol, description=None):
        self.asset_id = asset_id
        self.asset_type_id = asset_type_id
        self.asset_name = asset_name
        self.asset_symbol = asset_symbol
        self.description = description

class MockAssetType:
    def __init__(self, asset_type_id, asset_type_name, description=None):
        self.asset_type_id = asset_type_id
        self.asset_type_name = asset_type_name
        self.description = description

class MockSchedule:
    def __init__(self, schedule_id, schedule_name, schedule_version, initial_query_time, timezone_str="UTC", description=None):
        self.schedule_id = schedule_id
        self.schedule_name = schedule_name
        self.schedule_version = schedule_version
        self.initial_query_time = initial_query_time
        self.timezone = timezone_str
        self.description = description

class MockQuerySchedule:
    def __init__(self, query_schedule_id, schedule_id, query_type_id, delay_hours, paired_followup_delay_hours=None):
        self.query_schedule_id = query_schedule_id
        self.schedule_id = schedule_id
        self.query_type_id = query_type_id
        self.delay_hours = delay_hours
        self.paired_followup_delay_hours = paired_followup_delay_hours

class MockQueryType:
    def __init__(self, query_type_id, query_type_name, description=None):
        self.query_type_id = query_type_id
        self.query_type_name = query_type_name
        self.description = description

class MockPrompt:
    def __init__(self, prompt_id, llm_id, prompt_name, prompt_text, target_llm_id, prompt_type, **kwargs):
        self.prompt_id = prompt_id
        self.llm_id = llm_id
        self.prompt_name = prompt_name
        self.prompt_text = prompt_text
        self.target_llm_id = target_llm_id
        self.prompt_type = prompt_type
        self.attribute_1 = kwargs.get('attribute_1')
        self.attribute_2 = kwargs.get('attribute_2')
        self.attribute_3 = kwargs.get('attribute_3')
        self.prompt_version = kwargs.get('prompt_version', 1)

class MockLLM:
    def __init__(self, llm_id, llm_name, llm_model, api_url, api_key_secret):
        self.llm_id = llm_id
        self.llm_name = llm_name
        self.llm_model = llm_model
        self.api_url = api_url
        self.api_key_secret = api_key_secret

# Create mock data
def create_mock_data():
    """Create mock database data for testing"""
    
    # Mock surveys
    surveys = [
        MockSurvey(1, 1, 1, 1, 5, True),  # Bitcoin with live prompt 1, forecast prompt 5
        MockSurvey(2, 2, 1, 2, 6, True),  # Ethereum with live prompt 2, forecast prompt 6
        MockSurvey(3, 1, 2, 1, 5, False),  # Inactive survey
    ]
    
    # Mock assets
    assets = [
        MockAsset(1, 1, "Bitcoin", "BTC", "Bitcoin cryptocurrency"),
        MockAsset(2, 1, "Ethereum", "ETH", "Ethereum cryptocurrency"),
    ]
    
    # Mock asset types
    asset_types = [
        MockAssetType(1, "Cryptocurrency", "Digital currencies"),
    ]
    
    # Mock schedules
    schedules = [
        MockSchedule(1, "Daily Crypto Schedule", 1, time(9, 0, 0), "UTC", "Daily crypto analysis"),
        MockSchedule(2, "Weekly Crypto Schedule", 1, time(10, 0, 0), "UTC", "Weekly crypto analysis"),
    ]
    
    # Mock query schedules
    query_schedules = [
        MockQuerySchedule(1, 1, 1, 0, 24),  # Initial query with 24h followup
        MockQuerySchedule(2, 1, 2, 1, None),  # 1 hour delay, no followup
        MockQuerySchedule(3, 2, 1, 0, 168),  # Weekly schedule with 1 week followup
    ]
    
    # Mock query types
    query_types = [
        MockQueryType(1, "BASELINE_FORECAST", "Initial forecast query"),
        MockQueryType(2, "PRICE_ANALYSIS", "Price analysis query"),
    ]
    
    # Mock prompts
    prompts = [
        MockPrompt(1, 1, "Bitcoin Live Analysis", "Analyze Bitcoin price trends live", 1, "live"),
        MockPrompt(2, 2, "Ethereum Live Analysis", "Analyze Ethereum price trends live", 2, "live"),
        MockPrompt(5, 1, "Bitcoin Forecast Analysis", "Forecast Bitcoin price trends", 1, "forecast"),
        MockPrompt(6, 2, "Ethereum Forecast Analysis", "Forecast Ethereum price trends", 2, "forecast"),
    ]
    
    # Mock LLMs
    llms = [
        MockLLM(1, "GPT-4", "gpt-4", "https://api.openai.com", "secret-key-1"),
        MockLLM(2, "Claude", "claude-3", "https://api.anthropic.com", "secret-key-2"),
    ]
    
    return {
        'surveys': surveys,
        'assets': assets,
        'asset_types': asset_types,
        'schedules': schedules,
        'query_schedules': query_schedules,
        'query_types': query_types,
        'prompts': prompts,
        'llms': llms
    }

async def mock_session_execute(query):
    """Mock session execute method"""
    mock_data = create_mock_data()
    
    # Create a mock result object
    mock_result = MagicMock()
    
    # Determine which data to return based on the query
    query_str = str(query)
    if 'surveys' in query_str.lower():
        # Return only active surveys
        active_surveys = [s for s in mock_data['surveys'] if s.is_active]
        mock_result.scalars.return_value.all.return_value = active_surveys
    elif 'assets' in query_str.lower() and 'asset_types' not in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['assets']
    elif 'asset_types' in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['asset_types']
    elif 'schedules' in query_str.lower() and 'query_schedules' not in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['schedules']
    elif 'query_schedules' in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['query_schedules']
    elif 'query_type' in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['query_types']
    elif 'prompts' in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['prompts']
    elif 'llms' in query_str.lower():
        mock_result.scalars.return_value.all.return_value = mock_data['llms']
    else:
        mock_result.scalars.return_value.all.return_value = []
    
    return mock_result

async def test_forecast_planning_with_mocks():
    """Test the forecast_planning function with mocked data"""
    print("Testing forecast_planning function with mock data...")
    print("=" * 60)
    
    # Mock the SessionLocal context manager
    mock_session = AsyncMock()
    mock_session.execute = mock_session_execute
    
    # Create a proper async context manager mock
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_context.__aexit__ = AsyncMock(return_value=None)
    
    # Create a mock SessionLocal that returns our context manager
    mock_session_local = MagicMock(return_value=mock_session_context)
    
    try:
        # Patch the SessionLocal import and test the function
        with patch('functions.planning.forecast_planning.SessionLocal', mock_session_local):
            # Import the function after patching
            from functions.planning.forecast_planning import forecast_planning
            
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
                
                created_schedules = result.get('created_schedules', [])
                print(f"\nCreated {len(created_schedules)} EventBridge schedules")
                
                if created_schedules:
                    print("\nSample EventBridge Schedule:")
                    sample = created_schedules[0]
                    print(f"  Schedule ARN: {sample.get('ScheduleArn', 'N/A')}")
                    print(f"  State: {sample.get('State', 'N/A')}")
                    print(f"  Creation Date: {sample.get('CreationDate', 'N/A')}")
                
                print("\n✅ Test PASSED: Function executed successfully with mock data")
                return True
            else:
                print(f"❌ Test FAILED: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ Test FAILED with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_forecast_planning_with_mocks())
    if success:
        print("\n🎉 All tests passed! The forecast_planning function is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the implementation.")
