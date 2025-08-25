# tests/test_prompts.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_prompts_crud_with_fk(client):
    """
    End-to-end CRUD for /prompts with required FK to /llms.

    Assumes your API:
      - POST /llms                        -> 201 + {"llm_id", "name", "provider", "model", ...}
      - POST /prompts                     -> 201 + {"prompt_id", "title", "llm_id", "body", ...}
      - GET  /prompts/{id}                -> 200
      - GET  /prompts                     -> 200 (list or {"items":[...]})
      - PATCH /prompts/{id}               -> 200
      - DELETE /prompts/{id}              -> 200 or 204
      - Optional filters: name/title, llm_id
    """

    # ---- Create FK parent: LLM ----
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    llm_id = llm["llm_id"]

    # ---- Create Prompt ----
    payload = data.prompt_payload(llm_id)   # {"title": unique("MarketPrompt"), "llm_id": <>, "body": "..."}
    r = await client.post("/prompts", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    prompt_id = created["prompt_id"]
    assert created["title"] == payload["title"]
    assert created["llm_id"] == llm_id
    assert created.get("body")

    # ---- Read by id ----
    r = await client.get(f"/prompts/{prompt_id}")
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["prompt_id"] == prompt_id
    assert got["llm_id"] == llm_id

    # ---- List (no filter) ----
    r = await client.get("/prompts")
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(p["prompt_id"] == prompt_id for p in items)

    # ---- List (filter by title exact) ----
    r = await client.get("/prompts", params={"title": payload["title"]})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(p["prompt_id"] == prompt_id for p in items)

    # ---- List (filter by llm_id) ----
    r = await client.get("/prompts", params={"llm_id": llm_id})
    assert r.status_code == 200, r.text
    body = r.json()
    items = body["items"] if isinstance(body, dict) and "items" in body else body
    assert any(p["prompt_id"] == prompt_id for p in items)

    # ---- Update (PATCH) ----
    r = await client.patch(f"/prompts/{prompt_id}", json={"body": "Updated body text"})
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["body"] == "Updated body text"

    # ---- Confirm update ----
    r = await client.get(f"/prompts/{prompt_id}")
    assert r.status_code == 200, r.text
    assert r.json()["body"] == "Updated body text"

    # ---- Delete ----
    r = await client.delete(f"/prompts/{prompt_id}")
    assert r.status_code in (200, 204), r.text

    # ---- Verify deletion ----
    r = await client.get(f"/prompts/{prompt_id}")
    assert r.status_code == 404
