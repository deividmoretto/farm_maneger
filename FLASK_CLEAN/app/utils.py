# app/utils.py
import random

def get_sensor_data():
    temperature = round(random.uniform(15.0, 30.0), 2)  # Temperatura entre 15 e 30 graus Celsius
    humidity = round(random.uniform(30.0, 70.0), 2)  # Umidade entre 30% e 70%
    return temperature, humidity