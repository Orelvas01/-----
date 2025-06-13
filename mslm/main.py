import numpy as np
from src.data_loader import load_dat
from src.calibration import calibrate, compute_nonlinearity
from src.drift import convert_to_rate, compute_trend
from src.allan import allan_deviation
from src.plotting import plot_calibration, plot_nonlinearity, plot_drift, plot_allan
import src.config as cfg

def main():
    # === 1. КАЛИБРОВКА ===
    mk = load_dat(cfg.MK_FILE)
    rate = mk[:, 1]      # командная скорость, °/s
    gyro  = mk[:, 2]      # GYR_X_865

    # S и B
    S, B = calibrate(rate, gyro)
    print(f"Scale factor S = {S:.6f} ед/°/s, Bias B = {B:.6f} ед")
    plot_calibration(rate, gyro, S, B)

    # Нелинейность
    nl = compute_nonlinearity(rate, gyro, S, B)
    avg_nl = np.mean(np.abs(nl))
    print(f"Avg nonlinearity = {avg_nl:.3f}%")
    plot_nonlinearity(rate, nl, avg_nl)

    # === 2. ДРЕЙФ ===
    drift = load_dat(cfg.DRIFT_FILE)
    time_d = drift[:, 0]
    gyro_d  = drift[:, 1]

    rate_d = convert_to_rate(gyro_d, S, B)
    offset = rate_d.mean()
    trend  = compute_trend(time_d, rate_d)
    print(f"Drift bias = {offset:.6f} °/s, Trend = {trend:.6f} °/h²")
    plot_drift(time_d, rate_d, offset, trend)

    # === 3. ALLAN DEVIATION ===
    taus, adev = allan_deviation(rate_d - offset, np.mean(np.diff(time_d)))
    slope, _ = np.polyfit(np.log10(taus), np.log10(adev), 1)
    print(f"Allan deviation slope (log-log) = {slope:.3f}")
    plot_allan(taus, adev, slope)

if __name__ == '__main__':
    main()
