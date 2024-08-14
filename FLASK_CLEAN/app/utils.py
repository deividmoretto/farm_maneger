# app/utils.py
import random

def get_sensor_data():
    """
    Gera dados simulados de sensores para temperatura e umidade.
    A função simula a leitura de dados de sensores para temperatura e umidade,
    gerando valores aleatórios dentro de um intervalo predefinido. Esses valores
    são arredondados para duas casas decimais.

    """
   
    temperature = round(random.uniform(15.0, 30.0), 2)  # Gera um valor de temperatura aleatório entre 15.0 e 30.0 graus Celsius
    humidity = round(random.uniform(30.0, 70.0), 2) # Gera um valor de umidade aleatório entre 30.0% e 70%
    return temperature, humidity # Retorna os valores de temperatura e umidade como uma tupla
