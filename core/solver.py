# solver.py

import numpy as np
from core.env import SmartHomeEnv


class ValIterSolver:
    def __init__(
        self,
        env: SmartHomeEnv,
        gamma: float = 0.95,
        theta: float = 1e-4,
        max_iters: int = 1000,
    ):
        self.env = env
        self.gamma = gamma
        self.theta = theta
        self.max_iters = max_iters

        # тут у нас политика и V
        self.V = np.zeros((24, self.env.max_battery + 1))
        self.Policy = np.zeros_like(self.V, dtype=int)

        self.iters = 0
        self.converged = False

    def solve(self):
        for k in range(1, self.max_iters + 1):
            V_new = np.copy(self.V)

            for t in range(24):
                for b in range(self.env.max_battery + 1):
                    state = (t, b)
                    best_val = -float("inf")
                    best_a = 0

                    for action in self.env.get_actions(b):
                        exp_val = 0
                        for transition in self.env.get_transitions(state, action):
                            next_t, next_b = transition.next_state
                            prob = transition.probability
                            reward = transition.reward

                            exp_val += prob * (
                                reward + self.gamma * self.V[next_t, next_b]
                            )
                        if exp_val > best_val:
                            best_val = exp_val
                            best_a = action

                    V_new[t, b] = best_val
                    self.Policy[t, b] = best_a

            delta = np.max(np.abs(self.V - V_new))
            self.V = V_new
            self.iters = k

            if delta < self.theta:
                self.converged = True
                break

        return self.V, self.Policy
