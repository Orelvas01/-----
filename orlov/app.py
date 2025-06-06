import tkinter as tk
from tkinter import filedialog
import json
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
#from scipy.optimize import curve_fit

def save_data_to_json(key, data):
    try:
        with open('paths_and_coords.json', 'r', encoding='utf-8') as f:
            data_file = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data_file = {}

    data_file[key] = data
    with open('paths_and_coords.json', 'w', encoding='utf-8') as f:
        json.dump(data_file, f, indent=4, ensure_ascii=False)

def read_json(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчёт масштабных коэффициентов")
        self.geometry("990x600")

        self.mk_file_path = None
        self.mk_values = None  # сюда сохраним рассчитанные МК

        self.btn_load_mk = tk.Button(self, text="Загрузить файл MK.dat", command=self.upload_file_MK)
        self.btn_load_mk.grid(row=1, column=0, padx=10, pady=10)

        self.btn_calc = tk.Button(self, text="Рассчитать МК", command=self.rashet)
        self.btn_calc.grid(row=2, column=0, padx=10, pady=10)

        self.output_text = tk.Text(self, height=10, width=120)
        self.output_text.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.btn_plot = tk.Button(self, text="Показать график МК", command=self.plot_nonlinearity)
        self.btn_plot.grid(row=3, column=0, padx=10, pady=10)

        self.btn_zero_offset = tk.Button(self, text="Рассчитать смещение нуля", command=self.calculate_zero_offset)
        self.btn_zero_offset.grid(row=4, column=0, padx=10, pady=10)

        self.btn_nonlinearity = tk.Button(self, text="Показать график нелинейности", command=self.plot_mk_nonlinearity)
        self.btn_nonlinearity.grid(row=5, column=0, padx=10, pady=10)

        self.btn_asymmetry = tk.Button(self, text="Показать несимметричность МК (%)", command=self.show_asymmetry)
        self.btn_asymmetry.grid(row=6, column=0, padx=10, pady=10)

        # Кнопка очистки поля вывода
        self.btn_clear = tk.Button(self, text="Очистить вывод", command=self.erase)
        self.btn_clear.grid(row=9, column=0, padx=10, pady=10)

        self.btn_load_drift = tk.Button(self, text="Загрузить файл Дрейф.dat", command=self.upload_file_drift)
        self.btn_load_drift.grid(row=1, column=1, padx=10, pady=10)

        self.btn_raw_plot = tk.Button(self, text="График «сырых» измерений (°/с)", command=self.plot_raw_data)
        self.btn_raw_plot.grid(row=2, column=1, padx=10, pady=10)

        self.btn_zero_offset = tk.Button(self, text="Смещение нуля (°/с)", command=self.calculate_zero_offset_drift)
        self.btn_zero_offset.grid(row=3, column=1, padx=10, pady=10)

        self.btn_trend = tk.Button(self, text="Тренд (°/ч²)", command=self.calculate_trend)
        self.btn_trend.grid(row=4, column=1, padx=10, pady=10)

        self.btn_allan_dev = tk.Button(self, text="Девиация Аллана (график)", command=self.plot_allan_deviation)
        self.btn_allan_dev.grid(row=5, column=1, padx=10,pady=10)

        self.btn_allan_approx = tk.Button(self, text="Аппроксимация Девиации Аллана", command=self.plot_allan_approximation)
        self.btn_allan_approx.grid(row=6, column=1, padx=10, pady=10)

        self.btn_params = tk.Button(self, text="Параметры ARW, Bias Instability, RRW", command=self.calculate_allan_parameters)
        self.btn_params.grid(row=7, column=1, padx=10, pady=10)


        self.drift_file_path = None
        self.drift_data = None  # numpy array с данными дрейфа
        self.sampling_rate = None  # Частота дискретизации, с/с (нужно задать или вычислить)

    def erase(self):
        """Метод для отчистки поля вывода"""
        self.output_text.config(state=tk.NORMAL)  # Разрешаем редактирование
        self.output_text.delete('1.0', tk.END)   # Удаляем содержимое
        self.output_text.config(state=tk.DISABLED)  # Снова делаем поле только для чтения

    def print_to_output(self, msg):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def upload_file_MK(self):
        file_path = filedialog.askopenfilename(title="Выберите файл MK.dat", filetypes=[("DAT files", "*.dat")])
        if file_path:
            save_data_to_json("MK", file_path)
            self.print_to_output(f"Файл MK загружен: {file_path}")

            # Попытка показать пример данных
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                cleaned_lines = [line for i, line in enumerate(lines) if i not in (0,1,2)]  # пропускаем 3 строки
                data = np.loadtxt(StringIO(''.join(cleaned_lines)))
                self.print_to_output(f"Пример данных (первые 5 строк):\n{data[:5]}")
            except Exception as e:
                self.print_to_output(f"Ошибка чтения файла: {e}")

    def upload_file_drift(self):
        file_path = filedialog.askopenfilename(title="Выберите файл Дрейф.dat", filetypes=[("DAT files", "*.dat"), ("Все файлы", "*.*")])
        if file_path:
            self.drift_file_path = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[3:]  # Пропускаем заголовки, если есть
                self.drift_data = np.loadtxt(lines)
                # Допустим, первая колонка — время или индекс, вторая — значение в °/с
                self.sampling_rate = 1 / np.mean(np.diff(self.drift_data[:,0]))  # Гц
                self.print_to_output(f"Файл дрейфа загружен. Размер данных: {len(self.drift_data)} точек.")
                self.print_to_output(f"Частота дискретизации (Гц): {self.sampling_rate:.2f}")
            except Exception as e:
                self.print_to_output(f"Ошибка при загрузке дрейфа: {e}")

    def calculate_nonlinearity(self, mk_values):
        """
        Расчет нелинейности МК в процентах для каждого канала.
        Возвращает массив нелинейностей и среднее значение по каналам.
        """
        mk_values = np.array(mk_values)
        mean_val = np.mean(mk_values)
        if np.isclose(mean_val, 0):
            # Среднее слишком близко к нулю — нелинейность считать невозможно корректно
            return float('inf')
        # Можно отфильтровать выбросы (например, отбросить значения, выходящие за 3 сигмы)
        std_val = np.std(mk_values)
        filtered_values = mk_values[(mk_values > mean_val - 3*std_val) & (mk_values < mean_val + 3*std_val)]
        if len(filtered_values) == 0:
            filtered_values = mk_values
        max_dev = np.max(np.abs(filtered_values - mean_val))
        nonlinearity_percent = (max_dev / abs(mean_val)) #* 100
        return nonlinearity_percent
    
    def rashet(self):
        data = read_json("paths_and_coords.json")
        if "MK" not in data:
            self.print_to_output("Ошибка: файл MK не загружен")
            return

        try:
            file_path = data["MK"]
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Пропускаем первые три строки
            cleaned_lines = [line for i, line in enumerate(lines) if i >= 3]
            arr = np.loadtxt(StringIO(''.join(cleaned_lines)))

            rate = arr[:, 1]
            voltages = arr[:, 2:3]  # Только третий столбец (один канал)

            # Исключаем нулевые rate
            mask = rate != 0
            if np.sum(mask) == 0:
                self.print_to_output("Ошибка: все значения rate равны нулю!")
                return

            rate_filtered = rate[mask]
            voltages_filtered = voltages[mask]

            # Расчет масштабного коэффициента (мВ / (°/с))
            mk_values = (voltages_filtered / rate_filtered[:, None]) * 1000  # Умножаем на 1000
            mk_mean = np.nanmean(mk_values)

            self.mk_values = mk_mean

            self.print_to_output("Масштабный коэффициент (мВ/(°/с)) только по 3-му каналу:")
            self.print_to_output(f"Канал 3: {mk_mean:.4f}")

            # Нелинейность только по 3-му каналу
            nonlinearity = self.calculate_nonlinearity(mk_values.flatten())
            self.nonlinearity_list = [nonlinearity]

            nonlinearity_div_1000 = float(nonlinearity) / 1000  # Явно приводим к float и делим
            self.print_to_output(f"Нелинейность МК (канал 3): {nonlinearity_div_1000:.6f} %")

        except Exception as e:
            self.print_to_output(f"Ошибка при расчёте: {e}")
        
    def plot_nonlinearity(self):
        import json
        from io import StringIO
        import numpy as np
        import matplotlib.pyplot as plt

        try:
            data = json.load(open("paths_and_coords.json", encoding="utf-8"))
            if "MK" not in data:
                self.print_to_output("Ошибка: файл MK не загружен")
                return

            file_path = data["MK"]
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            cleaned_lines = [line for i, line in enumerate(lines) if i not in (0,1,2)]
            arr = np.loadtxt(StringIO(''.join(cleaned_lines)))

            speeds = arr[:,1]
            voltages = arr[:,2]
            times = arr[:,0]

            # == Часть 1: текущий график МК по парам ==
            indices_50 = np.where(speeds == 50)[0]
            indices_minus_50 = np.where(speeds == -50)[0]

            if len(indices_50) == 0 or len(indices_minus_50) == 0:
                self.print_to_output("Не найдено значений скорости 50 или -50")
                return

            mk_list = []
            num_pairs = min(len(indices_50), len(indices_minus_50))

            for i in range(num_pairs):
                u_50 = voltages[indices_50[i]]
                u_minus_50 = voltages[indices_minus_50[i]]
                mk = (u_50 - u_minus_50) / 100
                mk_list.append(mk * 1000)  # мВ/(°/с)

            plt.figure(figsize=(8,5))
            plt.plot(range(1, num_pairs+1), mk_list, marker='o', linestyle='-', color='blue')
            plt.xlabel('Номер пары')
            plt.ylabel('МК, мВ/(°/с)')
            plt.title('Масштабный коэффициент по третьему каналу')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            # == Часть 2: график измеренной угловой скорости от времени ==
            if not hasattr(self, 'mk_values'):
                self.print_to_output("Сначала выполните расчёт масштабного коэффициента (функция rashet).")
                return

            
            #mk_converted = self.mk_values / 1000  # теперь В/(°/с)

            # Берем напряжение по 3-му каналу
            mk_converted = self.mk_values #/ 1000  # мВ/(°/с) → В/(°/с)

            voltages = arr[:, 2]           # напряжение (3-й канал)
            measured_speed = arr[:, 1]     # сырые значения скорости

            # Идеальная прямая от min напряжения к max
            x1, y1 = min(voltages), 50     # начало: min U → 50 °/с
            x2, y2 = max(voltages), -50    # конец: max U → -50 °/с

            ideal_voltage = [x1, x2]
            ideal_speed = [y1, y2]

            plt.figure(figsize=(10,5))
            plt.plot(ideal_voltage, ideal_speed, label='Идеальная угловая скорость', color='orange')
            plt.plot(voltages, measured_speed, label='Сырые измерения', linestyle='--', color='black')
            plt.xlabel('Напряжение, В')
            plt.ylabel('Угловая скорость, °/с')
            plt.title('Зависимость скорости от напряжения (3-й канал)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            self.print_to_output(f"▶ MK из rashet: {self.mk_values}")
            self.print_to_output(f"▶ Пример напряжения (3-й канал): {voltages[:5]}")
        except Exception as e:
            self.print_to_output(f"Ошибка при построении графиков: {e}")

    def show_asymmetry(self):
        import numpy as np

        # Загружаем данные из json с путём к файлу MK
        data = read_json("paths_and_coords.json")
        file_path = data.get("MK")
        if not file_path:
            self.print_to_output("Файл MK не загружен.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[3:]  # пропускаем 3 заголовка

            arr = np.loadtxt(lines)

            rate = arr[:, 1]
            voltages = arr[:, 2:3]  # только 3-й канал (сохраняем размерность)

            # Фильтрация строк, где rate != 0
            mask = rate != 0
            if np.sum(mask) == 0:
                self.print_to_output("Ошибка: все значения rate равны нулю!")
                return

            rate_filtered = rate[mask]
            voltages_filtered = voltages[mask]

            # Рассчитываем масштабный коэффициент (мВ/(°/с)) по 3-му каналу
            mk_values = (voltages_filtered[:, 0] / rate_filtered) * 1000  # 1D массив

            if len(mk_values) < 2:
                self.print_to_output("Недостаточно данных для расчёта асимметрии по каналу.")
                return

            mean_val = np.nanmean(mk_values)
            if mean_val == 0:
                self.print_to_output("Среднее значение равно нулю, нельзя вычислить асимметрию.")
                return

            asymmetry = np.nanmean(np.abs(mk_values - mean_val) / mean_val) * (-1)
            asymmetry_div_1000 = float(asymmetry) / 1000  # Делим на 1000
            self.print_to_output(f"Асимметрия по 3-му каналу: {asymmetry_div_1000:.6f} %")

        except Exception as e:
            self.print_to_output(f"Ошибка при расчёте асимметрии: {e}")

    def calculate_zero_offset(self):
        import numpy as np
        try:
            data = read_json("paths_and_coords.json")
            file_path = data.get("MK")
            if not file_path:
                self.print_to_output("Файл MK не загружен.")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[3:]  # пропускаем первые 3 строки заголовка

            data = np.loadtxt(lines)

            rate = data[:, 1]
            voltages = data[:, 2:]  # все каналы

            zero_rate_mask = rate == 0
            if not np.any(zero_rate_mask):
                self.print_to_output("Нет строк с rate=0 для расчёта смещения нуля.")
                return

            zero_offset_values = voltages[zero_rate_mask, 2]  # только 3-й канал, индекс 2

            zero_offset_mean = np.nanmean(zero_offset_values) * 1000  # умножаем на 1000 (мВ)

            self.print_to_output(f"Смещение нуля (мВ) по 3-му каналу: {zero_offset_mean:.4f}")

        except Exception as e:
            self.print_to_output(f"Ошибка при расчёте смещения нуля: {e}")

    def plot_mk_nonlinearity(self):
        import matplotlib.pyplot as plt
        import numpy as np
        from io import StringIO

        try:
            data = read_json("paths_and_coords.json")
            file_path = data.get("MK")
            if not file_path:
                self.print_to_output("Файл MK не найден в paths_and_coords.json")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            cleaned_lines = [line for i, line in enumerate(lines) if i >= 3]
            arr = np.loadtxt(StringIO(''.join(cleaned_lines)))

            rate = arr[:, 1]
            voltages = arr[:, 2]  # третий канал

            mask = rate != 0
            if np.sum(mask) == 0:
                self.print_to_output("Все значения rate равны нулю!")
                return

            rate_filtered = rate[mask]
            voltages_filtered = voltages[mask]

            mk_values = (voltages_filtered / rate_filtered) * 1000  # масштабный коэффициент (мВ/(°/с))

            mean_mk = np.mean(mk_values)
            nonlinearity_per_row = 100 * (mk_values - mean_mk) /( mean_mk * 100)  # в %
             # Делим значения на 1000
            nonlinearity_per_row_scaled = nonlinearity_per_row / 1000
            x = range(1, len(nonlinearity_per_row_scaled) + 1)

            plt.figure(figsize=(8,5))
            plt.plot(x, nonlinearity_per_row_scaled, marker='o', linestyle='-', color='orange')
            plt.xlabel('Номер строки')
            plt.ylabel('Нелинейность, %')
            plt.title('Нелинейность масштабного коэффициента (3-й канал) по строкам')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            self.print_to_output(f"Ошибка при построении графика нелинейности: {e}")

    def plot_raw_data(self):
        if self.drift_data is None:
            self.print_to_output("Данные дрейфа не загружены!")
            return
        plt.figure()
        plt.plot(self.drift_data[:,0], self.drift_data[:,1], label='Сырые данные (°/с)')
        plt.xlabel('Время (с)')
        plt.ylabel('Угол скорости (°/с)')
        plt.title('График сырых измерений')
        plt.legend()
        plt.grid()
        plt.show()   

    def calculate_zero_offset_drift(self):
        if self.drift_data is None:
            self.print_to_output("Данные дрейфа не загружены!")
            return

        # Столбец 2 — это второй канал (нумерация с 0)
        zero_offset = np.mean(self.drift_data[:, 2])

        self.print_to_output(f"Смещение нуля по 2-му каналу: {zero_offset:.6f} °/с")

    def calculate_trend(self):
        if self.drift_data is None:
            self.print_to_output("Данные дрейфа не загружены!")
            return

        t = self.drift_data[:, 0]       # Время (секунды)
        y = self.drift_data[:, 2]       # Канал 2 (индекс 2)

        coeffs = np.polyfit(t, y, 1)    # Линейная регрессия: y = k*t + b
        slope = coeffs[0]               # Скат (°/с²)
        slope_hour = slope * 3600**2    # Переводим в °/ч²

        self.print_to_output(f"Тренд угловой скорости по 2-му каналу: {slope_hour:.6f} °/ч²")

    def allan_variance(self, data, rate, taus=None):
        import numpy as np

        n = len(data)
        if taus is None:
            max_m = n // 2
            taus = np.arange(1, max_m)

        allan_devs = []

        for tau in taus:
            m = int(tau * rate)
            if m == 0 or m * 2 >= len(data):
                continue
            n_blocks = len(data) // m
            avgs = [np.mean(data[i*m:(i+1)*m]) for i in range(n_blocks)]
            avgs = np.array(avgs)
            diff = np.diff(avgs)
            allan_var = 0.5 * np.mean(diff**2)
            allan_devs.append(np.sqrt(allan_var))

        taus = np.array(taus[:len(allan_devs)])  # обрезаем до длины
        allan_devs = np.array(allan_devs)
        return taus, allan_devs

    def estimate_allan_params(self, taus, allan_dev):
        """
        Аппроксимация параметров ARW, Bias Instability и RRW
        на трех логарифмических интервалах.
        """
        log_tau = np.log10(taus)
        log_dev = np.log10(allan_dev)
        n = len(taus)

        def linreg(x, y):
            A = np.vstack([x, np.ones(len(x))]).T
            k, b = np.linalg.lstsq(A, y, rcond=None)[0]
            return k, b

        # Интервалы делим примерно на три части
        low_idx = slice(0, n//3)
        mid_idx = slice(n//3, 2*n//3)
        high_idx = slice(2*n//3, n)

        _, b_low = linreg(log_tau[low_idx], log_dev[low_idx])
        _, b_mid = linreg(log_tau[mid_idx], log_dev[mid_idx])
        _, b_high = linreg(log_tau[high_idx], log_dev[high_idx])

        ARW = 10**b_low
        BiasInst = 10**b_mid
        RRW = 10**b_high

        return ARW, BiasInst, RRW

    def plot_allan_deviation(self):
        if self.drift_data is None or self.sampling_rate is None:
            self.print_to_output("Данные дрейфа не загружены или не задана частота дискретизации!")
            return
        data = self.drift_data[:,1]
        taus, allan_dev = self.allan_variance(data, self.sampling_rate)
        plt.figure()
        plt.loglog(taus, allan_dev, label='Девиация Аллана')
        plt.xlabel('τ, с')
        plt.ylabel('σ(τ), °/с')
        plt.title('Девиация Аллана')
        plt.grid(True, which='both')
        plt.legend()
        plt.show()

    def plot_allan_approximation(self):
        import numpy as np
        import matplotlib.pyplot as plt

        if self.drift_data is None or self.sampling_rate is None:
            self.print_to_output("Данные дрейфа не загружены или не задана частота дискретизации!")
            return

        try:
            data = self.drift_data[:, 1]  # канал 1 (второй столбец)
            fs = self.sampling_rate
            N = len(data)
            max_m = N // 2

            # Логарифмически распределенные интервалы усреднения
            m_values = np.unique(np.round(np.logspace(0, np.log10(max_m), 2000)).astype(int))
            m_values = m_values[m_values > 0]
            tau = m_values / fs

            adev = []
            for m in m_values:
                K = N // m
                if K < 2:
                    continue
                reshaped = data[:K*m].reshape((K, m))
                means = np.mean(reshaped, axis=1)
                diffs = np.diff(means)
                sigma = np.sqrt(np.sum(diffs**2) / (2 * (K - 1)))
                adev.append(sigma)

            adev = np.array(adev)
            tau = tau[:len(adev)]

            # ---- Анализ ----
            min_idx = np.argmin(adev)
            tau_min = tau[min_idx]
            bias_instability = adev[min_idx]

            mask_white = tau < tau_min
            mask_rrw = tau > tau_min

            ARW = None
            RRW = None

            plt.figure(figsize=(9, 5))
            plt.loglog(tau, adev, 'b', label='Данные')
            plt.scatter(tau_min, bias_instability, c='r', label='Bias Instability')

            # ARW аппроксимация
            if np.sum(mask_white) >= 2:
                p_white = np.polyfit(np.log10(tau[mask_white]), np.log10(adev[mask_white]), 1)
                k_arw, b_arw = p_white
                y_fit_arw = 10 ** b_arw * tau[mask_white] ** k_arw
                plt.loglog(tau[mask_white], y_fit_arw, 'g--', label=f'ARW ~ τ^{k_arw:.2f}')

            # RRW аппроксимация
            if np.sum(mask_rrw) >= 2:
                p_rrw = np.polyfit(np.log10(tau[mask_rrw]), np.log10(adev[mask_rrw]), 1)
                k_rrw, b_rrw = p_rrw
                y_fit_rrw = 10 ** b_rrw * tau[mask_rrw] ** k_rrw
                plt.loglog(tau[mask_rrw], y_fit_rrw, 'm--', label=f'RRW ~ τ^{k_rrw:.2f}')

            plt.xlabel(r'$\tau$, с')
            plt.ylabel(r'$\sigma(\tau)$, °/с')
            plt.title('Аппроксимация девиации Аллана')
            plt.grid(True, which='both')
            plt.legend()
            plt.tight_layout()
            plt.show()

            # Текстовый вывод
            self.print_to_output(f"Bias Instability: {bias_instability:.4e} °/с при τ = {tau_min:.2f} с")
            if ARW:
                self.print_to_output(f"ARW наклон: {k_arw:.2f}, смещение: 10^{b_arw:.2f}")
            if RRW:
                self.print_to_output(f"RRW наклон: {k_rrw:.2f}, смещение: 10^{b_rrw:.2f}")

        except Exception as e:
            self.print_to_output(f"Ошибка при построении или аппроксимации: {e}")
            
    def calculate_allan_parameters(self):
        if self.drift_data is None or self.sampling_rate is None:
            self.print_to_output("Данные дрейфа не загружены или не задана частота дискретизации!")
            return
        data = self.drift_data[:,1]
        taus, allan_dev = self.allan_variance(data, self.sampling_rate)

        try:
            ARW, BiasInst, RRW = self.estimate_allan_params(taus, allan_dev)
            self.print_to_output(f"Параметры, определённые по аппроксимации Девиации Аллана:")
            self.print_to_output(f"Angular Random Walk (ARW): {ARW:.6e} °/с/√Hz")
            self.print_to_output(f"Bias Instability: {BiasInst:.6e} °/с")
            self.print_to_output(f"Rate Random Walk (RRW): {RRW:.6e} °/с/√Hz")
        except Exception as e:
            self.print_to_output(f"Ошибка при расчёте параметров: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()