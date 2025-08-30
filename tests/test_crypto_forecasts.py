# tests/test_crypto_forecasts.py
import pytest
from datetime import datetime, timezone
from . import data

@pytest.mark.asyncio
async def test_crypto_forecasts_crud(client):
    # Minimal graph to create a crypto_query first
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    prompt = (await client.post("/prompts", json=data.prompt_payload(llm["llm_id"]))).json()
    schedule = (await client.post("/schedules", json=data.schedule_payload())).json()
    survey = (await client.post("/surveys", json=data.survey_payload(asset["asset_id"], schedule["schedule_id"], prompt["prompt_id"], True))).json()

    t0_utc = datetime.now(timezone.utc)
    cq = (await client.post("/crypto-queries", json=data.cq_initial(survey["survey_id"], schedule["schedule_id"], t0_utc))).json()

    # Create forecast for that query
    r = await client.post("/crypto-forecasts", json=data.forecast_payload(cq["query_id"], "OneHour"))
    assert r.status_code == 201, r.text
    created = r.json()
    fid = created["forecast_id"]
    assert created["query_id"] == cq["query_id"]
    assert created["horizon_type"] == "OneHour"

    # Read
    r = await client.get(f"/crypto-forecasts/{fid}")
    assert r.status_code == 200

    # List (filter by query_id)
    r = await client.get("/crypto-forecasts", params={"query_id": cq["query_id"]})
    assert r.status_code == 200

    # Update
    r = await client.patch(f"/crypto-forecasts/{fid}", json={"forecast_value": {"price": 65100, "note": "upd"}})
    assert r.status_code == 200
    assert r.json()["forecast_value"]["price"] == 65100

    # Delete
    r = await client.delete(f"/crypto-forecasts/{fid}")
    assert r.status_code in (200, 204)

    # Confirm gone
    r = await client.get(f"/crypto-forecasts/{fid}")
    assert r.status_code == 404
