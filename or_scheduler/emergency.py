import heapq
import itertools
from typing import Optional

from .models import SurgicalCase


class EmergencyQueue:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, case: SurgicalCase) -> None:
        case.is_emergency = True
        heapq.heappush(self._heap, (-case.base_severity, next(self._counter), case))

    def pop(self) -> SurgicalCase:
        if self.is_empty():
            raise IndexError("pop from an empty EmergencyQueue")
        _, _, case = heapq.heappop(self._heap)
        return case

    def peek(self) -> Optional[SurgicalCase]:
        if self.is_empty():
            return None
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)