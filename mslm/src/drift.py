import numpy as np
from typing import Tuple

def convert_to_rate(gyro: np.ndarray, S: float, B: float) -> np.ndarray:
    """
    Перевод показаний GYR_X_865 в °/s: (gyro - B)/S.
    """
    return (gyro - B) / S


def compute_trend(time: np.ndarray, rate: np.ndarray) -> float:
    """
    Тренд дрейфа: наклон (°/s²) * 3600 = °/h².
    """
    slope, _ = np.polyfit(time, rate, 1)
    return slope * 3600