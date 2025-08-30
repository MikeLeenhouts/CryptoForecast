import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.utils.deps import db
from app.db import models as m
from app.schemas.dto import (
    SurveyCreate, SurveyUpdate, SurveyOut,
    QueryCreateInitial, QueryCreateFollowUp
)

r = APIRouter(tags=["provisioning"])

@r.post("/surveys", response_model=SurveyOut, status_code=201)
async def create_survey(payload: SurveyCreate, s: AsyncSession = Depends(db)):
    # Unique on (asset_id, schedule_id, prompt_id)
    dup = await s.scalar(
        select(func.count()).select_from(m.Survey).where(
            m.Survey.asset_id == payload.asset_id,
            m.Survey.schedule_id == payload.schedule_id,
            m.Survey.prompt_id == payload.prompt_id,
        )
    )
    if dup:
        raise HTTPException(409, "duplicate survey")
    obj = m.Survey(**payload.model_dump())
    s.add(obj); await s.commit(); await s.refresh(obj)
    return obj

@r.get("/surveys/{survey_id}", response_model=SurveyOut)
async def get_survey(survey_id: int, s: AsyncSession = Depends(db)):
    obj = await s.get(m.Survey, survey_id)
    if not obj: raise HTTPException(404, "not found")
    return obj

@r.get("/surveys", response_model=list[SurveyOut])
async def list_surveys(asset_id: int | None = None, is_active: bool | None = None, s: AsyncSession = Depends(db)):
    stmt = select(m.Survey)
    if asset_id is not None:
        stmt = stmt.where(m.Survey.asset_id == asset_id)
    if is_active is not None:
        stmt = stmt.where(m.Survey.is_active == is_active)
    rows = (await s.execute(stmt)).scalars().all()
    return rows

@r.patch("/surveys/{survey_id}", response_model=SurveyOut)
async def update_survey(survey_id: int, payload: SurveyUpdate, s: AsyncSession = Depends(db)):
    obj = await s.get(m.Survey, survey_id)
    if not obj: raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    try:
        await s.commit()
    except Exception as e:
        await s.rollback(); raise HTTPException(409, str(e))
    await s.refresh(obj)
    return obj

@r.patch("/surveys/{survey_id}/activate", response_model=SurveyOut)
async def activate_survey(survey_id: int, s: AsyncSession = Depends(db)):
    obj = await s.get(m.Survey, survey_id)
    if not obj: raise HTTPException(404, "not found")
    obj.is_active = True; await s.commit(); await s.refresh(obj); return obj

@r.patch("/surveys/{survey_id}/deactivate", response_model=SurveyOut)
async def deactivate_survey(survey_id: int, s: AsyncSession = Depends(db)):
    obj = await s.get(m.Survey, survey_id)
    if not obj: raise HTTPException(404, "not found")
    obj.is_active = False; await s.commit(); await s.refresh(obj); return obj

# ---- Runtime write-paths (per PDD)
def _get_ids_for_runtime(s: AsyncSession, survey_id: int):
    async def inner():
        survey = await s.get(m.Survey, survey_id)
        if not survey:
            raise HTTPException(404, "survey not found")
        schedule_id = survey.schedule_id
        return survey, schedule_id
    return inner

@r.post("/surveys/{survey_id}/queries/initial", status_code=201)
async def create_initial_query(survey_id: int, body: QueryCreateInitial, s: AsyncSession = Depends(db)):
    survey, schedule_id = await _get_ids_for_runtime(s, survey_id)()
    # map to 'Initial Baseline' query_type (planning uses query_type table)
    qt_id = await s.scalar(select(m.QueryType.query_type_id).where(m.QueryType.query_type_name == "Initial Baseline"))
    if not qt_id:
        raise HTTPException(400, "query_type 'Initial Baseline' not found")

    q = m.CryptoQuery(
        survey_id=survey_id,
        schedule_id=schedule_id,
        query_type_id=qt_id,
        initial_query_id=None,
        scheduled_for_utc=sa.func.str_to_date(body.query_timestamp, "%Y-%m-%d %H:%i:%s"),
        status="SUCCEEDED",
        executed_at_utc=sa.func.utc_timestamp(),
        result_json=None,
    )
    s.add(q); await s.flush()

    # 7 horizons expected by PDD; accept any dict for flexibility
    for horizon, payload in body.initial_forecasts.items():
        s.add(m.CryptoForecast(query_id=q.query_id, horizon_type=horizon, forecast_value=payload.model_dump()))

    await s.commit()
    return {"query_id": q.query_id, "forecasts": len(body.initial_forecasts)}

@r.post("/surveys/{survey_id}/queries/followup", status_code=201)
async def create_followup_query(survey_id: int, body: QueryCreateFollowUp, s: AsyncSession = Depends(db)):
    survey, schedule_id = await _get_ids_for_runtime(s, survey_id)()
    qt_id = await s.scalar(select(m.QueryType.query_type_id).where(m.QueryType.query_type_name == "Follow-up"))
    if not qt_id:
        raise HTTPException(400, "query_type 'Follow-up' not found")

    q = m.CryptoQuery(
        survey_id=survey_id,
        schedule_id=schedule_id,
        query_type_id=qt_id,
        initial_query_id=body.initial_query_id,
        scheduled_for_utc=sa.func.str_to_date(body.query_timestamp, "%Y-%m-%d %H:%i:%s"),
        status="SUCCEEDED",
        executed_at_utc=sa.func.utc_timestamp(),
    )
    s.add(q); await s.flush()
    s.add(m.CryptoForecast(query_id=q.query_id, horizon_type=body.horizon_type, forecast_value=body.forecast.model_dump()))
    await s.commit()
    return {"query_id": q.query_id}
