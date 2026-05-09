# ui/simulation.py

from dataclasses import dataclass

import numpy as np

from core.env import SmartHomeEnv


@dataclass
class SimulationResult:
    history_b: list[int]
    history_a: list[int]
    history_money: list[float]
    final_cash: float
    final_battery: int


def run_simulation(
    env: SmartHomeEnv,
    policy: np.ndarray,
    start_battery: int,
    seed: int = 42,
    horizon: int = 24,
) -> SimulationResult:
    rng = np.random.default_rng(seed)

    current_b = min(start_battery, env.max_battery)
    total_money = 0.0
    history_b: list[int] = []
    history_a: list[int] = []
    history_money: list[float] = []

    for hour in range(horizon):
        t = hour % 24
        action = int(policy[t, current_b])

        transitions = env.get_transitions((t, current_b), action)
        probs = np.array([tr.probability for tr in transitions])
        probs = probs / probs.sum()
        idx = int(rng.choice(len(transitions), p=probs))

        total_money -= action * env.prices[t]
        current_b = transitions[idx].next_state[1]

        history_b.append(current_b)
        history_a.append(action)
        history_money.append(total_money)

    return SimulationResult(
        history_b=history_b,
        history_a=history_a,
        history_money=history_money,
        final_cash=history_money[-1],
        final_battery=history_b[-1],
    )
