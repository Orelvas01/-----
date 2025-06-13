import numpy as np
from pathlib import Path

def load_dat(path: Path, skiprows: int = 2) -> np.ndarray:
    """
    Загружает .dat-файл и возвращает NumPy-массив.
    """
    return np.loadtxt(path, skiprows=skiprows)