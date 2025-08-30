# tests/test_prompts.py
import pytest
from . import data

@pytest.mark.asyncio
async def test_prompts_crud_with_fk(client):
    llm = (await client.post("/llms", json=data.llm_payload())).json()
    llm_id = llm["llm_id"]

    payload = data.prompt_payload(llm_id)
    r = await client.post("/prompts", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    prompt_id = created["prompt_id"]
    assert created["llm_id"] == llm_id

    r = await client.get(f"/prompts/{prompt_id}")
    assert r.status_code == 200

    # Filters: llm_id, prompt_version
    r = await client.get("/prompts", params={"llm_id": llm_id})
    assert r.status_code == 200

    r = await client.get("/prompts", params={"prompt_version": payload["prompt_version"]})
    assert r.status_code == 200

    r = await client.patch(f"/prompts/{prompt_id}", json={"prompt_text": "Updated body text"})
    assert r.status_code == 200
    assert r.json()["prompt_text"] == "Updated body text"

    r = await client.delete(f"/prompts/{prompt_id}")
    assert r.status_code in (200, 204)

    r = await client.get(f"/prompts/{prompt_id}")
    assert r.status_code == 404
