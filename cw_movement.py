import json
import random
from cw_constants import CWConstants
from cw_state import Cell


class CWMove:
    def __init__(self, x: int, y: int, ex: int, ey: int):
        self.ey = ey
        self.ex = ex
        self.y = y
        self.x = x

    def as_dict(self):
        return {'x': self.x, 'y': self.y, 'eX': self.ex, 'eY': self.ey}

    def __str__(self):
        return json.dumps(self.as_dict)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_cell(cls, cell: Cell):
        return cls(
            cell.x,
            cell.y,
            random.randint(Cell.CELL_W_PX * (cell.x - 1), Cell.CELL_W_PX * cell.x),
            random.randint(Cell.CELL_H_PX * (cell.y - 1), Cell.CELL_H_PX * cell.y),
        )


class CWMoveSequence(list):
    UP = CWMove(0, -1, 7272, 7272)
    DOWN = CWMove(0, 1, 7272, 7272)
    LEFT = CWMove(-1, 0, 7272, 7272)
    RIGHT = CWMove(1, 0, 7272, 7272)
    UP_LEFT = CWMove(-1, -1, 7272, 7272)
    UP_RIGHT = CWMove(1, -1, 7272, 7272)
    DOWN_LEFT = CWMove(-1, 1, 7272, 7272)
    DOWN_RIGHT = CWMove(1, 1, 7272, 7272)

    def __init__(
        self,
        *args,
        interval_ms: int = CWConstants.DEFAULT_MOVE_INTERVAL_MS,
        delta_ms: int = CWConstants.DEFAULT_MOVE_DELTA_MS,
    ):
        self.interval = interval_ms
        self.delta = delta_ms
        super().__init__(args)

    @property
    def interval_w_delta(self):
        return random.randint(self.interval - self.delta, self.interval + self.delta)
