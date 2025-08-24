from typing import Optional, Literal, Dict
from pydantic import BaseModel, Field

Action = Literal["BUY","SELL","HOLD"]

class ForecastPayload(BaseModel):
    action: Action
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    reason: Optional[str] = None

# Common id-only responses
class IdOut(BaseModel):
    id: int

# ---- Asset Types
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

# ---- Assets
class AssetCreate(BaseModel):
    asset_type_id: int
    asset_name: str
    description: Optional[str] = None

class AssetUpdate(BaseModel):
    asset_type_id: Optional[int] = None
    asset_name: Optional[str] = None
    description: Optional[str] = None

class AssetOut(BaseModel):
    asset_id: int
    asset_type_id: int
    asset_name: str
    description: Optional[str] = None

# ---- LLMs
class LLMCreate(BaseModel):
    llm_name: str
    api_url: str
    api_key_secret: str

class LLMUpdate(BaseModel):
    llm_name: Optional[str] = None
    api_url: Optional[str] = None
    api_key_secret: Optional[str] = None

class LLMOut(BaseModel):
    llm_id: int
    llm_name: str
    api_url: str

# ---- Prompts
class PromptCreate(BaseModel):
    llm_id: int
    prompt_text: str
    prompt_version: int = 1

class PromptUpdate(BaseModel):
    llm_id: Optional[int] = None
    prompt_text: Optional[str] = None
    prompt_version: Optional[int] = None

class PromptOut(BaseModel):
    prompt_id: int
    llm_id: int
    prompt_text: str
    prompt_version: int

# ---- Schedules & Followups
class ScheduleCreate(BaseModel):
    schedule_name: str
    schedule_version: int = 1
    initial_query_time: str  # HH:MM:SS
    description: Optional[str] = None

class ScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = None
    schedule_version: Optional[int] = None
    initial_query_time: Optional[str] = None
    description: Optional[str] = None

class ScheduleOut(BaseModel):
    schedule_id: int
    schedule_name: str
    schedule_version: int
    initial_query_time: str
    description: Optional[str] = None

class ScheduleFollowupCreate(BaseModel):
    schedule_id: int
    followup_type: str
    delay_hours: int

class ScheduleFollowupUpdate(BaseModel):
    schedule_id: Optional[int] = None
    followup_type: Optional[str] = None
    delay_hours: Optional[int] = None

class ScheduleFollowupOut(BaseModel):
    followup_id: int
    schedule_id: int
    followup_type: str
    delay_hours: int

# ---- Surveys
class SurveyCreate(BaseModel):
    asset_id: int
    schedule_id: int
    prompt_id: int
    llm_id: int
    is_active: bool = True

class SurveyUpdate(BaseModel):
    asset_id: Optional[int] = None
    schedule_id: Optional[int] = None
    prompt_id: Optional[int] = None
    llm_id: Optional[int] = None
    is_active: Optional[bool] = None

class SurveyOut(BaseModel):
    survey_id: int
    asset_id: int
    schedule_id: int
    prompt_id: int
    llm_id: int
    is_active: bool

# ---- Crypto Queries & Forecasts
class QueryCreate(BaseModel):
    survey_id: int
    query_type: str
    query_timestamp: str
    initial_query_id: Optional[int] = None

class QueryUpdate(BaseModel):
    survey_id: Optional[int] = None
    query_type: Optional[str] = None
    query_timestamp: Optional[str] = None
    initial_query_id: Optional[int] = None

class QueryOut(BaseModel):
    query_id: int
    survey_id: int
    query_type: str
    query_timestamp: str
    initial_query_id: Optional[int] = None

class ForecastCreate(BaseModel):
    query_id: int
    horizon_type: str
    forecast_value: ForecastPayload

class ForecastUpdate(BaseModel):
    query_id: Optional[int] = None
    horizon_type: Optional[str] = None
    forecast_value: Optional[ForecastPayload] = None

class ForecastOut(BaseModel):
    forecast_id: int
    query_id: int
    horizon_type: str
    forecast_value: ForecastPayload

# ---- Runtime write-path DTOs (PDD)
class QueryCreateInitial(BaseModel):
    query_timestamp: str
    initial_forecasts: Dict[str, ForecastPayload]  # e.g., {'Initial': {...}, 'OneHour': {...}, ...}

class QueryCreateFollowUp(BaseModel):
    query_timestamp: str
    initial_query_id: int
    horizon_type: str
    forecast: ForecastPayload
