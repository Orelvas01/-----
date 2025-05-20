import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import allantools

# Загрузка данных
mk_data = np.loadtxt("МК.dat")
drift_data = np.loadtxt("Дрейф.dat")

### 1. Анализ МК ###
def analyze_scale_factor(data):
    # Масштабный коэффициент
    scale_factor = np.mean(data)
    print(f"Масштабный коэффициент (мВ/(°/с)): {scale_factor:.3f}")

    # График сигнала
    plt.figure()
    plt.plot(data)
    plt.title("Масштабный коэффициент")
    plt.xlabel("Измерение")
    plt.ylabel("мВ")
    plt.grid()

    # Нелинейность (%)
    ideal_line = np.linspace(np.min(data), np.max(data), len(data))
    nonlinearity = np.abs(data - ideal_line) / scale_factor * 100
    nonlinearity_mean = np.mean(nonlinearity)
    print(f"Нелинейность МК (средн.): {nonlinearity_mean:.3f} %")

    plt.figure()
    plt.plot(nonlinearity)
    plt.title("Нелинейность МК")
    plt.xlabel("Измерение")
    plt.ylabel("Нелинейность (%)")
    plt.grid()

    # Несимметричность
    pos = data[data > 0]
    neg = data[data < 0]
    if len(pos) > 0 and len(neg) > 0:
        asymmetry = np.abs(np.mean(pos) - np.abs(np.mean(neg))) / scale_factor * 100
    else:
        asymmetry = 0
    print(f"Несимметричность МК: {asymmetry:.3f} %")

    # Смещение нуля
    offset = np.mean(data[data < 0])
    print(f"Смещение нуля (°/с): {offset:.3f}")

### 2. Анализ дрейфа ###
def analyze_drift(data):
    plt.figure()
    plt.plot(data)
    plt.title("Сырые измерения дрейфа")
    plt.xlabel("Время (отн.)")
    plt.ylabel("°/с")
    plt.grid()

    # Смещение нуля
    bias = np.mean(data)
    print(f"Смещение нуля: {bias:.5f} °/с")

    # Тренд
    x = np.arange(len(data))
    slope, _, _, _, _ = stats.linregress(x, data)
    trend_per_hour_per_hour = slope * 3600  # °/ч/ч
    print(f"Тренд: {trend_per_hour_per_hour:.5f} °/ч/ч")

    # Девиация Аллана
    rate = 1  # Частота дискретизации (1 Гц по умолчанию)
    (taus, adevs, _, _, _) = allantools.oadev(data, rate=rate, data_type='freq')

    plt.figure()
    plt.loglog(taus, adevs, label='Allan Deviation')
    plt.title("Девиация Аллана")
    plt.xlabel("tau (сек)")
    plt.ylabel("Allan Deviation (°/с)")
    plt.grid(True, which='both')

    # Аппроксимация — нахождение ARW, Bias Instability, RRW
    log_tau = np.log10(taus)
    log_adev = np.log10(adevs)

    # Angular Random Walk (наклон -0.5)
    arw_idx = np.argmin(np.abs(log_tau + 0.5))
    arw = adevs[arw_idx] * np.sqrt(taus[arw_idx])
    print(f"Angular Random Walk (ARW): {arw:.5f} °/√ч")

    # Bias Instability (минимум на графике Allan deviation)
    bias_instability = np.min(adevs)
    print(f"Bias Instability: {bias_instability:.5f} °/с")

    # Rate Random Walk (наклон +0.5)
    rrw_idx = np.argmin(np.abs(log_tau - 0.5))
    rrw = adevs[rrw_idx] / np.sqrt(taus[rrw_idx])
    print(f"Rate Random Walk (RRW): {rrw:.5f} °/ч√ч")

    plt.legend()

### Основная программа
if __name__ == "__main__":
    analyze_scale_factor(mk_data)
    analyze_drift(drift_data)
    plt.show()