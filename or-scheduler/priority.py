# Calculates priority scores for cases

from .models import SurgicalCase
from typing import Dict, Iterable

class DynamicPriorityCalculator:
    def __init__(self, aging_rate: float = 0.05, displacement_penalty: float = 2.0):
        # aging_rate: score added per minute that is added to the waiting time
        # displacement_penalty: the score added each time a case is displaced by an emergency
        self.aging_rate = aging_rate
        self.displacement_penalty = displacement_penalty

    # computes priority for a single case
    def compute_priority(self, case: SurgicalCase) -> float:
        score = (
            case.base_severity + (self.aging_rate * case.waiting_time) + (self.displacement_penalty * case.displacement_count)
        )
        return round(score, 2)

    # computes priority for a batch/all cases
    def compute_all(self, cases: Iterable[SurgicalCase]) -> Dict[str, float]:
        return {c.case_id: self.compute_priority(c) for c in cases}
        