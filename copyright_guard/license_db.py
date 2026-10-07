"""Known license rules and allowed uses."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class License:
    code: str
    commercial_ok: bool
    modification_ok: bool
    attribution_required: bool


LICENSES: dict[str, License] = {
    "CC0": License("CC0", True, True, False),
    "PUBLIC_DOMAIN": License("PUBLIC_DOMAIN", True, True, False),
    "OWNED": License("OWNED", True, True, False),
    "LICENSED": License("LICENSED", True, True, True),
    "CC-BY": License("CC-BY", True, True, True),
    "CC-BY-SA": License("CC-BY-SA", True, True, True),
    "CC-BY-ND": License("CC-BY-ND", True, False, True),
    "CC-BY-NC": License("CC-BY-NC", False, True, True),
    "CC-BY-NC-ND": License("CC-BY-NC-ND", False, False, True),
    "ALL_RIGHTS_RESERVED": License("ALL_RIGHTS_RESERVED", False, False, True),
}


def get(code: str) -> License | None:
    return LICENSES.get(code.upper())
