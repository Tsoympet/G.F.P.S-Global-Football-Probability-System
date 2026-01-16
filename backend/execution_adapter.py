from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Protocol


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


class MockExecutionAdapter:
    name = "mock"

    def execute_value_bet(self, request: ExecutionRequest) -> Dict[str, Any]:
        return {
            "id": f"mock-{int(time.time() * 1000)}",
            "status": "queued",
            "adapter": self.name,
            "payload": asdict(request),
        }


def get_execution_adapter() -> Optional[ExecutionAdapter]:
    name = os.getenv("EXECUTION_ADAPTER", "mock").lower()
    if name in {"", "none", "disabled"}:
        return None
    # extendable registry
    if name == "mock":
        return MockExecutionAdapter()
    return MockExecutionAdapter()
