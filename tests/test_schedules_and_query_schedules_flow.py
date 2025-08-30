# tests/test_schedules_and_query_schedules.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_schedules_and_query_schedules_flow(client):
    # Create a schedule
    sched = (await client.post("/schedules", json=data.schedule_payload())).json()
    schedule_id = sched["schedule_id"]
    assert sched["timezone"] == "America/Chicago"

    # Insert the 1 Initial Baseline row (T0)
    r = await client.post("/query_schedules", json=data.query_schedule_baseline(schedule_id))
    assert r.status_code == 201, r.text

    # Insert 6 Baseline Forecast @ T0 paired rows
    for h in (1, 6, 11, 24, 120, 240):
        r = await client.post("/query_schedules", json=data.query_schedule_bf(schedule_id, h))
        assert r.status_code == 201, r.text

    # Insert 6 Follow-ups
    for h in (1, 6, 11, 24, 120, 240):
        r = await client.post("/query_schedules", json=data.query_schedule_followup(schedule_id, h))
        assert r.status_code == 201, r.text

    # List and verify counts
    r = await client.get("/query_schedules", params={"schedule_id": schedule_id})
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    assert len(items) == 13

    # Ensure BF@T0 rows have paired_followup_delay_hours populated
    bf = [x for x in items if x["query_type_id"] == 2 and x["delay_hours"] == 0]
    assert sorted([x["paired_followup_delay_hours"] for x in bf]) == [1, 6, 11, 24, 120, 240]
