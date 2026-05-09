# env.py

from dataclasses import dataclass
import numpy as np


@dataclass
class Transition:
    probability: float
    next_state: tuple[int, int]
    reward: float


class SmartHomeEnv:
    """
    Состояние: (t, b) - час (от 0 до 23) и заряд батареи
    """

    def __init__(
        self,
        prices: np.ndarray,
        actions: list,
        max_battery: int = 10,
        prob_sun: float = 0.7,
    ):
        self.max_battery = max_battery
        self.prob_sun = prob_sun
        self.demand = 1  # это просто потребление киловат в час

        self.prices = prices  # цены за электр. по часам
        self.actions = actions.copy()  # доступные действия, ака продажа и покупка

    def get_actions(self, b: int) -> list[int]:
        """Возвращает список действий, которые ваще возможно сделать при заряде b"""
        valid = []
        for a in self.actions:
            if 0 <= b + a <= self.max_battery:
                valid.append(a)
        return valid

    def get_transitions(self, state: tuple[int, int], action: int) -> list[Transition]:
        """Возвращает список переходов для s и a"""
        t, b = state
        next_t = (t + 1) % 24
        reward = -action * self.prices[t]

        is_day = 8 <= t <= 18  # когда может светить солнце
        transitions = []

        if is_day:
            # если у нас светит солнце днем
            next_b_sun = min(max(b + action + 2 - self.demand, 0), self.max_battery)
            transitions.append(
                Transition(
                    probability=self.prob_sun,
                    next_state=(next_t, next_b_sun),
                    reward=reward,
                )
            )

            # если не светит днем
            next_b_cloud = min(max(b + action + 0 - self.demand, 0), self.max_battery)
            transitions.append(
                Transition(
                    probability=1.0 - self.prob_sun,
                    next_state=(next_t, next_b_cloud),
                    reward=reward,
                )
            )
        else:
            # ночью солнышка вообще нет
            next_b_night = min(max(b + action + 0 - self.demand, 0), self.max_battery)
            transitions.append(
                Transition(
                    probability=1.0, next_state=(next_t, next_b_night), reward=reward
                )
            )

        return transitions
