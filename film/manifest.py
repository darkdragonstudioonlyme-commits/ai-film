import hashlib
import json
from copy import deepcopy

REQUIRED = {
    "asset_id","kind","model","model_version","model_hash",
    "prompt","negative_prompt","seed","references","workflow_version",
    "config","worker","gpu","generation_time","parent_assets"
}

def _digest(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def make_manifest(**fields):
    missing = REQUIRED - set(fields)
    if missing:
        raise ValueError(f"missing manifest fields: {sorted(missing)}")
    payload = deepcopy(fields)
    payload["manifest_sha256"] = _digest(payload)
    return payload

def validate_manifest(payload):
    missing = REQUIRED - set(payload)
    if missing:
        raise ValueError(f"missing manifest fields: {sorted(missing)}")
    expected = payload.get("manifest_sha256")
    body = {k: v for k, v in payload.items() if k != "manifest_sha256"}
    if expected != _digest(body):
        raise ValueError("manifest digest mismatch")
    return True
