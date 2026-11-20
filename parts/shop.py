"""Load house constants from skills/SKILL.md (the single source of truth).

Usage:
    from parts.shop import const
    tube_id = const("airframe.loc_38mm_paper.id_measured_mm")   # mm

A constant still marked TBD raises TBDError instead of returning a guess.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

SKILL_PATH = Path(__file__).resolve().parent.parent / "skills" / "SKILL.md"
_BLOCK = re.compile(r"```yaml shop-constants\n(.*?)```", re.DOTALL)


class TBDError(KeyError):
    """Raised when code asks for a constant the owner has not supplied yet."""


@lru_cache(maxsize=1)
def constants() -> dict:
    text = SKILL_PATH.read_text()
    m = _BLOCK.search(text)
    if not m:
        raise RuntimeError(f"No ```yaml shop-constants block in {SKILL_PATH}")
    return yaml.safe_load(m.group(1))


def const(dotted: str):
    node = constants()
    for key in dotted.split("."):
        if not isinstance(node, dict) or key not in node:
            raise KeyError(f"Unknown shop constant: {dotted}")
        node = node[key]
    if node == "TBD":
        raise TBDError(f"Shop constant '{dotted}' is TBD in skills/SKILL.md — ask the owner.")
    return node
