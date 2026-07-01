# All algorithms to be used for scheduling

from .models import SurgicalCase
from typing import List, Dict

# instant real-time calculator, preferred over the knapsack in times of crisis due to it being computationally lighter
def greedy_schedule(
    cases: List[SurgicalCase], capacity: int, priority_scores: Dict[str, float]
) -> dict:

    # sorts cases based on efficiency: (value / time)
    ranked = sorted(
        cases, key=lambda c: priority_scores[c.case_id] / c.duration, reverse=True
    )

    # selects highest efficiency cases
    selected = []
    remaining = capacity
    for case in ranked:
        if case.duration <= remaining:
            selected.append(case)
            remaining -= case.duration

    total_value = round(sum(priority_scores[c.case_id] for c in selected), 2)
    total_time = capacity - remaining

    # returns result
    return{
        "method": "greedy",
        "selected": selected,
        "total_value": total_value,
        "total_time": total_time,
        "idle_time": remaining,
    }

# finds optimal solution in terms of value (clinical priority) within the time capacity (minutes)
# more operationally heavy than greedy algorithm
# bottom-up 0/1 knapsack dynamic programming
def knapsack_dp(
    cases: List[SurgicalCase], capacity: int, priority_scores: Dict[str, float]
) -> dict:

    # ensures that capacity is a positive number
    n = len(cases)
    capacity = max(capacity, 0)

    # creates dp table: (n+1) x capacity
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    # populate the table
    for i in range(1, n + 1):
        case = cases[i - 1]
        weight = case.duration
        value = priority_scores[case.case_id]
        for w in range (capacity + 1):
            if weight <= w:
                dp[i][w] = max(dp[i - 1][w], value + dp[i - 1][w - weight])
            else:
                dp[i][w] = dp[i - 1][w]
    
    # reconstruct solution
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            case = cases[i - 1]
            selected.append(case)
            w -= case.duration
    selected.reverse()

    # calculates total duration of selected cases
    total_time = sum(c.duration for c in selected)

    # returns results
    return{
        "method": "dp",
        "selected": selected,
        "total_value": round(dp[n][capacity], 2),
        "total_time": total_time,
        "idle_time": capacity - total_time,
    }