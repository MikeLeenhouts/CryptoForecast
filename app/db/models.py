from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Time, DateTime, Float
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import JSON
import datetime

class Base(DeclarativeBase):
    pass

class AssetType(Base):
    __tablename__ = "asset_types"
    asset_type_id: Mapped[int] = mapped_column(primary_key=True)
    asset_type_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

class Asset(Base):
    __tablename__ = "assets"
    asset_id: Mapped[int] = mapped_column(primary_key=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.asset_type_id", ondelete="RESTRICT"), index=True)
    asset_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    asset_symbol: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)

class LLM(Base):
    __tablename__ = "llms"
    llm_id: Mapped[int] = mapped_column(primary_key=True)
    llm_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    llm_model: Mapped[str] = mapped_column(String(255))
    api_url: Mapped[str] = mapped_column(String(255))
    api_key_secret: Mapped[str] = mapped_column(String(255))

class Prompt(Base):
    __tablename__ = "prompts"
    prompt_id: Mapped[int] = mapped_column(primary_key=True)
    llm_id: Mapped[int] = mapped_column(ForeignKey("llms.llm_id", ondelete="RESTRICT"), index=True)
    prompt_name: Mapped[str | None] = mapped_column(String(255), default=None)
    prompt_text: Mapped[str] = mapped_column(Text)
    followup_llm: Mapped[int] = mapped_column(ForeignKey("llms.llm_id", ondelete="RESTRICT"), index=True)
    prompt_type: Mapped[str] = mapped_column(SAEnum("live", "forecast", name="prompt_type_enum"), index=True)
    attribute_1: Mapped[str | None] = mapped_column(Text, default=None)
    attribute_2: Mapped[str | None] = mapped_column(Text, default=None)
    attribute_3: Mapped[str | None] = mapped_column(Text, default=None)
    prompt_version: Mapped[int] = mapped_column(default=1)

class Schedule(Base):
    __tablename__ = "schedules"
    schedule_id: Mapped[int] = mapped_column(primary_key=True)
    schedule_name: Mapped[str] = mapped_column(String(255))
    schedule_version: Mapped[int] = mapped_column(default=1)
    initial_query_time: Mapped[datetime.time] = mapped_column(Time)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")  # NEW
    description: Mapped[str | None] = mapped_column(Text)

class QueryType(Base):
    __tablename__ = "query_type"
    query_type_id: Mapped[int] = mapped_column(primary_key=True)
    query_type_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

class QuerySchedule(Base):
    __tablename__ = "query_schedules"
    query_schedule_id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.schedule_id", ondelete="CASCADE"), index=True)
    query_type_id: Mapped[int] = mapped_column(ForeignKey("query_type.query_type_id", ondelete="CASCADE"), index=True)
    delay_hours: Mapped[int]
    paired_followup_delay_hours: Mapped[int | None] = mapped_column(default=None)  # NEW
class Survey(Base):
    __tablename__ = "surveys"
    survey_id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.asset_id", ondelete="RESTRICT"), index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.schedule_id", ondelete="RESTRICT"), index=True)
    live_prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.prompt_id", ondelete="RESTRICT"), index=True)
    forecast_prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.prompt_id", ondelete="RESTRICT"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)



class CryptoQuery(Base):
    __tablename__ = "queries"
    query_id: Mapped[int] = mapped_column(primary_key=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.survey_id", ondelete="RESTRICT"), index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.schedule_id", ondelete="RESTRICT"), index=True)
    query_schedule_id: Mapped[int] = mapped_column(ForeignKey("query_schedules.query_schedule_id", ondelete="RESTRICT"), index=True)
    query_type_id: Mapped[int] = mapped_column(ForeignKey("query_type.query_type_id", ondelete="RESTRICT"), index=True)
    paired_query_id: Mapped[int | None] = mapped_column(Integer, default=None)  # For Baseline Forecast to link to its Follow-up

    scheduled_for_utc: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False))
    status: Mapped[str] = mapped_column(
        SAEnum("PLANNED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", name="cq_status"),
        default="PLANNED"
    )
    executed_at_utc: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=False), default=None)
    result_json: Mapped[dict | None] = mapped_column(JSON, default=None)
    
    # Four additional fields for query recommendations (matching init.sql schema)
    recommendation: Mapped[str | None] = mapped_column(
        SAEnum("BUY", "SELL", "HOLD", name="recommendation_enum"), 
        default=None
    )
    confidence: Mapped[float | None] = mapped_column(Float, default=None)
    rationale: Mapped[str | None] = mapped_column(Text, default=None)
    source: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=False), default=None)




class CryptoForecast(Base):
    __tablename__ = "crypto_forecasts"
    forecast_id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.query_id", ondelete="CASCADE"), index=True)
    horizon_type: Mapped[str] = mapped_column(String(50))
    forecast_value: Mapped[dict | None] = mapped_column(JSON)
