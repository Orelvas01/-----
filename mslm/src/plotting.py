import matplotlib.pyplot as plt
import numpy as np

# Функция для калибровки
def plot_calibration(rate, gyro, S, B):
    plt.figure()
    plt.scatter(rate, gyro, label='Данные')
    plt.plot(rate, S*rate + B, 'r-', label=f'S={S:.3f}, B={B:.3f}')
    plt.xlabel('Rate (°/s)')
    plt.ylabel('GYR_X_865 (единицы датчика)')
    plt.title('Калибровка (IEEE 528)')
    plt.legend()
    plt.grid()
    plt.show()

# Функция для нелинейности
def plot_nonlinearity(rate, nl, avg_nl):
    plt.figure()
    plt.plot(rate, nl, 'o-')
    plt.xlabel('Rate (°/s)')
    plt.ylabel('Nonlinearity (%)')
    plt.title(f'Нелинейность, ср={avg_nl:.3f}%')
    plt.grid()
    plt.show()

# Функция для дрейфа
def plot_drift(time, rate_d, offset, trend):
    plt.figure()
    plt.plot(time, rate_d, label='Сырые данные')
    plt.axhline(offset, color='r', linestyle='--', label=f'Offset={offset:.3f} °/s')
    plt.xlabel('Time (s)')
    plt.ylabel('Rate (°/s)')
    plt.title(f'Дрейф GYR_X_865, тренд={trend:.3f} °/h²')
    plt.legend()
    plt.grid()
    plt.show()

# Функция для девиации Аллана
def plot_allan(taus, adev, slope):
    plt.figure()
    plt.loglog(taus, adev, label='Allan Deviation')
    # аппроксимационная линия в лог-лог масштабе
    line = 10**(slope * np.log10(taus) + (np.log10(adev[0]) - slope * np.log10(taus[0])))
    plt.loglog(taus, line, '--', label=f'slope={slope:.3f}')
    plt.xlabel('Tau (s)')
    plt.ylabel('Allan Dev (°/s)')
    plt.title('Allan Deviation')
    plt.legend()
    plt.grid(which='both')
    plt.show()