import numpy as np
from typing import Tuple

def calibrate(rate: np.ndarray, gyro: np.ndarray) -> Tuple[float, float]:
    """
    Модель IEEE 528: gyro = S*rate + B.
    Возвращает S (sensitivity) и B (bias) в единицах датчика.
    """
    S, B = np.polyfit(rate, gyro, 1)
    return S, B

def compute_nonlinearity(rate: np.ndarray, gyro: np.ndarray, S: float, B: float) -> np.ndarray:
    """
    Нелинейность (%) каждой точки:
      100*(gyro - (S*rate+B)) / ((S*rate).max() - (S*rate).min())
    """
    fitted = S * rate + B
    return 100 * (gyro - fitted) / (fitted.max() - fitted.min())
