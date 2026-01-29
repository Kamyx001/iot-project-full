
import random
from typing import Tuple


def random_range(start: float, end: float) -> Tuple[float, float]:
    """Generate a random range within [start, end] and return (min, max).

    Two independent random floats are sampled inside the provided bounds
    and returned as an ordered pair (min_value, max_value).
    """
    a = random.uniform(start, end)
    b = random.uniform(start, end)
    return (round(min(a, b), 2), round(max(a, b), 2))