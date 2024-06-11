import requests

def read_sensor_data(sensor_id):
    try:
        # Simular leitura de dados do sensor
        response = requests.get(f"http://api.sensors.com/{sensor_id}")
        response.raise_for_status()  # Lança um erro para códigos de status HTTP 4xx/5xx
        data = response.json()
        return data
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Erro de conexão: {conn_err}')  # Manipula erros de conexão
    except requests.exceptions.HTTPError as http_err:
        print(f'Erro HTTP: {http_err}')  # Manipula erros HTTP
    except requests.exceptions.RequestException as req_err:
        print(f'Erro de solicitação: {req_err}')  # Manipula outros erros de solicitação
    except ValueError as json_err:
        print(f'Erro de decodificação JSON: {json_err}')  # Manipula erros de decodificação JSON
        print(f'Conteúdo da resposta: {response.text}')  # Exibe o conteúdo da resposta para depuração

    return None  # Retorna None em caso de erro
