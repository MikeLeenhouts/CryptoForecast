# tests/test_asset_types.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_asset_types_crud(client):
    payload = data.asset_type_payload()
    r = await client.post("/asset-types", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    asset_type_id = created["asset_type_id"]
    assert created["asset_type_name"] == payload["asset_type_name"]

    r = await client.get(f"/asset-types/{asset_type_id}")
    assert r.status_code == 200
    assert r.json()["asset_type_id"] == asset_type_id

    r = await client.get("/asset-types", params={"asset_type_name": payload["asset_type_name"]})
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    assert any(it["asset_type_id"] == asset_type_id for it in items)

    r = await client.patch(f"/asset-types/{asset_type_id}", json={"description": "Updated"})
    assert r.status_code == 200
    assert r.json()["description"] == "Updated"

    r = await client.delete(f"/asset-types/{asset_type_id}")
    assert r.status_code in (200, 204)

    r = await client.get(f"/asset-types/{asset_type_id}")
    assert r.status_code == 404
