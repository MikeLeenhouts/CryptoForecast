import pytest
from . import data

@pytest.mark.asyncio
async def test_survey_reports_flow(client):
    # Seed minimal graph: asset_type -> asset -> llm -> prompt -> survey -> query -> forecast
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    prompt = (await client.post("/prompts", json=data.prompt_payload(llm["llm_id"]))).json()
    survey = (await client.post("/surveys", json=data.survey_payload())).json()

    cq = (await client.post("/crypto_queries", json=data.crypto_query_payload(survey["survey_id"], asset["asset_id"]))).json()
    _ = (await client.post("/crypto_forecasts", json=data.forecast_payload(survey["survey_id"], cq["crypto_query_id"]))).json()

    # Reports
    r = await client.get(f"/reports/surveys/{survey['survey_id']}/runs")
    assert r.status_code == 200
    assert isinstance(r.json(), list) or "runs" in r.json()

    r = await client.get(f"/reports/surveys/{survey['survey_id']}/comparison")
    assert r.status_code == 200
