# tests/test_llms.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_llms_crud(client):
    payload = data.llm_payload()
    r = await client.post("/llms", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    llm_id = created["llm_id"]

    r = await client.get(f"/llms/{llm_id}")
    assert r.status_code == 200

    r = await client.get("/llms", params={"llm_name": payload["llm_name"]})
    assert r.status_code == 200

    r = await client.patch(f"/llms/{llm_id}", json={"api_url": "https://api.fake/v1/new"})
    assert r.status_code == 200
    assert r.json()["api_url"] == "https://api.fake/v1/new"

    r = await client.delete(f"/llms/{llm_id}")
    assert r.status_code in (200, 204)

    r = await client.get(f"/llms/{llm_id}")
    assert r.status_code == 404
