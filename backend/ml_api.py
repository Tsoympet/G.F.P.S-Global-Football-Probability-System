from typing import List

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/ml", tags=["ml"])

_models = [
    {"version": "v1", "roi": 0.08, "logLoss": 0.55, "status": "active"},
    {"version": "v2", "roi": 0.05, "logLoss": 0.52, "status": "ready"},
]


@router.post("/train")
async def train_model():
    new_version = f"v{len(_models) + 1}"
    _models.append({"version": new_version, "roi": 0.0, "logLoss": 1.0, "status": "training"})
    return {"message": f"Training started for {new_version}"}


@router.get("/models")
async def list_models() -> List[dict]:
    return _models


@router.post("/activate/{version}")
async def activate_model(version: str):
    found = False
    for m in _models:
        if m["version"] == version:
            m["status"] = "active"
            found = True
        elif m.get("status") == "active":
            m["status"] = "ready"
    if not found:
        raise HTTPException(404, f"Model {version} not found")
    return {"message": f"Activated model {version}"}
