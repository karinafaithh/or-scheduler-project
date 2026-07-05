# main.py
#
# Interactive entry point: prompts the user for each value, but every prompt
# has a sensible auto-assigned default shown in [brackets] -- just press
# Enter to accept it, or type a value to override it.

import itertools

from or_scheduler.models import SurgicalCase
from or_scheduler.scheduler import ORScheduler


def prompt_str(prompt: str, default: str) -> str:
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw if raw else default


def prompt_int(prompt: str, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            return int(raw)
        except ValueError:
            print("  Please enter a whole number.")


def prompt_float(prompt: str, default: float) -> float:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a number (e.g. 0.05).")


def prompt_yes_no(prompt: str, default: bool) -> bool:
    default_hint = "Y/n" if default else "y/N"
    raw = input(f"{prompt} [{default_hint}]: ").strip().lower()
    if raw == "":
        return default
    return raw in ("y", "yes")


def main():
    print("=== OR Scheduler Setup ===")
    capacity = prompt_int("OR shift capacity in minutes", 480)
    
    aging_rate, displacement_penalty = 0.05, 2.0

    scheduler = ORScheduler(capacity=capacity, aging_rate=aging_rate, displacement_penalty=displacement_penalty)

    # Auto-assigned, not asked per case: case_id increments on its own so the
    # user never has to track IDs manually.
    case_id_counter = itertools.count(1)

    print("\n=== Add Surgical Cases ===")
    print("(Enter cases one at a time. Type 'n' when asked to add another to stop.)\n")

    while prompt_yes_no("Add a surgical case?", True):
        case_id = next(case_id_counter)

        name = prompt_str("  Patient name", f"Patient {case_id}")
        duration = prompt_int("  Estimated duration (minutes)", 30)
        severity = prompt_int("  Base clinical severity (higher = more urgent)", 5)
        is_emergency = prompt_yes_no("  Is this an emergency case?", False)

        # New cases always start with zero waiting time / zero displacements
        # unless the user explicitly wants to seed a case that's "already
        # been waiting" (e.g. re-entering existing backlog data).
        waiting_time, displacement_count = 0, 0
        if prompt_yes_no("  Override starting waiting_time / displacement_count?", False):
            waiting_time = prompt_int("    Starting waiting_time (minutes)", 0)
            displacement_count = prompt_int("    Starting displacement_count", 0)

        case = SurgicalCase(case_id, name, duration, severity, waiting_time, displacement_count, is_emergency)
        scheduler.add_case(case)

        tag = " (EMERGENCY -- queued for preemption)" if is_emergency else ""
        print(f"  -> Added case [{case_id}] {name}{tag}\n")

    method = prompt_str("\nScheduling method: 'dp' (optimal) or 'greedy' (fast)", "dp").strip().lower()
    if method not in ("dp", "greedy"):
        print(f"  Unrecognized method '{method}', defaulting to 'dp'.")
        method = "dp"

    scheduler.optimize(method=method)

    if len(scheduler.emergency_queue) > 0:
        scheduler.run_emergency_preemption()

    print()
    scheduler.print_schedule()


if __name__ == "__main__":
    main()