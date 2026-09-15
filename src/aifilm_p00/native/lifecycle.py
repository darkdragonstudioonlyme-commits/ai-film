"""Pure lifecycle classification for reviewed Phase00 operator boundaries.

These helpers classify already-observed facts. They never request a reboot,
launch a process, issue an owner receipt, or turn an intent into proof.
"""
from copy import deepcopy

from ..errors import require

C3_INSTALL_ACTIONS = frozenset({'ENABLE_PREREQUISITES', 'INSTALL_RUNTIME'})


def classify_c3_process_result(action: str, result: dict, pending_reboot: dict) -> dict:
    """Convert an observed post-process reboot requirement into an operator wait."""
    require(action in C3_INSTALL_ACTIONS, 10, 'C3_LIFECYCLE_ACTION')
    require(type(result) is dict and type(pending_reboot) is dict and bool(pending_reboot),
            11, 'REBOOT_STATE_UNAVAILABLE')
    require(all(type(value) is bool for value in pending_reboot.values()),
            11, 'REBOOT_STATE_UNAVAILABLE')
    if result.get('state') == 'AWAITING_REBOOT':
        return deepcopy(result)
    if any(pending_reboot.values()):
        out = deepcopy(result)
        out.update({'exit': 20, 'state': 'AWAITING_REBOOT',
                    'wait_reason': 'PENDING_REBOOT_OBSERVED',
                    'pending_reboot': deepcopy(pending_reboot)})
        return out
    return deepcopy(result)


def reboot_resume_boundary(fence: dict, observed_host: dict, pending_reboot: dict) -> dict:
    """Require an actual host boot boundary before a reboot-wait may reconcile."""
    require(type(fence) is dict and type(fence.get('witness')) is dict,
            15, 'REBOOT_FENCE_WITNESS')
    before = fence['witness'].get('host_boot')
    after = observed_host.get('boot_utc') if type(observed_host) is dict else None
    require(type(before) is str and bool(before) and type(after) is str and bool(after),
            11, 'REBOOT_WITNESS_UNAVAILABLE')
    require(before != after, 20, 'REBOOT_NOT_OBSERVED')
    require(type(pending_reboot) is dict and bool(pending_reboot)
            and all(type(value) is bool for value in pending_reboot.values()),
            11, 'REBOOT_STATE_UNAVAILABLE')
    require(not any(pending_reboot.values()), 20, 'REBOOT_STILL_PENDING')
    return {'kind': 'HOST_REBOOT_BOUNDARY', 'before_boot': before,
            'after_boot': after, 'pending_reboot': deepcopy(pending_reboot),
            'action': fence.get('action'), 'step_id': fence['witness'].get('step_id')}


def owner_wait_can_relabel(opening_fence: dict, reason: str) -> bool:
    """Only operator-wait fences may move to owner-verification wait."""
    return (reason == 'AWAITING_OWNER_VERIFICATION'
            and type(opening_fence) is dict
            and opening_fence.get('state') in
                ('AWAITING_REBOOT', 'AWAITING_USER_INIT', 'AWAITING_OWNER_VERIFICATION'))
