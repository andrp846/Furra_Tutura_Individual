from __future__ import annotations
import json
from typing import List, Any
from terra_futura.interfaces import InterfaceGrid
from terra_futura.simple_types import GridPosition

class ActivationPattern:
    _pattern: list[GridPosition]
    _selected: bool
    _grid: InterfaceGrid

    def __init__(self, grid: InterfaceGrid, pattern: List[GridPosition]):
        self._grid = grid
        self._pattern = pattern.copy()
        self._selected = False

    def select(self) -> None:
        assert self._selected is False
        self._grid.setActivationPattern(self._pattern)
        self._selected = True

    def is_selected(self) -> bool:
        return self._selected

    def state(self) -> str:
        serializable_pattern = [
            [pos.x, pos.y] for pos in self._pattern
        ]

        state: Any = {
            "activations": serializable_pattern, 
            "selected": self._selected,
        }
        return json.dumps(state)
