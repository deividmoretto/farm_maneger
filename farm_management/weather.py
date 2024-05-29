import http.client
import json
import ssl
import certifi

def get_weather_forecast(lat, lon, start, end):
    context = ssl.create_default_context(cafile=certifi.where())
    conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com", context=context)

    headers = {
        'x-rapidapi-key': "98bac9efaemshbb492e7779f0433p18fe14jsna0a0f74a6c97",
        'x-rapidapi-host': "meteostat.p.rapidapi.com"
    }

    url = f"/point/monthly?lat={lat}&lon={lon}&start={start}&end={end}"
    conn.request("GET", url, headers=headers)

    try:
        res = conn.getresponse()
        data = res.read()
        weather_data = json.loads(data.decode("utf-8"))

        # Supondo que a estrutura do JSON retornado tenha esses campos
        return weather_data
    except Exception as e:
        print(f'Error occurred: {e}')
        return None
