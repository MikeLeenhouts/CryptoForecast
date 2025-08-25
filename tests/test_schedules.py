# tests/test_schedules.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_schedules_crud_with_fk(client):
    """
    End-to-end CRUD for /schedules with required FK to /surveys.

    Assumes your API:
      - POST /surveys                      -> 201 + {"survey_id", "name", "is_active", ...}
      - POST /schedules                    -> 201 + {"schedule_id","survey_id","cron","timezone","enabled",...}
      - GET  /schedules/{id}               -> 200
      - GET  /schedules                    -> 200 (list or {"items":[...]})
      - PATCH /schedules/{id}              -> 200
      - DELETE /schedules/{id}             -> 200 or 204
      - Optional filters: survey_id, enabled (and possibly cron/timezone)
    """

    # ---- Create FK parent: Survey ----
    survey = (await client.post("/surveys", json=data.survey_payload())).json()
    survey_id = survey["survey_id"]

    # ---- Create Schedule ----
    payload = data.schedule_payload(survey_id)   # e.g., {"survey_id":..., "cron":"0 1 * * ? *", "timezone":"UTC", "enabled":True}
    r = await client.post("/schedules", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    schedule_id = created["schedule_id"]

    assert created["survey_id"] == survey_id
    assert created["cron"] == payload["cron"]
    assert created["timezone"] == payload["timezone"]
    assert created["enabled"] is True

    # ---- Read by id ----
    r = await client.get(f"/schedules/{schedule_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["schedule_id"] == schedule_id
    assert got["survey_id"] == survey_id

    # ---- List (no filter) ----
    r = await client.get("/schedules")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["schedule_id"] == schedule_id for s in items)

    # ---- Filter by survey_id ----
    r = await client.get("/schedules", params={"survey_id": survey_id})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["schedule_id"] == schedule_id for s in items)

    # ---- Filter by enabled=true ----
    r = await client.get("/schedules", params={"enabled": True})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["schedule_id"] == schedule_id for s in items)

    # ---- Update (PATCH -> disable, change cron) ----
    r = await client.patch(
        f"/schedules/{schedule_id}",
        json={"enabled": False, "cron": "0 3 * * ? *"}  # switch to 03:00
    )
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["enabled"] is False
    assert updated["cron"] == "0 3 * * ? *"

    # ---- Confirm update ----
    r = await client.get(f"/schedules/{schedule_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["enabled"] is False
    assert got["cron"] == "0 3 * * ? *"

    # ---- Filter by enabled=false ----
    r = await client.get("/schedules", params={"enabled": False})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(s["schedule_id"] == schedule_id for s in items)

    # ---- Delete ----
    r = await client.delete(f"/schedules/{schedule_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Verify deletion ----
    r = await client.get(f"/schedules/{schedule_id}")
    assert r.status_code == 404
