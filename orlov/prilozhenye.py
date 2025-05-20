import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

def simple_linear_regression(x, y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    intercept = y_mean - slope * x_mean
    return slope, intercept

def process_mk_file(filepath):
    data = np.loadtxt(filepath)
    omega = data[:, 0]  # Угловая скорость (°/с)
    voltage = data[:, 1]  # Напряжение (мВ)

    # Масштабный коэффициент
    scale = voltage / omega
    avg_scale = np.mean(scale)

    # Нелинейность
    ideal_voltage = avg_scale * omega
    nonlinearity = 100 * np.abs((voltage - ideal_voltage) / ideal_voltage)
    avg_nonlinearity = np.mean(nonlinearity)

    # Асимметрия
    pos = scale[omega > 0]
    neg = scale[omega < 0]
    asymmetry = 100 * np.abs(np.mean(pos) - np.mean(neg)) / avg_scale

    # Смещение нуля
    bias = voltage[omega == 0]
    if len(bias) > 0:
        zero_offset = np.mean(bias) / avg_scale
    else:
        zero_offset = 0

    # Графики
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(omega, voltage, label="Измерения")
    plt.plot(omega, ideal_voltage, label="Идеальная прямая", linestyle='--')
    plt.xlabel("Угловая скорость (°/с)")
    plt.ylabel("Выходное напряжение (мВ)")
    plt.title("Масштабный коэффициент")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(omega, nonlinearity)
    plt.xlabel("Угловая скорость (°/с)")
    plt.ylabel("Нелинейность (%)")
    plt.title("Нелинейность МК")

    plt.tight_layout()
    plt.show()

    return avg_scale, avg_nonlinearity, asymmetry, zero_offset

def process_drift_file(filepath):
    data = np.loadtxt(filepath)
    time = data[:, 0]  # Время (сек)
    rate = data[:, 1]  # Угловая скорость (°/с)

    # Смещение нуля
    bias = np.mean(rate)

    # Тренд — в °/ч/ч
    slope, _ = simple_linear_regression(time, rate)
    trend = slope * 3600  # т.к. 1 ч = 3600 сек

    # График дрейфа
    plt.figure(figsize=(8, 4))
    plt.plot(time, rate, label="Сырые данные")
    plt.plot(time, slope * time + bias, linestyle='--', label="Тренд")
    plt.xlabel("Время (с)")
    plt.ylabel("Угловая скорость (°/с)")
    plt.title("Дрейф гироскопа")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return bias, trend

def select_file(title="Выберите файл"):
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title=title, filetypes=[("DAT files", "*.dat"), ("All files", "*.*")])
    return filepath

def main():
    print("Выберите файл МК.dat")
    mk_path = select_file("Выберите файл с масштабным коэффициентом (МК.dat)")
    if not mk_path:
        print("Файл не выбран.")
        return

    scale, nonlinearity, asymmetry, bias_offset = process_mk_file(mk_path)
    print(f"\n📏 Масштабный коэффициент: {scale:.3f} мВ/(°/с)")
    print(f"📉 Средняя нелинейность: {nonlinearity:.2f}%")
    print(f"⚖️  Асимметрия: {asymmetry:.2f}%")
    print(f"🎯 Смещение нуля: {bias_offset:.3f} °/с")

    print("\nВыберите файл Дрейф.dat")
    drift_path = select_file("Выберите файл с дрейфом (Дрейф.dat)")
    if not drift_path:
        print("Файл не выбран.")
        return

    bias, trend = process_drift_file(drift_path)
    print(f"\n🌀 Смещение нуля: {bias:.4f} °/с")
    print(f"📈 Тренд (дрейф): {trend:.4f} °/ч/ч")

if __name__ == "__main__":
    main()