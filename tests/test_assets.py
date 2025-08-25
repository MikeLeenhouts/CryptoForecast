import pytest
from . import data

@pytest.mark.asyncio
async def test_assets_crud_with_fk(client):
    # Need an asset_type first
    at = (await client.post("/asset_types", json=data.asset_type_payload())).json()
    # Create asset
    asset = (await client.post("/assets", json=data.asset_payload(at["asset_type_id"]))).json()
    asset_id = asset["asset_id"]

    # Filter by asset_type_id
    r = await client.get("/assets", params={"asset_type_id": at["asset_type_id"]})
    assert r.status_code == 200
    body = r.json()
    items = body["items"] if isinstance(body, dict) else body
    assert any(x["asset_id"] == asset_id for x in items)

    # Update, then delete
    assert (await client.patch(f"/assets/{asset_id}", json={"description": "upd"})).status_code == 200
    assert (await client.delete(f"/assets/{asset_id}")).status_code in (200, 204)
