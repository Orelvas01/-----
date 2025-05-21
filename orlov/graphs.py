from matplotlib.pylab import eig as  plt
import pandas as pd
import numpy as np
from datetime import datetime
import plotly
import plotly.graph_objects as go 
import os
from plotly.io import write_image

def parse_time_string_to_hms(time_string):
    """
    Преобразует строку времени в формате '7:02:08.993' в строку 'HH:MM:SS'.
    :param time_string: строка времени в формате '%H:%M:%S.%f'
    :return: строка времени в формате 'HH:MM:SS'
    """
    try:
        parsed_time = datetime.strptime(time_string.strip(), '%H:%M:%S.%f')
        return parsed_time.strftime('%H:%M:%S')  # Форматируем как 'HH:MM:SS'
    except ValueError:
        print(f"Некорректное значение времени: {time_string}")
        return None
    





