#!/usr/bin/env python3
"""Main FastAPI app for CryptoForecast, adapted for AWS Lambda."""

from fastapi import FastAPI
from mangum import Mangum
from app.api.crud import build_crud_router
from app.api.provisioning import r as provisioning_router
from app.db.models import (
    AssetType, Asset, LLM, Prompt, QueryType, Schedule, QuerySchedule, Survey, CryptoQuery, CryptoForecast
)
from app.schemas.dto import (
    AssetTypeCreate, AssetTypeUpdate, AssetTypeOut,
    AssetCreate, AssetUpdate, AssetOut,
    LLMCreate, LLMUpdate, LLMOut,
    PromptCreate, PromptUpdate, PromptOut,
    QueryTypeCreate, QueryTypeUpdate, QueryTypeOut,
    ScheduleCreate, ScheduleUpdate, ScheduleOut,
    QueryScheduleCreate, QueryScheduleUpdate, QueryScheduleOut,
    SurveyCreate, SurveyUpdate, SurveyOut,
    CryptoQueryCreate, CryptoQueryUpdate, CryptoQueryOut,
    CryptoForecastCreate, CryptoForecastUpdate, CryptoForecastOut
)

# Initialize FastAPI app
app = FastAPI(title="CryptoForecast API", version="1.0.0")

# Define allowed filters for CRUD endpoints
asset_filters = {
    "asset_type_id": lambda model, val: model.asset_type_id == val
}
prompt_filters = {
    "llm_id": lambda model, val: model.llm_id == val,
    "prompt_version": lambda model, val: model.prompt_version == val
}
query_filters = {
    "survey_id": lambda model, val: model.survey_id == val,
    "schedule_id": lambda model, val: model.schedule_id == val,
    "query_type_id": lambda model, val: model.query_type_id == val,
    "status": lambda model, val: model.status == val
}
forecast_filters = {
    "query_id": lambda model, val: model.query_id == val,
    "horizon_type": lambda model, val: model.horizon_type == val
}

# Build CRUD routers
app.include_router(build_crud_router(
    model=AssetType, table_name="asset-types",
    create_schema=AssetTypeCreate, update_schema=AssetTypeUpdate, out_schema=AssetTypeOut
))
app.include_router(build_crud_router(
    model=Asset, table_name="assets",
    create_schema=AssetCreate, update_schema=AssetUpdate, out_schema=AssetOut,
    allowed_filters=asset_filters
))
app.include_router(build_crud_router(
    model=LLM, table_name="llms",
    create_schema=LLMCreate, update_schema=LLMUpdate, out_schema=LLMOut
))
app.include_router(build_crud_router(
    model=Prompt, table_name="prompts",
    create_schema=PromptCreate, update_schema=PromptUpdate, out_schema=PromptOut,
    allowed_filters=prompt_filters
))
app.include_router(build_crud_router(
    model=QueryType, table_name="query-types",
    create_schema=QueryTypeCreate, update_schema=QueryTypeUpdate, out_schema=QueryTypeOut
))
app.include_router(build_crud_router(
    model=Schedule, table_name="schedules",
    create_schema=ScheduleCreate, update_schema=ScheduleUpdate, out_schema=ScheduleOut
))
app.include_router(build_crud_router(
    model=QuerySchedule, table_name="query-schedules",
    create_schema=QueryScheduleCreate, update_schema=QueryScheduleUpdate, out_schema=QueryScheduleOut
))
app.include_router(build_crud_router(
    model=Survey, table_name="surveys",
    create_schema=SurveyCreate, update_schema=SurveyUpdate, out_schema=SurveyOut
))
app.include_router(build_crud_router(
    model=CryptoQuery, table_name="queries",
    create_schema=CryptoQueryCreate, update_schema=CryptoQueryUpdate, out_schema=CryptoQueryOut,
    allowed_filters=query_filters
))
app.include_router(build_crud_router(
    model=CryptoForecast, table_name="crypto-forecasts",
    create_schema=CryptoForecastCreate, update_schema=CryptoForecastUpdate, out_schema=CryptoForecastOut,
    allowed_filters=forecast_filters
))

# Include provisioning router
app.include_router(provisioning_router)

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)