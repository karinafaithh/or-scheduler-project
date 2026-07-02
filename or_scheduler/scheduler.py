# TODO: Define ORScheduler here
# - add_case, add_emergency
# - optimize(method="dp"|"greedy")
# - run_emergency_preemption()
# - print_schedule()

from typing import List, Optional

from .models import SurgicalCase
from .priority import DynamicPriorityCalculator
from .emergency import EmergencyQueue
from .algorithms import knapsack_dp, greedy_schedule

class ORScheduler:
    def __init__(self, capacity: int, aging_rate: float = 0.05, displacement_penalty: float = 2.0):
        self.capacity = capacity
        self.priority_calc = DynamicPriorityCalculator(aging_rate, displacement_penalty)
        self.pending_cases: List[SurgicalCase] = []
        self.emergency_queue = EmergencyQueue()
        self.schedule: Optional[dict] = None

    def add_case(self, case: SurgicalCase) -> None:
        """Add an elective case to the pending pool (routes to the emergency queue if flagged)."""
        if case.is_emergency:
            self.add_emergency(case)
            return
        self.pending_cases.append(case)
 
    def add_emergency(self, case: SurgicalCase) -> None:
        """Flag a case as an emergency and push it onto the emergency queue."""
        self.emergency_queue.push(case)

    def optimize(self, method: str = "dp") -> dict:
        priority_scores = self.priority_calc.compute_all(self.pending_cases)
 
        if method == "dp":
            self.schedule = knapsack_dp(self.pending_cases, self.capacity, priority_scores)
        elif method == "greedy":
            self.schedule = greedy_schedule(self.pending_cases, self.capacity, priority_scores)
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'dp' or 'greedy'.")
 
        selected_ids = {c.case_id for c in self.schedule["selected"]}
        self.pending_cases = [c for c in self.pending_cases if c.case_id not in selected_ids]
 
        return self.schedule

    

    def run_emergency_preemption(self) -> dict:
        if self.schedule is None:
            raise ValueError("Call optimize() before run_emergency_preemption().")
 
        while not self.emergency_queue.is_empty():
            emergency_case = self.emergency_queue.pop()
            self._insert_emergency(emergency_case)
 
        return self.schedule

    def _insert_emergency(self, emergency_case: SurgicalCase) -> None:
        selected = self.schedule["selected"]
        needed = emergency_case.duration
        idle = self.schedule["idle_time"]

        if needed > self.capacity:
            self.pending_cases.append(emergency_case)
            return

        if needed <= idle:
            selected.append(emergency_case)
            self.schedule["idle_time"] -= needed
            self.schedule["total_time"] += needed
        else:
            by_priority_asc = sorted(selected, key=self.priority_calc.compute_priority)
            freed = idle
            displaced = []
            for case in by_priority_asc:
                if freed >= needed:
                    break
                displaced.append(case)
                freed += case.duration

            for case in displaced:
                selected.remove(case)
                case.displacement_count += 1
                case.waiting_time += case.duration
                self.pending_cases.append(case)

            selected.append(emergency_case)
            self.schedule["idle_time"] = freed - needed
            self.schedule["total_time"] = self.capacity - self.schedule["idle_time"]

        self.schedule["total_value"] = round(
            sum(self.priority_calc.compute_priority(c) for c in selected), 2
        )



    def print_schedule(self) -> None:
        if self.schedule is None:
            print("No schedule has been generated yet. Call optimize() first.")
            return
 
        print(f"=== OR Schedule ({self.schedule['method'].upper()}) | Capacity: {self.capacity} min ===")
        header = f"{'ID':<6}{'Patient':<20}{'Duration':<10}{'Priority':<10}{'Emergency':<10}"
        print(header)
        print("-" * len(header))
        for case in self.schedule["selected"]:
            priority = self.priority_calc.compute_priority(case)
            print(
                f"{case.case_id:<6}{case.patient_name:<20}{case.duration:<10}"
                f"{priority:<10}{'Yes' if case.is_emergency else 'No':<10}"
            )
        print("-" * len(header))
        print(f"Total Value: {self.schedule['total_value']}")
        print(f"Total Time Used: {self.schedule['total_time']} / {self.capacity} min")
        print(f"Idle Time: {self.schedule['idle_time']} min")
 
        if self.pending_cases:
            print(f"\nUnscheduled / Displaced Cases ({len(self.pending_cases)}):")
            for case in self.pending_cases:
                print(
                    f"  - [{case.case_id}] {case.patient_name} "
                    f"(displaced {case.displacement_count}x, waiting {case.waiting_time} min)"
                )


