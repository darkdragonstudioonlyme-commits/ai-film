"""Pure lifecycle classification and bounded durable wait metadata.

These helpers classify already-observed facts. They never request a reboot,
launch a process, issue an owner receipt, or turn intent into proof. Durable
wait metadata is deliberately small and typed; raw process/owner evidence stays
behind its existing protected journal/evidence references.
"""
from copy import deepcopy

from ..codec import canonical, digest, hash_value
from ..errors import require

C3_INSTALL_ACTIONS = frozenset({"ENABLE_PREREQUISITES", "INSTALL_RUNTIME"})
WAIT_KINDS = frozenset({"AWAITING_REBOOT", "AWAITING_USER_INIT",
                        "AWAITING_OWNER_VERIFICATION"})
WAIT_OBSERVATION_CAP = 1024
_PENDING_KEYS = frozenset({"cbs_reboot_pending", "windows_update_reboot_required"})
_WAIT_FIELDS = frozenset({"schema_version", "kind", "reason", "previous_state",
                          "result_digest", "pending_reboot", "previous_wait_digest"})


def _pending(value):
    require(value is None or (type(value) is dict and set(value) == _PENDING_KEYS
            and all(type(v) is bool for v in value.values())),
            10, "WAIT_PENDING_SCHEMA")
    return deepcopy(value)


def validate_wait_observation(kind: str, observation: dict) -> dict:
    """Exact small schema for durable operator-wait context."""
    require(kind in WAIT_KINDS and type(observation) is dict, 10, "WAIT_OBSERVATION_SCHEMA")
    require(len(canonical(observation)) <= WAIT_OBSERVATION_CAP, 22, "WAIT_OBSERVATION_CAP")
    require(set(observation) == _WAIT_FIELDS and observation.get("schema_version") == 1
            and observation.get("kind") == kind, 10, "WAIT_OBSERVATION_SCHEMA")
    previous = observation.get("previous_state")
    require(previous in {"INTENT", "RUNNING", "AWAITING_REBOOT",
                         "AWAITING_USER_INIT", "AWAITING_OWNER_VERIFICATION"},
            10, "WAIT_PREVIOUS_STATE")
    result_ref = observation.get("result_digest")
    prior_ref = observation.get("previous_wait_digest")
    if result_ref is not None: hash_value(result_ref)
    if prior_ref is not None: hash_value(prior_ref)
    pending = _pending(observation.get("pending_reboot"))
    reason = observation.get("reason")
    if kind == "AWAITING_REBOOT":
        require(previous in {"INTENT", "RUNNING"} and result_ref is not None
                and prior_ref is None, 10, "WAIT_REBOOT_SCHEMA")
        require(reason in {"PENDING_REBOOT_OBSERVED", "NATIVE_RESTART_REQUIRED",
                           "OWNER_PLANNED_RESTART"}, 10, "WAIT_REASON")
        if reason == "PENDING_REBOOT_OBSERVED":
            require(pending is not None and any(pending.values()), 10, "WAIT_PENDING_SCHEMA")
        else:
            require(pending is None, 10, "WAIT_PENDING_SCHEMA")
    elif kind == "AWAITING_USER_INIT":
        require(previous in {"INTENT", "RUNNING"} and result_ref is not None
                and prior_ref is None and pending is None
                and reason == "OWNER_USER_INIT_REQUIRED", 10, "WAIT_USER_INIT_SCHEMA")
    else:
        require(pending is None, 10, "WAIT_OWNER_SCHEMA")
        if reason == "OWNER_VERIFICATION_REQUIRED":
            require(previous in {"INTENT", "RUNNING"} and result_ref is not None
                    and prior_ref is None, 10, "WAIT_OWNER_SCHEMA")
        else:
            require(reason == "POSTCONDITION_OWNER_EVIDENCE_PENDING"
                    and previous in {"AWAITING_REBOOT", "AWAITING_USER_INIT",
                                     "AWAITING_OWNER_VERIFICATION"}
                    and result_ref is None and prior_ref is not None,
                    10, "WAIT_OWNER_SCHEMA")
    return deepcopy(observation)


