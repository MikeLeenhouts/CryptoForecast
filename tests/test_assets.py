# tests/test_assets.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_assets_crud_with_fk(client):
    at = (await client.post("/asset-types", json=data.asset_type_payload())).json()
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    asset_id = asset["asset_id"]

    r = await client.get("/assets", params={"asset_type_id": at["asset_type_id"]})
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    assert any(x["asset_id"] == asset_id for x in items)

    r = await client.patch(f"/assets/{asset_id}", json={"description": "upd"})
    assert r.status_code == 200

    r = await client.delete(f"/assets/{asset_id}")
    assert r.status_code in (200, 204)
