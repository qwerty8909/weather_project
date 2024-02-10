import os
from dotenv import load_dotenv
import requests
from django.http import JsonResponse
from django.core.cache import cache
from .models import Weather
from django.utils.timezone import now
from datetime import timedelta
import csv

# Загрузка переменных из файла .env
load_dotenv()

csv_file_path = 'koord_russia.csv'
expired_time = timedelta(minutes=30)


def load_city_coordinates_from_csv():
    # Проверяем кэш перед загрузкой из CSV
    city_coordinates = cache.get('city_coordinates')
    if city_coordinates is None:
        city_coordinates = {}
        with open(csv_file_path, mode='r', encoding='windows-1251') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                city_name = row['Город'].lower()
                lat = float(row['lat'].replace(',', '.'))  # Заменяем запятую на точку и преобразуем в float
                lon = float(row['lng'].replace(',', '.'))  # Заменяем запятую на точку и преобразуем в float
                city_coordinates[city_name] = {"lat": lat, "lon": lon}
        # Кэшируем данные на 24 часа
        cache.set('city_coordinates', city_coordinates, timeout=86400)
    return city_coordinates


def weather_view(request):
    city_name = request.GET.get('city', '').lower()
    if not city_name:
        return JsonResponse({'error': 'City parameter is required'}, status=400)

    city_to_coords = load_city_coordinates_from_csv()
    if city_name not in city_to_coords:
        return JsonResponse({'error': f'Coordinates for the city {city_name} not found'}, status=404)

    lat = city_to_coords[city_name]["lat"]
    lon = city_to_coords[city_name]["lon"]

    # Проверяем наличие актуальных данных в базе
    recent_weather = Weather.objects.filter(city=city_name, updated_at__gte=now() - expired_time).first()

    if recent_weather:
        time_difference = recent_weather.updated_at + expired_time - now()
        # Используем данные из базы данных
        response_data = {
            'temperature': recent_weather.temperature,
            'pressure': recent_weather.pressure,
            'wind_speed': recent_weather.wind_speed,
            'expired': int(time_difference.total_seconds())
        }
    else:
        # Делаем запрос к API Яндекса за новыми данными
        api_key = os.getenv('WEATHER_API_KEY')
        url = f'https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}'

        try:
            response = requests.get(url, headers={'X-Yandex-API-Key': api_key})

            if response.status_code == 200:
                data = response.json()

                # Сохраняем новые данные о погоде в базу данных
                new_weather_data = Weather.objects.create(
                    city=city_name,
                    temperature=data["fact"]["temp"],
                    pressure=data["fact"]["pressure_mm"],
                    wind_speed=data["fact"]["wind_speed"]
                )

                response_data = {
                    'temperature': new_weather_data.temperature,
                    'pressure': new_weather_data.pressure,
                    'wind_speed': new_weather_data.wind_speed,
                    'expired': int(expired_time.total_seconds())

                }
            else:
                return JsonResponse({'error': f'Weather API error: {response.status_code}'}, status=response.status_code)

        except requests.RequestException as e:  # Обработка возможных ошибок при запросе
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(response_data)