def wait_observation(action: str, result: dict, previous_state: str) -> dict:
    """Project an action result to safe durable wait metadata."""
    require(type(result) is dict and result.get("state") in WAIT_KINDS,
            10, "WAIT_RESULT_SCHEMA")
    kind = result["state"]
    pending = None
    if kind == "AWAITING_REBOOT":
        if result.get("wait_reason") == "PENDING_REBOOT_OBSERVED":
            reason = "PENDING_REBOOT_OBSERVED"
            pending = _pending(result.get("pending_reboot"))
        elif action == "AWAIT_OWNER_RESTART":
            reason = "OWNER_PLANNED_RESTART"
        else:
            reason = "NATIVE_RESTART_REQUIRED"
    elif kind == "AWAITING_USER_INIT":
        reason = "OWNER_USER_INIT_REQUIRED"
    else:
        reason = "OWNER_VERIFICATION_REQUIRED"
    value = {"schema_version": 1, "kind": kind, "reason": reason,
             "previous_state": previous_state, "result_digest": digest(result),
             "pending_reboot": pending, "previous_wait_digest": None}
    return validate_wait_observation(kind, value)


def owner_verification_wait(opening_fence: dict) -> dict:
    """Relabel an existing operator wait without copying its raw observation."""
    require(type(opening_fence) is dict and opening_fence.get("state") in WAIT_KINDS,
            10, "WAIT_OWNER_SCHEMA")
    previous = opening_fence.get("wait_observation")
    require(type(previous) is dict, 15, "WAIT_OBSERVATION_MISSING")
    validate_wait_observation(opening_fence["state"], previous)
    value = {"schema_version": 1, "kind": "AWAITING_OWNER_VERIFICATION",
             "reason": "POSTCONDITION_OWNER_EVIDENCE_PENDING",
             "previous_state": opening_fence["state"], "result_digest": None,
             "pending_reboot": None, "previous_wait_digest": digest(previous)}
    return validate_wait_observation("AWAITING_OWNER_VERIFICATION", value)


def classify_c3_process_result(action: str, result: dict, pending_reboot: dict) -> dict:
    """Convert an observed post-process reboot requirement into an operator wait."""
    require(action in C3_INSTALL_ACTIONS, 10, "C3_LIFECYCLE_ACTION")
    require(type(result) is dict and type(pending_reboot) is dict
            and set(pending_reboot) == _PENDING_KEYS
            and all(type(value) is bool for value in pending_reboot.values()),
            11, "REBOOT_STATE_UNAVAILABLE")
    if result.get("state") == "AWAITING_REBOOT":
        return deepcopy(result)
    if any(pending_reboot.values()):
        out = deepcopy(result)
        out.update({"exit": 20, "state": "AWAITING_REBOOT",
                    "wait_reason": "PENDING_REBOOT_OBSERVED",
                    "pending_reboot": deepcopy(pending_reboot)})
        return out
    return deepcopy(result)


def reboot_resume_boundary(fence: dict, observed_host: dict, pending_reboot: dict) -> dict:
    """Require an actual host boot boundary before a reboot-wait may reconcile."""
    require(type(fence) is dict and type(fence.get("witness")) is dict,
            15, "REBOOT_FENCE_WITNESS")
    before = fence["witness"].get("host_boot")
    after = observed_host.get("boot_utc") if type(observed_host) is dict else None
    require(type(before) is str and bool(before) and type(after) is str and bool(after),
            11, "REBOOT_WITNESS_UNAVAILABLE")
    require(before != after, 20, "REBOOT_NOT_OBSERVED")
    require(type(pending_reboot) is dict and set(pending_reboot) == _PENDING_KEYS
            and all(type(value) is bool for value in pending_reboot.values()),
            11, "REBOOT_STATE_UNAVAILABLE")
    require(not any(pending_reboot.values()), 20, "REBOOT_STILL_PENDING")
    return {"kind": "HOST_REBOOT_BOUNDARY", "before_boot": before,
            "after_boot": after, "pending_reboot": deepcopy(pending_reboot),
            "action": fence.get("action"), "step_id": fence["witness"].get("step_id")}


def owner_wait_can_relabel(opening_fence: dict, reason: str) -> bool:
    return (reason == "AWAITING_OWNER_VERIFICATION" and type(opening_fence) is dict
            and opening_fence.get("state") in WAIT_KINDS)
