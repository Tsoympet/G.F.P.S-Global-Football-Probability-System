from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Protocol

from .db import SessionLocal
from .models import ExecutionOrder


class ExecutionAdapter(Protocol):
    def execute_value_bet(self, request: "ExecutionRequest") -> Dict[str, Any]:
        ...


@dataclass
class ExecutionRequest:
    fixture_id: str
    market: str
    outcome: str
    odds: float
    ev: float
    meta: Dict[str, Any]


class DbExecutionAdapter:
    name = "db"

    def execute_value_bet(self, request: ExecutionRequest) -> Dict[str, Any]:
        with SessionLocal() as db:
            row = ExecutionOrder(
                fixture_id=request.fixture_id,
                market=request.market,
                outcome=request.outcome,
                odds=request.odds,
                ev=request.ev,
                status="queued",
                meta=request.meta,
                adapter=self.name,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            payload = asdict(request)
            payload["id"] = row.id
            return {"id": row.id, "status": row.status, "adapter": self.name, "payload": payload}


def get_execution_adapter() -> Optional[ExecutionAdapter]:
    name = os.getenv("EXECUTION_ADAPTER", "db").lower()
    if name in {"", "none", "disabled"}:
        return None
    return DbExecutionAdapter()
