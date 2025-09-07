# tests/test_crypto_queries.py
import pytest
from datetime import datetime, timezone
from . import data

@pytest.mark.asyncio
async def test_crypto_queries_with_query_schedule_id_and_filters(client):
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

    # Create query schedules first
    # Initial Baseline @ T0
    qs_baseline = (await client.post("/query-schedules", json=data.query_schedule_baseline(schedule_id))).json()
    
    # Baseline Forecast @ T0 (6 horizons, distinguished by paired_followup_delay_hours)
    qs_bf_ids = []
    for h in (1, 6, 11, 24, 120, 240):
        qs_bf = (await client.post("/query-schedules", json=data.query_schedule_bf(schedule_id, h))).json()
        qs_bf_ids.append(qs_bf["query_schedule_id"])

    # Follow-ups (create 2)
    qs_followup_ids = []
    for h in (1, 6):
        qs_followup = (await client.post("/query-schedules", json=data.query_schedule_followup(schedule_id, h))).json()
        qs_followup_ids.append(qs_followup["query_schedule_id"])

    # Now create queries using the query_schedule_ids
    # Initial Baseline @ T0
    r = await client.post("/queries", json=data.cq_initial(survey_id, schedule_id, qs_baseline["query_schedule_id"], t0_utc))
    assert r.status_code == 201, r.text
    cq0 = r.json()

    # Baseline Forecast @ T0 (6 horizons)
    for qs_id in qs_bf_ids:
        r = await client.post("/queries", json=data.cq_baseline_forecast(survey_id, schedule_id, qs_id, t0_utc))
        assert r.status_code == 201, r.text

    # Follow-ups (create 2)
    for i, qs_id in enumerate(qs_followup_ids):
        delay = [1, 6][i]
        r = await client.post("/queries", json=data.cq_followup(survey_id, schedule_id, qs_id, t0_utc, delay))
        assert r.status_code == 201, r.text

    # Filter by survey_id + type
    r = await client.get("/queries", params={"survey_id": survey_id, "query_type_id": 2})
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    # should be 6 BF rows
    assert len(items) >= 6
    assert set(i["query_schedule_id"] for i in items) == set(qs_bf_ids)

    # Update a row's status
    cq_id = items[0]["query_id"]
    r = await client.patch(f"/queries/{cq_id}", json={"status": "SUCCEEDED"})
    assert r.status_code == 200
    assert r.json()["status"] == "SUCCEEDED"
