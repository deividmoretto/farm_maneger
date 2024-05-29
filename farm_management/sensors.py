import requests

def read_sensor_data(sensor_id):
    # Simular leitura de dados do sensor
    response = requests.get(f"http://api.sensors.com/{sensor_id}")
    data = response.json()
    return data
