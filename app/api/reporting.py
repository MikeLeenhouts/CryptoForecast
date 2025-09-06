import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.deps import db

r = APIRouter(prefix="/reports", tags=["reports"])

@r.get("/surveys/{survey_id}/runs")
async def survey_runs(survey_id: int, s: AsyncSession = Depends(db)):
    # Use query_schedules (not schedule_followups), count only follow-ups (delay_hours > 0)
    stmt = sa.text("""
    SELECT
      q.query_id,
      q.query_type_id,
      COALESCE(q.executed_at_utc, q.scheduled_for_utc) AS query_timestamp,
      q.initial_query_id,
      f.horizon_type,
      JSON_EXTRACT(f.forecast_value, '$.action')     AS action,
      JSON_EXTRACT(f.forecast_value, '$.confidence') AS confidence,
      JSON_EXTRACT(f.forecast_value, '$.reason')     AS reason,
      (SELECT COUNT(*) FROM queries cq WHERE cq.survey_id = q.survey_id) AS total_queries,
      (SELECT COUNT(*) + 1
         FROM query_schedules qs
         JOIN surveys s2 ON s2.schedule_id = qs.schedule_id
        WHERE s2.survey_id = q.survey_id
          AND qs.delay_hours > 0) AS expected_queries
    FROM queries q
    JOIN crypto_forecasts f ON q.query_id = f.query_id
    WHERE q.survey_id = :sid
    ORDER BY query_timestamp, f.horizon_type
    """)
    res = await s.execute(stmt, {"sid": survey_id})
    return [dict(r._mapping) for r in res.fetchall()]

@r.get("/surveys/{survey_id}/comparison")
async def survey_comparison(survey_id: int, s: AsyncSession = Depends(db)):
    # Compare initial predictions vs follow-up actuals by horizon
    stmt = sa.text("""
    SELECT
      f.horizon_type,
      MAX(CASE WHEN qt.query_type_name='Initial Baseline'
               THEN JSON_EXTRACT(f.forecast_value,'$.action') END) AS initial_prediction,
      MAX(CASE WHEN qt.query_type_name='Follow-up'
               THEN JSON_EXTRACT(f.forecast_value,'$.action') END) AS follow_up_actual,
      MAX(CASE WHEN qt.query_type_name='Initial Baseline'
               THEN COALESCE(q.executed_at_utc, q.scheduled_for_utc) END) AS initial_timestamp,
      MAX(CASE WHEN qt.query_type_name='Follow-up'
               THEN COALESCE(q.executed_at_utc, q.scheduled_for_utc) END) AS follow_up_timestamp
    FROM queries q
    JOIN crypto_forecasts f ON q.query_id=f.query_id
    JOIN query_type qt ON qt.query_type_id = q.query_type_id
    WHERE q.survey_id=:sid
    GROUP BY f.horizon_type
    HAVING f.horizon_type != 'Initial'
    """)
    res = await s.execute(stmt, {"sid": survey_id})
    return [dict(r._mapping) for r in res.fetchall()]
