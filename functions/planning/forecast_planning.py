"""
Forecast Planning Module

This module contains the forecast_planning function that reads active surveys from the database
and builds collections of related data for scheduling crypto forecast queries via EventBridge.

The function is designed to work locally during development and will be migrated to AWS Lambda
with EventBridge Rule for daily execution.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import database models and session
from app.db.models import (
    Survey, Asset, AssetType, Schedule, QuerySchedule, 
    QueryType, Prompt, LLM
)
from app.db.session import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AssetData:
    """Data class for asset information"""
    asset_id: int
    asset_type_id: int
    asset_name: str
    asset_symbol: str
    description: Optional[str] = None
    asset_type_name: Optional[str] = None
    asset_type_description: Optional[str] = None


@dataclass
class LLMData:
    """Data class for LLM configuration"""
    llm_id: int
    llm_name: str
    llm_model: str
    api_url: str
    api_key_secret: str


@dataclass
class PromptData:
    """Data class for prompt configuration"""
    prompt_id: int
    llm_id: int
    prompt_name: Optional[str]
    prompt_text: str
    followup_llm: int
    prompt_type: str
    attribute_1: Optional[str] = None
    attribute_2: Optional[str] = None
    attribute_3: Optional[str] = None
    prompt_version: int = 1


@dataclass
class QueryTypeData:
    """Data class for query type information"""
    query_type_id: int
    query_type_name: str
    description: Optional[str] = None


@dataclass
class QueryScheduleData:
    """Data class for query schedule configuration"""
    query_schedule_id: int
    schedule_id: int
    query_type_id: int
    delay_hours: int
    paired_followup_delay_hours: Optional[int] = None


@dataclass
class ScheduleData:
    """Data class for schedule configuration"""
    schedule_id: int
    schedule_name: str
    schedule_version: int
    initial_query_time: time
    timezone: str
    description: Optional[str] = None
    query_schedules: List[QueryScheduleData] = field(default_factory=list)


@dataclass
class SurveyData:
    """Data class for survey configuration with all related data"""
    survey_id: int
    asset_id: int
    schedule_id: int
    prompt_id: int
    is_active: bool
    
    # Related data objects
    asset: Optional[AssetData] = None
    schedule: Optional[ScheduleData] = None
    prompt: Optional[PromptData] = None


@dataclass
class PlanningDataCollections:
    """Container for all planning data collections"""
    surveys: List[SurveyData] = field(default_factory=list)
    assets: Dict[int, AssetData] = field(default_factory=dict)
    schedules: Dict[int, ScheduleData] = field(default_factory=dict)
    query_schedules: Dict[int, List[QueryScheduleData]] = field(default_factory=lambda: defaultdict(list))
    query_types: Dict[int, QueryTypeData] = field(default_factory=dict)
    prompts: Dict[int, PromptData] = field(default_factory=dict)
    llms: Dict[int, LLMData] = field(default_factory=dict)


@dataclass
class EventBridgeScheduleRequest:
    """Data structure for EventBridge One Time Schedule requests"""
    schedule_name: str
    schedule_expression: str  # e.g., "at(2024-01-15T10:30:00)"
    target_arn: str
    input_payload: Dict[str, Any]
    description: Optional[str] = None
    timezone: str = "UTC"


class EventBridgeScheduler:
    """
    Stub class for EventBridge scheduling functionality.
    
    This class will be implemented to create EventBridge One Time Schedules
    for each required crypto forecast query based on the survey configurations.
    """
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        # In AWS implementation, this would initialize boto3 EventBridge client
        # self.eventbridge_client = boto3.client('events', region_name=region)
        # self.scheduler_client = boto3.client('scheduler', region_name=region)
        
    def create_one_time_schedule(self, request: EventBridgeScheduleRequest) -> Dict[str, Any]:
        """
        Creates a one-time EventBridge schedule for a crypto forecast query.
        
        This is a stub implementation. In AWS, this would:
        1. Create an EventBridge One Time Schedule using the Scheduler service
        2. Configure the target Lambda function (forecast_worker)
        3. Set up the input payload with survey and query details
        4. Handle timezone conversions and scheduling
        
        Args:
            request: EventBridgeScheduleRequest with schedule configuration
            
        Returns:
            Dict containing the created schedule details
            
        Implementation Notes:
        - Uses AWS EventBridge Scheduler for one-time schedules
        - Target Lambda function: forecast_worker
        - Input payload includes survey_id, query_type, asset_info, etc.
        - Handles timezone conversion from survey schedule timezone to UTC
        - Implements retry logic and error handling
        - Logs all scheduling activities for monitoring
        """
        logger.info(f"STUB: Would create EventBridge schedule: {request.schedule_name}")
        logger.info(f"STUB: Schedule expression: {request.schedule_expression}")
        logger.info(f"STUB: Target ARN: {request.target_arn}")
        logger.info(f"STUB: Payload: {request.input_payload}")
        
        # Stub return - in AWS this would return actual schedule details
        return {
            "ScheduleArn": f"arn:aws:scheduler:{self.region}:123456789012:schedule/default/{request.schedule_name}",
            "State": "ENABLED",
            "CreationDate": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_schedule_requests(self, planning_data: PlanningDataCollections, base_date: datetime = None) -> List[EventBridgeScheduleRequest]:
        """
        Generates EventBridge schedule requests for all active surveys.
        
        This method processes the planning data and creates schedule requests
        for each query type in each active survey's schedule.
        
        Args:
            planning_data: Collections of survey and related data
            base_date: Base date for scheduling (defaults to tomorrow)
            
        Returns:
            List of EventBridgeScheduleRequest objects
        """
        if base_date is None:
            base_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        schedule_requests = []
        
        for survey in planning_data.surveys:
            if not survey.is_active:
                continue
                
            schedule = planning_data.schedules.get(survey.schedule_id)
            if not schedule:
                logger.warning(f"Schedule {survey.schedule_id} not found for survey {survey.survey_id}")
                continue
            
            asset = planning_data.assets.get(survey.asset_id)
            prompt = planning_data.prompts.get(survey.prompt_id)
            
            # Process each query schedule for this survey's schedule
            for query_schedule in schedule.query_schedules:
                query_type = planning_data.query_types.get(query_schedule.query_type_id)
                if not query_type:
                    continue
                
                # Calculate scheduled time
                scheduled_datetime = self._calculate_scheduled_time(
                    base_date, schedule.initial_query_time, 
                    query_schedule.delay_hours, schedule.timezone
                )
                
                # Create schedule request
                request = EventBridgeScheduleRequest(
                    schedule_name=f"crypto-forecast-{survey.survey_id}-{query_schedule.query_schedule_id}-{int(scheduled_datetime.timestamp())}",
                    schedule_expression=f"at({scheduled_datetime.strftime('%Y-%m-%dT%H:%M:%S')})",
                    target_arn="arn:aws:lambda:us-east-1:123456789012:function:forecast_worker",
                    input_payload={
                        "survey_id": survey.survey_id,
                        "query_schedule_id": query_schedule.query_schedule_id,
                        "query_type_id": query_schedule.query_type_id,
                        "asset_symbol": asset.asset_symbol if asset else None,
                        "asset_name": asset.asset_name if asset else None,
                        "prompt_id": survey.prompt_id,
                        "scheduled_for_utc": scheduled_datetime.isoformat(),
                        "query_type_name": query_type.query_type_name
                    },
                    description=f"Crypto forecast query for {asset.asset_symbol if asset else 'Unknown'} - {query_type.query_type_name}",
                    timezone=schedule.timezone
                )
                
                schedule_requests.append(request)
                
                # Handle paired followup queries if configured
                if query_schedule.paired_followup_delay_hours is not None:
                    followup_datetime = scheduled_datetime + timedelta(hours=query_schedule.paired_followup_delay_hours)
                    
                    followup_request = EventBridgeScheduleRequest(
                        schedule_name=f"crypto-forecast-followup-{survey.survey_id}-{query_schedule.query_schedule_id}-{int(followup_datetime.timestamp())}",
                        schedule_expression=f"at({followup_datetime.strftime('%Y-%m-%dT%H:%M:%S')})",
                        target_arn="arn:aws:lambda:us-east-1:123456789012:function:forecast_worker",
                        input_payload={
                            "survey_id": survey.survey_id,
                            "query_schedule_id": query_schedule.query_schedule_id,
                            "query_type_id": query_schedule.query_type_id,
                            "asset_symbol": asset.asset_symbol if asset else None,
                            "asset_name": asset.asset_name if asset else None,
                            "prompt_id": survey.prompt_id,
                            "scheduled_for_utc": followup_datetime.isoformat(),
                            "query_type_name": f"{query_type.query_type_name}_FOLLOWUP",
                            "is_followup": True
                        },
                        description=f"Crypto forecast followup query for {asset.asset_symbol if asset else 'Unknown'} - {query_type.query_type_name}",
                        timezone=schedule.timezone
                    )
                    
                    schedule_requests.append(followup_request)
        
        return schedule_requests
    
    def _calculate_scheduled_time(self, base_date: datetime, initial_time: time, 
                                delay_hours: int, timezone: str) -> datetime:
        """Calculate the scheduled datetime for a query"""
        # Combine base date with initial time
        scheduled_dt = datetime.combine(base_date.date(), initial_time)
        
        # Add delay hours
        scheduled_dt += timedelta(hours=delay_hours)
        
        # TODO: In AWS implementation, handle timezone conversion properly
        # For now, assuming UTC
        return scheduled_dt


async def load_survey_data(session: AsyncSession) -> PlanningDataCollections:
    """
    Load all active surveys and their related data from the database.
    
    Args:
        session: Database session
        
    Returns:
        PlanningDataCollections with all loaded data
    """
    collections = PlanningDataCollections()
    
    # Load active surveys - no relationships defined in models, so load separately
    survey_query = select(Survey).where(Survey.is_active == True)
    result = await session.execute(survey_query)
    surveys = result.scalars().all()
    
    # Load all related data
    await _load_assets(session, collections)
    await _load_schedules(session, collections)
    await _load_query_schedules(session, collections)
    await _load_query_types(session, collections)
    await _load_prompts(session, collections)
    await _load_llms(session, collections)
    
    # Process surveys and build survey data objects
    for survey in surveys:
        survey_data = SurveyData(
            survey_id=survey.survey_id,
            asset_id=survey.asset_id,
            schedule_id=survey.schedule_id,
            prompt_id=survey.prompt_id,
            is_active=survey.is_active,
            asset=collections.assets.get(survey.asset_id),
            schedule=collections.schedules.get(survey.schedule_id),
            prompt=collections.prompts.get(survey.prompt_id)
        )
        collections.surveys.append(survey_data)
    
    return collections


async def _load_assets(session: AsyncSession, collections: PlanningDataCollections):
    """Load all assets with their asset types"""
    # Load assets
    asset_query = select(Asset)
    asset_result = await session.execute(asset_query)
    assets = asset_result.scalars().all()
    
    # Load asset types
    asset_type_query = select(AssetType)
    asset_type_result = await session.execute(asset_type_query)
    asset_types = asset_type_result.scalars().all()
    
    # Create asset type lookup
    asset_type_lookup = {at.asset_type_id: at for at in asset_types}
    
    for asset in assets:
        asset_type = asset_type_lookup.get(asset.asset_type_id)
        asset_data = AssetData(
            asset_id=asset.asset_id,
            asset_type_id=asset.asset_type_id,
            asset_name=asset.asset_name,
            asset_symbol=asset.asset_symbol,
            description=asset.description,
            asset_type_name=asset_type.asset_type_name if asset_type else None,
            asset_type_description=asset_type.description if asset_type else None
        )
        collections.assets[asset.asset_id] = asset_data


async def _load_schedules(session: AsyncSession, collections: PlanningDataCollections):
    """Load all schedules"""
    query = select(Schedule)
    result = await session.execute(query)
    schedules = result.scalars().all()
    
    for schedule in schedules:
        schedule_data = ScheduleData(
            schedule_id=schedule.schedule_id,
            schedule_name=schedule.schedule_name,
            schedule_version=schedule.schedule_version,
            initial_query_time=schedule.initial_query_time,
            timezone=schedule.timezone,
            description=schedule.description
        )
        collections.schedules[schedule.schedule_id] = schedule_data


async def _load_query_schedules(session: AsyncSession, collections: PlanningDataCollections):
    """Load all query schedules"""
    query = select(QuerySchedule)
    result = await session.execute(query)
    query_schedules = result.scalars().all()
    
    for qs in query_schedules:
        query_schedule_data = QueryScheduleData(
            query_schedule_id=qs.query_schedule_id,
            schedule_id=qs.schedule_id,
            query_type_id=qs.query_type_id,
            delay_hours=qs.delay_hours,
            paired_followup_delay_hours=qs.paired_followup_delay_hours
        )
        collections.query_schedules[qs.schedule_id].append(query_schedule_data)
        
        # Also add to the schedule object if it exists
        if qs.schedule_id in collections.schedules:
            collections.schedules[qs.schedule_id].query_schedules.append(query_schedule_data)


async def _load_query_types(session: AsyncSession, collections: PlanningDataCollections):
    """Load all query types"""
    query = select(QueryType)
    result = await session.execute(query)
    query_types = result.scalars().all()
    
    for qt in query_types:
        query_type_data = QueryTypeData(
            query_type_id=qt.query_type_id,
            query_type_name=qt.query_type_name,
            description=qt.description
        )
        collections.query_types[qt.query_type_id] = query_type_data


async def _load_prompts(session: AsyncSession, collections: PlanningDataCollections):
    """Load all prompts"""
    query = select(Prompt)
    result = await session.execute(query)
    prompts = result.scalars().all()
    
    for prompt in prompts:
        prompt_data = PromptData(
            prompt_id=prompt.prompt_id,
            llm_id=prompt.llm_id,
            prompt_name=prompt.prompt_name,
            prompt_text=prompt.prompt_text,
            followup_llm=prompt.followup_llm,
            prompt_type=prompt.prompt_type,
            attribute_1=prompt.attribute_1,
            attribute_2=prompt.attribute_2,
            attribute_3=prompt.attribute_3,
            prompt_version=prompt.prompt_version
        )
        collections.prompts[prompt.prompt_id] = prompt_data


async def _load_llms(session: AsyncSession, collections: PlanningDataCollections):
    """Load all LLMs"""
    query = select(LLM)
    result = await session.execute(query)
    llms = result.scalars().all()
    
    for llm in llms:
        llm_data = LLMData(
            llm_id=llm.llm_id,
            llm_name=llm.llm_name,
            llm_model=llm.llm_model,
            api_url=llm.api_url,
            api_key_secret=llm.api_key_secret
        )
        collections.llms[llm.llm_id] = llm_data


async def forecast_planning(base_date: datetime = None) -> Dict[str, Any]:
    """
    Main forecast planning function that reads active surveys and prepares EventBridge schedules.
    
    This function:
    1. Reads all active surveys from the cryptoforecastdatabase
    2. Loads all related data (assets, schedules, query_schedules, query_types, prompts, llms)
    3. Builds collections of data classes for processing
    4. Generates EventBridge One Time Schedule requests for each required query
    5. Returns summary information about the planning process
    
    Args:
        base_date: Base date for scheduling (defaults to tomorrow)
        
    Returns:
        Dict containing planning results and statistics
        
    Usage:
        # Local development
        result = await forecast_planning()
        
        # AWS Lambda (future implementation)
        def lambda_handler(event, context):
            result = asyncio.run(forecast_planning())
            return result
    """
    logger.info("Starting forecast planning process")
    
    try:
        # Create database session
        async with SessionLocal() as session:
            # Load all survey data and related entities
            logger.info("Loading survey data from database")
            planning_data = await load_survey_data(session)
            
            logger.info(f"Loaded {len(planning_data.surveys)} active surveys")
            logger.info(f"Loaded {len(planning_data.assets)} assets")
            logger.info(f"Loaded {len(planning_data.schedules)} schedules")
            logger.info(f"Loaded {len(planning_data.query_types)} query types")
            logger.info(f"Loaded {len(planning_data.prompts)} prompts")
            logger.info(f"Loaded {len(planning_data.llms)} LLMs")
            
            # Initialize EventBridge scheduler
            scheduler = EventBridgeScheduler()
            
            # Generate schedule requests
            logger.info("Generating EventBridge schedule requests")
            schedule_requests = scheduler.generate_schedule_requests(planning_data, base_date)
            
            logger.info(f"Generated {len(schedule_requests)} schedule requests")
            
            # In AWS implementation, this would create the actual schedules
            created_schedules = []
            for request in schedule_requests:
                schedule_result = scheduler.create_one_time_schedule(request)
                created_schedules.append(schedule_result)
            
            # Prepare summary results
            results = {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "statistics": {
                    "active_surveys": len(planning_data.surveys),
                    "total_assets": len(planning_data.assets),
                    "total_schedules": len(planning_data.schedules),
                    "total_query_types": len(planning_data.query_types),
                    "total_prompts": len(planning_data.prompts),
                    "total_llms": len(planning_data.llms),
                    "schedules_created": len(created_schedules)
                },
                "survey_summary": [
                    {
                        "survey_id": survey.survey_id,
                        "asset_symbol": survey.asset.asset_symbol if survey.asset else None,
                        "schedule_name": survey.schedule.schedule_name if survey.schedule else None,
                        "query_count": len(survey.schedule.query_schedules) if survey.schedule else 0
                    }
                    for survey in planning_data.surveys
                ],
                "created_schedules": created_schedules
            }
            
            logger.info("Forecast planning completed successfully")
            return results
            
    except Exception as e:
        logger.error(f"Error in forecast planning: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


# Example usage for local development
async def main():
    """Example usage for local development and testing"""
    result = await forecast_planning()
    print("Forecast Planning Results:")
    print(f"Status: {result['status']}")
    print(f"Active Surveys: {result.get('statistics', {}).get('active_surveys', 0)}")
    print(f"Schedules Created: {result.get('statistics', {}).get('schedules_created', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
