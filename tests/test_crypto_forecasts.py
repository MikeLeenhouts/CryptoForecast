# tests/test_schedule_followups.py
import pytest
from datetime import datetime, timedelta, timezone
from . import data

def iso_utc(dt: datetime) -> str:
    """Return RFC3339/ISO-8601 with trailing Z (UTC)."""
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def make_followup_payload(schedule_id: int, label: str = "plus_1h", delta: timedelta = timedelta(hours=1)):
    return {
        "schedule_id": schedule_id,
        "label": label,
        "run_at_utc": iso_utc(datetime.now(timezone.utc) + delta),
        "enabled": True,
    }

@pytest.mark.asyncio
async def test_schedule_followups_crud_with_fk(client):
    """
    End-to-end CRUD for /schedule_followups with required FK to /schedules (and /surveys upstream).

    Assumes your API:
    - POST /surveys                          -> 201 + {"survey_id", ...}
    - POST /schedules                        -> 201 + {"schedule_id","survey_id","cron","timezone","enabled",...}
    - POST /schedule_followups               -> 201 + {"schedule_followup_id","schedule_id","label","run_at_utc","enabled",...}
    - GET  /schedule_followups/{id}          -> 200
    - GET  /schedule_followups               -> 200 (list or {"items":[...]})
    - PATCH /schedule_followups/{id}         -> 200
    - DELETE /schedule_followups/{id}        -> 200 or 204
    - Optional filters: schedule_id, label, enabled
    """

    # ---- Create upstream FKs: Survey -> Schedule ----
    survey = (await client.post("/surveys", json=data.survey_payload())).json()
    survey_id = survey["survey_id"]

    sched_payload = data.schedule_payload(survey_id)  # e.g., {"survey_id":..,"cron":"0 1 * * ? *","timezone":"UTC","enabled":True}
    schedule = (await client.post("/schedules", json=sched_payload)).json()
    schedule_id = schedule["schedule_id"]

    # ---- Create Followup ----
    payload = make_followup_payload(schedule_id, label="plus_1h", delta=timedelta(hours=1))
    r = await client.post("/schedule_followups", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    followup_id = created["schedule_followup_id"]

    assert created["schedule_id"] == schedule_id
    assert created["label"] == "plus_1h"
    assert created["enabled"] is True
    assert "run_at_utc" in created

    # ---- Read by id ----
    r = await client.get(f"/schedule_followups/{followup_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["schedule_followup_id"] == followup_id
    assert got["schedule_id"] == schedule_id

    # ---- List (no filter) ----
    r = await client.get("/schedule_followups")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["schedule_followup_id"] == followup_id for it in items)

    # ---- List (filter by schedule_id) ----
    r = await client.get("/schedule_followups", params={"schedule_id": schedule_id})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["schedule_followup_id"] == followup_id for it in items)

    # ---- List (filter by label) ----
    r = await client.get("/schedule_followups", params={"label": "plus_1h"})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["schedule_followup_id"] == followup_id for it in items)

    # ---- Update (PATCH) -> disable + change run_at_utc ----
    new_time = iso_utc(datetime.now(timezone.utc) + timedelta(hours=2))
    r = await client.patch(
        f"/schedule_followups/{followup_id}",
        json={"enabled": False, "run_at_utc": new_time}
    )
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["enabled"] is False
    assert updated["run_at_utc"].startswith(new_time[:16])  # ignore seconds drift if server normalizes

    # ---- Confirm update ----
    r = await client.get(f"/schedule_followups/{followup_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["enabled"] is False

    # ---- Delete ----
    r = await client.delete(f"/schedule_followups/{followup_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Verify deletion ----
    r = await client.get(f"/schedule_followups/{followup_id}")
    assert r.status_code == 404
