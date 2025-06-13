import numpy as np
from typing import Tuple

def allan_deviation(y: np.ndarray, tau0: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    \sigma_y(\tau) = \sqrt{\tfrac12\langle(y_{i+1}-y_i)^2\rangle}
    """
    N = len(y)
    ms = np.unique(np.logspace(0, np.log10(N//2), num=50, dtype=int))
    taus, adev = [], []
    for m in ms:
        M = N//m
        if M < 2: continue
        clusters = y[:M*m].reshape(M, m).mean(axis=1)
        diff = np.diff(clusters)
        adev.append(np.sqrt(0.5 * np.mean(diff**2)))
        taus.append(m * tau0)
    return np.array(taus), np.array(adev)