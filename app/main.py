from fastapi import FastAPI
from app.db.models import Base, AssetType, Asset, LLM, Prompt, Schedule, ScheduleFollowup, Survey, CryptoQuery, CryptoForecast
from app.db.session import engine
from app.routers.provisioning import r as provisioning_router
from app.routers.reporting import r as reporting_router
from app.routers.crud import build_crud_router
from app.schemas import dto as D

app = FastAPI(title="Crypto Forecasts API")

@app.get("/healthz")
async def healthz(): return {"ok": True}

# ---- Generic CRUD routers (add simple filters per table)
asset_types = build_crud_router(
    model=AssetType, pk="asset_type_id",
    create_schema=D.AssetTypeCreate, update_schema=D.AssetTypeUpdate, out_schema=D.AssetTypeOut,
    table_name="asset-types",
)
assets = build_crud_router(
    model=Asset, pk="asset_id",
    create_schema=D.AssetCreate, update_schema=D.AssetUpdate, out_schema=D.AssetOut,
    table_name="assets",
    allowed_filters={"asset_type_id": lambda m, v: m.asset_type_id==v}
)
llms = build_crud_router(
    model=LLM, pk="llm_id",
    create_schema=D.LLMCreate, update_schema=D.LLMUpdate, out_schema=D.LLMOut,
    table_name="llms",
)
prompts = build_crud_router(
    model=Prompt, pk="prompt_id",
    create_schema=D.PromptCreate, update_schema=D.PromptUpdate, out_schema=D.PromptOut,
    table_name="prompts",
    allowed_filters={"llm_id": lambda m, v: m.llm_id==v, "prompt_version": lambda m, v: m.prompt_version==v}
)
schedules = build_crud_router(
    model=Schedule, pk="schedule_id",
    create_schema=D.ScheduleCreate, update_schema=D.ScheduleUpdate, out_schema=D.ScheduleOut,
    table_name="schedules",
)
schedule_followups = build_crud_router(
    model=ScheduleFollowup, pk="followup_id",
    create_schema=D.ScheduleFollowupCreate, update_schema=D.ScheduleFollowupUpdate, out_schema=D.ScheduleFollowupOut,
    table_name="schedule-followups",
    allowed_filters={"schedule_id": lambda m, v: m.schedule_id==v}
)
surveys = build_crud_router(
    model=Survey, pk="survey_id",
    create_schema=D.SurveyCreate, update_schema=D.SurveyUpdate, out_schema=D.SurveyOut,
    table_name="surveys",
)

crypto_queries = build_crud_router(
    model=CryptoQuery, pk="query_id",
    create_schema=D.QueryCreate, update_schema=D.QueryUpdate, out_schema=D.QueryOut,
    table_name="crypto-queries",
    allowed_filters={"survey_id": lambda m, v: m.survey_id==v, "query_type": lambda m, v: m.query_type==v}
)
crypto_forecasts = build_crud_router(
    model=CryptoForecast, pk="forecast_id",
    create_schema=D.ForecastCreate, update_schema=D.ForecastUpdate, out_schema=D.ForecastOut,
    table_name="crypto-forecasts",
    allowed_filters={"query_id": lambda m, v: m.query_id==v, "horizon_type": lambda m, v: m.horizon_type==v}
)

# Register routers
for r in [asset_types, assets, llms, prompts, schedules, schedule_followups, surveys, crypto_queries, crypto_forecasts]:
    app.include_router(r)

app.include_router(provisioning_router)
app.include_router(reporting_router)
