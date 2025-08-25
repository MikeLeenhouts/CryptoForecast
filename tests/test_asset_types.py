import pytest
from . import data

@pytest.mark.asyncio
async def test_asset_types_crud(client):
    # Create
    payload = data.asset_type_payload()
    r = await client.post("/asset_types", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    asset_type_id = created["asset_type_id"]

    # Get by id
    r = await client.get(f"/asset_types/{asset_type_id}")
    assert r.status_code == 200
    assert r.json()["name"] == payload["name"]

    # List + filter
    r = await client.get("/asset_types", params={"name": payload["name"]})
    assert r.status_code == 200
    items = r.json()["items"] if isinstance(r.json(), dict) else r.json()
    assert any(it["asset_type_id"] == asset_type_id for it in items)

    # Update
    r = await client.patch(f"/asset_types/{asset_type_id}", json={"description": "Updated"})
    assert r.status_code == 200
    assert r.json()["description"] == "Updated"

    # Delete
    r = await client.delete(f"/asset_types/{asset_type_id}")
    assert r.status_code in (200, 204)
    r = await client.get(f"/asset_types/{asset_type_id}")
    assert r.status_code == 404
