# tests/test_surveys.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_surveys_crud_with_fks(client):
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    prompt = (await client.post("/prompts", json=data.prompt_payload(llm["llm_id"]))).json()
    schedule = (await client.post("/schedules", json=data.schedule_payload())).json()

    payload = data.survey_payload(asset["asset_id"], schedule["schedule_id"], prompt["prompt_id"], True)
    r = await client.post("/surveys", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    survey_id = created["survey_id"]

    r = await client.get(f"/surveys/{survey_id}")
    assert r.status_code == 200

    # Filter by asset_id / schedule_id / prompt_id / is_active
    r = await client.get("/surveys", params={"asset_id": asset["asset_id"]})
    assert r.status_code == 200
    r = await client.get("/surveys", params={"schedule_id": schedule["schedule_id"]})
    assert r.status_code == 200
    r = await client.get("/surveys", params={"prompt_id": prompt["prompt_id"]})
    assert r.status_code == 200
    r = await client.get("/surveys", params={"is_active": True})
    assert r.status_code == 200

    r = await client.patch(f"/surveys/{survey_id}", json={"is_active": False})
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    r = await client.delete(f"/surveys/{survey_id}")
    assert r.status_code in (200, 204)

    r = await client.get(f"/surveys/{survey_id}")
    assert r.status_code == 404
