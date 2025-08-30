# app/api/crud.py

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status, Body
from pydantic import BaseModel
from sqlalchemy import and_, delete as sa_delete, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.deps import db  # dependency that yields AsyncSession


def _coerce_value(raw: str | None) -> Any:
    """
    Best-effort coercion of query param strings into useful Python types.
    - ints: "123" -> 123
    - floats: "12.3" -> 12.3
    - bools: "true"/"false" (case-insensitive)
    - leave as str otherwise
    """
    if raw is None:
        return None
    s = raw.strip()

    # bools
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"

    # ints
    if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
        try:
            return int(s)
        except ValueError:
            pass

    # floats
    try:
        f = float(s)
        # avoid turning "00123" into float if it was intended int-like string
        if "." in s or "e" in s.lower():
            return f
    except ValueError:
        pass

    return s


def build_crud_router(
    *,
    model: Type[DeclarativeBase],
    table_name: str,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    out_schema: Type[BaseModel],
    allowed_filters: Optional[Dict[str, Callable[[Any, Any], Any]]] = None,
    order_by: Optional[Any] = None,
) -> APIRouter:
    """
    Factory that returns a FastAPI router with:
      - POST /{table}
      - GET  /{table}            (with optional filters, limit, offset)
      - GET  /{table}/{id}
      - PATCH/{table}/{id}
      - DELETE/{table}/{id}

    Args:
        model: SQLAlchemy ORM model (Declarative)
        table_name: URL segment to mount under
        create_schema / update_schema / out_schema: Pydantic models
        allowed_filters: mapping of query param name -> builder(model, value) -> SQLA expression
        order_by: optional SQLA ordering (e.g., model.created_at.desc())
    """
    r = APIRouter(prefix=f"/{table_name}", tags=[table_name])

    # Resolve primary key column dynamically
    pk_col = model.__mapper__.primary_key[0]

    # Capture the schema types to avoid forward reference issues
    CreateSchema = create_schema
    UpdateSchema = update_schema
    OutSchema = out_schema

    @r.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(payload: Annotated[Any, Body()], s: AsyncSession = Depends(db)):
        # Convert the payload to the proper schema type
        validated_payload = create_schema(**payload)
        obj = model(**validated_payload.model_dump(exclude_unset=True))
        s.add(obj)
        await s.commit()
        await s.refresh(obj)
        return obj

    @r.get("", response_model=list[out_schema])
    async def list_items(
        request: Request,
        s: AsyncSession = Depends(db),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0),
    ):
        stmt = select(model)

        # Apply filters from query string using allowed_filters map
        if allowed_filters:
            conds = []
            qp = request.query_params
            for key, builder in allowed_filters.items():
                if key in qp:
                    raw = qp.get(key)
                    val = _coerce_value(raw)
                    conds.append(builder(model, val))
            if conds:
                stmt = stmt.where(and_(*conds))

        # Optional ordering
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        # Pagination
        stmt = stmt.limit(limit).offset(offset)

        rows = (await s.execute(stmt)).scalars().all()
        return rows

    @r.get("/{item_id}", response_model=out_schema)
    async def get_item(item_id: int, s: AsyncSession = Depends(db)):
        stmt = select(model).where(pk_col == item_id)
        obj = (await s.execute(stmt)).scalars().first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{table_name[:-1].capitalize()} not found")
        return obj

    @r.patch("/{item_id}", response_model=out_schema)
    async def update_item(item_id: int, payload: Annotated[Any, Body()], s: AsyncSession = Depends(db)):
        # Convert the payload to the proper schema type
        validated_payload = update_schema(**payload)
        data = validated_payload.model_dump(exclude_unset=True)
        if not data:
            # No-op update — fetch the current row
            stmt = select(model).where(pk_col == item_id)
            obj = (await s.execute(stmt)).scalars().first()
            if not obj:
                raise HTTPException(status_code=404, detail=f"{table_name[:-1].capitalize()} not found")
            return obj

        stmt = sa_update(model).where(pk_col == item_id).values(**data)
        await s.execute(stmt)
        await s.commit()

        # Return the updated row
        stmt = select(model).where(pk_col == item_id)
        obj = (await s.execute(stmt)).scalars().first()
        if not obj:
            # Extremely rare race: row deleted between update and select
            raise HTTPException(status_code=404, detail=f"{table_name[:-1].capitalize()} not found after update")
        return obj

    @r.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(item_id: int, s: AsyncSession = Depends(db)):
        stmt = sa_delete(model).where(pk_col == item_id)
        res = await s.execute(stmt)
        await s.commit()
        # res.rowcount can be None on some dialects; do a quick check:
        if (res.rowcount or 0) == 0:
            raise HTTPException(status_code=404, detail=f"{table_name[:-1].capitalize()} not found")
        return None

    return r
