# tests/test_crypto_queries.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_crypto_queries_crud_with_fks(client):
    """
    End-to-end CRUD for /crypto_queries with required FKs to /surveys and /assets.

    Assumes your API:
      - POST /asset_types                 -> 201 + {"asset_type_id", "name", ...}
      - POST /assets                      -> 201 + {"asset_id","asset_name","asset_type_id",...}
      - POST /surveys                     -> 201 + {"survey_id","name","is_active",...}
      - POST /crypto_queries              -> 201 + {"crypto_query_id","survey_id","asset_id","query_text",...}
      - GET  /crypto_queries/{id}         -> 200
      - GET  /crypto_queries              -> 200 (list or {"items":[...]})
      - PATCH /crypto_queries/{id}        -> 200
      - DELETE /crypto_queries/{id}       -> 200 or 204
      - Optional filters: survey_id, asset_id, query_text
    """

    # ---- Create FK parents: asset_type -> asset, and survey ----
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    survey = (await client.post("/surveys", json=data.survey_payload())).json()

    asset_id = asset["asset_id"]
    survey_id = survey["survey_id"]

    # ---- Create crypto_query ----
    payload = data.crypto_query_payload(survey_id=survey_id, asset_id=asset_id)
    r = await client.post("/crypto_queries", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    cq_id = created["crypto_query_id"]

    assert created["survey_id"] == survey_id
    assert created["asset_id"] == asset_id
    assert created["query_text"] == payload["query_text"]

    # ---- Read by id ----
    r = await client.get(f"/crypto_queries/{cq_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["crypto_query_id"] == cq_id
    assert got["survey_id"] == survey_id
    assert got["asset_id"] == asset_id

    # ---- List (no filter) ----
    r = await client.get("/crypto_queries")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["crypto_query_id"] == cq_id for it in items)

    # ---- Filter by survey_id ----
    r = await client.get("/crypto_queries", params={"survey_id": survey_id})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["crypto_query_id"] == cq_id for it in items)

    # ---- Filter by asset_id ----
    r = await client.get("/crypto_queries", params={"asset_id": asset_id})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["crypto_query_id"] == cq_id for it in items)

    # ---- (Optional) Filter by query_text exact or contains ----
    r = await client.get("/crypto_queries", params={"query_text": payload["query_text"]})
    assert r.status_code == 200, r.text

    # ---- Update (PATCH) ----
    r = await client.patch(
        f"/crypto_queries/{cq_id}",
        json={"query_text": "Predict 6h price change"}
    )
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["query_text"] == "Predict 6h price change"

    # ---- Confirm update ----
    r = await client.get(f"/crypto_queries/{cq_id}")
    assert r.status_code == 200, r.text
    assert r.json()["query_text"] == "Predict 6h price change"

    # ---- Delete ----
    r = await client.delete(f"/crypto_queries/{cq_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Verify deletion ----
    r = await client.get(f"/crypto_queries/{cq_id}")
    assert r.status_code == 404
