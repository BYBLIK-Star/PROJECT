import random
from typing import List

DEFAULT_CELLS = 100


def generate_boxes(total_prisoners: int) -> List[int]:
    boxes = list(range(1, total_prisoners + 1))
    random.shuffle(boxes)
    return boxes


def theoretical_optimal_success_rate(total_prisoners: int) -> float:
    max_open = total_prisoners // 2
    if total_prisoners <= 1:
        return 0.0
    fail_probability = sum(1 / length for length in range(max_open + 1, total_prisoners + 1))
    return max(0.0, (1.0 - fail_probability) * 100.0)


def theoretical_random_success_rate(total_prisoners: int) -> float:
    if total_prisoners <= 1:
        return 0.0
    max_open = total_prisoners // 2
    return ((max_open / total_prisoners) ** total_prisoners) * 100.0
