# tests/test_crypto_queries.py
import pytest
from datetime import datetime, timezone
from . import data

@pytest.mark.asyncio
async def test_crypto_queries_with_target_delay_hours_and_filters(client):
    # Build upstream graph
    at = (await client.post("/asset-types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    prompt = (await client.post("/prompts", json=data.prompt_payload(llm["llm_id"]))).json()
    schedule = (await client.post("/schedules", json=data.schedule_payload())).json()
    survey = (await client.post("/surveys", json=data.survey_payload(asset["asset_id"], schedule["schedule_id"], prompt["prompt_id"], True))).json()

    survey_id = survey["survey_id"]
    schedule_id = schedule["schedule_id"]
    t0_utc = datetime.now(timezone.utc)

    # Initial Baseline @ T0
    r = await client.post("/crypto-queries", json=data.cq_initial(survey_id, schedule_id, t0_utc))
    assert r.status_code == 201, r.text
    cq0 = r.json()

    # Baseline Forecast @ T0 (6 horizons, distinguished by target_delay_hours)
    for h in (1, 6, 11, 24, 120, 240):
        r = await client.post("/crypto-queries", json=data.cq_baseline_forecast(survey_id, schedule_id, t0_utc, h))
        assert r.status_code == 201, r.text

    # Follow-ups (create 2)
    for h in (1, 6):
        r = await client.post("/crypto-queries", json=data.cq_followup(survey_id, schedule_id, t0_utc, h))
        assert r.status_code == 201, r.text

    # Filter by survey_id + type
    r = await client.get("/crypto-queries", params={"survey_id": survey_id, "query_type_id": 2})
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    # should be 6 BF rows
    assert len(items) >= 6
    assert set(i["target_delay_hours"] for i in items) >= {1, 6, 11, 24, 120, 240}

    # Update a row's status
    cq_id = items[0]["query_id"]
    r = await client.patch(f"/crypto-queries/{cq_id}", json={"status": "SUCCEEDED"})
    assert r.status_code == 200
    assert r.json()["status"] == "SUCCEEDED"
