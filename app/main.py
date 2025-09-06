# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.db.models import (
    Base, AssetType, Asset, LLM, Prompt, Schedule, QueryType, QuerySchedule,
    Survey, CryptoQuery, CryptoForecast
)
from app.db.session import engine
from app.api.provisioning import r as provisioning_router
from app.api.reporting import r as reporting_router
from app.api.crud import build_crud_router
from app.schemas import dto as D

app = FastAPI(title="Crypto Forecasts API")
# Force reload to pick up llm_model field changes

# CORS (relax for dev; tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def maybe_create_tables():
    # Optional: create tables at boot when not using Alembic (DEV only)
    if os.getenv("AUTO_CREATE_TABLES", "0") == "1":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

# ---------- Generic CRUD routers ----------
asset_types = build_crud_router(
    model=AssetType,
    create_schema=D.AssetTypeCreate, update_schema=D.AssetTypeUpdate, out_schema=D.AssetTypeOut,
    table_name="asset-types",
)

assets = build_crud_router(
    model=Asset,
    create_schema=D.AssetCreate, update_schema=D.AssetUpdate, out_schema=D.AssetOut,
    table_name="assets",
    allowed_filters={"asset_type_id": lambda m, v: m.asset_type_id == v},
)

llms = build_crud_router(
    model=LLM,
    create_schema=D.LLMCreate, update_schema=D.LLMUpdate, out_schema=D.LLMOut,
    table_name="llms",
)

prompts = build_crud_router(
    model=Prompt,
    create_schema=D.PromptCreate, update_schema=D.PromptUpdate, out_schema=D.PromptOut,
    table_name="prompts",
    allowed_filters={
        "llm_id": lambda m, v: m.llm_id == v,
        "prompt_version": lambda m, v: m.prompt_version == v,
    },
)

schedules = build_crud_router(
    model=Schedule,
    create_schema=D.ScheduleCreate, update_schema=D.ScheduleUpdate, out_schema=D.ScheduleOut,
    table_name="schedules",
)

# NEW: query_type
query_types = build_crud_router(
    model=QueryType,
    create_schema=D.QueryTypeCreate, update_schema=D.QueryTypeUpdate, out_schema=D.QueryTypeOut,
    table_name="query-types",
)

# REPLACE schedule_followups -> query_schedules
query_schedules = build_crud_router(
    model=QuerySchedule,
    create_schema=D.QueryScheduleCreate, update_schema=D.QueryScheduleUpdate, out_schema=D.QueryScheduleOut,
    table_name="query-schedules",
    allowed_filters={"schedule_id": lambda m, v: m.schedule_id == v},
)

surveys = build_crud_router(
    model=Survey,
    create_schema=D.SurveyCreate, update_schema=D.SurveyUpdate, out_schema=D.SurveyOut,
    table_name="surveys",
    allowed_filters={
        "asset_id": lambda m, v: m.asset_id == v,
        "schedule_id": lambda m, v: m.schedule_id == v,
        "prompt_id": lambda m, v: m.prompt_id == v,
        "is_active": lambda m, v: m.is_active == (str(v).lower() in ("1", "true", "t", "yes", "y")),
    },
)



queries = build_crud_router(
    model=CryptoQuery,
    create_schema=D.CryptoQueryCreate,
    update_schema=D.CryptoQueryUpdate,
    out_schema=D.CryptoQueryOut,
    table_name="queries",
    allowed_filters={
        "survey_id": lambda m, v: m.survey_id == v,
        "schedule_id": lambda m, v: m.schedule_id == v,
        "query_type_id": lambda m, v: m.query_type_id == v,
        "status": lambda m, v: m.status == v,
    },
)

crypto_forecasts = build_crud_router(
    model=CryptoForecast,
    create_schema=D.CryptoForecastCreate,
    update_schema=D.CryptoForecastUpdate,
    out_schema=D.CryptoForecastOut,
    table_name="crypto-forecasts",
    allowed_filters={
        "query_id": lambda m, v: m.query_id == v,
        "horizon_type": lambda m, v: m.horizon_type == v,
    },
)


# Register routers
for r in [
    asset_types, assets, llms, prompts, schedules, query_types, query_schedules,
    surveys, queries, crypto_forecasts
]:
    app.include_router(r)

# Domain-specific routers
app.include_router(provisioning_router)
app.include_router(reporting_router)
