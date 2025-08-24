from typing import Any, Callable, Optional, Type
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_
from pydantic import BaseModel
from app.utils.deps import db

def build_crud_router(
    *,
    model: Any,
    pk: str,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    out_schema: Type[BaseModel],
    table_name: str,
    allowed_filters: dict[str, Callable[[Any, Any], Any]] | None = None
) -> APIRouter:
    r = APIRouter(prefix=f"/{table_name}", tags=[table_name])

    # List (with filters)
    @r.get("", response_model=list[out_schema])
    async def list_items(
        s: AsyncSession = Depends(db),
        **kwargs
    ):
        stmt = select(model)
        if allowed_filters:
            clauses = []
            for k, fn in allowed_filters.items():
                v = kwargs.get(k)
                if v is not None:
                    clauses.append(fn(model, v))
            if clauses:
                stmt = stmt.where(and_(*clauses))
        rows = (await s.execute(stmt)).scalars().all()
        return rows

    # Get by id
    @r.get("/{item_id}", response_model=out_schema)
    async def get_item(item_id: int, s: AsyncSession = Depends(db)):
        row = await s.get(model, item_id)
        if not row:
            raise HTTPException(404, "not found")
        return row

    # Create
    @r.post("", response_model=out_schema, status_code=201)
    async def create_item(payload: create_schema, s: AsyncSession = Depends(db)):
        obj = model(**payload.model_dump())
        s.add(obj)
        try:
            await s.commit()
        except Exception as e:
            await s.rollback()
            # FK/unique violations become 409/400
            raise HTTPException(status_code=409, detail=str(e))
        await s.refresh(obj)
        return obj

    # Update (partial)
    @r.patch("/{item_id}", response_model=out_schema)
    async def update_item(item_id: int, payload: update_schema, s: AsyncSession = Depends(db)):
        data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if not data:
            row = await s.get(model, item_id)
            if not row: raise HTTPException(404, "not found")
            return row
        stmt = (
            update(model)
            .where(getattr(model, pk) == item_id)
            .values(**data)
        )
        res = await s.execute(stmt)
        if res.rowcount == 0:
            raise HTTPException(404, "not found")
        try:
            await s.commit()
        except Exception as e:
            await s.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        row = await s.get(model, item_id)
        return row

    # Delete
    @r.delete("/{item_id}", status_code=204)
    async def delete_item(item_id: int, s: AsyncSession = Depends(db)):
        stmt = delete(model).where(getattr(model, pk) == item_id)
        res = await s.execute(stmt)
        if res.rowcount == 0:
            raise HTTPException(404, "not found")
        try:
            await s.commit()
        except Exception as e:
            await s.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        return None

    return r
