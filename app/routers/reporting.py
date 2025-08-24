import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.deps import db

r = APIRouter(prefix="/reports", tags=["reports"])

@r.get("/surveys/{survey_id}/runs")
async def survey_runs(survey_id: int, s: AsyncSession = Depends(db)):
    stmt = sa.text("""
    SELECT q.query_id, q.query_type, q.query_timestamp, q.initial_query_id,
          f.horizon_type,
          JSON_EXTRACT(f.forecast_value, '$.action')     AS action,
          JSON_EXTRACT(f.forecast_value, '$.confidence') AS confidence,
          JSON_EXTRACT(f.forecast_value, '$.reason')     AS reason,
          (SELECT COUNT(*) FROM crypto_queries cq WHERE cq.survey_id = q.survey_id) AS total_queries,
          (SELECT COUNT(*) + 1 FROM schedule_followups sf
              JOIN surveys s2 ON s2.schedule_id = sf.schedule_id
            WHERE s2.survey_id = q.survey_id) AS expected_queries
    FROM crypto_queries q
    JOIN crypto_forecasts f ON q.query_id = f.query_id
    WHERE q.survey_id = :sid
    ORDER BY q.query_timestamp, f.horizon_type
    """)
    res = await s.execute(stmt, {"sid": survey_id})
    return [dict(r._mapping) for r in res.fetchall()]

@r.get("/surveys/{survey_id}/comparison")
async def survey_comparison(survey_id: int, s: AsyncSession = Depends(db)):
    stmt = sa.text("""
    SELECT
      f.horizon_type,
      MAX(CASE WHEN q.query_type='Initial'  THEN JSON_EXTRACT(f.forecast_value,'$.action') END) AS initial_prediction,
      MAX(CASE WHEN q.query_type='FollowUp' THEN JSON_EXTRACT(f.forecast_value,'$.action') END) AS follow_up_actual,
      MAX(CASE WHEN q.query_type='Initial'  THEN q.query_timestamp END) AS initial_timestamp,
      MAX(CASE WHEN q.query_type='FollowUp' THEN q.query_timestamp END) AS follow_up_timestamp
    FROM crypto_queries q
    JOIN crypto_forecasts f ON q.query_id=f.query_id
    WHERE q.survey_id=:sid
    GROUP BY f.horizon_type
    HAVING f.horizon_type != 'Initial'
    """)
    res = await s.execute(stmt, {"sid": survey_id})
    return [dict(r._mapping) for r in res.fetchall()]
