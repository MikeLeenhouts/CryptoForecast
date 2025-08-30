# tests/test_reports.py
import pytest
from datetime import datetime, timezone
from . import data

@pytest.mark.asyncio
async def test_reports_surveys_runs_and_comparison(client):
    # Seed minimal graph
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    prompt = (await client.post("/prompts", json=data.prompt_payload(llm["llm_id"]))).json()
    schedule = (await client.post("/schedules", json=data.schedule_payload())).json()
    survey = (await client.post("/surveys", json=data.survey_payload(asset["asset_id"], schedule["schedule_id"], prompt["prompt_id"], True))).json()

    # Create one query + forecast to give the report something to show
    t0_utc = datetime.now(timezone.utc)
    cq = (await client.post("/crypto-queries", json=data.cq_initial(survey["survey_id"], schedule["schedule_id"], t0_utc))).json()
    _ = (await client.post("/crypto-forecasts", json=data.forecast_payload(cq["query_id"], "OneHour"))).json()

    # Reports
    r = await client.get(f"/reports/surveys/{survey['survey_id']}/runs")
    assert r.status_code == 200

    r = await client.get(f"/reports/surveys/{survey['survey_id']}/comparison")
    assert r.status_code == 200
