import os
from statistics import stdev
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
import json
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from tkinter import messagebox
from docx import Document
from docx.shared import Inches
import shutil

from main import *
from graphs import *
import os
import pandas as pd


def save_data_to_json(key, data):
    """
    Сохраняет данные в JSON файл под указанным ключом.
    
    :param key: Ключ для записи данных (например, 'true_coords', 'true_speeds')
    :param data: Данные для сохранения (например, кортеж с координатами или скоростями)
    """
    try:
        # Загружаем существующие данные из paths.json
        with open('paths_and_coords.json', 'r', encoding='utf-8') as f:
            data_file = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data_file = {}  # Если файл не существует или пустой, создаем новый словарь

    # Обновляем данные по ключу
    data_file[key] = data

    # Сохраняем данные обратно в JSON файл
    with open('paths_and_coords.json', 'w', encoding='utf-8') as f:
        json.dump(data_file, f, indent=4, ensure_ascii=False)

    print(f"Данные сохранены: {key} -> {data}")

def read_json(file_name):
    """
    Считывает данные из json файла и возвращает словарь.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при чтении файла {file_name}: {e}")
        return {}  # Возвращаем пустой словарь в случае ошибки


def analyze():
    """Обновленный метод анализа с фильтрацией нулевых строк."""
    data = read_json("paths_and_coords.json")
    
    # Проверяем, существует ли ключ "solution"
    if "solution" in data:
        solution_file = data["solution"]
        # Прочее выполнение анализа
    else:
        print("Ошибка: ключ 'solution' отсутствует в данных")


#-----------------------------------------------------------------------------------------------------------------------------#
                                                        #Интерфейс программы
#-----------------------------------------------------------------------------------------------------------------------------#



class Windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("Расчет и синтез приборов")
        self.center_window(900, 700)
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in [DataInputPage, ]:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(DataInputPage)


    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class DataInputPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

  
        label = tk.Label(self, text="Интерфейс управления")
        label.grid(row=0, column=1,  padx=10, pady=10)
        label = tk.Label(self, text="Ввод и обработка данных")
        label.grid(row=0, column=0,  padx=10, pady=10)

            

        self.upload_button_solution = tk.Button(self, text="Загрузить файл дрейфа", command=self.upload_file_dreif, width=27) #solution
        self.upload_button_solution.grid(row=3, column=0, padx=10, pady=10)

        self.upload_button_coo = tk.Button(self, text="Загрузить файл МК", command=self.upload_file_MK, width=27) #coo
        self.upload_button_coo.grid(row=2, column=0, padx=10, pady=10)

        analyze_button = tk.Button(self, text="Произвести расчет", command=self.rashet, width=27) #Анализировать телеметрию
        analyze_button.grid(row=5, column=0,  padx=10, pady=10)

        button_plot_coords = tk.Button(self, text="Графики МК и Дрейфа", command=self.plot, width=27)
        button_plot_coords.grid(row=4, column=0, padx=10, pady=10)


        # Поле для вывода информации, как терминал
        self.grid_columnconfigure(0, weight=500)  # Первая колонка будет растягиваться
        self.grid_rowconfigure(11, weight=50)   # Строка с текстовым полем также растягивается

        # Поле для вывода информации, как терминал
        self.output_text = tk.Text(self, height=16)
        self.output_text.grid(row=11, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.output_text.config(state=tk.DISABLED)  

        # Кнопка отчистки поля
        analyze_button = tk.Button(self, text="Стереть", command=self.erase, width=27)
        analyze_button.grid(row=6, column=1,  padx=100, pady=15)


        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)




        #-----------------------------------------------------------------------------------------------------------------------------#
                                                                #Интерфейс управления
        #-----------------------------------------------------------------------------------------------------------------------------#


    
    def upload_file_MK(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл MK.dat",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )

        if file_path:
            self.print_to_output(f"Файл MK загружен: {file_path}")
            save_data_to_json("MK", file_path)

            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Удаляем 1-ю, 2-ю и 3-ю строки (индексы 0, 1, 2)
                cleaned_lines = [line for i, line in enumerate(lines) if i not in (0, 1, 2)]

                from io import StringIO
                data = np.loadtxt(StringIO(''.join(cleaned_lines)))

                '''print("▶ Первые 5 значений:")
                print(data[:5])
                print("▶ Размерность:", data.shape)'''

                self.print_to_output(f"Пример данных: {data[:5]}")
                self.print_to_output(f"Всего значений: {len(data)}")

            except Exception as e:
                self.print_to_output(f"Ошибка при чтении данных из файла: {e}")
                print("❌ Ошибка при чтении .dat файла:", e)

    def upload_file_dreif(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл Дрейф",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )

        if file_path:
            self.print_to_output(f"Файл Дрейф загружен: {file_path}")
            save_data_to_json("Дрейф", file_path)

            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Удаляем первые 3 строки (индексы 0, 1, 2)
                cleaned_lines = [line for i, line in enumerate(lines) if i not in (0, 1, 2)]

                # Чтение очищенного содержимого
                from io import StringIO
                data = np.loadtxt(StringIO(''.join(cleaned_lines)))

                '''  # Вывод для проверки
                print("▶ Первые 5 значений из файла Дрейф:")
                print(data[:5])
                print("▶ Размерность:", data.shape)'''

                self.print_to_output(f"Пример данных: {data[:5]}")
                self.print_to_output(f"Всего значений: {len(data)}")

            except Exception as e:
                self.print_to_output(f"Ошибка при чтении файла Дрейф: {e}")
                print("❌ Ошибка при чтении .dat файла (Дрейф):", e)


#-----------------------------------------------------------------------------------------------------------------------------#
                                                    #Вывод в окно программы
#-----------------------------------------------------------------------------------------------------------------------------#


    

    def print_to_output(self, message):
        """Метод для вывода информации в поле вывода"""
        self.output_text.config(state=tk.NORMAL)  # Разрешаем редактирование
        self.output_text.insert(tk.END, message + "\n")  # Вставляем новое сообщение
        self.output_text.config(state=tk.DISABLED)  # Возвращаем поле в режим только для чтения
        self.output_text.yview(tk.END)  # Прокручиваем текст до конца
    
    

    def erase(self):
        """Метод для отчистки поля вывода"""
        self.output_text.config(state=tk.NORMAL)  # Разрешаем редактирование
        self.output_text.delete('1.0', tk.END)   # Удаляем содержимое
        self.output_text.config(state=tk.DISABLED)  # Снова делаем поле только для чтения

    def rashet(self):   
        self.print_to_output("ЛОХ")

    def plot(self):   
        self.print_to_output("ЛОХ")
    
    

if __name__ == "__main__":
    app = Windows()
    app.mainloop()