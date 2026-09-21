#!/usr/bin/env python3
"""Read the explicitly selected project snapshot; never choose by filename order."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
from typing import Any


class StateContractError(ValueError):
    """Canonical state cannot be unambiguously and safely selected."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StateContractError('duplicate-json-key:' + key)
        result[key] = value
    return result


def load_selected_state(root: Path) -> tuple[int, Path, dict[str, Any]]:
    """Return (version, selected path, object), rejecting ambiguous selectors."""
    try:
        text = (root / 'PROJECT_STATE.md').read_text(encoding='utf-8')
        selectors = re.findall(r'^STATE_VERSION:[^\r\n]*$', text, re.M)
        if len(selectors) != 1:
            raise StateContractError('state-selector-count:' + str(len(selectors)))
        match = re.fullmatch(r'STATE_VERSION:[ \t]*([1-9][0-9]*)[ \t]*', selectors[0])
        if match is None:
            raise StateContractError('state-selector-invalid')
        version = int(match.group(1))
        path = root / f'AI_FILM_PROJECT_STATE_V{version}.json'
        if path.is_symlink() or not path.is_file():
            raise StateContractError('selected-state-missing-or-symlink:' + path.name)
        state = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        if not isinstance(state, dict):
            raise StateContractError('selected-state-not-object')
        if type(state.get('state_version')) is not int or state['state_version'] != version:
            raise StateContractError('selected-state-version-mismatch')
        return version, path, state
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StateContractError('selected-state-unreadable:' + type(exc).__name__) from exc


def main() -> int:
    try:
        version, path, _ = load_selected_state(Path(__file__).resolve().parents[1])
    except StateContractError as exc:
        print('STATE_CONTRACT_CHECK_FAIL', exc)
        return 1
    print('STATE_CONTRACT_CHECK_PASS', f'state=V{version}', f'selected={path.name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
