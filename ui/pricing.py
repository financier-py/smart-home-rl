import numpy as np


ACTIONS = (-2, -1, 0, 1, 2)

NIGHT_HOURS_EARLY = range(0, 7)  # 0..6
DAY_HOURS = range(7, 17)  # 7..16
PEAK_HOURS = range(17, 21)  # 17..20
NIGHT_HOURS_LATE = range(21, 24)  # 21..23

SUN_HOURS = (8, 18)  # включительно
SUN_GAIN = 2
DEMAND = 1


def build_prices(night_price: int, day_price: int, peak_price: int) -> np.ndarray:
    return np.array(
        [night_price] * 7  # 0..6
        + [day_price] * 10  # 7..16
        + [peak_price] * 4  # 17..20
        + [night_price] * 3,  # 21..23
        dtype=int,
    )
