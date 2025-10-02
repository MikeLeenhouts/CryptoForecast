from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_serializer
import datetime

# ---------------------------------------------------------------------
# Shared types
# ---------------------------------------------------------------------

Action = Literal["BUY", "SELL", "HOLD"]
QueryStatus = Literal["PLANNED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]
PromptType = Literal["live", "forecast"]

class ForecastPayload(BaseModel):
    action: Action
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    reason: Optional[str] = None


# ---------------------------------------------------------------------
# Asset Types
# ---------------------------------------------------------------------

class AssetTypeCreate(BaseModel):
    asset_type_name: str
    description: Optional[str] = None

class AssetTypeUpdate(BaseModel):
    asset_type_name: Optional[str] = None
    description: Optional[str] = None

class AssetTypeOut(BaseModel):
    asset_type_id: int
    asset_type_name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------

class AssetCreate(BaseModel):
    asset_type_id: int
    asset_name: str
    asset_symbol: str
    description: Optional[str] = None

class AssetUpdate(BaseModel):
    asset_type_id: Optional[int] = None
    asset_name: Optional[str] = None
    asset_symbol: Optional[str] = None
    description: Optional[str] = None

class AssetOut(BaseModel):
    asset_id: int
    asset_type_id: int
    asset_name: str
    asset_symbol: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# LLMs
# ---------------------------------------------------------------------

class LLMCreate(BaseModel):
    llm_name: str
    llm_model: str
    api_url: str
    api_key_secret: str

class LLMUpdate(BaseModel):
    llm_name: Optional[str] = None
    llm_model: Optional[str] = None
    api_url: Optional[str] = None
    api_key_secret: Optional[str] = None

class LLMOut(BaseModel):
    llm_id: int
    llm_name: str
    llm_model: str
    api_url: str
    # Note: api_key_secret is intentionally excluded for security
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------

class PromptCreate(BaseModel):
    llm_id: int
    prompt_name: Optional[str] = None
    prompt_text: str
    target_llm_id: int
    prompt_type: PromptType
    attribute_1: Optional[str] = None
    attribute_2: Optional[str] = None
    attribute_3: Optional[str] = None
    prompt_version: int = 1

class PromptUpdate(BaseModel):
    llm_id: Optional[int] = None
    prompt_name: Optional[str] = None
    prompt_text: Optional[str] = None
    target_llm_id: Optional[int] = None
    prompt_type: Optional[PromptType] = None
    attribute_1: Optional[str] = None
    attribute_2: Optional[str] = None
    attribute_3: Optional[str] = None
    prompt_version: Optional[int] = None

class PromptOut(BaseModel):
    prompt_id: int
    llm_id: int
    prompt_name: Optional[str] = None
    prompt_text: str
    target_llm_id: int
    prompt_type: PromptType
    attribute_1: Optional[str] = None
    attribute_2: Optional[str] = None
    attribute_3: Optional[str] = None
    prompt_version: int
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Query Types
# ---------------------------------------------------------------------

class QueryTypeCreate(BaseModel):
    query_type_name: str
    description: Optional[str] = None

class QueryTypeUpdate(BaseModel):
    query_type_name: Optional[str] = None
    description: Optional[str] = None

class QueryTypeOut(BaseModel):
    query_type_id: int
    query_type_name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Schedules & Query Schedules
# ---------------------------------------------------------------------

class ScheduleCreate(BaseModel):
    schedule_name: str
    schedule_version: int = 1
    initial_query_time: str  # "HH:MM:SS"
    timezone: str = "UTC"
    description: Optional[str] = None

class ScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = None
    schedule_version: Optional[int] = None
    initial_query_time: Optional[str] = None
    timezone: Optional[str] = None
    description: Optional[str] = None

class ScheduleOut(BaseModel):
    schedule_id: int
    schedule_name: str
    schedule_version: int
    initial_query_time: datetime.time
    timezone: str
    description: Optional[str] = None

    @field_serializer("initial_query_time")
    def serialize_time(self, value: datetime.time) -> str:
        return value.strftime("%H:%M:%S")

    model_config = {"from_attributes": True}

# ✅ Single, final definition (includes paired_followup_delay_hours)
class QueryScheduleCreate(BaseModel):
    schedule_id: int
    query_type_id: int
    delay_hours: int
    paired_followup_delay_hours: Optional[int] = None  # NEW

class QueryScheduleUpdate(BaseModel):
    schedule_id: Optional[int] = None
    query_type_id: Optional[int] = None
    delay_hours: Optional[int] = None
    paired_followup_delay_hours: Optional[int] = None  # NEW

class QueryScheduleOut(BaseModel):
    query_schedule_id: int
    schedule_id: int
    query_type_id: int
    delay_hours: int
    paired_followup_delay_hours: Optional[int] = None  # NEW
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Surveys
# ---------------------------------------------------------------------

class SurveyCreate(BaseModel):
    asset_id: int
    schedule_id: int
    live_prompt_id: int
    forecast_prompt_id: int
    is_active: bool = True

class SurveyUpdate(BaseModel):
    asset_id: Optional[int] = None
    schedule_id: Optional[int] = None
    live_prompt_id: Optional[int] = None
    forecast_prompt_id: Optional[int] = None
    is_active: Optional[bool] = None

class SurveyOut(BaseModel):
    survey_id: int
    asset_id: int
    schedule_id: int
    live_prompt_id: int
    forecast_prompt_id: int
    is_active: bool
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Runtime write-path DTOs (PDD)
# ---------------------------------------------------------------------

class QueryCreateInitial(BaseModel):
    # when the Worker executed (UTC ISO string); Planner can also pass scheduled time
    query_timestamp: str
    # e.g., {"Initial": {...}, "OneHour": {...}, ...}
    initial_forecasts: Dict[str, ForecastPayload]

class QueryCreateFollowUp(BaseModel):
    query_timestamp: str
    horizon_type: str
    forecast: ForecastPayload


# ---------------------------------------------------------------------
# Crypto Queries (admin CRUD)
# ---------------------------------------------------------------------

class CryptoQueryCreate(BaseModel):
    survey_id: int
    schedule_id: int
    query_schedule_id: int
    query_type_id: int
    paired_query_id: Optional[int] = None  # For Baseline Forecast to link to its Follow-up

    scheduled_for_utc: datetime.datetime
    status: Optional[QueryStatus] = "PLANNED"
    executed_at_utc: Optional[datetime.datetime] = None
    result_json: Optional[Dict[str, Any]] = None
    
    # Four additional fields for query recommendations
    recommendation: Optional[Action] = None
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    source: Optional[str] = None

class CryptoQueryUpdate(BaseModel):
    survey_id: Optional[int] = None
    schedule_id: Optional[int] = None
    query_schedule_id: Optional[int] = None
    query_type_id: Optional[int] = None
    paired_query_id: Optional[int] = None  # For Baseline Forecast to link to its Follow-up

    scheduled_for_utc: Optional[datetime.datetime] = None
    status: Optional[QueryStatus] = None
    executed_at_utc: Optional[datetime.datetime] = None
    result_json: Optional[Dict[str, Any]] = None
    
    # Four additional fields for query recommendations
    recommendation: Optional[Action] = None
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    source: Optional[str] = None

class CryptoQueryOut(BaseModel):
    query_id: int
    survey_id: int
    schedule_id: int
    query_schedule_id: int
    query_type_id: int
    paired_query_id: Optional[int] = None  # For Baseline Forecast to link to its Follow-up

    scheduled_for_utc: datetime.datetime
    status: QueryStatus
    executed_at_utc: Optional[datetime.datetime] = None
    result_json: Optional[Dict[str, Any]] = None
    
    # Four additional fields for query recommendations
    recommendation: Optional[Action] = None
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    source: Optional[str] = None
    
    model_config = {"from_attributes": True}




# ---------------------------------------------------------------------
# Crypto Forecasts (admin CRUD)
# ---------------------------------------------------------------------

class CryptoForecastCreate(BaseModel):
    query_id: int
    horizon_type: str
    forecast_value: Optional[Dict[str, Any]] = None

class CryptoForecastUpdate(BaseModel):
    query_id: Optional[int] = None
    horizon_type: Optional[str] = None
    forecast_value: Optional[Dict[str, Any]] = None

class CryptoForecastOut(BaseModel):
    forecast_id: int
    query_id: int
    horizon_type: str
    forecast_value: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}
