# tests/test_llms.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_llms_crud(client):
    """
    End-to-end CRUD for /llms
    Assumes your API returns:
      - POST /llms           -> 201 + {"llm_id", "name", "provider", "model", ...}
      - GET  /llms/{id}      -> 200 + same shape
      - GET  /llms           -> 200 + list (or {"items":[...]})
      - PATCH/PUT /llms/{id} -> 200
      - DELETE    /llms/{id} -> 200 or 204
    """

    # ---- Create ----
    payload = data.llm_payload()  # {"name": unique("gpt-..."), "provider": "openai", "model": "gpt-4o-mini"}
    r = await client.post("/llms", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    llm_id = created["llm_id"]
    assert created["name"] == payload["name"]
    assert created["provider"] == payload["provider"]
    assert created["model"] == payload["model"]

    # ---- Read (by id) ----
    r = await client.get(f"/llms/{llm_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["llm_id"] == llm_id

    # ---- List (no filter) ----
    r = await client.get("/llms")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["llm_id"] == llm_id for it in items)

    # ---- List (with filter: name EXACT) ----
    r = await client.get("/llms", params={"name": payload["name"]})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(it["llm_id"] == llm_id for it in items)

    # ---- Update (PATCH) ----
    r = await client.patch(f"/llms/{llm_id}", json={"model": "gpt-4.1-mini"})
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["model"] == "gpt-4.1-mini"

    # ---- Read (confirm update) ----
    r = await client.get(f"/llms/{llm_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["model"] == "gpt-4.1-mini"

    # ---- Delete ----
    r = await client.delete(f"/llms/{llm_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Read (should be gone) ----
    r = await client.get(f"/llms/{llm_id}")
    assert r.status_code == 404
