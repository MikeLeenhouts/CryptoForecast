# tests/test_surveys.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_surveys_crud(client):
    """
    End-to-end CRUD for /surveys.

    Assumes your API:
      - POST /surveys                 -> 201 + {"survey_id","name","is_active","description",...}
      - GET  /surveys/{id}            -> 200
      - GET  /surveys                 -> 200 (list or {"items":[...]})
      - PATCH /surveys/{id}           -> 200
      - DELETE /surveys/{id}          -> 200 or 204
      - Optional filters: name (exact/contains), is_active (true/false)
    """

    # ---- Create ----
    payload = data.survey_payload()  # e.g., {"name": unique("DailySurvey"), "is_active": True, "description": "..."}
    r = await client.post("/surveys", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    survey_id = created["survey_id"]

    assert created["name"] == payload["name"]
    assert created["is_active"] is True
    assert "description" in created

    # ---- Read by id ----
    r = await client.get(f"/surveys/{survey_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["survey_id"] == survey_id
    assert got["name"] == payload["name"]

    # ---- List (no filter) ----
    r = await client.get("/surveys")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["survey_id"] == survey_id for s in items)

    # ---- Filter by name (exact) ----
    r = await client.get("/surveys", params={"name": payload["name"]})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["survey_id"] == survey_id for s in items)

    # ---- Filter by is_active=true ----
    r = await client.get("/surveys", params={"is_active": True})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["survey_id"] == survey_id for s in items)

    # ---- Update (PATCH) -> deactivate + change description ----
    r = await client.patch(
        f"/surveys/{survey_id}",
        json={"is_active": False, "description": "Updated description"}
    )
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["is_active"] is False
    assert updated["description"] == "Updated description"

    # ---- Confirm update ----
    r = await client.get(f"/surveys/{survey_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["is_active"] is False
    assert got["description"] == "Updated description"

    # ---- Filter by is_active=false ----
    r = await client.get("/surveys", params={"is_active": False})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["survey_id"] == survey_id for s in items)

    # ---- Delete ----
    r = await client.delete(f"/surveys/{survey_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Verify deletion ----
    r = await client.get(f"/surveys/{survey_id}")
    assert r.status_code == 404
